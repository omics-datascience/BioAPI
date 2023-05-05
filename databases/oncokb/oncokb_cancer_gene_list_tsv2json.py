#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Descripcion: 
#	Filtra el archivo cancergeneList.tsv con la lista de genes de cancer de OncoKB
#   y lo reformatea de TSV a un Json importable en MongoDB 
# -_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_

import csv
import argparse

class C:
	pass


c = C()
parser = argparse.ArgumentParser(description='Procesa la base de datos de lista de genes relacionados con algun tipo de cancer de OncoKB. Genera un nuevo archivo en Formato Json importable en MongoDB.')
parser.add_argument('--input', help='archivo tsv correspondiente a la base de datos de genes relacionados con cancer de OncoKB', required=True)
parser.add_argument('--output', help='Nombre del archivo Json de salida', required=False, default="oncokb_cgl_output.json")

args = parser.parse_args(namespace=c)

if __name__ == '__main__':
    archivo = c.input
    archivo_salida = c.output
    tsvfile = open(archivo)
    contenido = csv.reader(tsvfile, dialect='excel', delimiter='\t')
    cont_json = []
    print("Procesando archivo...")
    headers = next(contenido) 
    # Cambio nombres en el header:
    headers[headers.index('Hugo Symbol')] = 'hgnc_symbol'
    headers[headers.index('GRCh38 RefSeq')] = 'refseq_transcript'
    headers[headers.index('OncoKB Annotated')] = 'oncokb_annotated'
    headers[headers.index('Is Oncogene')] = 'oncogene'
    headers[headers.index('Is Tumor Suppressor Gene')] = 'tumor_suppressor_gene'
    headers[headers.index('MSK-IMPACT')] = 'msk_impact'
    headers[headers.index('MSK-HEME')] = 'msk_impact_heme'
    headers[headers.index('FOUNDATION ONE')] = 'foundation_one_cdx'
    headers[headers.index('FOUNDATION ONE HEME')] = 'foundation_one_heme'
    headers[headers.index('Vogelstein')] = 'vogelstein'
    headers[headers.index('SANGER CGC(05/30/2017)')] = 'sanger_cgc' 

    headers_a_filtrar = [1,2,3,4,6,16]

    for registro in contenido:
        json_file = {}
        for i in range(0, len(headers)):
            if i not in headers_a_filtrar:
                if registro[i] != "" and registro[i] != None and registro[i].upper() != 'NULL':
                    if registro[i].upper() == "YES":
                        json_file[headers[i]] = 1
                    elif registro[i].upper() == "NO":
                        json_file[headers[i]] = 0
                    else:
                        json_file[headers[i]] = registro[i]
        cont_json.append(json_file)
        
    jsonfile = open(archivo_salida, "w")
    jsonfile.write(str(cont_json).replace("'", "\""))
    jsonfile.close()
    print("Finalizado!")