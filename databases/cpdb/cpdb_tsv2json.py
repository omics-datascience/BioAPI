#!/usr/bin/env python
# -*- coding: utf-8 -*-
import csv
from tqdm import tqdm
import re
import argparse

class C:
	pass

c = C()
parser = argparse.ArgumentParser(description='Procesa la base de datos CPDB. Genera un nuevo archivo en Formato Json importable en MongoDB.')
parser.add_argument('--input', help='archivo tsv correspondiente a la base de datos CPDB', required=True)
parser.add_argument('--output', help='Nombre del archivo Json de salida', required=False, default="cpdb_output.json")

args = parser.parse_args(namespace=c)

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
    for registro in tqdm(contenido, desc = 'Reformateando'):
        json_file = {}
        for i in range(0, len(headers)):
            if i == 0:
                json_file[headers[i]] = registro[i].split(" - Homo sapiens (human)")[0]
            elif i == 1:
                if registro[i] == "None" and registro[2] in ["Signalink", "INOH"]:
                    json_file[headers[i]] = json_file[headers[0]] #pongo mismo nombre que el pathway
                else:
                    json_file[headers[i]] = registro[i]
            elif i == 3:
                v = splitear_string(registro[i], ",")
                if v != "":
                    json_file[headers[i]] = v
            else:
                json_file[headers[i]] = registro[i]
        cont_json.append(json_file)
        
    
    jsonfile = open(archivo_salida, "w")
    jsonfile.write(str(cont_json).replace("'", "\""))
    jsonfile.close()
    print("Finalizado!")