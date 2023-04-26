import urllib.request
import os
import gzip
import shutil
from pymongo import MongoClient
import json



# import sys
# # adding bioapi app folder to the system path
# # sys.path.insert(0, '/../../bio-api/bioapi.py')
# sys.path.insert(0, 'C:/Users/franc/OneDrive/Documents/GitHub/BioAPI/bio-api')
# import bioapi 
# print(bioapi.map_gene("BRCA1"))



############# MongoDB Conf ############
ip_mongo="localhost"
port_mongo=8888
user="root"
password="root"
db_name="bio_api"
#######################################



def pile_into_dict(dic,key,content):
    if key in dic:
        if isinstance(dic[key], list):
            dic[key].append(content)
        else:
             dic[key]= [dic[key],content]
    else:
        dic[key]= content


print("INFO	Downloading Gene Ontology database...")
urllib.request.urlretrieve("http://purl.obolibrary.org/obo/go.obo", "go.obo")
print("INFO	OK.")

print("INFO	Downloading Gene Ontology anotations database...")
urllib.request.urlretrieve("http://geneontology.org/gene-associations/goa_human_isoform.gaf.gz", "goa_human_isoform.gaf.gz")
urllib.request.urlretrieve("http://geneontology.org/gene-associations/goa_human.gaf.gz", "goa_human.gaf.gz")
print("INFO	OK.")

print("INFO	Uncompresing anotations")
with gzip.open('goa_human_isoform.gaf.gz', 'rb') as f_in:
    with open('goa_human_isoform.gaf', 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)
with gzip.open('goa_human.gaf.gz', 'rb') as f_in:
    with open('goa_human.gaf', 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)
print("INFO	OK.")


print("INFO	Processing Gene Ontology database...")

go = open("go.obo", "r")

# line = go.readline().strip()
# while line != "[Term]":
    # line = go.readline().strip()
    
all_terms= []
term= {"is_obsolete": True}

for line in go:
    line = line.strip().split(": ",1)
    if line == ["[Term]"] :
        if "relationship" in term:
            relationships = term.pop("relationship")
            if not isinstance(relationships, list): relationships = [relationships]
            for r in relationships:
                r= r.strip().split(" ")
                pile_into_dict(term,r[0],r[1].split(":")[1])
                
        atributes_with_ids = ["is_a","alt_id","disjoint_from","id"]
        
        for atr_name in atributes_with_ids:
            if atr_name in term:
                atr = term[atr_name]
                if isinstance(atr, list):
                    term[atr_name]= []
                    for i in atr: 
                        i= i.strip().split(" ")
                        term[atr_name].append(i[0].split(":")[1])
                else:
                    term[atr_name]= atr.strip().split(" ")[0].split(":")[1]
        if "id" in term: term["go_id"] = term.pop("id")
        if "namespace" in term: term["ontology_type"] = term.pop("namespace")
        if not ("is_obsolete" in term):
            all_terms.append(term)
        term= {}
    elif line == ["[Typedef]"] :
        break
    elif line != [""]:
        pile_into_dict(term,line[0],line[1])

go.close()
print("INFO	OK.")




print("INFO	Conecting to MongoDB...")
mongoClient = MongoClient(ip_mongo + ":" + str(port_mongo),username=user,password=password,authSource='admin',authMechanism='SCRAM-SHA-1')
db = mongoClient[db_name]
print("INFO	OK.")

print("INFO	Processing Gene Ontology anotations database (may take a while)...")

from typing import List, Dict
from pymongo.collation import Collation, CollationStrength
def map_gene(gene: str) -> List[str]:
    """
    Gets all the aliases for a specific gene
    :return List of aliases
    """
    collection_hgnc = db["hgnc"]  # HGNC collection

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

def process_anotations(anotations,all_genes,rejected_aliases):
    line = anotations.readline().strip()
    gene={}
    gene_symbol= ""
    for line in anotations:
        if line[0]!="!":
            line = line.strip().split("\t")

            if gene_symbol == line[2]:
                pass
            else:
                if gene_symbol != "":
                    real_alias= map_gene(gene["gene_symbol"])
                    if len(real_alias)==1 or gene["gene_symbol"] in real_alias: 
                        if len(real_alias)!=1 and gene["gene_symbol"] in real_alias:
                            rejected_aliases["accepted: "+gene["gene_symbol"]]=real_alias
                            real_alias = gene["gene_symbol"]
                        else:
                            real_alias = real_alias[0]
                        if real_alias in all_genes: 
                            gene.pop("gene_symbol")
                            for att in gene:
                                if att in all_genes[real_alias]:
                                    if isinstance(all_genes[real_alias][att],str):
                                        all_genes[real_alias][att]= [all_genes[real_alias][att]]
                                    if isinstance(gene[att],str):
                                        gene[att] = [gene[att]]
                                    all_genes[real_alias][att].extend(gene[att])
                                        
                                else:
                                    all_genes[real_alias][att] = gene[att]
                            # print(all_genes[real_alias])
                        else:
                            gene["gene_symbol"] = real_alias
                            all_genes[gene["gene_symbol"]]=gene
                            # print("agregado"+str(gene["gene_symbol"]))
                    else:
                        rejected_aliases[gene["gene_symbol"]]=real_alias
                gene_symbol = line[2]
                gene={"gene_symbol":gene_symbol}
            pile_into_dict(gene,line[3],line[4].split(":")[1])


anotations = open("goa_human_isoform.gaf", "r")
all_genes={}
rejected_aliases = dict()
process_anotations(anotations,all_genes,rejected_aliases)
anotations.close()

print("INFO	Processing MORE Gene Ontology anotations...")
anotations = open("goa_human.gaf", "r")
process_anotations(anotations,all_genes,rejected_aliases)
anotations.close()

with open('logs.json', 'w') as fp:
    json.dump(rejected_aliases, fp)
print("INFO	log.json was created containing all the rejected aliases")
print("INFO	OK.")



print("INFO	Importing to MongoDB...")


anotation_colection = db["go_anotations"]
anotation_colection.drop()
anotation_colection.insert_many(list(all_genes.values()))


go_colection = db["go"]
go_colection.drop()
go_colection.insert_many(all_terms)
print("INFO	OK.")




print("INFO	Creating indexes in MongoDB...")

go_colection.create_index([ ("id", 1) ]) 
anotation_colection.create_index([ ("gene_symbol", 1) ]) 

mongoClient.close()
print("INFO	OK.")



print("INFO	Removing intermediate files...")
os.remove("go.obo")
os.remove("goa_human_isoform.gaf.gz")
os.remove("goa_human_isoform.gaf")
os.remove("goa_human.gaf.gz")
os.remove("goa_human.gaf")

print("INFO	OK.")