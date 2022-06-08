from flask import Flask
from flask import jsonify
from flask import make_response
from flask import abort
from flask import render_template
from flask import request
import urllib.parse
import pymongo
import re
import os
import configparser
import logging
from pymongo.database import Database

# Gets production flag
IS_DEBUG: bool = os.environ.get('DEBUG', 'true') == 'true'

# Levanto configuracion
Config = configparser.ConfigParser()
Config.read("config.txt")

# configuracion log
logging.getLogger("urllib3").setLevel(logging.DEBUG)

# In development logs in console, in production logs in file
if not IS_DEBUG:
    logging.basicConfig(filename=Config.get('log', 'file'), filemode='a',
                        format='%(asctime)s\t%(name)s\t%(levelname)s\t%(message)s', datefmt='%d-%b-%y %H:%M:%S',
                        level=logging.DEBUG)
logging.info('BIO-API iniciado')

# Defino header de respuestas (puede que este al pedo)
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
            port = Config.get('mongodb', 'port')
            user = Config.get('mongodb', 'user')
            password = Config.get('mongodb', 'pass')
            db = Config.get('mongodb', 'db_name')
        else:
            host = os.environ.get('MONGO_HOST')
            port = os.environ.get('MONGO_PORT')
            user = os.environ.get('MONGO_USER')
            password = os.environ.get('MONGO_PASSWORD')
            db = os.environ.get('MONGO_DB')

            if not host or not port or not db:
                logging.error(f'Host ({host}), port ({port}) or db ({db}) is invalid', exc_info=True)
                exit(-1)

        mongo_client = pymongo.MongoClient(f"mongodb://{user}:{password}@{host}:{port}/?authSource=admin")
        return mongo_client[db]
    except Exception as e:
        logging.error("BioAPI no se pudo conectar a la base de datos MongoDB configurada." + str(e), exc_info=True)
        exit(-1)


mydb = get_mongo_connection()


def mapear_gen(gen):
    er = re.compile("^" + re.escape(gen) + "$", re.IGNORECASE)
    mycol_hgnc = mydb["hgnc"]  # coneccion a coleccion hgnc
    dbs = ["hgnc_id", "symbol", "status", "alias_symbol", "prev_symbol", "entrez_id", "ensembl_gene_id", "vega_id",
           "ucsc_id", "ena", "refseq_accession", "ccds_id", "uniprot_ids", "cosmic", "omim_id", "mirbase", "homeodb",
           "snornabase", "bioparadigms_slc", "orphanet", "pseudogene", "horde_id", "merops", "imgt", "iuphar",
           "kznf_gene_catalog", "mamit-trnadb", "cd", "lncrnadb", "enzyme_id", "intermediate_filament_db", "agr"]
    # armo query
    or_search = []
    for db in dbs:
        q = {db: {"$regex": er}}
        or_search.append(q)
    query = {'$or': or_search, "status": "Approved"}
    proyection = {'_id': 0, 'symbol': 1}
    # hago consulta a la db
    mydocs = mycol_hgnc.find(query, proyection)
    results = []
    for doc in mydocs:
        results.append(doc["symbol"])
    return results


def buscar_grupo_gen(gen):  # AGREGAR LO QUE PASA SI NO PERTENECE A NINGUN gene_group_id (EJ gen:AADACP1)
    results = {'locus_group': None, 'locus_type': None, 'gene_group': None, 'gene_group_id': None}
    mycol_hgnc = mydb["hgnc"]  # coneccion a coleccion hgnc
    query = {"symbol": gen, "status": "Approved"}
    # hago consulta a la db
    mydocs = mycol_hgnc.find(query)
    if mydocs.count() == 1:
        results['locus_group'] = mydocs[0]['locus_group']
        results['locus_type'] = mydocs[0]['locus_type']
        if "gene_group" in list(mydocs[0].keys()):
            if type(mydocs[0]['gene_group']) == list:
                results['gene_group'] = mydocs[0]['gene_group']
                results['gene_group_id'] = mydocs[0]['gene_group_id']
            else:
                results['gene_group'] = [mydocs[0]['gene_group']]
                results['gene_group_id'] = [mydocs[0]['gene_group_id']]

    return results


