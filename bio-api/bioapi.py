import re
import os
import json
import gzip
import logging
from concurrent.futures import ThreadPoolExecutor
import pymongo
import configparser
import urllib.parse
from typing import List, Dict
from flask import Flask, jsonify, make_response, abort, render_template, request
from pymongo.database import Database
from pymongo.collation import Collation, CollationStrength

# Gets production flag
IS_DEBUG: bool = os.environ.get('DEBUG', 'true') == 'true'

# Number of threads to use in Pool
THREAD_POOL_WORKERS = 8

# BioAPI version
VERSION = '0.1.5'

# Valid pathways sources
PATHWAYS_SOURCES = ["kegg", "biocarta", "ehmn", "humancyc", "inoh", "netpath", "pid", "reactome",
                    "smpdb", "signalink", "wikipathways"]

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

        mongo_client = pymongo.MongoClient(f"mongodb://{user}:{password}@{host}:{mongo_port}/?authSource=admin", serverSelectionTimeoutMS=60)
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
    collection_hgnc = mydb["hgnc"]  # HGNC collection

    dbs = ["hgnc_id", "symbol", "alias_symbol", "prev_symbol", "entrez_id", "ensembl_gene_id", "vega_id",
           "ucsc_id", "ena", "refseq_accession", "ccds_id", "uniprot_ids", "cosmic", "omim_id", "mirbase", "homeodb",
           "snornabase", "bioparadigms_slc", "orphanet", "pseudogene", "horde_id", "merops", "imgt", "iuphar",
           "kznf_gene_catalog", "mamit-trnadb", "cd", "lncrnadb", "enzyme_id", "intermediate_filament_db", "agr"]

    # Generates query
    or_search = [{db: gene} for db in dbs]
    query = {'$or': or_search}
    coll = Collation(locale='en', strength=CollationStrength.SECONDARY)
    docs = collection_hgnc.find(query, collation=coll)
    res = [doc["symbol"] for doc in docs]
    return res


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
        if limit_elements_full:
            break
        query = {db: {"$regex": er}}
        projection = {'_id': 0, db: 1}
        docs = collection_hgnc.find(query, projection)
        for doc in docs:
            if len(res) < limit_elements:
                doc_db = doc[db]
                if type(doc_db) == list:
                    for doc_id in doc_db:
                        if doc_id.upper().startswith(query_string.upper()) and doc_id not in res:
                            res.append(doc_id)
                else:
                    if doc_db not in res:
                        res.append(doc_db)
            else:
                limit_elements_full = True
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
        document = docs[0]

        results['locus_group'] = document['locus_group']
        results['locus_type'] = document['locus_type']

        if "gene_group" in document:
            if type(document['gene_group']) == list:
                results['gene_group'] = document['gene_group']
                results['gene_group_id'] = document['gene_group_id']
            else:
                results['gene_group'] = [document['gene_group']]
                results['gene_group_id'] = [document['gene_group_id']]

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


def get_information_of_genes(genes: List[str]) -> Dict:
    res = {}
    collection_gene_grch37 = mydb["gene_grch37"]
    collection_gene_grch38 = mydb["gene_grch38"]
    collection_gene_oncokb = mydb["oncokb_gene_cancer_list"]
    collection_hgnc = mydb["hgnc"]

    # Generates query
    query = {"hgnc_symbol": {"$in": genes}}
    projection = {'_id': 0, 'description':0, 'hgnc_id': 0, 'entrezgene_id':0, 'ensembl_gene_id':0} # saco los identificadores porque los obtengo desde la coleccion hgnc

    docs_grch37 = collection_gene_grch37.find(query, projection)
    docs_grch38 = collection_gene_grch38.find(query, projection)
    docs_oncokb = collection_gene_oncokb.find(query, projection)
    docs_hgnc = collection_hgnc.find({"symbol": {"$in": genes}})

    for doc_grch38 in docs_grch38:
        res[doc_grch38["hgnc_symbol"]] = doc_grch38
        res[doc_grch38["hgnc_symbol"]]["chromosome"] = str(res[doc_grch38["hgnc_symbol"]].pop("chromosome_name"))
        res[doc_grch38["hgnc_symbol"]].pop("hgnc_symbol")   

    for doc_grch37 in docs_grch37:
        if doc_grch37["hgnc_symbol"] in res:
            res[doc_grch37["hgnc_symbol"]]["start_GRCh37"] = doc_grch37["start_position"]
            res[doc_grch37["hgnc_symbol"]]["end_GRCh37"] = doc_grch37["end_position"]

    for doc_hgnc in docs_hgnc:
        if doc_hgnc["symbol"] in res:
            res[doc_hgnc["symbol"]]["hgnc_id"] = doc_hgnc["hgnc_id"]
            if "name" in doc_hgnc:
                res[doc_hgnc["symbol"]]["name"] = doc_hgnc["name"]
            if "alias_symbol" in doc_hgnc:
                res[doc_hgnc["symbol"]]["alias_symbol"] = doc_hgnc["alias_symbol"]
            if "uniprot_ids" in doc_hgnc:
                res[doc_hgnc["symbol"]]["uniprot_ids"] = doc_hgnc["uniprot_ids"]
            if "omim_id" in doc_hgnc:
                res[doc_hgnc["symbol"]]["omim_id"] = doc_hgnc["omim_id"]

    for doc_oncokb in docs_oncokb:
        if doc_oncokb["hgnc_symbol"] in res:            
            if doc_oncokb["oncogene"]:
                res[doc_oncokb["hgnc_symbol"]]["oncokb_cancer_gene"] = "Oncogene"
            elif doc_oncokb["tumor_suppressor_gene"]:
                res[doc_oncokb["hgnc_symbol"]]["oncokb_cancer_gene"] = "Tumor Suppressor Gene"

    return res


