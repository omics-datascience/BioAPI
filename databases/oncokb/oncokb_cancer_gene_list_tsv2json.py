#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Descripcion:
# Filtra el archivo cancer_gene_list.tsv con la lista de genes de cancer de OncoKB
#   y lo reformatea de TSV a un Json importable en MongoDB
# -_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_

import csv
import json
import argparse


parser = argparse.ArgumentParser(
    description='Procesa la base de datos de lista de genes relacionados con algun tipo de cancer de OncoKB. Genera un nuevo archivo en Formato Json importable en MongoDB.')
parser.add_argument(
    '--input', help='archivo tsv correspondiente a la base de datos de genes relacionados con cancer de OncoKB', required=True)
parser.add_argument('--output', help='Nombre del archivo Json de salida',
                    required=False, default="oncokb_cgl_output.json")

args = parser.parse_args()


def clean_value(value):
    if value is None:
        return None
    parsed = value.strip()
    if parsed == "" or parsed.upper() == "NULL":
        return None
    if parsed.upper() == "YES":
        return 1
    if parsed.upper() == "NO":
        return 0
    return parsed


if __name__ == '__main__':
    archivo = args.input
    archivo_salida = args.output
    cont_json = []
    print("Procesando archivo...")

    # Permite parsear tanto formato viejo como actualizado del dataset.
    rename_map = {
        'Hugo Symbol': 'hgnc_symbol',
        'GRCh38 RefSeq': 'refseq_transcript',
        'OncoKB Annotated': 'oncokb_annotated',
        'Is Oncogene': 'oncogene',
        'Is Tumor Suppressor Gene': 'tumor_suppressor_gene',
        'MSK-IMPACT': 'msk_impact',
        'MSK-HEME': 'msk_impact_heme',
        'FOUNDATION ONE': 'foundation_one_cdx',
        'FOUNDATION ONE HEME': 'foundation_one_heme',
        'Vogelstein': 'vogelstein',
        'SANGER CGC(05/30/2017)': 'cosmic_cgc',
        'COSMIC CGC (v99)': 'cosmic_cgc',
    }

    excluded_columns = {
        'Entrez Gene ID',
        'GRCh37 Isoform',
        'GRCh37 RefSeq',
        'GRCh38 Isoform',
        'Gene Type',
        'Gene Aliases',
    }

    with open(archivo, newline='', encoding='utf-8') as tsvfile:
        contenido = csv.DictReader(tsvfile, delimiter='\t')
        for registro in contenido:
            json_file = {}

            for header, value in registro.items():
                if header in excluded_columns:
                    continue

                parsed_value = clean_value(value)
                if parsed_value is None:
                    continue

                output_key = rename_map.get(header, header)
                json_file[output_key] = parsed_value

            # En el formato nuevo no hay columnas Is Oncogene/Is Tumor Suppressor Gene.
            if 'oncogene' not in json_file or 'tumor_suppressor_gene' not in json_file:
                gene_type = (registro.get('Gene Type') or '').strip().upper()
                if gene_type:
                    if 'oncogene' not in json_file:
                        json_file['oncogene'] = 1 if 'ONCOGENE' in gene_type else 0
                    if 'tumor_suppressor_gene' not in json_file:
                        json_file['tumor_suppressor_gene'] = 1 if 'TSG' in gene_type else 0

            cont_json.append(json_file)

    with open(archivo_salida, "w", encoding='utf-8') as jsonfile:
        json.dump(cont_json, jsonfile, ensure_ascii=False)

    print("Finalizado!")
