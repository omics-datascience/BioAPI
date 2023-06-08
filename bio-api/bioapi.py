import re
import os
import json
import gzip
import logging
from concurrent.futures import ThreadPoolExecutor
import configparser
import urllib.parse
from typing import List, Dict, Optional, Any
from flask import Flask, jsonify, make_response, abort, render_template, request
from utils import map_gene
from gprofiler import GProfiler

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

from db import get_mongo_connection
mydb = get_mongo_connection(IS_DEBUG,Config)


# TODO: if it's not used, remove!!!
# def get_mongo_connection() -> Database:
    # """
    # Gets Mongo connection using config.txt file if DEBUG env var is 'true', or all the env variables in case of prod
    # (DEBUG = 'false')
    # :return: Database instance
    # """
    # try:
        # if IS_DEBUG:
            # host = Config.get('mongodb', 'host')
            # mongo_port = Config.get('mongodb', 'port')
            # user = Config.get('mongodb', 'user')
            # password = Config.get('mongodb', 'pass')
            # db = Config.get('mongodb', 'db_name')
        # else:
            # host = os.environ.get('MONGO_HOST')
            # mongo_port = os.environ.get('MONGO_PORT')
            # user = os.environ.get('MONGO_USER')
            # password = os.environ.get('MONGO_PASSWORD')
            # db = os.environ.get('MONGO_DB')

            # if not host or not mongo_port or not db:
                # logging.error(f'Host ({host}), port ({mongo_port}) or db ({db}) is invalid', exc_info=True)
                # exit(-1)

        # mongo_client = pymongo.MongoClient(f"mongodb://{user}:{password}@{host}:{mongo_port}/?authSource=admin")
        # return mongo_client[db]
    # except Exception as e:
        # logging.error("Database connection error." + str(e), exc_info=True)
        # exit(-1)




# def map_gene(gene: str) -> List[str]:
    # """
    # Gets all the aliases for a specific gene
    # :return List of aliases
    # """
    # collection_hgnc = mydb["hgnc"]  # HGNC collection

    # dbs = ["hgnc_id", "symbol", "alias_symbol", "prev_symbol", "entrez_id", "ensembl_gene_id", "vega_id",
           # "ucsc_id", "ena", "refseq_accession", "ccds_id", "uniprot_ids", "cosmic", "omim_id", "mirbase", "homeodb",
           # "snornabase", "bioparadigms_slc", "orphanet", "pseudogene", "horde_id", "merops", "imgt", "iuphar",
           # "kznf_gene_catalog", "mamit-trnadb", "cd", "lncrnadb", "enzyme_id", "intermediate_filament_db", "agr"]

    # # Generates query
    # or_search = [{db: gene} for db in dbs]
    # query = {'$or': or_search}
    # coll = Collation(locale='en', strength=CollationStrength.SECONDARY)
    # docs = collection_hgnc.find(query, collation=coll)
    # res = [doc["symbol"] for doc in docs]
    # return res


def get_potential_gene_symbols(query_string, limit_elements):
    """
    TODO: document and add types
    :param query_string:
    :param limit_elements:
    :return:
    """
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
    """
    TODO: document
    :param gen:
    :return:
    """
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
                results['gene_group'] = [document['gene_group']] # type: ignore
                results['gene_group_id'] = [document['gene_group_id']] # type: ignore

    return results


def search_genes_in_same_group(group_id: int):
    """
    TODO: document
    :param group_id:
    :return:
    """
    collection_hgnc = mydb["hgnc"]  # HGNC collection
    query = {'gene_group_id': group_id}
    projection = {'_id': 0, 'symbol': 1}
    docs = collection_hgnc.find(query, projection)
    return [doc["symbol"] for doc in docs]


