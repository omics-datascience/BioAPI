#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
from tqdm import tqdm
import argparse

class C:
    pass

c = C()
parser = argparse.ArgumentParser(
    description='Procesa la base de datos GTEx. Genera archivos en Formato Json importables en MongoDB.')
parser.add_argument('--input_db', help='archivo gct (Gene Cluster Text) correspondiente a la base de datos GTEx v8',
                    required=True)
parser.add_argument('--input_annotations', help='archivo txt con los atributos anotados para cada muestra de la base de datos GTEx v8',
                    required=True)
parser.add_argument('--output_dir', help='Directorio donde se guardaran los archivos CSV generados', required=False, default=None)
args = parser.parse_args(namespace=c)

def parse_tissue_detail(full_tissue_detail: str) -> str:
    aux = full_tissue_detail.split(" - ")
    short_tissue_detail = aux.pop()
    return short_tissue_detail

def get_atributes_of_samples(file_path: str) -> object:
    respuesta = {}
    ann_file = open(file_path)
    contenido_ann = csv.reader(ann_file, dialect='excel', delimiter='\t')
    next(contenido_ann)  # salteo el header del tsv
    for row in contenido_ann:
        respuesta[row[0]] = {"tissue": row[5], "tissue_detail": parse_tissue_detail(row[6])}
    return respuesta

def write_data_to_file_csv(file_name, list_of_list_of_elem):
    with open(file_name, 'a+', newline='') as write_obj:
        csv_writer = csv.writer(write_obj)
        for list_of_elem in list_of_list_of_elem:
            csv_writer.writerow(list_of_elem)


if __name__ == '__main__':
    archivo = c.input_db
    anotaciones = c.input_annotations
    prefijo_archivo_salida = "gtex_v8"
    
    if c.output_dir != None:
        path_out = str(c.output_dir)
        if not path_out.endswith("/"):
            path_out = path_out + "/"
    else:
        path_out = ""

    ann = get_atributes_of_samples(anotaciones)

    count = 1
    gct_file = open(archivo)
    contenido_db = csv.reader(gct_file, dialect='excel', delimiter='\t')
    gct_file_version = next(contenido_db)   #Guarda version del archivo
    row_col = next(contenido_db)            #Guarda numero de filas y columnas en el archivo
    header = next(contenido_db)             #Guarda valores del header
    docs = {}
    for row in tqdm(contenido_db):          #Por cada linea en la DB (por cada gen)...
        for i in range(2, len(row)):        #Por cada columna en la DB (por cada muestra)
            try:
                d = [ float(row[i]), row[1], header[i], ann[header[i]]["tissue_detail"] ]
                tissue = ann[header[i]]["tissue"]
                if tissue not in list(docs.keys()):
                    docs[tissue] = []
                docs[tissue].append(d)
                if len(docs[tissue]) == 1000000:
                    full_filename = path_out + prefijo_archivo_salida + "_" +tissue + ".csv"
                    write_data_to_file_csv(full_filename, docs[tissue])
                    docs[tissue] = []
            except KeyError as e:
                print("Error al obtener los datos de GTEx!. Detalle: " + str(e))
    
    for tissue in list(docs.keys()):
        full_filename = path_out + prefijo_archivo_salida + "_" +tissue + ".csv"
        write_data_to_file_csv(full_filename, docs[tissue])
    
    gct_file.close()