#!/bin/bash

############# MongoDB Conf ############
ip_mongo=localhost
port_mongo=27017
user=
password=
db=bio_api
############# Database URL ############
expression_url="https://storage.googleapis.com/gtex_analysis_v8/rna_seq_data/GTEx_Analysis_2017-06-05_v8_RNASeQCv1.1.9_gene_tpm.gct.gz"
annotation_url="https://storage.googleapis.com/gtex_analysis_v8/annotations/GTEx_Analysis_v8_Annotations_SampleAttributesDS.txt"
#######################################

expression_file="GTEx_expressions_data.gct"
annotation_file="GTEx_annotations_data.txt"
date
echo "Descargando bases de datos..."
wget -t 10 -O "$expression_file.gz" $expression_url
wget -t 10 -O $annotation_file $annotation_url 

date
echo "Descomprimiendo base de datos..."
gunzip $expression_file

date
echo "Eliminando lineas de encabezado..."
csvtool drop 2 $expression_file >GTEx_whitout_header.csv
rm $expression_file

date
echo "Eliminando primer columna..." #Corresponde a un ID que no queremos
cut -f2- GTEx_whitout_header.csv >GTEx_whitout_header_and_first_column.csv
rm GTEx_whitout_header.csv

date
echo "Seteando variables..."
inicio=1
incremento=500
fin=$(csvtool -t TAB width GTEx_whitout_header_and_first_column.csv)

date
echo "Dividiendo y procesando archivo..."
cat /dev/null >GTEx_full_dataset.csv
tf=1
for start_col in $(seq $inicio $incremento $fin)
do
	hasta=$(($start_col+$incremento-1))
	filename=columnas_$start_col-$hasta
	echo "	Generando archivo nuevo desde columna "$start_col" hasta "$hasta 
	cut -f $start_col-$hasta GTEx_whitout_header_and_first_column.csv >$filename
	date
	echo "	Transponiendo archivo "$filename"..."
	csvtool -t TAB transpose $filename >>"$filename-transposed.csv"
	date
	rm $filename
	echo "	Uniendo archivo "$filename"..."
	python3 join_datasets.py --annotations_file $annotation_file --expression_file "$filename-transposed.csv" --output_file "$filename-joined.csv"
	date
	rm "$filename-transposed.csv"
	echo "	Agregando al dataset final el archivo "$filename"..."
	if [ $tf -eq 1 ]; 
	then
		head -n 1 "$filename-joined.csv" >>GTEx_full_dataset.csv
		tf=0
	fi
	awk '(NR>1)' "$filename-joined.csv" >>GTEx_full_dataset.csv
	rm "$filename-joined.csv"
done
rm GTEx_whitout_header_and_first_column.csv

date
echo "Dividiendo archivo por tejidos..."
python3 split_dataset_by_tissue.py --transposed_gtex_file GTEx_full_dataset.csv

date
echo "Importando a MongoDB..."
python3 import_gtex_to_mongodb.py --original_gtex GTEx_full_dataset.csv --mongodb_ip $ip_mongo --mongodb_port $port_mongo --mongo_user $user --mongo_pass $password --bioapi_db $db
rm GTEx_full_dataset.csv
rm $annotation_file 

date
echo "Finalizado!"
