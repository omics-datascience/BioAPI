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
mydb = conexion_mongodb(Config.get('mongodb', 'host'),Config.get('mongodb', 'port'))


#############   Definicion de funciones   #############

# def validar_simbolo_gen(gene_symbol):
# 	respuesta = { "simbolo_valido": True, "detalle": "", "simbolo_aprobado" : "" }	#respuesta default de simbolo aprobado.
# 	#chequeo que no tenga espacios el parametro aprsado como gen
# 	if " " in gene_symbol or "%20" in gene_symbol:
# 		respuesta["simbolo_valido"] = False
# 		respuesta["detalle"] = "Error: El gen ingresado contiene caracteres de espacio: " + gene_symbol + ". Elimine los espacios antes de intentar validar el simbolo de gen."
# 	else:
		
# 		mycol_hugo_nomenclature = mydb["hugo_nomenclature"]				#coneccion a DB: hugo_nomenclature
		
# 		er = re.compile("^"+gene_symbol+"$", re.IGNORECASE) #lo pongo como expresion regular para que sea independiente de mayusculas o minusculas	
# 		myquery = { "Approved symbol": {"$regex": er} }						#Armo query
# 		mydocs = mycol_hugo_nomenclature.find(myquery)											#busco en la DB
# 		if mydocs.count() == 1:			#Si es simbolo aprovado... reviso su estado
# 			if mydocs[0]["Status"] == "Approved":		#estado == aprobado, listo
# 				respuesta["simbolo_aprobado"] = gene_symbol.upper()
# 				respuesta["detalle"] = gene_symbol+" es un simbolo aprobado para la nomenclatura HUGO."
# 			else:
# 				respuesta["detalle"] = gene_symbol+" tiene estado "+mydocs[0]["Status"]+" en la nomenclatura HUGO."
# 				respuesta["simbolo_valido"] = False
# 		else:
# 			respuesta["simbolo_valido"] = False
			
# 		if respuesta["simbolo_valido"] == False:
# 			er = re.compile("(^|\s)"+gene_symbol+"(,|$)", re.IGNORECASE)		#Si el simbolo del gen esta al principio o despues de un espacio y seguido de una coma o al final.
# 			myquery = { "Alias symbols": {"$regex": er} }
# 			mydocs = mycol_hugo_nomenclature.find(myquery)
# 			if mydocs.count() == 1:		#Si lo encontre como alias una sola vez...
# 				respuesta["simbolo_aprobado"] = mydocs[0]["Approved symbol"].upper()
# 				respuesta["detalle"] = respuesta["detalle"] +" "+ gene_symbol+" es un alias del simbolo "+mydocs[0]["Approved symbol"]+"."
# 			elif mydocs.count() > 1:
# 				simbolos_aprobados = []
# 				for d in mydocs:
# 					if d["Approved symbol"].upper() not in simbolos_aprobados:
# 						simbolos_aprobados.append(d["Approved symbol"].upper())
# 				texto_a_devolver = ", ".join(simbolos_aprobados)
# 				pos = texto_a_devolver.rfind(", ")
# 				if pos != -1:
# 					texto_a_devolver = texto_a_devolver[:pos] + " y " + texto_a_devolver[pos + 2:]
# 				respuesta["simbolo_aprobado"] = texto_a_devolver
# 				respuesta["detalle"] = respuesta["detalle"] +" "+ gene_symbol+" es un alias del/los simbolo/s "+texto_a_devolver+"."
# 			else:
# 				myquery = { "Previous symbols": {"$regex": er} }
# 				mydocs = mycol_hugo_nomenclature.find(myquery)
# 				if mydocs.count() == 1:		#Si lo encontre como simbolo previo una sola vez...
# 					respuesta["simbolo_aprobado"] = mydocs[0]["Approved symbol"].upper()
# 					respuesta["detalle"] = respuesta["detalle"] +" "+ gene_symbol+" es un simbolo previo de "+mydocs[0]["Approved symbol"]+"."
# 				elif mydocs.count() > 1:
# 					simbolos_aprobados = []
# 					for d in mydocs:
# 						if d["Approved symbol"].upper() not in simbolos_aprobados:
# 							simbolos_aprobados.append(d["Approved symbol"].upper())
# 					texto_a_devolver = ", ".join(simbolos_aprobados)
# 					pos = texto_a_devolver.rfind(", ")
# 					if pos != -1:
# 						texto_a_devolver = texto_a_devolver[:pos] + " y " + texto_a_devolver[pos + 2:]
# 					respuesta["simbolo_aprobado"] = texto_a_devolver
# 					respuesta["detalle"] = respuesta["detalle"] +" "+ gene_symbol+" es un simbolo previo del/los simbolo/s "+texto_a_devolver+"."
# 				else:
# 					respuesta["detalle"] = "El simbolo de gen ingresado no un simbolo valido, simbolo previo o alias segun la nomenclatura HUGO."
# 	return respuesta

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
	try:
		#Controlo parametros
		args = request.args
		if "gen_id" not in args:
			abort(400, "Parametro incorrecto. Parametros valido: gen_id.")	
		respuesta = buscar_caracteristicas_dbsnp(version_genoma, id_dbsnp)
	except TypeError as e:
		abort(400,e)
	except ValueError as e:
		abort(400,e)
	except KeyError as e:
		abort(400,e)

	return make_response(respuesta,200,headers)
# 	logging.info('hello world')



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