def buscar_genes_mismo_grupo(id_grupo):
    mycol_hgnc = mydb["hgnc"]  # coneccion a coleccion hgnc
    query = {'gene_group_id': id_grupo}
    proyection = {'_id': 0, 'symbol': 1}
    # hago consulta a la db
    mydocs = mycol_hgnc.find(query, proyection)
    results = []
    for doc in mydocs:
        results.append(doc["symbol"])
    return results


def create_app():
    # create and configure the app
    flask_app = Flask(__name__, instance_relative_config=True)

    # Endpoints
    @flask_app.route("/")  # Pantalla de inicio
    def inicio():
        return render_template('homePage.html')

    @flask_app.route("/ping")  # Para chequear que este levantada la bioapi
    def ping_ok():
        output = "ok"
        return make_response(output, 200, headers)

    @flask_app.route("/bioapi-map")  # Lista todos los endpoint de bioapi
    def list_routes():
        output = {"endpoints": []}
        for rule in flask_app.url_map.iter_rules():
            methods = ','.join(rule.methods)
            line = urllib.parse.unquote("{:50s} {:20s} {}".format(rule.endpoint, methods, rule))
            output["endpoints"].append(line)
        return make_response(output, 200, headers)

    @flask_app.route("/gene-symbol/<gene_id>")
    def genSymbol(gene_id):
        """Recibe un ID del gen en cualquier estandar y devuelve el ID del Gen estandarizado. En caso de que no se
        encuentre debe retornar [ ] en el valor."""
        respuesta = {gene_id: []}
        try:
            gv = mapear_gen(gene_id)
            respuesta[gene_id] = gv
        except Exception as e:
            abort(400, e)
        return make_response(respuesta, 200, headers)

    @flask_app.route("/genes-symbols", methods = ['POST'])
    def genSymbols():
        if(request.method == 'POST'):
            body = request.get_json()
            if "genes_ids" not in list(body.keys()):
                abort(400, "genes_ids is mandatory")
            genes_ids = body['genes_ids']
            if type(genes_ids) != list:
                abort(400, "genes_ids must be a list")
            respuesta = {}
            try:
                for gene in genes_ids:
                    gv = mapear_gen(gene)
                    respuesta[gene] = gv
            except Exception as e:
                abort(400, e)
        return make_response(respuesta, 200, headers)

    @flask_app.route("/genes-same-group/<gene_id>")
    def genes_of_the_same_family(gene_id):
        respuesta = {"gene_id": None, "groups": [], "locus_group": None, "locus_type": None}
        try:
            
            mapped_gene = mapear_gen(gene_id)
            if len(mapped_gene) == 0:
                abort(400, "invalid gene identifier")
            elif len(mapped_gene) >= 2:
                abort(400, "ambiguous gene identifier. The identifier may refer to more than one HGNC-approved gene (" + ",".join(mapped_gene) + ")")
            approved_symbol = mapped_gene[0]
            respuesta["gene_id"] = approved_symbol
            gene_group = buscar_grupo_gen(approved_symbol)
            respuesta['locus_group'] = gene_group['locus_group']
            respuesta['locus_type'] = gene_group['locus_type']
            if gene_group['gene_group_id'] != None:
                respuesta["groups"] = []
                for i in range(0, len(gene_group['gene_group_id'])):
                    g = {}
                    g["gene_group_id"] = gene_group['gene_group_id'][i]
                    g["gene_group"] = gene_group['gene_group'][i]
                    g["genes"] = buscar_genes_mismo_grupo(gene_group['gene_group_id'][i])
                    respuesta["groups"].append(g)

        except TypeError as e:
            abort(400, e)
        except ValueError as e:
            abort(400, e)
        except KeyError as e:
            abort(400, e)
        return make_response(respuesta, 200, headers)

    # Manejo de errores
    @flask_app.errorhandler(400)
    def resource_not_found(e):
        return jsonify(error=str(e)), 400

    @flask_app.errorhandler(405)
    def resource_not_found(e):
        return jsonify(error=str(e)), 405

    @flask_app.errorhandler(404)
    def resource_not_found(e):
        return jsonify(error=str(e)), 404

    @flask_app.errorhandler(409)
    def resource_not_found(e):
        return jsonify(error=str(e)), 409

    @flask_app.errorhandler(500)
    def resource_not_found(e):
        return jsonify(error=str(e)), 500

    return flask_app


app = create_app()

if __name__ == "__main__":
    port_str = os.environ.get('PORT', Config.get('flask', 'port'))
    port = int(port_str)
    app.run(host='localhost', port=port, debug=IS_DEBUG)