def get_expression_from_gtex(tissue: str, genes: List) -> List:
    """
    Gets all the expressions for a specific tissue and a list of genes
    :param tissue: Tissue to filter
    :param genes: List of genes to filter
    :return: List of expressions
    """
    collection = mydb["gtex_" + tissue]  # Connects to specific tissue's collection
    query = {'gene': {'$in': genes}}
    projection = {'_id': 0, 'expression': 1, 'gene': 1, 'sample_id': 1}
    docs = collection.find(query, projection)
    temp = {}
    for doc in docs:
        sample_id = doc["sample_id"]
        if sample_id not in temp:
            temp[sample_id] = {}
        temp[sample_id][doc["gene"]] = doc["expression"]

    return list(temp.values())


def get_data_from_oncokb(genes: List) -> List:
    """
    Gets all data associated with a gene list
    :param genes: List of genes to filter
    :return: Dict of genes with their associated drugs and information according to OncoKB database
    """
    collection_accionability_gene = mydb["oncokb_biomarker_drug_associations"]  
    collection_cancer_gene = mydb["oncokb_gene_cancer_list"] 
    query1 = {'gene': {'$in': genes}}
    query2 = {'hgnc_symbol': {'$in': genes}}
    projection = {'_id': 0}
    docs_acciobility = collection_accionability_gene.find(query1, projection)
    docs_cancer = collection_cancer_gene.find(query2, projection)
    res = {}
    for doc_a in docs_acciobility:
        gen = doc_a.pop("gene")
        classification = doc_a.pop("classification")
        if gen not in res:
            res[gen] = {}
        if classification not in res[gen]:
            res[gen][classification] = []
        res[gen][classification].append(doc_a)

    for doc_c in docs_cancer:
        gen = doc_c.pop("hgnc_symbol")
        if gen not in res:
            res[gen] = {}
        res[gen]["oncokb_cancer_gene"] = []
        if doc_c["oncogene"]:
            res[gen]["oncokb_cancer_gene"].append("Oncogene")
        if doc_c["tumor_suppressor_gene"]:
            res[gen]["oncokb_cancer_gene"].append("Tumor Suppressor Gene")
        
        if len(res[gen]["oncokb_cancer_gene"]) == 0:
            res[gen].pop("oncokb_cancer_gene")
        
        sources = []
        for key in doc_c:
            if doc_c[key] == 1:
                if key not in ["oncogene", "tumor_suppressor_gene"]:
                    sources.append(key)
        res[gen]["sources"] = sources

        res[gen]["refseq_transcript"] = doc_c["refseq_transcript"]

    return res


