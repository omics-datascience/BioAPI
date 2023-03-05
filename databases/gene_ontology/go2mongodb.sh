#!/bin/bash

############# MongoDB Conf ############
# ip_mongo=localhost
# port_mongo=8888
# user=root
# password=root
# db=bio_api
#######################################



# echo "INFO	Downloading Gene Ontology database..."
# wget -t 10 -O "gos.obo" "purl.obolibrary.org/obo/go.obo"
# echo "INFO	OK."

# echo "INFO	Downloading Gene Ontology anotations database..."
# wget -t 10 -O goa_human_complex.gaf.gz http://geneontology.org/gene-associations/goa_human_complex.gaf.gz
# echo "INFO	OK."


# echo "Uncompresing anotations base de datos..."
# gunzip goa_human_complex.gaf.gz


python go2mongo.py



# echo "INFO	Removing intermediate files..."
# rm go.obo
# rm goa_human_complex.gaf.gz





# echo "INFO	Importing to MongoDB..."
# cat go.json | docker container exec -i bio_api_mongo_db mongoimport --verbose=1 --host $ip_mongo --port $port_mongo --username $user --password $password --drop --stopOnError --db $db --collection go --authenticationDatabase admin --jsonArray
# echo "INFO	OK."


# cat go.json | docker container exec -i bio_api_mongo_db mongoimport --verbose=1 --host localhost --port 27017 --username admin --password admin1 --drop --stopOnError --db bio_api --collection go --authenticationDatabase admin --jsonArray