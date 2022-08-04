import csv
import os
import time
from typing import List
import numpy as np
import numpy
import psutil as psutil
import argparse
from pymongo import MongoClient
import numpy as np
import pandas as pd


class C:
    pass


def writemongodb(data: numpy.ndarray, tissue, mongo_db):
    # Conexión a la coleccion
    gtex_db_tissue = mongo_db[tissue]
    gtex_db_tissue.insert_many(data.tolist())


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
        respuesta[row[0]] = {"tissue": row[5].replace(' ','_'), "tissue_detail": parse_tissue_detail(row[6])}
    return respuesta


def get_mem_usage():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss


def get_diferent_tissues(file_path: str):
    csv_atr = pd.read_csv(file_path, delimiter='\t')
    tejidos = csv_atr.SMTS.unique()
    tejidos_sin_espacios = [x.replace(' ','_') for x in tejidos]
    return tejidos_sin_espacios
    


if __name__ == '__main__':
    c = C()
    parser = argparse.ArgumentParser(
        description='Procesa la base de datos GTEx y la importa a MongoDB.')
    parser.add_argument('--input_db', help='archivo gct (Gene Cluster Text) correspondiente a la base de datos GTEx',
                        required=True)
    parser.add_argument('--input_annotations', help='archivo txt con los atributos anotados para cada muestra',
                        required=True)
    parser.add_argument('--mongodb_ip', help='IP de la base de datos MongoDB', default="localhost", required=False)
    parser.add_argument('--mongodb_port', help='Puerto de la base de datos MongoDB', default="27017", required=False)

    args = parser.parse_args(namespace=c)

    archivo = c.input_db
    anotaciones = c.input_annotations
    database_mongo_ip = c.mongodb_ip
    database_mongo_port = c.mongodb_port

    # Conexión a MongoDB
    mongoClient = MongoClient(database_mongo_ip + ":" + database_mongo_port,
                                username='root',
                                password='root',
                                authSource='admin',
                                authMechanism='SCRAM-SHA-1')
                     
    ann = get_atributes_of_samples(anotaciones)
    tissues = get_diferent_tissues(anotaciones)    

    
    for n_rows in [1_000_000, 500_000, 200_000, 100_000]:
        used_memory = get_mem_usage()
        print(f'Python_memory_usage_on_first_iteration_is\t{(used_memory / 1024) / 1024 }\tmb')
        times: List[float] = []
        chunks_inserted = 1

        # Conexión a la base de datos GTEx
        db = mongoClient[f"gtex_{n_rows}"]

        count = 0
        gct_file = open(archivo)
        contenido_db = csv.reader(gct_file, dialect='excel', delimiter='\t')
        gct_file_version = next(contenido_db)  # Guarda version del archivo
        row_col = next(contenido_db)  # Guarda numero de filas y columnas en el archivo
        header = next(contenido_db)  # Guarda valores del header

        docs = {}
        contador = {}
        for t in tissues:
            docs[t] = np.zeros((n_rows,), dtype=object)
            contador[t] = 0

        
        for row in contenido_db:  # Por cada linea en la DB (por cada gen)...
            for i in range(2, len(row)):  # Por cada columna en la DB (por cada muestra)
                try:
                    d = {
                        "expression": float(row[i]),
                        "gene": row[1],
                        "sample_id": header[i],
                        "tissue_detail": ann[header[i]]["tissue_detail"]
                    }
                    tissue = ann[header[i]]["tissue"]
                    docs[tissue][contador[tissue]] = d
                    contador[tissue] += 1
                    count += 1
                    if contador[tissue] == n_rows:
                        start_time = time.time()
                        writemongodb(docs[tissue], tissue, db)
                        insert_time = time.time() - start_time
                        docs[tissue] = np.zeros((n_rows,), dtype=object)
                        contador[tissue] = 0
                        used_memory = get_mem_usage()
                        print(f'Chunk_of\t{n_rows}\tinserted_in\t{insert_time}\tseconds. Current_Python_memory_usage\t{(used_memory / 1024) / 1024}\tmb')
                        times.append(insert_time)

                        chunks_inserted += 1
                        if chunks_inserted == 15:
                            break
                except KeyError as e:
                    print(f"Error al obtener los datos de GTEx!. Detalle: {e}")

            if chunks_inserted == 15:
                mean_time = round(np.mean(times), 3)
                std_time = round(np.std(times), 3)
                print(f'Average\t{mean_time}\t(±{std_time})\tseconds_to_insert\t{n_rows}documents')
                break

        gct_file.close()
    mongoClient.close()