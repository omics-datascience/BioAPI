#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Descripcion:
# Procesa el archivo databases/oncokb/oncokb_precision_oncology_therapies.tsv
#   y lo reformatea de TSV a un Json importable en MongoDB
# -_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_

import csv
import argparse
import re
from typing import List


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

with open('valid_genes_from_hgnc.txt', 'r') as archivo:
    valid_genes = [linea.strip() for linea in archivo.readlines()][1:]

valid_genes_compiled_patern = [re.compile(
    r'\b' + gene + r'\b') for gene in valid_genes]


def search_gene(biomarker_description: str) -> List[str]:
    genes = []
    special_cases = {"NTRK1/2/3": ["NTRK1", "NTRK2", "NTRK3"],
                     "BRCA1/2": ["BRCA1", "BRCA2"],
                     "TSC1/2": ["TSC1", "TSC2"],
                     "PDGFRA/B": ["PDGFRA", "PDGFRB"]
                     }
    for special_case in special_cases:
        if re.search(special_case, biomarker_description):
            genes = special_cases[special_case]

    for i in range(0, len(valid_genes)):
        if re.search(valid_genes_compiled_patern[i], biomarker_description):
            if valid_genes[i] not in genes:
                genes.append(valid_genes[i])

    return genes


if __name__ == '__main__':
    archivo = c.input  # type: ignore
    archivo_salida = c.output  # type: ignore
    tsvfile = open(archivo)

    contenido = csv.reader(tsvfile, delimiter='\t')
    cont_json = []
    patron = "\?\s*\d+\s*\*"

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
            json_file[headers[i]] = json_file[headers[i]].replace("�", " ")
            json_file[headers[i]] = json_file[headers[i]].replace("\n", " ")
            if headers[i] == "drug_classification" and str(json_file[headers[i]]).upper() == "NA":
                json_file[headers[i]] = ""
            if headers[i] == "fda_first_approval":
                if re.search(patron, str(json_file[headers[i]])):
                    json_file[headers[i]] = json_file[headers[i]
                                                      ].replace("?", "-").replace("*", "")
            if headers[i] == "fda_recognized_biomarkers":
                json_file["hgnc_symbol"] = search_gene(json_file[headers[i]])

        cont_json.append(json_file)

    jsonfile = open(archivo_salida, "w")
    jsonfile.write(str(cont_json).replace("'", "\""))
    jsonfile.close()
    print("Finalizado!")
