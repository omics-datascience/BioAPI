#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Descripcion:
# Procesa el archivo databases/oncokb/oncokb_precision_oncology_therapies.tsv
#   y lo reformatea de TSV a un Json importable en MongoDB
# -_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_

import csv
import argparse


class C:
    pass


c = C()
parser = argparse.ArgumentParser(
    description='Procesa la base de datos de lista de genes relacionados con algun tipo de cancer de OncoKB. Genera un nuevo archivo en Formato Json importable en MongoDB.')
parser.add_argument(
    '--input', help='archivo tsv correspondiente a la base de datos de terapias oncologicas de presicion de OncoKB', required=True)
parser.add_argument('--output', help='Nombre del archivo Json de salida',
                    required=False, default="oncokb_pot_output.json")

args = parser.parse_args(namespace=c)

if __name__ == '__main__':
    archivo = c.input  # type: ignore
    archivo_salida = c.output  # type: ignore
    tsvfile = open(archivo)
    contenido = csv.reader(tsvfile, dialect='excel', delimiter='\t')
    cont_json = []
    print("Procesando archivo...")
    headers = next(contenido)
    # Cambio nombres en el header:
    headers[headers.index("Year of drug’s first FDA-approval a")
            ] = 'fda_first_approval'
    headers[headers.index("Precision oncology therapy\nN=86")
            ] = 'precision_oncology_therapy'
    headers[headers.index("FDA-recognized biomarker(s) b")
            ] = 'fda_recognized_biomarkers'
    headers[headers.index("Method of biomarker detection c")
            ] = 'method_of_biomarker_detection'
    headers[headers.index("Drug classification  d")] = 'drug_classification'

    for registro in contenido:
        json_file = {}
        for i in range(0, len(headers)):
            json_file[headers[i]] = registro[i].encode(
                'latin1', errors='replace').decode('utf-8', errors='replace')
        cont_json.append(json_file)

    jsonfile = open(archivo_salida, "w")
    jsonfile.write(str(cont_json).replace("'", "\""))
    jsonfile.close()
    print("Finalizado!")
