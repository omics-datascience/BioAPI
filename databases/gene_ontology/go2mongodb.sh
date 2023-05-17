#!/bin/bash

############# MongoDB Conf ############
ip_mongo="localhost"
port_mongo=8888
user="root"
password="root"
db_name="bio_api"
############# Database URL ############
urla="http://purl.obolibrary.org/obo/go.obo"
urlb="http://geneontology.org/gene-associations/goa_human_isoform.gaf.gz"
urlc="http://geneontology.org/gene-associations/goa_human.gaf.gz"

date
python go2mongodb.py $urla $ip_mongo $port_mongo $user $password $db_name $urlb $urlc

