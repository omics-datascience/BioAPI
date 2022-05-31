#!/bin/bash

############# EDIT ##################
ip_mongo=localhost
port_mongo=27017
user=root
password=root
db=bio_api
#######################################

date
echo "INFO	Descargando base de datos HGNC..."
wget -t 10 -O hgnc_dataset.tsv "ftp://ftp.ebi.ac.uk/pub/databases/genenames/hgnc/tsv/hgnc_complete_set.txt"
echo "INFO	OK."
date
echo "INFO	Reformateando base de datos..."
python3 hgnc_tsv2json.py --input hgnc_dataset.tsv --output hgnc_output.json
echo "INFO	OK."
date
echo "INFO	Importando a MongoDB..."
cat hgnc_output.json | docker container exec -i bio_api_mongo_db mongoimport --verbose=1 --host $ip_mongo --port $port_mongo --username $user --password $password --drop --stopOnError --db $db --collection hgnc --authenticationDatabase admin --jsonArray
echo "INFO	OK."
date
echo "INFO	Creando indices..."
cat createIndex_hgnc.js | docker container exec -i bio_api_mongo_db mongo --quiet --host $ip_mongo --port $port_mongo --username $user --password $password
echo "INFO	OK"
date
echo "INFO	Eliminando archivos intermedios..."
rm hgnc_dataset.tsv
rm hgnc_output.json
echo "INFO	OK."
echo "FINALIZADO! ya puede acceder a la base de datos HGNC desde MongoDB!"
