import re
import os
import json
import gzip
import logging
import pymongo
import configparser
import urllib.parse
from typing import List
from flask import Flask, jsonify, make_response, abort, render_template, request
from pymongo.database import Database
from pymongo.collation import Collation, CollationStrength
from multiprocessing import Pool

# Gets production flag
IS_DEBUG: bool = os.environ.get('DEBUG', 'true') == 'true'
PROCESS=8

# Gets configuration
Config = configparser.ConfigParser()
Config.read("config.txt")

# Sets logging level
logging.getLogger("urllib3").setLevel(logging.DEBUG)

# In development logs in console, in production logs in file
if not IS_DEBUG:
    logging.basicConfig(filename=Config.get('log', 'file'), filemode='a',
                        format='%(asctime)s\t%(name)s\t%(levelname)s\t%(message)s', datefmt='%d-%b-%y %H:%M:%S',
                        level=logging.DEBUG)
logging.info('BioAPI is up and running')

# Common response header
headers = {"Content-Type": "application/json"}


def get_mongo_connection() -> Database:
    """
    Gets Mongo connection using config.txt file if DEBUG env var is 'true', or all the env variables in case of prod
    (DEBUG = 'false')
    :return: Database instance
    """
    try:
        if IS_DEBUG:
            host = Config.get('mongodb', 'host')
            mongo_port = Config.get('mongodb', 'port')
            user = Config.get('mongodb', 'user')
            password = Config.get('mongodb', 'pass')
            db = Config.get('mongodb', 'db_name')
        else:
            host = os.environ.get('MONGO_HOST')
            mongo_port = os.environ.get('MONGO_PORT')
            user = os.environ.get('MONGO_USER')
            password = os.environ.get('MONGO_PASSWORD')
            db = os.environ.get('MONGO_DB')

            if not host or not mongo_port or not db:
                logging.error(f'Host ({host}), port ({mongo_port}) or db ({db}) is invalid', exc_info=True)
                exit(-1)

        mongo_client = pymongo.MongoClient(f"mongodb://{user}:{password}@{host}:{mongo_port}/?authSource=admin")
        return mongo_client[db]
    except Exception as e:
        logging.error("Database connection error." + str(e), exc_info=True)
        exit(-1)


mydb = get_mongo_connection()

def map_gene(gene: str) -> List[str]:
    """
    Gets all the aliases for a specific gene
    :return List of aliases
    """
    #db=get_mongo_connection()
    collection_hgnc = mydb["hgnc"]  # HGNC collection

    dbs = ["hgnc_id", "symbol", "alias_symbol", "prev_symbol", "entrez_id", "ensembl_gene_id", "vega_id",
           "ucsc_id", "ena", "refseq_accession", "ccds_id", "uniprot_ids", "cosmic", "omim_id", "mirbase", "homeodb",
           "snornabase", "bioparadigms_slc", "orphanet", "pseudogene", "horde_id", "merops", "imgt", "iuphar",
           "kznf_gene_catalog", "mamit-trnadb", "cd", "lncrnadb", "enzyme_id", "intermediate_filament_db", "agr"]

    # Generates query
    or_search = [{db: gene} for db in dbs]
    query = {'$or': or_search}
    coll=Collation(locale='en', strength=CollationStrength.SECONDARY)
    docs = collection_hgnc.find(query, collation=coll)
    return [doc["symbol"] for doc in docs]


def get_potential_gene_symbols(query_string, limit_elements):
    er = re.compile("^" + re.escape(query_string), re.IGNORECASE)
    collection_hgnc = mydb["hgnc"]  # HGNC collection
    dbs = ["hgnc_id", "symbol", "entrez_id", "ensembl_gene_id", "vega_id",
           "ucsc_id", "ena", "refseq_accession", "ccds_id", "uniprot_ids", "cosmic", "omim_id", "mirbase", "homeodb",
           "snornabase", "bioparadigms_slc", "orphanet", "pseudogene", "horde_id", "merops", "imgt", "iuphar",
           "kznf_gene_catalog", "mamit-trnadb", "cd", "lncrnadb", "enzyme_id", "intermediate_filament_db", "agr"]

    res = []
    limit_elements_full = False
    for db in dbs:
        query = {db: {"$regex": er}}
        projection = {'_id': 0, db: 1}
        docs = collection_hgnc.find(query, projection)
        for doc in docs:
            if len(res) < limit_elements:
                res.append(doc[db])
                # Removes duplicated (it's possible that different DBs have the same gene symbol)
                res = list(dict.fromkeys(res))
            else:
                limit_elements_full = True
                break
        if limit_elements_full:
            break
    return res


