#!/bin/bash

############# MongoDB Conf ############
ip_mongo=localhost
port_mongo=27017
user=
password=
db=bio_api
#######################################
CIVIC_URL="https://civicdb.org/downloads/nightly/nightly-GeneSummaries.tsv"
# Using this URL you always get the latest release of CiVIC Gene Summaries

date
echo "INFO	Downloading genes database..."
R -f get_datasets.R
echo "INFO	OK."
date
echo "INFO	Importing to MongoDB..."
cat gene_info_grch37.csv | sudo docker container exec -i bio_api_mongo_db mongoimport --verbose=1 --host $ip_mongo --port $port_mongo --username $user --password $password --drop --stopOnError --db $db --collection gene_grch37 --authenticationDatabase admin --type csv --headerline
cat gene_info_grch38.csv | sudo docker container exec -i bio_api_mongo_db mongoimport --verbose=1 --host $ip_mongo --port $port_mongo --username $user --password $password --drop --stopOnError --db $db --collection gene_grch38 --authenticationDatabase admin --type csv --headerline
echo "INFO	OK."
date
echo "INFO	Creating indexes..."
cat createIndex_gene.js | sudo docker container exec -i bio_api_mongo_db mongosh --quiet --host $ip_mongo --port $port_mongo --username $user --password $password
echo "INFO	OK"
date
echo "INFO	Removing intermediate files..."
rm gene_info_grch37.csv
rm gene_info_grch38.csv
echo "INFO	OK."
echo "COMPLETED! You can now access the genes databases from MongoDB!"
