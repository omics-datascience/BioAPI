import urllib.request
import os
import gzip
import shutil
from pymongo import MongoClient

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
print("INFO	OK.")

print("INFO Uncompresing anotations")
with gzip.open('goa_human_isoform.gaf.gz', 'rb') as f_in:
    with open('goa_human_isoform.gaf', 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)
print("INFO	OK.")


print("INFO	Processing Gene Ontology database...")

go = open("go.obo", "r")
line = go.readline().strip()

while line != "[Term]":
    line = go.readline().strip()

all_terms= []
term= {}

for line in go:
    line = line.strip().split(": ",1)
    if line == ["[Term]"] :
        if "relationship" in term:
            relationships = term.pop("relationship")
            if not isinstance(relationships, list): relationships = [relationships]
            for r in relationships:
                r= r.strip().split(" ",1)
                pile_into_dict(term,r[0],r[1])
        if not ("is_obsolete" in term):
            all_terms.append(term)
        term= {}
    elif line == ["[Typedef]"] :
        break
    elif line != [""]:
        pile_into_dict(term,line[0],line[1])
        # if line[0] in term:
            # if isinstance(term[line[0]], list):
                # term[line[0]].append(line[1])
            # else:
                 # term[line[0]]= [term[line[0]],line[1]]
        # else:
            # term[line[0]]= line[1]

# save as JASON
# jsonfile = open("go.json", "w")
# jsonfile.write(str(all_terms))
# jsonfile.close()
print("INFO	OK.")


print("INFO	Processing Gene Ontology anotations database...")
anotations = open("goa_human_isoform.gaf", "r")
line = anotations.readline().strip()

gene={}
all_genes=[]
gene_symbol= ""

for line in anotations:
    if line[0]!="!":
        line = line.strip().split("\t")

        if gene_symbol == line[2]:
            pass
        else:
            all_genes.append(gene)
            gene_symbol = line[2]
            gene={"gene_symbol":gene_symbol}
        pile_into_dict(gene,line[3],line[4])
print(all_genes)

# -----------------
ip_mongo="localhost"
port_mongo="8888"
user="root"
password="root"
db_name="bio_api"

mongoClient = MongoClient(ip_mongo + ":" + port_mongo,username=user,password=password,authSource='admin',authMechanism='SCRAM-SHA-1')


db = mongoClient[db_name]

# jsonfile = open("go.json", "r")
# jsonfile.close()

collection = db["go_anotations"]
collection.drop()
collection.insert_many(all_genes)


# collection = db["go"]
# collection.drop()
# collection.insert_many(all_terms)


mongoClient.close()


print("INFO	OK.")

# ------

# import urllib.request
# import os
# import gzip
# import shutil


# print("INFO	Downloading Gene Ontology anotations database...")
# urllib.request.urlretrieve("http://geneontology.org/gene-associations/goa_human_complex.gaf.gz", "goa_human_complex.gaf.gz")
# print("INFO	OK.")


# print("INFO Uncompresing anotations")
# with gzip.open('goa_human_complex.gaf.gz', 'rb') as f_in:
    # with open('goa_human_complex.gaf', 'wb') as f_out:
        # shutil.copyfileobj(f_in, f_out)
# print("INFO	OK.")



# [{"test":"false"}]

# print("INFO	Removing intermediate files...")
# os.remove("go.obo")
# os.remove("goa_human_complex.gaf.gz")
# print("INFO	OK.")