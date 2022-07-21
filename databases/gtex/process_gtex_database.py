import csv
from tqdm import tqdm
import argparse
from pymongo import MongoClient


class C:
    pass


def writemongodb(data, tissue, mongo_db):
    # Conexión a la coleccion
    gtex_db_tissue = mongo_db[tissue]
    gtex_db_tissue.insert_many(data)


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
    mongoClient = MongoClient(database_mongo_ip + ":" + database_mongo_port)

    # Conexión a la base de datos GTEx
    db = mongoClient["gtex"]

    # Obtengo atributos de la muestra
    ann = get_atributes_of_samples(anotaciones)

    count = 0
    gct_file = open(archivo)
    contenido_db = csv.reader(gct_file, dialect='excel', delimiter='\t')
    gct_file_version = next(contenido_db)  # Guarda version del archivo
    row_col = next(contenido_db)  # Guarda numero de filas y columnas en el archivo
    header = next(contenido_db)  # Guarda valores del header

    docs = {}
    for row in tqdm(contenido_db):  # Por cada linea en la DB (por cada gen)...
        for i in range(2, len(row)):  # Por cada columna en la DB (por cada muestra)
            try:
                d = {
                    "expression": float(row[i]),
                    "gene": row[1],
                    "sample_id": header[i],
                    "tissue_detail": ann[header[i]]["tissue_detail"]
                }
                tissue = ann[header[i]]["tissue"]
                if tissue not in list(docs.keys()):
                    docs[tissue] = []
                docs[tissue].append(d)
                count += 1
                if len(docs[tissue]) == 1000000:
                    documents = docs[tissue]
                    docs[tissue] = []
                    writemongodb(documents, tissue, db)
            except KeyError as e:
                print(f"Error al obtener los datos de GTEx!. Detalle: {e}")

    for tissue in list(docs.keys()):
        writemongodb(docs[tissue], tissue, db)

    gct_file.close()
    print(f"FINALIZADO!\n\tSe cargaron {count} registros!")  # Son aproximadamente 1.000.000.000 de documentos!