def get_genes_of_pathway(pathway_id, pathway_source):
    """
    TODO: document and add types
    :param pathway_id:
    :param pathway_source:
    :return:
    """
    collection_cpdb = mydb["cpdb"]  # CPDB collection
    ps = re.compile("^" + pathway_source + "$", re.IGNORECASE)
    query = {'external_id': str(pathway_id), "source": {"$regex": ps}}
    doc = collection_cpdb.find_one(query)
    return doc["hgnc_symbol_ids"] if doc is not None else []


def get_pathways_of_gene(gene):
    """
    TODO: document and add types
    :param gene:
    :return:
    """
    collection_cpdb = mydb["cpdb"]  # CPDB collection
    query = {'hgnc_symbol_ids': gene}
    projection = {'_id': 0, 'pathway': 1, 'external_id': 1, 'source': 1}
    docs = collection_cpdb.find(query, projection)
    return [str(doc) for doc in docs]


def get_information_of_genes(genes: List[str]) -> Dict:
    """
    TODO: document
    :param genes:
    :return:
    """
    res = {}
    collection_gene_grch37 = mydb["gene_grch37"]
    collection_gene_grch38 = mydb["gene_grch38"]
    collection_gene_oncokb = mydb["oncokb_gene_cancer_list"]
    collection_hgnc = mydb["hgnc"]

    # Generates query
    query = {"hgnc_symbol": {"$in": genes}}

    # Removes the identifiers because they're retrieved from the HGNC collection
    projection = {'_id': 0, 'description': 0, 'hgnc_id': 0, 'entrezgene_id': 0, 'ensembl_gene_id': 0}

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
            if "ensembl_gene_id" in doc_hgnc:
                res[doc_hgnc["symbol"]]["ensembl_gene_id"] = doc_hgnc["ensembl_gene_id"]
            if "entrez_id" in doc_hgnc:
                res[doc_hgnc["symbol"]]["entrez_id"] = doc_hgnc["entrez_id"]

    for doc_oncokb in docs_oncokb:
        if doc_oncokb["hgnc_symbol"] in res:            
            if doc_oncokb["oncogene"]:
                res[doc_oncokb["hgnc_symbol"]]["oncokb_cancer_gene"] = "Oncogene"
            elif doc_oncokb["tumor_suppressor_gene"]:
                res[doc_oncokb["hgnc_symbol"]]["oncokb_cancer_gene"] = "Tumor Suppressor Gene"

    return res


def get_expression_from_gtex(tissue: str, genes: List[str]) -> List:
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


def terms_related_to_one_gene(gene: str, relation_type: Optional[List[str]] = None) -> Dict[str, List[Dict[str, Any]]]:
    """
    TODO: add documentation
    :param gene:
    :param relation_type:
    :return:
    """
    if relation_type is None:
        relation_type = ["enables", "involved_in", "part_of", "located_in"]
    collection_go_annotations = mydb["go_anotations"]
    
    annotation = list(collection_go_annotations.find({"gene_symbol": gene}))
    related_genes = {}
    if annotation:
        annotation = annotation[0]
        for relation in relation_type:
            if relation in annotation:
                for term in annotation[relation]:
                    aux = {"evidence": term["evidence"], "gene": gene, "relation_type":relation}
                    if term["go_id"] in related_genes:
                        related_genes[term["go_id"]].append(aux)
                    else:
                        related_genes[term["go_id"]]= [aux]

    return related_genes


def is_term_on_db(term_id):
    collection_go = mydb["go"]
    return collection_go.find_one({"go_id": term_id}) is None


