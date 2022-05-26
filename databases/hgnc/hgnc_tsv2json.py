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

class C:
	pass

c = C()
parser = argparse.ArgumentParser(description='Procesa la base de datos HGNC. Genera un nuevo archivo en Formato Json importable en MongoDB.')
parser.add_argument('--input', help='archivo tsv correspondiente a la base de datos HGNC', required=True)
parser.add_argument('--output', help='Nombre del archivo Json de salida', required=False, default="hgnc_output.json")

args = parser.parse_args(namespace=c)

#Campos que quiero eliminar de la DB
fields_to_remove = ["date_approved_reserved","date_symbol_changed","date_name_changed","date_modified","location","mgd_id","rgd_id", "kznf_gene_catalog"]

#Defino Expresiones regulares para buscar caracteres que producen error en la importacion a MongoDB
er0 = re.compile("\'\'", re.IGNORECASE) #si tiene dos comillas simples juntas 
er1 = re.compile(".\'", re.IGNORECASE) #si tiene cualquier caracter seguido de una tilde '  (por ejemplo, 5' o 3')
er2 = re.compile("\'s", re.IGNORECASE) #si tiene 's  (por ejemplo, descripciones de patologias)

#Defino funciones
def repair_values(elementos): #arregla caracteres especiales en los strings obtenidos de la base de datos
    r = []
    for e in elementos:
        new_value = e.encode('latin1', errors='replace').decode('utf-8', errors='replace')
        if re.search(er0, new_value) != None:
            new_value = new_value.replace("\'\'", "") #Si tiene doble comillas simples, las elimina
        if re.search(er1, new_value) != None:
            if re.search(er2, new_value) != None:
                new_value = new_value.replace("\'s", "s") #Si tiene comilla simple seguido de "s", lo cambio solo por " s" (Ej, Sjogren's syndrome pasa a ser Sjogren s syndrome)
            else:
                new_value = new_value.replace("\'", "p")  #Si tiene solo una comilla simple, las cambio por la letra "p" (Ej, pasaria de 3' a 3p)
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
    i = headers.index('pseudogene.org')
    headers[i] = 'pseudogene'

    # c=0
    for registro in tqdm(contenido, desc = 'Reformateando'):
        # c=c+1
        registro_arreglado = repair_values(registro)
        # if c==535:
        #     print()
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