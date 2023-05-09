#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Descripcion: 
#	Anota el archivo oncokb_biomarker_drug_associations.tsv con los niveles de evidencia de OncoKB
#   y lo reformatea de TSV a un Json importable en MongoDB 
# -_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_

import csv
import argparse

class C:
	pass

# La siguiente evidencia fue obtenida desde el sitio oficiald e OncoKB: https://www.oncokb.org/levels
EVIDENCE = {
      "Therapeutic": ["1", "2", "3", "3A", "3B", "4", "R1", "R2"],
      "Diagnostic": ["Dx1", "Dx2", "Dx3"],
      "Prognostic": ["Px1", "Px2", "Px3"]
}

c = C()
parser = argparse.ArgumentParser(description='Procesa la base de datos de genes accionables de OncoKB. Genera un nuevo archivo en Formato Json importable en MongoDB.')
parser.add_argument('--input', help='archivo tsv correspondiente a la base de datos de genes accionables de OncoKB', required=True)
parser.add_argument('--output', help='Nombre del archivo Json de salida', required=False, default="oncokb_bda_output.json")

args = parser.parse_args(namespace=c)

#Defino funciones
def get_classification(evidence: str): # Obtiene el nivel de evidencia nivel 2 desde OncoKB
    result = None
    for key in EVIDENCE:
        if evidence in EVIDENCE[key]:
            result = key
            break    
    return result

if __name__ == '__main__':
    archivo = c.input
    archivo_salida = c.output
    tsvfile = open(archivo)
    contenido = csv.reader(tsvfile, dialect='excel', delimiter='\t')
    cont_json = []
    print("Procesando archivo...")
    headers = next(contenido) 
    # Level	Gene	Alterations	Cancer Types	Drugs (for therapeutic implications only)
    # Cambio nombres en el header:
    headers[headers.index('Drugs (for therapeutic implications only)')] = 'drugs'
    headers[headers.index('Cancer Types')] = 'cancer_types'
    headers[headers.index('Level')] = 'level_of_evidence'
    headers[headers.index('Alterations')] = 'alterations'
    headers[headers.index('Gene')] = 'gene'

    for registro in contenido:
        json_file = {}
        for i in range(0, len(headers)):
            if headers[i] == 'level_of_evidence':
                json_file["level_of_evidence"] = registro[i]
                classification = get_classification(registro[i])
                json_file["classification"] = classification
            else: 
                if registro[i] != "":
                    json_file[headers[i]] = registro[i]
        cont_json.append(json_file)
        
    jsonfile = open(archivo_salida, "w")
    jsonfile.write(str(cont_json).replace("'", "\""))
    jsonfile.close()
    print("Finalizado!")