def terms_related_to_many_genes(gene_ids: list, filter_type: str = "intersection",
                                relation_type: Optional[List[str]] = None):
    """
    TODO: document
    :param gene_ids:
    :param filter_type:
    :param relation_type:
    :return:
    """
    if relation_type is None:
        relation_type = ["enables", "involved_in", "part_of", "located_in"]
    gene = gene_ids.pop()
    term_set= terms_related_to_one_gene(gene,relation_type)

    for gene in gene_ids:
        terms = terms_related_to_one_gene(gene,relation_type)
        if filter_type == "intersection":
            current_terms = term_set.keys() & terms.keys()
            new_set = {}
            for cterm in current_terms:
                if cterm in term_set:
                    term_set[cterm].extend(terms[cterm])
                    new_set[cterm] = term_set[cterm]
                else:
                    new_set[cterm] = (terms[cterm])
            term_set = new_set
        elif filter_type == "union":
            for cterm in terms:
                if cterm in term_set:
                    term_set[cterm].extend(terms[cterm])
                else:
                    term_set[cterm]=(terms[cterm])  
    return term_set


def genes_evidence(gene_ids: List[str]) -> Dict[str, List[Dict[str, Any]]]:
    """
    TODO: document
    :param gene_ids:
    :return:
    """
    collection_go_anotations = mydb["go_anotations"]
    annotation_list = list(collection_go_anotations.find({"gene_symbol": {"$in":gene_ids}},{"_id":0}))
    res = {}
    for annotation in annotation_list:
        gene = annotation.pop("gene_symbol")
        for relation_type in annotation.keys():
            for evidence in annotation[relation_type]:
                obj = {"evidence": evidence["evidence"], "gene": gene, "relation_type":relation_type}
                if evidence["go_id"] in res:
                    res[evidence["go_id"]].append(obj)
                else:
                    res[evidence["go_id"]] = [obj]
    return res

def enrich(gene_ids: list, filter_type = "enrich", p_value_threshold = 0.05, correction_method = "analytical"):
    """
    TODO: document and remove unused parameters
    :param gene_ids:
    :param filter_type:
    :param p_value_threshold:
    :param correction_method:
    :return:
    """
    gp = GProfiler(return_dataframe=False)
    enrichment = gp.profile(organism='hsapiens',
                            query=gene_ids,
                            sources=['GO'],
                            user_threshold=p_value_threshold,
                            significance_threshold_method=correction_method,
                            all_results=False,
                            no_evidences=False)
    metrics={}
    relations={}
    for term in enrichment:
        if ("native" in term) and ("GO:" in term["native"]):
            go_id = term["native"].split(":")[1]
            metrics[go_id]= {"p_value" : term["p_value"],
                        "term_size" : term["term_size"],
                        "query_size" : term["query_size"],
                        "intersection_size" : term["intersection_size"],
                        "effective_domain_size" : term["effective_domain_size"],
                        "precision" : term["precision"],
                        "recall" : term["recall"]}
            
            for i in range(len(term["intersections"])):
                gene = term["intersections"][i]
                evlist = []  # TODO: fixme. Here is assigning only the last time it iterates to relations[go_id]
                for evcode in term["evidences"][i]:
                    evlist.append({"evidence": evcode, "gene": gene, "relation_type":"relation obtained from gProfiler"})
            relations[go_id] = evlist
    return metrics, relations


def populate_terms_with_data(term_list, ontology_type: Optional[List[str]] = None):
    if ontology_type is None:
        ontology_type = ["biological_process", "molecular_function", "cellular_component"]
    collection_go = mydb["go"]
    terms = (list(collection_go.find({"go_id": { "$in": term_list }, "ontology_type": { "$in": ontology_type }},{"_id":0})))
    return terms

  
def strip_term(term,relations):
    new_term = {"go_id": term["go_id"], "name": term["name"], "ontology_type": term["ontology_type"], "relations": {}}
    for r in relations:
        if r in term:
            if not isinstance(term[r], list): term[r] = [term[r]]
            new_term["relations"][r]= term[r]
    return new_term


