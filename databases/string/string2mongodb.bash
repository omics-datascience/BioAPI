#!/bin/bash

############# MongoDB Conf ############
ip_mongo="localhost"
port_mongo=27017
user=
password=
db_name="bio_api"
############# Database URL ############


date
python string2mongodb.py $ip_mongo $port_mongo $user $password $db_name 
