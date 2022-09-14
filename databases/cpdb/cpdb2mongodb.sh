#!/bin/bash

############# MongoDB Conf ############
ip_mongo=localhost
port_mongo=27017
user=
password=
db=bio_api
#######################################

date
echo "INFO	Downloading CPDB database..."
wget -t 10 -O cpdb_dataset.tsv "http://cpdb.molgen.mpg.de/CPDB/getPathwayGenes?idtype=hgnc-symbol"
echo "INFO	OK."
date
echo "INFO	Reformatting database..."
python3 cpdb_tsv2json.py --input cpdb_dataset.tsv --output cpdb_output.json
echo "INFO	OK."
date
echo "INFO	Importing to MongoDB..."
cat cpdb_output.json | docker container exec -i bio_api_mongo_db mongoimport --verbose=0 --host $ip_mongo --port $port_mongo --username $user --password $password --drop --stopOnError --db $db --collection cpdb --authenticationDatabase admin --jsonArray
echo "INFO	OK."
date
echo "INFO	Creating indexes..."
cat createIndex_cpdb.js | docker container exec -i bio_api_mongo_db mongo --quiet --host $ip_mongo --port $port_mongo --username $user --password $password
echo "INFO	OK"
date
echo "INFO	Removing intermediate files..."
rm cpdb_dataset.tsv
rm cpdb_output.json
echo "INFO	OK."
echo "COMPLETED! You can now access the CPDB database from MongoDB!"