def bfs_on_terms(term_id, relations: Optional[List[str]] = None, general_depth= 0, hierarchical_depth_to_children= 0,
                 ontology_type: Optional[List[str]] = None, to_root = True):
    """
    TODO: document and add types
    :param term_id:
    :param relations:
    :param general_depth:
    :param hierarchical_depth_to_children:
    :param ontology_type:
    :param to_root:
    :return:
    """
    if ontology_type is None:
        ontology_type = ["biological_process", "molecular_function", "cellular_component"]
    if relations is None:
        relations = ["part_of", "regulates", "has_part"]
    collection_go = mydb["go"]
    graph = {}
    depth_mark = "*"
    
    visited = [] # List for visited nodes.
    queue = []     #Initialize a queue
    visited.append(term_id)
    queue.append(term_id)
    queue.append(depth_mark)
    actual_depth = 0

    while queue:          # Creating loop to visit each conected with non-hierarchical relationship
        act = queue.pop(0) 
        if act == depth_mark:
            if actual_depth == general_depth or not queue:
                break
            queue.append(depth_mark)
            actual_depth += 1  
        else:
            #could be optimized by pooling all the next level neighbours and doing one db call per level
            #but on the other side you have to control for already visited nodes, so im not sure if its faster
            term = collection_go.find_one({"go_id": act}) 
            if not term["ontology_type"] in ontology_type:
                continue
            term =strip_term(term,relations)
            graph[term["go_id"]] = term
            for rel in term["relations"].values():
                for neighbour in rel:
                  if neighbour not in visited:
                    visited.append(neighbour)
                    queue.append(neighbour)
    
    #go to the ontology children
    terms= [term_id]
    next_level_terms = []
    for i in range(hierarchical_depth_to_children):
        terms = collection_go.find({"is_a": { "$in": terms }} )
        for t in terms:
            t_id = t["go_id"]
            if t_id in visited:
                term =strip_term(t,["is_a"])
                graph[t_id]["relations"]['is_a']= term["relations"]["is_a"]
            else:
                term =strip_term(t,["is_a"])
                graph[term["go_id"]] = term
                visited.append(t_id)
            next_level_terms.append(term["go_id"])
            
        terms = next_level_terms
        next_level_terms = []
    
    #go to the ontology root
    if to_root:
        terms= [term_id]
        next_level_terms = []
        while terms: 
            terms = collection_go.find({"go_id": { "$in": terms }} )
            for t in terms:
                if "is_a" in t:
                    new_terms = t["is_a"]
                    if isinstance(new_terms, list):
                        next_level_terms.extend(new_terms)
                    else:
                        next_level_terms.append(new_terms)
                t_id = t["go_id"]
                if t_id in visited:
                    term =strip_term(t,["is_a"])
                    if "is_a" in t: graph[t_id]["relations"]['is_a']= term["relations"]["is_a"]
                else:
                    term =strip_term(t,["is_a"])
                    graph[term["go_id"]] = term
                    visited.append(t_id)
            terms = next_level_terms
            next_level_terms = []
    
    return list(graph.values())

# PharmGKB

def cancer_drugs_related_to_gene(gene):
    collection_pharm = mydb["pharmgkb"]
    return list(collection_pharm.find({"genes":gene},{"_id":0}))

# App