def search_gene_group(gen):  # AGREGAR LO QUE PASA SI NO PERTENECE A NINGUN gene_group_id (EJ gen:AADACP1)
    results = {'locus_group': None, 'locus_type': None, 'gene_group': None, 'gene_group_id': None}
    collection_hgnc = mydb["hgnc"]  # HGNC collection
    query = {"symbol": gen, "status": "Approved"}

    # Makes the query to the DB
    docs_cursor = collection_hgnc.find(query)
    docs: List = list(docs_cursor)
    if len(docs) == 1:
        results['locus_group'] = docs[0]['locus_group']
        results['locus_type'] = docs[0]['locus_type']
        if "gene_group" in list(docs[0].keys()):
            if type(docs[0]['gene_group']) == list:
                results['gene_group'] = docs[0]['gene_group']
                results['gene_group_id'] = docs[0]['gene_group_id']
            else:
                results['gene_group'] = [docs[0]['gene_group']]
                results['gene_group_id'] = [docs[0]['gene_group_id']]

    return results


def search_genes_in_same_group(group_id: int):
    collection_hgnc = mydb["hgnc"]  # HGNC collection
    query = {'gene_group_id': group_id}
    projection = {'_id': 0, 'symbol': 1}
    docs = collection_hgnc.find(query, projection)
    return [doc["symbol"] for doc in docs]


def get_genes_of_pathway(pathway_id, pathway_source):
    collection_cpdb = mydb["cpdb"]  # CPDB collection
    ps = re.compile("^" + pathway_source + "$", re.IGNORECASE)
    query = {'external_id': str(pathway_id), "source": {"$regex": ps}}
    doc = collection_cpdb.find_one(query)
    return doc["hgnc_symbol_ids"] if doc is not None else []


def get_pathways_of_gene(gene):
    collection_cpdb = mydb["cpdb"]  # CPDB collection
    query = {'hgnc_symbol_ids': gene}
    projection = {'_id': 0, 'pathway': 1, 'external_id': 1, 'source': 1}
    docs = collection_cpdb.find(query, projection)
    return [str(doc) for doc in docs]


def get_expression_from_gtex(tissue: str, genes: List) -> List:
    collection = mydb["gtex_" + tissue]  # Connects to specific tissue's collection
    query = {'gene': {'$in': genes}}
    projection = {'_id': 0, 'expression': 1, 'gene': 1, 'sample_id': 1}
    docs = collection.find(query, projection)
    temp = {}
    for doc in docs:
        if doc["sample_id"] not in temp:
            temp[doc["sample_id"]] = {}
        temp[doc["sample_id"]][doc["gene"]] = doc["expression"]
    results = [temp[sample] for sample in temp.keys()]
    return results


