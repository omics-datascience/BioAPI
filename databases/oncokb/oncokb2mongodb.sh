#!/bin/bash

############# MongoDB Conf ############
ip_mongo=localhost
port_mongo=27017
user=root
password=root
db=bio_api
############# Database URL ############
oncokb_biomarker_drug_associations_dataset="oncokb_biomarker_drug_associations.tsv"

date
echo "INFO	Reformatting database..."
python3 oncokb_tsv2json.py --input $oncokb_biomarker_drug_associations_dataset --output oncokb_output.json
echo "INFO	OK."
date
echo "INFO	Importing to MongoDB..."
cat oncokb_output.json | docker container exec -i bio_api_mongo_db mongoimport --verbose=0 --host $ip_mongo --port $port_mongo --username $user --password $password --drop --stopOnError --db $db --collection oncokb --authenticationDatabase admin --jsonArray
echo "INFO	OK."
date
echo "INFO	Removing intermediate files..."
rm oncokb_output.json
echo "INFO	OK."
echo "COMPLETED! You can now access the OncoKB database from MongoDB!"