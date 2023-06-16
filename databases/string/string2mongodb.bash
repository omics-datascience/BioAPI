#!/bin/bash

############# MongoDB Conf ############
ip_mongo="localhost"
port_mongo=27017
user=
password=
db_name="bio_api"
############# Database URL ############
url= "https://stringdb-static.org/download/protein.info.v11.5/9606.protein.info.v11.5.txt.gz"

date
python string2mongodb.py $ip_mongo $port_mongo $user $password $db_name $url