def create_app():
    # Creates and configures the app
    flask_app = Flask(__name__, instance_relative_config=True)

    # Endpoints
    @flask_app.route("/")
    def homepage():
        return render_template('homePage.html', version=VERSION)

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


    @flask_app.route("/gene-symbols", methods=['POST'])
    def gene_symbols():
        """Receives a list of gene IDs in any standard and returns the standardized corresponding gene IDs.
        In case it is not found it returns an empty list for the specific not found gene."""
        response = {}
        if request.method == 'POST':
            body = request.get_json()
            if "gene_ids" not in body:
                abort(400, "gene_ids is mandatory")

            gene_ids = body['gene_ids']
            if type(gene_ids) != list:
                abort(400, "gene_ids must be a list")

            try:
                with ThreadPoolExecutor(max_workers=THREAD_POOL_WORKERS) as executor:
                    for gene_id, result in zip(gene_ids, executor.map(map_gene, gene_ids)):
                        response[gene_id] = result
            except Exception as e:
                abort(400, e)
        return make_response(response, 200, headers)

    @flask_app.route("/gene-symbols-finder/", methods=['GET'])
    def gene_symbol_finder():
        """Takes a string of any length and returns a list of genes that contain that search criteria."""
        query = None  # To prevent MyPy warning
        if "query" not in request.args:
            abort(400, "'query' parameter is mandatory")
        else:
            query = request.args.get('query')

        limit = 50
        if "limit" in request.args:
            limit_arg = request.args.get('limit')
            if limit_arg.isnumeric():
                limit = int(limit_arg)
            else:
                abort(400, "'limit' parameter must be a numeric value")

        try:
            response = get_potential_gene_symbols(query, limit)
            return make_response(json.dumps(response), 200, headers)
        except (TypeError, ValueError, KeyError) as e:
            abort(400, e)

    @flask_app.route("/information-of-genes", methods=['POST'])
    def information_of_genes():
        """Receives a list of gene IDs and returns information about them."""
        body = request.get_json()
        if "gene_ids" not in body:
            abort(400, "gene_ids is mandatory")

        gene_ids = body['gene_ids']
        if type(gene_ids) != list:
            abort(400, "gene_ids must be a list")

        try:
            response = get_information_of_genes(gene_ids)
        except Exception as e:
            response = {}  # To prevent mypy warnings
            abort(400, e)
        return make_response(response, 200, headers)

    @flask_app.route("/genes-of-its-group/<gene_id>", methods=['GET'])
    def genes_in_the_same_group(gene_id):
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

        except (TypeError, ValueError, KeyError) as e:
            abort(400, e)
        return make_response(response, 200, headers)

    @flask_app.route("/pathway-genes/<pathway_source>/<pathway_id>", methods=['GET'])
    def pathway_genes(pathway_source, pathway_id):
        if pathway_source not in PATHWAYS_SOURCES:
            abort(404, f'{pathway_source} is an invalid pathway source')
        response = {"genes": get_genes_of_pathway(pathway_id, pathway_source)}
        return make_response(response, 200, headers)

    @flask_app.route("/pathways-in-common", methods=['POST'])
    def pathways_in_common():
        body = request.get_json()
        if "gene_ids" not in body:
            abort(400, "gene_ids is mandatory")

        gene_ids = body['gene_ids']
        if type(gene_ids) != list:
            abort(400, "gene_ids must be a list")
        if len(gene_ids) == 0:
            abort(400, "gene_ids must contain at least one gene symbol")

        pathways_tmp = [get_pathways_of_gene(gene) for gene in gene_ids]
        pathways_intersection = list(set.intersection(*map(set, pathways_tmp)))
        response = {"pathways": []}
        for e in pathways_intersection:
            r = json.loads(e.replace("\'", "\""))
            response["pathways"].append(r)
        return make_response(response, 200, headers)

    @flask_app.route("/expression-of-genes", methods=['POST'])
    def expression_data_from_gtex():
        body = request.get_json()

        if "gene_ids" not in body:
            abort(400, "gene_ids is mandatory")

        gene_ids = body['gene_ids']
        if type(gene_ids) != list:
            abort(400, "gene_ids must be a list")

        if len(gene_ids) == 0:
            abort(400, "gene_ids must contain at least one gene symbol")

        if "tissue" not in body:
            abort(400, "tissue is mandatory")

        tissue = body['tissue']
        type_response = None  # To prevent MyPy warning
        if "type" in body:
            if body['type'] not in ["gzip", "json"]:
                abort(400, "allowed values for the 'type' key are 'json' or 'gzip'")
            else:
                type_response = body['type']
        else:
            type_response = 'json'

        expression_data = get_expression_from_gtex(tissue, gene_ids)

        if type_response == "gzip":
            content = gzip.compress(json.dumps(expression_data).encode('utf8'), 5)
            response = make_response(content)
            response.headers['Content-length'] = len(content)
            response.headers['Content-Encoding'] = 'gzip'
            return response
        return jsonify(expression_data)
    

    @flask_app.route("/information-of-oncokb", methods=['POST'])
    def oncokb_data():
        body = request.get_json()

        if "gene_ids" not in body:
            abort(400, "gene_ids is mandatory")

        gene_ids = body['gene_ids']
        if type(gene_ids) != list:
            abort(400, "gene_ids must be a list")

        if len(gene_ids) == 0:
            abort(400, "gene_ids must contain at least one gene symbol")

        data = get_data_from_oncokb(gene_ids)

        return jsonify(data)

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
