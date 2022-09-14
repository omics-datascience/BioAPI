import argparse
# import dask.dataframe as dd
import pandas as pd

class C:
    pass

c = C()
parser = argparse.ArgumentParser(
    description='Combina (join) los archivos de datos de expresion y de anotaciones de la DB GTEx')
parser.add_argument('--expression_file', help='matriz de expresion (Archivo original GTEx Traspuesto)', required=True)
parser.add_argument('--annotations_file', help='matriz de anotaciones (Archivo original GTEx)', required=True)
parser.add_argument('--output_file', help='nombre del archivo de salida (puede incluir el path)', default="joined_file.csv", required=False)   
args = parser.parse_args(namespace=c)

expression_file = c.expression_file
annotations_file = c.annotations_file
output_file = c.output_file



print("\tLevantando expressiones...")
df_expression = pd.read_csv(expression_file, 
                            #skiprows=1,
                            #sample=sample_size,
                            #blocksize="50MB",
                            #usecols=[0,1,2],
                            index_col=0,
                            dtype='object')

print("\tLevantando anotaciones...")
df_annotation = pd.read_csv(annotations_file,
                            delimiter='\t',
                            usecols=['SAMPID', 'SMTS', 'SMTSD'],
                            index_col='SAMPID',
                            dtype='object')

print("\tJoineando...")
joined_dataset = df_expression.join(df_annotation)

print("\tGuardando...")
joined_dataset.to_csv(output_file )
print("\tFinalizado!")