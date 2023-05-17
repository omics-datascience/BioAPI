#!/bin/bash

############# MongoDB Conf ############
ip_mongo="localhost"
port_mongo=8888
user="root"
password="root"
db_name="bio_api"
############# Database URL ############
url="https://api.pharmgkb.org/v1/download/file/data/drugLabels.zip"


date
python pharmgkb2mongodb.py $url $ip_mongo $port_mongo $user $password $db_name

