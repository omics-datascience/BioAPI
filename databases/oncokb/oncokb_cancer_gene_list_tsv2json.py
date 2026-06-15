#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Description:
# Filters the cancer_gene_list.tsv file with the OncoKB cancer gene list
#   and reformats it from TSV to a JSON file importable into MongoDB
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


def clean_value(value: str | None) -> str | int | None:
    """Normalize raw TSV values before exporting records to JSON.

    This helper standardizes incoming text values so the output is consistent
    and ready for MongoDB import:
    - trims surrounding whitespace,
    - maps empty values and "NULL" to None,
    - converts YES/NO flags to 1/0,
    - keeps any other non-empty value as string.
    """
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
    input_file = args.input
    output_file = args.output
    output_json = []
    print("Procesando archivo...")

    # Supports parsing both old and updated dataset formats.
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

    with open(input_file, newline='', encoding='utf-8') as tsvfile:
        rows = csv.DictReader(tsvfile, delimiter='\t')
        for record in rows:
            json_record = {}

            for header, value in record.items():
                if header in excluded_columns:
                    continue

                parsed_value = clean_value(value)
                if parsed_value is None:
                    continue

                output_key = rename_map.get(header, header)
                json_record[output_key] = parsed_value

            # The new format does not include Is Oncogene/Is Tumor Suppressor Gene columns.
            if 'oncogene' not in json_record or 'tumor_suppressor_gene' not in json_record:
                gene_type = (record.get('Gene Type') or '').strip().upper()
                if gene_type:
                    if 'oncogene' not in json_record:
                        json_record['oncogene'] = 1 if 'ONCOGENE' in gene_type else 0
                    if 'tumor_suppressor_gene' not in json_record:
                        json_record['tumor_suppressor_gene'] = 1 if 'TSG' in gene_type else 0

            output_json.append(json_record)

    with open(output_file, "w", encoding='utf-8') as jsonfile:
        json.dump(output_json, jsonfile, ensure_ascii=False)

    print("Finalizado!")
