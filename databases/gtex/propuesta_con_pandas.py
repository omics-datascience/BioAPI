import pandas as pd

# Esto en realidad lo levantarias con pd.read_csv(path, ...)
# Aca tambien omiti todos los otros campos
df_expressions = pd.DataFrame({
    'tissue':     ['Lung', 'Lung', 'Breast', 'Breast', 'Brain'],
    'expression':     [12.3, 0.1, 9.212, 8.0, 0.11],
})

df_annotations = None

# Leer https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.join.html
joined = df_expressions.join(df_annotations, on='columna que comparten')

df1_grouped = joined.groupby('tissue')  # Agrupa por tissue, ya no hace falta ponerse a chequear en un diccionario ni ir insertando en una lista

# iterate over each group
for tissue_name, all_tissue_values in df1_grouped:
    print(f'Tissue: {tissue_name}')

    # Esta tecnica se llama list-comprehension, es mas rapida en Python que hacer un for in con codigo adentro
    # Si esto sigue siendo lento, se puede probar creando un arreglo de Numpy con el tamaño ya alocado: docs_to_insert = np.zeros(len(chunk))
    # e ir insertando uno por uno dentro de ese arreglo: docs_to_insert[i] = {...}
    docs_to_insert = [
        {
            'expression': row['expression'],
            # Aca van los otros campos
            # 'gene': row['gene'],
            # 'sample_id': row['sample_id'],
            # 'tissue_detail': row['tissue_detail']
        }
        for _row_index, row in all_tissue_values.iterrows()
    ]

    # print(docs_to_insert)

    # Aca se termina insertando en MongoDB
    # insert_in_mongo(docs, db_name=tissue_name)
