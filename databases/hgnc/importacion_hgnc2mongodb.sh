#!/bin/bash

############# EDITAR ##################
ip_mongo=localhost
port_mongo=27017
#######################################

date
echo "INFO	Eliminando base de datos previa..."
mongo --quiet --host $ip_mongo --port $port_mongo remove_previous_hgnc_database.js
echo "INFO	OK"
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
mongoimport  --verbose=1 --host $ip_mongo --port $port_mongo --db genomics_dbs --collection hgnc --jsonArray hgnc_output.json
echo "INFO	OK."
date
echo "INFO	Creando indices..."
mongo --quiet --host $ip_mongo --port $port_mongo createIndex_hgnc.js
echo "INFO	OK"
date
echo "INFO	Eliminando archivos intermedios..."
rm hgnc_dataset.tsv
rm hgnc_output.json
echo "INFO	OK."
echo "FINALIZADO! ya puede acceder a la base de datos HGNC desde MongoDB!"
