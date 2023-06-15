import gzip
import urllib.request
import shutil
from pymongo import MongoClient
import json
import requests, zipfile, io
import os
import sys



############# MongoDB Conf ############
# ip_mongo=sys.argv[1]
# port_mongo=sys.argv[2]
# user=sys.argv[3]
# password=sys.argv[4]
# db_name=sys.argv[5]
#######################################
url1="https://stringdb-static.org/download/protein.links.full.v11.5/9606.protein.links.full.v11.5.txt.gz"
url2= "https://stringdb-static.org/download/protein.info.v11.5/9606.protein.info.v11.5.txt.gz"

############# MongoDB Conf ############
ip_mongo="localhost"
port_mongo=8888
user="root"
password="root"
db_name="bio_api"
############# Database URL ############




def pile_into_dict(dic,key,content):
    if key in dic:
        if isinstance(dic[key], list):
            dic[key].append(content)
        else:
             dic[key]= [dic[key],content]
    else:
        dic[key]= content



print("INFO	Downloading protein network...")
# urllib.request.urlretrieve(url1, "protein.info.txt.gz")
urllib.request.urlretrieve(url2, "protein.aliases.txt.gz")
print("INFO	OK.")

print("INFO	Decompresing files")
with gzip.open('protein.links.full.txt.gz', 'rb') as f_in:
    with open('protein.links.full.txt', 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)
with gzip.open('protein.aliases.txt.gz', 'rb') as f_in:
    with open('protein.aliases.txt', 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)
print("INFO	OK.")



print("INFO	Processing String aliases...")
protein_to_gene = open("protein.aliases.txt", "r")
alias_dict= {}
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
fields=None
gene_relations= []
for line in protein_relations:
    line = line.split(" ")
    if not skipped_first_line:
        fields = line
        fields[0] = "gene_1"
        fields[1] = "gene_2"
        fields[15] = "combined_score"
        skipped_first_line = True
    else:
        # rel ={
        #     fields[0] : alias_dict[line[0]],
        #     fields[1] : alias_dict[line[1]],
        #     fields[2] : int(line[2]),
        #     fields[3] : int(line[3]),
        #     fields[4] : int(line[4]),
        #     fields[5] : int(line[5]),
        #     fields[6] : int(line[6]),
        #     fields[7] : int(line[7]),
        #     fields[8] : int(line[8]),
        #     fields[9] : int(line[9]),
        #     fields[10] : int(line[10]),
        #     fields[11] : int(line[11]),
        #     fields[12] : int(line[12]),
        #     fields[13] : int(line[13]),
        #     fields[14] : int(line[14]),
        #     fields[15] : int(line[15])
        # }
        rel={}
        for f in range(16):
            if f <= 1:
                rel[fields[f]] = alias_dict[line[f]]
            elif int(line[f])>0:
                rel[fields[f]] = int(line[f])



        gene_relations.append(rel)

        if len(gene_relations) == 500000:
            string_collection.insert_many(gene_relations)
            gene_relations= []
string_collection.insert_many(gene_relations)
protein_relations.close()
print("INFO	OK.")





print("INFO	Creating indexes in MongoDB...")
string_collection.create_index([ ("gene_1", 1) ]) 
string_collection.create_index([ ("gene_2", 1) ]) 
string_collection.create_index([ ("combined_score", 1) ]) 
print("INFO	OK.")



print("INFO	deleting duplicates...")
for gene_symbol in alias_dict.values():
    print(gene_symbol)
    relations = string_collection.find({"gene_1": gene_symbol})
    to_del = []
    for r in relations:
        to_del.append(r["gene_2"])
        # string_collection.delete_one({"gene_1": r["gene_2"], "gene_2":  r["gene_1"]})
    # print(to_del)
    string_collection.delete_many({"gene_1": {"$in": to_del}, "gene_2":  gene_symbol})




print("INFO	Removing intermediate files...")
os.remove("protein.links.full.txt")
os.remove("protein.aliases.txt.gz")
os.remove("protein.aliases.txt")
print("INFO	OK.")