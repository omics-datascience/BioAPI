#!/bin/bash

############# MongoDB Conf ############
ip_mongo="localhost"
port_mongo=27017
user=
password=
db_name="bio_api"

date
python go2mongodb.py $ip_mongo $port_mongo $user $password $db_name 

