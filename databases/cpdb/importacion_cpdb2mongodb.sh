#!/bin/bash

############# EDIT ##################
ip_mongo=localhost
port_mongo=27017
user=root
password=root
db=bio_api
#######################################

date
echo "INFO	Descargando base de datos CPDB..."
wget -t 10 -O cpdb_dataset.tsv "http://cpdb.molgen.mpg.de/CPDB/getPathwayGenes?idtype=hgnc-symbol"
echo "INFO	OK."
date
echo "INFO	Reformateando base de datos..."
python3 cpdb_tsv2json.py --input cpdb_dataset.tsv --output cpdb_output.json
echo "INFO	OK."
date
echo "INFO	Importando a MongoDB..."
cat cpdb_output.json | docker container exec -i bio_api_mongo_db mongoimport --verbose=1 --host $ip_mongo --port $port_mongo --username $user --password $password --drop --stopOnError --db $db --collection cpdb --authenticationDatabase admin --jsonArray
echo "INFO	OK."
date
echo "INFO	Creando indices..."
cat createIndex_cpdb.js | docker container exec -i bio_api_mongo_db mongo --quiet --host $ip_mongo --port $port_mongo --username $user --password $password
echo "INFO	OK"
date
echo "INFO	Eliminando archivos intermedios..."
rm cpdb_dataset.tsv
rm cpdb_output.json
echo "INFO	OK."
echo "FINALIZADO! ya puede acceder a la base de datos CPDB desde MongoDB!"