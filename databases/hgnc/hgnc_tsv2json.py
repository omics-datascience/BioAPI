#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Descripcion: 
#	Convierte formato del archivo hgnc_complete_set.txt de TSV a uno Json importable en MongoDB 
#   El archivo se descarga de "http://ftp.ebi.ac.uk/pub/databases/genenames/hgnc/tsv/hgnc_complete_set.txt"
# -_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_

import csv
from tqdm import tqdm
import re
import argparse
import unicodedata

class C:
	pass

c = C()
parser = argparse.ArgumentParser(description='Procesa la base de datos HGNC. Genera un nuevo archivo en Formato Json importable en MongoDB.')
parser.add_argument('--input', help='archivo tsv correspondiente a la base de datos HGNC', required=True)
parser.add_argument('--output', help='Nombre del archivo Json de salida', required=False, default="hgnc_output.json")

args = parser.parse_args(namespace=c)

#Campos que quiero eliminar de la DB
fields_to_remove = ["date_approved_reserved","date_symbol_changed","date_name_changed","date_modified","location_sortable","mgd_id","rgd_id"]

#Defino Expresiones regulares para buscar caracteres que producen error en la importacion a MongoDB
er0 = re.compile("\'\'", re.IGNORECASE) #si tiene dos comillas simples juntas 
er1 = re.compile(".\'", re.IGNORECASE) #si tiene cualquier caracter seguido de una tilde '  (por ejemplo, 5' o 3')
er2 = re.compile("\'s", re.IGNORECASE) #si tiene 's  (por ejemplo, descripciones de patologias)
er3 = re.compile("\\xa0", re.IGNORECASE) # si tiene caracter \xa0
er4 = re.compile("\\x80", re.IGNORECASE) # si tiene caracter \x80
er5 = re.compile("\\x90", re.IGNORECASE) # si tiene caracter \x90

	
#Defino funciones
def repair_values(elementos): #arregla caracteres especiales en los strings obtenidos de la base de datos
    r = []
    for e in elementos:
        new_value = e
        if re.search(er0, new_value) != None:
            new_value = new_value.replace(u"\'\'", u"") #Si tiene doble comillas simples, las elimina
        if re.search(er1, new_value) != None:
            if re.search(er2, new_value) != None:
                new_value = new_value.replace(u"\'s", u"s") #Si tiene comilla simple seguido de "s", lo cambio solo por "s" (Ej, Sjogren's syndrome pasa a ser Sjogrens syndrome)
            else:
                new_value = new_value.replace(u"\'", u"p")  #Si tiene solo una comilla simple, las cambio por la letra "p" (Ej, pasaria de 3' a 3p)
        if re.search(er3, new_value) != None:
            new_value = new_value.replace(u"\xa0", u"") #Si tiene el caracter \xa0 lo elimino
        if re.search(er4, new_value) != None:
            new_value = new_value.replace(u"\x80", u"") #Si tiene el caracter \x80 lo elimino
        if re.search(er5, new_value) != None:
            new_value = new_value.replace(u"\x90", u"") #Si tiene el caracter \x90 lo elimino
        r.append(new_value)
    return r

def splitear_string(texto, caracter="|"):
    lista = []
    tmp = texto.split(caracter)
    for value in tmp:
        lista.append(value)
    if len(lista) == 0:
        return ""
    elif len(lista) == 1:
        return(lista[0])
    else:
        return lista

if __name__ == '__main__':
    archivo = c.input
    archivo_salida = c.output
    tsvfile = open(archivo)
    contenido = csv.reader(tsvfile, dialect='excel', delimiter='\t') 
    cont_json = []
    print("Procesando archivo...")
    headers = next(contenido) 
    # c=0
    for registro in tqdm(contenido):
        # c=c+1
        registro_arreglado = repair_values(registro)
        # if c==15130:
        #     print(registro)
        #     print(registro_arreglado)
        json_file = {}
        for i in range(0, len(headers)):
            if headers[i] not in fields_to_remove:
                if headers[i] == "lsdb":
                    value = {}
                    tmp = splitear_string(registro_arreglado[i])
                    if tmp != "":
                        for e in range(0,len(tmp),2):
                            value[tmp[e]] = tmp[e+1]
                        json_file[headers[i]] = value
                else:
                    v = splitear_string(registro_arreglado[i])
                    if v != "":
                        json_file[headers[i]] = v
        cont_json.append(json_file)
        
    
    jsonfile = open(archivo_salida, "w")
    jsonfile.write(str(cont_json).replace("'", "\""))
    jsonfile.close()
    print("Finalizado!")