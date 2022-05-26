#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask
from flask import jsonify
from flask import make_response
from flask import abort
from flask import url_for
from flask import render_template
from flask import request
from flask import redirect
from flask_cors import CORS
import urllib.parse
import os
import pymongo
import json
import re
import os
import requests
import configparser
import logging 

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

#Levanto configuracion
Config = configparser.ConfigParser()
Config.read("config.txt")

#configuracion log
logging.getLogger("urllib3").setLevel(logging.DEBUG)
logging.basicConfig(filename=Config.get('log', 'file'), filemode='a', format='%(asctime)s\t%(name)s\t%(levelname)s\t%(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.DEBUG)
logging.info('BIO-API iniciado')

#Defino header de respuestas (puede que este al pedo)
headers = {}
headers["Content-Type"] = "application/json"

#Funcion de conexion a MongoDB
def conexion_mongodb(url, port, user=None, password=None):
	#Para cuando agreguemos user y pass
	#myclient = pymongo.MongoClient("mongodb://"+user+":"+password+"@"+url+":"+port+"/?authSource=genomics_dbs&authMechanism=SCRAM-SHA-1")
	myclient = pymongo.MongoClient("mongodb://"+url+":"+port+"/?authSource=genomics_dbs&authMechanism=SCRAM-SHA-1")
	return myclient["genomics_dbs"]

#Conexion a MongoDB
try:
	mydb = conexion_mongodb(Config.get('mongodb', 'host'),Config.get('mongodb', 'port'))
except Exception as e:
	logging.error("BioAPI no se pudo conectar a la base de datos MongoDB configurada." + str(e), exc_info=True)


#############   Definicion de funciones   #############
def mapear_gen(gen):
	# gene = gen.upper()
	er = re.compile("^"+re.escape(gen)+"$", re.IGNORECASE) 	
	mycol_hgnc = mydb["hgnc"]		#coneccion a coleccion hgnc
	dbs = ["hgnc_id", "symbol", "status", "alias_symbol", "prev_symbol", "entrez_id", "ensembl_gene_id", "vega_id", "ucsc_id", "ena", "refseq_accession", "ccds_id", "uniprot_ids", "cosmic", "omim_id", "mirbase", "homeodb", "snornabase", "bioparadigms_slc", "orphanet", "pseudogene", "horde_id", "merops", "imgt", "iuphar", "kznf_gene_catalog", "mamit-trnadb", "cd", "lncrnadb", "enzyme_id", "intermediate_filament_db", "agr"]
	#armo query
	or_search = []
	for db in dbs:
		q = { db: {"$regex": er} }
		#q = { db : gene }
		or_search.append(q)
	query = { '$or': or_search, "status":"Approved"}
	proyection = { '_id': 0, 'symbol':1 }
	#hago consulta a la db
	mydocs = mycol_hgnc.find(query, proyection)
	results = []
	for doc in mydocs:
		results.append(doc["symbol"])
	return results

#############   Definicion de endpoints #############
@app.route("/")				#Pantalla de inicio
def inicio():
	# return redirect(url_documentacion, code=302, Response=None)
	return render_template('homePage.html')

@app.route("/ping")			#Para chequear que este levantada la bioapi
def ping_ok():
    output = "ok"
    return make_response(output,200,headers)

@app.route("/bioapi-map")	#Lista todos los endpoint de bioapi
def list_routes():
    output = { "endpoints" : []}
    for rule in app.url_map.iter_rules():
        methods = ','.join(rule.methods)
        line = urllib.parse.unquote("{:50s} {:20s} {}".format(rule.endpoint, methods, rule))
        output["endpoints"].append(line)
    return make_response(output,200,headers)

@app.route("/genSymbol")			
#recibe un ID del gen en cualquier estandard y devuelve el ID del Gen estandarizado. En caso de que no se encuentre debe retornar null en el valor.
def genSymbol():
	respuesta = { "gene" : None}
	try:
		#Controlo parametros
		args = request.args
		if "gene_id" not in args:
			abort(400, "gene_id is mandatory.")	
		gv = mapear_gen(args.get("gene_id"))
		if len(gv)>0:
			respuesta["gene"] = gv
	except TypeError as e:
		abort(400,e)
	except ValueError as e:
		abort(400,e)
	except KeyError as e:
		abort(400,e)

	return make_response(respuesta,200,headers)

@app.route("/genSymbols")			
#recibe un ID del gen en cualquier estandard y devuelve el ID del Gen estandarizado. En caso de que no se encuentre debe retornar null en el valor.
def genSymbols():
	respuesta = { "genes" : []}
	try:
		#Controlo parametros
		args = request.args
		if "genes_ids" not in args:
			abort(400, "genes_ids is mandatory.")
		
		genes = args.get("genes_ids").split(",")
		for gene in genes:
			gv = mapear_gen(gene)
			if len(gv)>0:
				respuesta["genes"].append(gv)
			else:
				respuesta["genes"].append(None)
	except TypeError as e:
		abort(400,e)
	except ValueError as e:
		abort(400,e)
	except KeyError as e:
		abort(400,e)

	return make_response(respuesta,200,headers)

#Manejo de errores
@app.errorhandler(400)
def resource_not_found(e):
	return jsonify(error=str(e)), 400

@app.errorhandler(405)
def resource_not_found(e):
	return jsonify(error=str(e)), 405
	
@app.errorhandler(404)
def resource_not_found(e):
	return jsonify(error=str(e)), 404
	
@app.errorhandler(409)
def resource_not_found(e):
	return jsonify(error=str(e)), 409
	
@app.errorhandler(500)
def resource_not_found(e):
	return jsonify(error=str(e)), 500

if __name__ == "__main__":
	port = int(os.environ.get('PORT', Config.get('flask', 'port')))
	app.run(host='localhost', port=port, debug=True)