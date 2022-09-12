import argparse
import dask.dataframe as dd
import pandas as pd
import csv
from typing import Dict

class C:
    pass

c = C()
parser = argparse.ArgumentParser( description='Ordena (sort) el dataset traspuesto de GTEx por tejido')
parser.add_argument('--transposed_gtex_file', help='Archivo GTEx Traspuesto y con la informacion del tejido', required=True)  
args = parser.parse_args(namespace=c)

transposed_gtex_file = c.transposed_gtex_file

def get_unique_tissues(dataset_path: str) -> list:
    distinct = []
    gtex_file = open(dataset_path)
    content = csv.reader(gtex_file)
    header = next(content)  # salteo el header
    tissue_col = len(header)-2
    for row in content:
        tissue = row[tissue_col]
        if tissue not in distinct:
            distinct.append(tissue)
    distinct.sort()
    gtex_file.close()
    return distinct

def split_in_tissue_files(dataset_path: str):
    gtex_file = open(dataset_path)
    content = csv.reader(gtex_file)
    header = next(content)  # almaceno el header
    tissue_col = len(header)-2
    tissues = get_unique_tissues(dataset_path)
    files = {}
    for tissue in tissues:
        files[tissue] = csv.writer(open(tissue.replace(" ", "_")+".csv", 'w'))
        files[tissue].writerow(header)
    for row in content:
        tissue = row[tissue_col]
        files[tissue].writerow(row)
    # for tissue in tissues:
    #     files[tissue].close()
    return True
        
res = split_in_tissue_files(transposed_gtex_file)
print(res)
