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

with open('valid_genes_from_hgnc.txt', 'r') as file:
    hgnc_genes = []  # list of valid genes symbols
    hgnc_aliases = {}  # dict of aliases and their valid symbols. If an alias has 2 or more valid symbols it will not appear in dict
    hgnc_previous = {}  # dict of previous and their valid symbols. If an previous has 2 or more valid symbols it will not appear in dict
    aliases_with_multiple_valid_symbols = []
    previous_with_multiple_valid_symbols = []

    content = file.readlines()[1:]
    for line in content:
        if line[-1:] == "\n":
            line = line[:-1]
        values = line.split("\t")
        hgnc_genes.append(values[0])

        if len(values) > 1:
            aliases = values[1].split(",")
            for alias in aliases:
                alias = alias.strip()
                if alias not in hgnc_aliases:
                    # { "alias" : "symbol"}
                    hgnc_aliases[alias] = values[0]
                else:
                    if alias not in aliases_with_multiple_valid_symbols:
                        aliases_with_multiple_valid_symbols.append(alias)
        if len(values) > 2:
            previous = values[2].strip().split(",")
            for prev in previous:
                prev = prev.strip()
                if prev not in hgnc_previous:
                    # { "prev" : "symbol"}
                    hgnc_previous[prev] = values[0]
                else:
                    if prev not in previous_with_multiple_valid_symbols:
                        previous_with_multiple_valid_symbols.append(prev)

    for a in aliases_with_multiple_valid_symbols:
        del hgnc_aliases[a]
    for p in previous_with_multiple_valid_symbols:
        del hgnc_previous[p]

valid_genes_compiled_patern = [re.compile(
    r'\b' + gene + r'\b') for gene in hgnc_genes]

aliases_compiled_patern = []
for alias in hgnc_aliases:
    try:
        aliases_compiled_patern.append(re.compile(r'\b' + alias + r'\b'))
    except Exception:
        pass

previous_compiled_patern = []
for prev in hgnc_previous:
    try:
        previous_compiled_patern.append(re.compile(r'\b' + prev + r'\b'))
    except Exception:
        pass


def search_gene(biomarker_description: str) -> List[str]:
    genes = []
    special_cases = {"NTRK1/2/3": ["NTRK1", "NTRK2", "NTRK3"],
                     "BRCA1/2": ["BRCA1", "BRCA2"],
                     "TSC1/2": ["TSC1", "TSC2"],
                     "PDGFRA/B": ["PDGFRA", "PDGFRB"]
                     }
    for special_case in special_cases:
        if re.search(special_case, biomarker_description):
            genes.extend(special_cases[special_case])

    for i in range(0, len(hgnc_genes)):
        if re.search(valid_genes_compiled_patern[i], biomarker_description):
            genes.append(hgnc_genes[i])
    a = 0
    for alias in hgnc_aliases:
        if re.search(aliases_compiled_patern[a], biomarker_description):
            genes.append(hgnc_aliases[alias])
        a += 1
    p = 0
    for prev in hgnc_previous:
        if re.search(previous_compiled_patern[p], biomarker_description):
            genes.append(hgnc_previous[prev])
        p += 1
    genes = list(set(genes))  # Remove duplicate genes
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
