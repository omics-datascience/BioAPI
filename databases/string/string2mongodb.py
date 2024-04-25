import gzip
import shutil
from pymongo import MongoClient
import os
import sys
from tqdm import tqdm

# MongoDB Conf ############
ip_mongo = sys.argv[1]
port_mongo = sys.argv[2]
user = sys.argv[3]
password = sys.argv[4]
db_name = sys.argv[5]
######################################
# url="https://stringdb-static.org/download/protein.links.full.v11.5/9606.protein.links.full.v11.5.txt.gz"

print("INFO	Decompressing files")
with gzip.open('protein.links.full.txt.gz', 'rb') as f_in:
    with open('protein.links.full.txt', 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)
with gzip.open('protein.info.txt.gz', 'rb') as f_in:
    with open('protein.info.txt', 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)
print("INFO	OK.")

print("INFO	Processing String aliases...")
protein_to_gene = open("protein.info.txt", "r")
alias_dict = {}
skipped_first_line = False
for line in protein_to_gene:
    line = line.split("\t")
    if not skipped_first_line:
        skipped_first_line = True
    else:
        alias_dict[line[0]] = line[1]
protein_to_gene.close()
print("INFO	OK.")

print("INFO	Connecting to MongoDB...")
mongoClient = MongoClient(ip_mongo + ":" + str(port_mongo),username=user,password=password,authSource='admin',authMechanism='SCRAM-SHA-1')
db = mongoClient[db_name]
print("INFO	OK.")

print("INFO	Preparing MongoDB...")
string_collection = db["string"]
string_collection.drop()
# anotation_colection.insert_many(list(gene_relations))
print("INFO	OK.")

print("INFO	Processing String DB...")
protein_relations = open("protein.links.full.txt", "r")
skipped_first_line = False
fields = None
gene_relations = []
for line in tqdm(protein_relations):
    line = line.split(" ")
    line.pop(2)
    if not skipped_first_line:
        fields = line
        fields[0] = "gene_1"
        fields[1] = "gene_2"
        fields[14] = "combined_score"
        skipped_first_line = True
    else:
        rel = {}
        for f in range(15):
            if f <= 1:
                rel[fields[f]] = alias_dict[line[f]]
            elif int(line[f]) > 0:
                rel[fields[f]] = int(line[f])
            else:
                rel[fields[f]] = None

        gene_relations.append(rel)

        if len(gene_relations) == 500000:
            print("INFO	Loading data in MongoDB...")
            string_collection.insert_many(gene_relations)
            gene_relations = []
string_collection.insert_many(gene_relations)
protein_relations.close()
print("INFO	OK.")

print("INFO	Creating indexes in MongoDB...")
string_collection.create_index([("gene_1", 1)])
string_collection.create_index([("gene_2", 1)])
string_collection.create_index([("combined_score", 1)])
print("INFO	OK.")

print("INFO	deleting duplicates...")
for gene_symbol in tqdm(alias_dict.values()):
    relations = string_collection.find({"gene_1": gene_symbol})
    to_del = []
    for r in relations:
        to_del.append(r["gene_2"])
    string_collection.delete_many({"gene_1": {"$in": to_del}, "gene_2": gene_symbol})

print("INFO	Removing intermediate files...")
os.remove("protein.links.full.txt")
os.remove("protein.info.txt")
print("INFO	OK.")
