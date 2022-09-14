import csv
from tqdm import tqdm
import argparse
from pymongo import MongoClient, ASCENDING
import numpy as np
import time
import os

class C:
    pass

DOCUMENTOS_X_INSERCION = 100000

def writemongodb(data, tissue, mongo_db):
    try:
        # Conexión a la coleccion
        gtex_db_tissue = mongo_db[tissue]
        gtex_db_tissue.insert_many(data[data != 0].tolist()) #Elimino los ceros y paso a lista
    except TypeError as e:
        print(e)
        print(data)
    except Exception as e:
        print(e)
        print(data)
    finally:
        return True

def createindex(tissue, mongo_db):
    try:
        # Conexión a la coleccion
        gtex_db_tissue = mongo_db[tissue]
        gtex_db_tissue.create_index([ ("gene", ASCENDING) ])
    except Exception as e:
        print(e)
    finally:
        return True

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
    distinct.sort(reverse=True)
    return distinct

if __name__ == '__main__':
    c = C()
    parser = argparse.ArgumentParser(
        description='Importa la base de datos GTEx a MongoDB.')
    parser.add_argument('--original_gtex', help='Archivo original de expresiones correspondiente a la base de datos descargada desde GTEx',
                        required=True)
    parser.add_argument('--mongodb_ip', help='IP de la base de datos MongoDB', default="localhost", required=False)
    parser.add_argument('--mongodb_port', help='Puerto de la base de datos MongoDB', default="27017", required=False)
    parser.add_argument('--mongo_user', help='Usuario para MongoDB', default="root", required=False)
    parser.add_argument('--mongo_pass', help='Password para MongoDB', default="root", required=False)
    parser.add_argument('--bioapi_db', help='Base de datos para BioAPI', default="bio_api", required=False)
    parser.add_argument('--rm_tmp', help='Elimina archivos temporales correspondientes a los valores de expresiones de cada tejido', default=1, choices=[0, 1], required=False)


    args = parser.parse_args(namespace=c)

    archivo_original_gtex = c.original_gtex
    database_mongo_ip = c.mongodb_ip
    database_mongo_port = c.mongodb_port
    mongo_user = c.mongo_user
    mongo_pass = c.mongo_pass
    mongo_database = c.bioapi_db
    remove_tmp_files = c.rm_tmp

    # Conexión a MongoDB
    # Conexión a MongoDB
    mongoClient = MongoClient(database_mongo_ip + ":" + database_mongo_port,
                                username=mongo_user,
                                password=mongo_pass,
                                authSource='admin',
                                authMechanism='SCRAM-SHA-1')

    # Conexión a la base de datos GTEx
    db = mongoClient[mongo_database]

    # Obtengo los diferentes tejidos
    tissues = get_unique_tissues(archivo_original_gtex)

    num_reg=0
    for tissue in tissues:
        print(" Insertando tejido " + tissue)
        print(" "+str(time.strftime("%Y-%m-%d %H:%M")))
        count_docs = 0
        db_file = open(tissue.replace(" ","_")+".csv")
        contenido_db = csv.reader(db_file)
        header = next(contenido_db)  # Guarda valores del header
        docs = np.zeros((DOCUMENTOS_X_INSERCION,), dtype=object)
        for row in tqdm(contenido_db,desc=tissue):  # Por cada linea en la DB (por cada muestra)...
            for i in range(2, len(row)-3):  # Por cada columna en la DB (por cada gen sin llegar a las ultimas dos columnas que son los tejidos)
                try:
                    d = {
                        "expression": float(row[i]),
                        "gene": header[i],
                        "sample_id": row[0],
                        "tissue_detail": row[len(row)-1]
                    }
                    docs[count_docs]=d
                    count_docs += 1
                    num_reg+=1
                    if count_docs == DOCUMENTOS_X_INSERCION:
                        count_docs = 0
                        writemongodb(docs, tissue, db)
                        docs.fill(0)
                except KeyError as e:
                    print(f"Error al obtener los datos de GTEx!. Detalle: {e}")
        if len(docs) > 0:
            writemongodb(docs, tissue, db)

        print(" Creando indices al tejido " + tissue)
        print(" "+str(time.strftime("%Y-%m-%d %H:%M")))
        createindex(tissue, db)

        db_file.close()
        if remove_tmp_files:
            os.remove(tissue.replace(" ","_")+".csv")

    mongoClient.close()


    print(f"FINALIZADO!\n\tSe cargaron {num_reg} registros!")  # Son aproximadamente 1.000.000.000 de documentos!
    print(time.strftime("%Y-%m-%d %H:%M"))