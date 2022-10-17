#!/bin/bash

############# MongoDB Conf ############
ip_mongo=localhost
port_mongo=27017
user=
password=
db=bio_api
#######################################

date
echo "INFO	Downloading Ensembl genes database..."
R -f get_datasets.R
echo "INFO	OK."
date
echo "INFO	Importing to MongoDB..."
cat ensembl_gene_grch37.csv | sudo docker container exec -i bio_api_mongo_db mongoimport --verbose=1 --host $ip_mongo --port $port_mongo --username $user --password $password --drop --stopOnError --db $db --collection ensembl_gene_grch37 --authenticationDatabase admin --type csv --headerline --ignoreBlanks
cat ensembl_gene_grch38.csv | sudo docker container exec -i bio_api_mongo_db mongoimport --verbose=1 --host $ip_mongo --port $port_mongo --username $user --password $password --drop --stopOnError --db $db --collection ensembl_gene_grch38 --authenticationDatabase admin --type csv --headerline --ignoreBlanks
echo "INFO	OK."
date
echo "INFO	Creating indexes..."
cat createIndex_ensembl_gene.js | sudo docker container exec -i bio_api_mongo_db mongosh --quiet --host $ip_mongo --port $port_mongo --username $user --password $password
echo "INFO	OK"
date
echo "INFO	Removing intermediate files..."
rm ensembl_gene_grch37.csv
rm ensembl_gene_grch38.csv
echo "INFO	OK."
echo "COMPLETED! You can now access the ensembl genes databases from MongoDB!"