def create_app():
    # Creates and configures the app
    flask_app = Flask(__name__, instance_relative_config=True)

    # Endpoints
    @flask_app.route("/")
    def homepage():
        return render_template('homePage.html')

    @flask_app.route("/ping")
    def ping_ok():
        """To use as healthcheck by Docker"""
        output = "ok"
        return make_response(output, 200, headers)

    @flask_app.route("/bioapi-map")
    def list_routes():
        """Lists all BioAPI endpoints"""
        output = {"endpoints": []}
        for rule in flask_app.url_map.iter_rules():
            methods = ','.join(rule.methods)
            line = urllib.parse.unquote("{:50s} {:20s} {}".format(rule.endpoint, methods, rule))
            output["endpoints"].append(line)
        return make_response(output, 200, headers)

    @flask_app.route("/gene-symbol/<gene_id>", methods=['GET'])
    def gene_symbol(gene_id: str):
        """Receives a gene ID in any standard and returns the standardized gene ID. In case it is not found it
        returns an empty list."""
        response = {gene_id: []}
        try:
            gv = map_gene(gene_id)
            if len(gv) == 0:
                abort(404, "invalid gene identifier")
            response[gene_id] = gv
        except TypeError as e:
            abort(400, e)
        except ValueError as e:
            abort(400, e)
        except KeyError as e:
            abort(400, e)
        return make_response(response, 200, headers)

    @flask_app.route("/genes-symbols", methods=['POST'])
    def genes_symbols():
        """Receives a list of genes IDs in any standard and returns the standardized corresponding genes IDs.
        In case it is not found it returns an empty list for the specific not found gene."""
        response = {}
        if request.method == 'POST':
            tem_list = []
            def add_result(res):
                tem_list.append(res)

            buscar_gen = Pool(processes = PROCESS)

            body = request.get_json()
            if "genes_ids" not in list(body.keys()):
                abort(400, "genes_ids is mandatory")

            genes_ids = body['genes_ids']
            if type(genes_ids) != list:
                abort(400, "genes_ids must be a list")

            try:
                res = [buscar_gen.apply_async(map_gene, args = (gene, ), callback=add_result) for gene in genes_ids]
                buscar_gen.close()  # close the process pool
                buscar_gen.join() # wait for all tasks to complete
                for i in range(0,len(genes_ids)):
                    response[genes_ids[i]]=res[i].get()
            except Exception as e:
                abort(400, e)
        return make_response(response, 200, headers)

    @flask_app.route("/genes-symbols-finder", methods=['GET'])
    def genes_symbol_finder():
        """Takes a string of any length and returns a list of genes that contain that search criteria."""
        query = None  # To prevent MyPy warning
        if "query" not in request.args:
            abort(400, "'query' parameter is mandatory")
        else:
            query = request.args.get('query')

        limit = 50
        if "limit" in request.args:
            if request.args.get('limit').isnumeric():
                limit = int(request.args.get('limit'))
            else:
                abort(400, "'limit' parameter must be a numeric value")

        response = {}  # To prevent MyPy warning
        try:
            possibles_symbols = get_potential_gene_symbols(query, limit)
            response = {"potential_gene_symbols": possibles_symbols}
        except TypeError as e:
            abort(400, e)
        except ValueError as e:
            abort(400, e)
        except KeyError as e:
            abort(400, e)
        return make_response(response, 200, headers)

    @flask_app.route("/genes-same-group/<gene_id>", methods=['GET'])
    def genes_of_the_same_family(gene_id):
        response = {"gene_id": None, "groups": [], "locus_group": None, "locus_type": None}
        try:
            mapped_gene = map_gene(gene_id)
            if len(mapped_gene) == 0:
                abort(404, "invalid gene identifier")
            elif len(mapped_gene) >= 2:
                joined = ",".join(mapped_gene)
                abort(
                    400,
                    f"ambiguous gene identifier. "
                    f"The identifier may refer to more than one HGNC-approved gene ({joined})"
                )
            approved_symbol = mapped_gene[0]
            response["gene_id"] = approved_symbol
            gene_group = search_gene_group(approved_symbol)
            response['locus_group'] = gene_group['locus_group']
            response['locus_type'] = gene_group['locus_type']
            if gene_group['gene_group_id'] is not None:
                response["groups"] = []
                for i in range(0, len(gene_group['gene_group_id'])):
                    g = {
                        "gene_group_id": gene_group['gene_group_id'][i],
                        "gene_group": gene_group['gene_group'][i],
                        "genes": search_genes_in_same_group(gene_group['gene_group_id'][i])
                    }
                    response["groups"].append(g)

        except TypeError as e:
            abort(400, e)
        except ValueError as e:
            abort(400, e)
        except KeyError as e:
            abort(400, e)
        return make_response(response, 200, headers)

    @flask_app.route("/genes-pathways/<pathway_source>/<pathway_id>", methods=['GET'])
    def pathways_of_genes(pathway_source, pathway_id):
        response = {"genes": get_genes_of_pathway(pathway_id, pathway_source)}
        return make_response(response, 200, headers)

    @flask_app.route("/genes-pathways-intersection", methods=['POST'])
    def genes_of_pathways():
        if request.method == 'POST':
            body = request.get_json()
            if "genes_ids" not in list(body.keys()):
                abort(400, "genes_ids is mandatory")
            genes_ids = body['genes_ids']
            if type(genes_ids) != list:
                abort(400, "genes_ids must be a list")
            if len(genes_ids) == 0:
                abort(400, "genes_ids must contain at least one gene symbol")

            pathways_tmp = [get_pathways_of_gene(gene) for gene in genes_ids]
            pathways_intersection = list(set.intersection(*map(set, pathways_tmp)))
            response = {"pathways": []}
            for e in pathways_intersection:
                r = json.loads(e.replace("\'", "\""))
                response["pathways"].append(r)
            return make_response(response, 200, headers)

    @flask_app.route("/genes-expression", methods=['POST'])
    def expression_data_from_gtex():
        if request.method == 'POST':
            body = request.get_json()
            body_keys = list(body.keys())

            if "genes_ids" not in body_keys:
                abort(400, "genes_ids is mandatory")

            genes_ids = body['genes_ids']
            if type(genes_ids) != list:
                abort(400, "genes_ids must be a list")
            if len(genes_ids) == 0:
                abort(400, "genes_ids must contain at least one gene symbol")
            if "tissue" not in body_keys:
                abort(400, "tissue is mandatory")

            tissue = body['tissue']
            type_response = None  # To prevent MyPy warning
            if "type" in body_keys:
                if body['type'] not in ["gzip", "json"]:
                    abort(400, "allowed values for the 'type' key are 'json' or 'gzip'")
                else:
                    type_response = body['type']
            else:
                type_response = 'json'

            expression_data = get_expression_from_gtex(tissue, genes_ids)

            if type_response == "gzip":
                content = gzip.compress(json.dumps(expression_data).encode('utf8'), 5)
                response = make_response(content)
                response.headers['Content-length'] = len(content)
                response.headers['Content-Encoding'] = 'gzip'
                return response
            return jsonify(expression_data)

    # Error handling
    @flask_app.errorhandler(400)
    def bad_request(e):
        return jsonify(error=str(e)), 400

    @flask_app.errorhandler(404)
    def not_found(e):
        return jsonify(error=str(e)), 404

    return flask_app


app = create_app()

if __name__ == "__main__":
    port_str = os.environ.get('PORT', Config.get('flask', 'port'))
    port = int(port_str)
    app.run(host='localhost', port=port, debug=IS_DEBUG)
