#!/bin/bash

############# MongoDB Conf ############
ip_mongo=localhost
port_mongo=27017
user=
password=
db=bio_api
############# Database URL ############
hgnc_url="ftp://ftp.ebi.ac.uk/pub/databases/genenames/hgnc/tsv/hgnc_complete_set.txt"

date
echo "INFO	Downloading HGNC database..."
wget -t 10 -O hgnc_dataset.tsv $hgnc_url
echo "INFO	OK."
date
echo "INFO	Reformatting database..."
python3 hgnc_tsv2json.py --input hgnc_dataset.tsv --output hgnc_output.json
echo "INFO	OK."
date
echo "INFO	Importing to MongoDB..."
cat hgnc_output.json | docker container exec -i bio_api_mongo_db mongoimport --verbose=1 --host $ip_mongo --port $port_mongo --username $user --password $password --drop --stopOnError --db $db --collection hgnc --authenticationDatabase admin --jsonArray
echo "INFO	OK."
date
echo "INFO	Creating indexes..."
cat createIndex_hgnc.js | docker container exec -i bio_api_mongo_db mongosh --quiet --host $ip_mongo --port $port_mongo --username $user --password $password
echo "INFO	OK"
date
echo "INFO	Removing intermediate files..."
rm hgnc_dataset.tsv
rm hgnc_output.json
echo "INFO	OK."
echo "FCOMPLETED! You can now access the HGNC database from MongoDB!"
