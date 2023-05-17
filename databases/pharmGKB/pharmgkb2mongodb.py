import urllib.request
import zipfile
import shutil
from pymongo import MongoClient
import json
import requests, zipfile, io
import os
import sys



############# MongoDB Conf ############
ip_mongo=sys.argv[2]
port_mongo=sys.argv[3]
user=sys.argv[4]
password=sys.argv[5]
db_name=sys.argv[6]
#######################################
url = sys.argv[1]




def pile_into_dict(dic,key,content):
    if key in dic:
        if isinstance(dic[key], list):
            dic[key].append(content)
        else:
             dic[key]= [dic[key],content]
    else:
        dic[key]= content




print("INFO	Downloading PharmGKB database...")
r = requests.get(url)
print("INFO	OK.")
print("INFO	Uncompresing...")
z = zipfile.ZipFile(io.BytesIO(r.content))
z.extractall()
print("INFO	OK.")


print("INFO	Processing PharmGKB database...")

drugs = open("drugLabels.tsv", "r")

drugs_data= []
skiped_first_line = False
for line in drugs:
    line = line.split("\t")
    if not skiped_first_line:
        skiped_first_line = True
    elif line[8]:
        drugs_data.append({"pharmgkb_id":line[0],
        "name":line[1],
        "source":line[2],
        "biomarker_flag":line[3], #if line[3]
        "testing_level":line[4],
        "chemicals":line[10],
        "genes":line[11].split("; "),
        "Variants/Haplotypes":line[12] #if line[3]
        
        })
drugs.close()
print("INFO	OK.")


print("INFO	Conecting to MongoDB...")
mongoClient = MongoClient(ip_mongo + ":" + str(port_mongo),username=user,password=password,authSource='admin',authMechanism='SCRAM-SHA-1')
db = mongoClient[db_name]
print("INFO	OK.")


print("INFO	Importing to MongoDB...")
anotation_colection = db["pharmgkb"]
anotation_colection.drop()
anotation_colection.insert_many(list(drugs_data))
mongoClient.close()
print("INFO	OK.")


# print("INFO	Creating indexes in MongoDB...")
# go_colection.create_index([ ("id", 1) ]) 
# anotation_colection.create_index([ ("gene_symbol", 1) ]) 
# print("INFO	OK.")


print("INFO	Removing intermediate files...")
os.remove("README.pdf")
os.remove("LICENSE.txt")
os.remove("drugLabels.tsv")
os.remove("drugLabels.byGene.tsv")
print("INFO	OK.")