def get_data_from_oncokb(genes: List[str]) -> Dict:
    """
    Gets all data associated with a gene list.
    :param genes: List of genes to filter.
    :return: Dict of genes with their associated drugs and information according to OncoKB database
    """
    collection_actionability_gene = mydb["oncokb_biomarker_drug_associations"]
    collection_cancer_gene = mydb["oncokb_gene_cancer_list"] 
    query1 = {'gene': {'$in': genes}}
    query2 = {'hgnc_symbol': {'$in': genes}}
    projection = {'_id': 0}
    docs_actionability = collection_actionability_gene.find(query1, projection)
    docs_cancer = collection_cancer_gene.find(query2, projection)
    res = {}
    for doc_a in docs_actionability:
        gen = doc_a.pop("gene")
        classification = doc_a.pop("classification").lower()
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

        if "refseq_transcript" in doc_c:
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
            body = request.get_json() # type: ignore
            if "gene_ids" not in body:
                abort(400, "gene_ids is mandatory")

            gene_ids = body['gene_ids']
            if type(gene_ids) != list:
                abort(400, "gene_ids must be a list")

            try:
                with ThreadPoolExecutor(max_workers=THREAD_POOL_WORKERS) as executor:
                    for gene_id, result in zip(gene_ids, executor.map(map_gene, gene_ids, [mydb for _ in gene_ids])):
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
            query = request.args.get('query') # type: ignore

        limit = 50
        if "limit" in request.args:
            limit_arg = request.args.get('limit') # type: ignore
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
        body = request.get_json() # type: ignore
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
            mapped_gene = map_gene(gene_id, mydb)
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
                        "genes": search_genes_in_same_group(gene_group['gene_group_id'][i])
                    }
                    if gene_group['gene_group'] is not None:
                        g["gene_group"] = gene_group['gene_group'][i]
                    response["groups"].append(g)

        except (TypeError, ValueError, KeyError) as e:
            abort(400, e)
        return make_response(response, 200, headers)

    @flask_app.route("/pathway-genes/<pathway_source>/<pathway_id>", methods=['GET'])
    def pathway_genes(pathway_source, pathway_id):
        if pathway_source.lower() not in PATHWAYS_SOURCES:
            abort(404, f'{pathway_source} is an invalid pathway source')
        response = {"genes": get_genes_of_pathway(pathway_id, pathway_source)}
        return make_response(response, 200, headers)

    @flask_app.route("/pathways-in-common", methods=['POST'])
    def pathways_in_common():
        body = request.get_json() # type: ignore
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
        body = request.get_json() # type: ignore

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
        
    
    @flask_app.route("/genes-to-terms", methods=['POST'])
    def genes_to_go_terms():
        """Receives a list of genes and returns the related terms"""
        valid_filter_types = ["union", "intersection", "enrichment"]
        valid_ontology_types = ["biological_process", "molecular_function", "cellular_component"]
        valid_correction_methods = ["analytical", "false_discovery_rate", "bonferroni"]
        response = {}
        gene_term_arguments= {}
        populate_arguments= {}
        if request.method == 'POST':
            body = request.get_json() # type: ignore
            if "gene_ids" not in body:
                abort(400, "gene_ids is mandatory")
            gene_term_arguments['gene_ids'] = body['gene_ids']
            if "relation_type" in body:
                if ("filter_type" in body) and (body["filter_type"] == "enrichment"):
                    abort(400, "relation_type filter is not valid on gene enrichment analysis, all the available relation types will be used.")
                gene_term_arguments["relation_type"] = body["relation_type"]
            for a in gene_term_arguments:
                if not isinstance(gene_term_arguments[a], list):
                    abort(400, str(a)+" must be a list")
            if "filter_type" in body:
                if not body["filter_type"] in valid_filter_types:
                    abort(400, "filter_type is invalid. Should be one of this options: "+ str(valid_filter_types))
                gene_term_arguments["filter_type"] = body["filter_type"]
            if "ontology_type" in body:
                populate_arguments["ontology_type"] = body["ontology_type"]
                if not isinstance(body["ontology_type"], list):
                    abort(400, "ontology_type must be a list")
                for ot in populate_arguments["ontology_type"]:
                    if not (ot in valid_ontology_types):
                        abort(400, str(ot)+" is not a valid ontology_type")
            
            if "p_value_threshold" in body:
                p_value_threshold = None  # To prevent MyPy warning
                if body["filter_type"] != "enrichment":
                    abort(400, "p_value_threshold is only valid on gene enrichment analysis")
                try:
                    p_value_threshold = float(body["p_value_threshold"])
                except ValueError:
                    abort(400, "p_value_threshold should be an float")
                gene_term_arguments["p_value_threshold"] = p_value_threshold
                        
            if "correction_method" in body:
                if body["filter_type"] != "enrichment":
                    abort(400, "correction_method is only valid on gene enrichment analysis")
                if not body["correction_method"] in valid_correction_methods:
                    abort(400, "correction_method is invalid. Should be one of this options: "+ str(valid_correction_methods))
                gene_term_arguments["correction_method"] = body["correction_method"]

            # To prevent MyPy warning
            enrichment_metrics = {}
            enrichment_evidence = {}
            if ("filter_type" in body) and (body["filter_type"] == "enrichment"):
                enrichment_metrics, enrichment_evidence = enrich(**gene_term_arguments)
                terms= list(enrichment_metrics)
                evidence = genes_evidence(gene_term_arguments['gene_ids'])
            else:
                evidence = terms_related_to_many_genes(**gene_term_arguments)
                terms= list(evidence)
                
                
            response = populate_terms_with_data(terms, **populate_arguments)

            for i in range(len(response)):
                if body["filter_type"] == "enrichment":
                    # It's safe to use 'enrichment_metrics' and 'enrichment_evidence' here
                    response[i]["enrichment_metrics"] = enrichment_metrics[response[i]["go_id"]]
                    response[i]["relations_to_genes"] = enrichment_evidence[response[i]["go_id"]]
                    if response[i]["go_id"] in evidence:
                        response[i]["relations_to_genes"].extend(evidence[response[i]["go_id"]])
                else:
                    response[i]["relations_to_genes"]= evidence[response[i]["go_id"]]

        return jsonify(response)
    
    @flask_app.route("/related-terms", methods=['POST'])
    def related_terms():
        """Receives a term and returns the related terms"""
        valid_ontology_types = ["biological_process", "molecular_function", "cellular_component"]
        response = {}
        arguments= {}
        if request.method == 'POST':
            body = request.get_json() # type: ignore
            if "term_id" not in body:
                abort(400, "term_id is mandatory")
            if is_term_on_db(body["term_id"]):
                abort(400, "term_id is not on database")
            arguments["term_id"] = body["term_id"]
            try:
                if "general_depth" in body:
                    arguments["general_depth"] = int(body["general_depth"])
                    if arguments["general_depth"] < 0:
                        abort(400, "depth should be a positive integer")
                if "hierarchical_depth_to_children" in body:
                    arguments["hierarchical_depth_to_children"] = int(body["hierarchical_depth_to_children"])
                    if arguments["hierarchical_depth_to_children"] < 0:
                        abort(400, "hierarchical depth should be a positive integer")
            except ValueError:
                abort(400, "depth should be an integer")
            if "relations" in body:
                arguments["relations"] = body["relations"]
                if type(arguments["relations"]) != list:
                    abort(400, "relations must be a list")
            if "ontology_type" in body:
                arguments["ontology_type"] = body["ontology_type"]
                if type(arguments["ontology_type"]) != list:
                    abort(400, "ontology_type must be a list")
                for ot in arguments["ontology_type"]:
                    if not (ot in valid_ontology_types):
                        abort(400, str(ot)+" is not a valid ontology_type")
            if "to_root" in body:
                arguments["to_root"] = bool(body["to_root"])
            response = bfs_on_terms(**arguments)
        return jsonify(response)

    @flask_app.route("/information-of-oncokb", methods=['POST'])
    def oncokb_data():
        body = request.get_json() # type: ignore

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
    @flask_app.route("/drugs-pharm-gkb", methods=['POST'])
    def cancer_drugs_related_to_genes():
        """Receives genes and returns the related drugs"""
        response= {}
        if request.method == 'POST':
            body = request.get_json()
            if "gene_ids" not in body:
                abort(400, "gene_ids is mandatory")
            if type(body["gene_ids"]) != list:
                abort(400, "gene_ids must be a list")
            for gene in body["gene_ids"]:
                response[gene] = cancer_drugs_related_to_gene(gene)
        return jsonify(response)

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
