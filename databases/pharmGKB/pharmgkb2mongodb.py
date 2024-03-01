import zipfile
from pymongo import MongoClient
import io
import requests
import os
import sys

# MongoDB Conf ############
ip_mongo = sys.argv[2]
port_mongo = sys.argv[3]
user = sys.argv[4]
password = sys.argv[5]
db_name = sys.argv[6]
#######################################
url = sys.argv[1]

print("INFO	Downloading PharmGKB database...")
r = requests.get(url)
print("INFO	OK.")
print("INFO	Uncompresing...")
z = zipfile.ZipFile(io.BytesIO(r.content))
z.extractall()
print("INFO	OK.")

print("INFO	Processing PharmGKB database...")
drugs = open("drugLabels.tsv", "r")
drugs_data = []
skiped_first_line = False
for line in drugs:
    line = line.split("\t")
    if not skiped_first_line:
        skiped_first_line = True
    elif line[9]:  # Cancer Genome column
        drugs_data.append({"pharmgkb_id": line[0],
                           "name": line[1],
                           "source": line[2],
                           "biomarker_flag": line[3],  # if line[3]
                           "testing_level": line[4],
                           "chemicals": line[11],
                           "genes": line[12].split("; "),
                           "variants_haplotypes": line[13]  # if line[3]
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

print("INFO	Removing intermediate files...")
os.remove("README.pdf")
os.remove("LICENSE.txt")
os.remove("drugLabels.tsv")
os.remove("drugLabels.byGene.tsv")
print("INFO	OK.")
