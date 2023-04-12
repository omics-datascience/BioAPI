#!/bin/bash

############# MongoDB Conf ############
ip_mongo=localhost
port_mongo=27017
user=root
password=root
db=bio_api
############# Database URL ############
oncokb_biomarker_drug_associations_dataset="oncokb_biomarker_drug_associations.tsv"
oncokb_gene_cancer_list_dataset="cancerGeneList.tsv"

date
echo "INFO	Reformatting database $oncokb_biomarker_drug_associations_dataset..."
python3 oncokb_biomarker_drug_tsv2json.py --input $oncokb_biomarker_drug_associations_dataset --output oncokb_bda_output.json
echo "INFO	OK."
date
echo "INFO	Reformatting database $oncokb_gene_cancer_list_dataset..."
python3 oncokb_cancer_gene_list_tsv2json.py --input $oncokb_gene_cancer_list_dataset --output oncokb_cgl_output.json
echo "INFO	OK."
date
echo "INFO	Importing $oncokb_biomarker_drug_associations_dataset to MongoDB..."
cat oncokb_bda_output.json | docker container exec -i bio_api_mongo_db mongoimport --verbose=0 --host $ip_mongo --port $port_mongo --username $user --password $password --drop --stopOnError --db $db --collection oncokb_biomarker_drug_associations --authenticationDatabase admin --jsonArray
echo "INFO	OK."
date
echo "INFO	Importing $oncokb_gene_cancer_list_dataset to MongoDB..."
cat oncokb_cgl_output.json | docker container exec -i bio_api_mongo_db mongoimport --verbose=0 --host $ip_mongo --port $port_mongo --username $user --password $password --drop --stopOnError --db $db --collection oncokb_gene_cancer_list --authenticationDatabase admin --jsonArray
echo "INFO	OK."
date
echo "INFO	Removing intermediate files..."
rm oncokb_bda_output.json
rm oncokb_cgl_output.json
echo "INFO	OK."
echo "COMPLETED! You can now access the OncoKB database from MongoDB!"