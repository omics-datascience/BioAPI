# BioAPI
A powerful abstraction of gene databases .

#################################################################################################################################

Implementation:
1- Import the HGNC database into MongoDB
	1.1 - Installation requirements: python3 'tqdm' and 'argparse' modules
		pip3 install tqdm argparse
	1.2 - Run the file "importacion_hgnc2mongodb.sh" that is inside the directory "BioAPI/databases/hgnc"
		bash import_hgnc2mongodb.sh
	Edit the import_hgnc2mongodb.sh file in case you want to use a different url and port for MongoDB (default: localhot:27017)
	
2- Run Bio-API
	2.1 - Use docker compose to get the API up
		cd bio-api
		docker-compose up --build -d
	By default, BioAPI runs on localhost:8087. Edit the docker-compose.yml file to modify these values

#################################################################################################################################

Endpoints:
/gene-symbol
	Gets the identifier of a gene from different genomic databases and returns the approved symbol according to HGNC.
	
	Parameters:
	gene_id <string>: Identifier of the gene for any database

	Example:
	http://localhost:8087/genSymbol?gene_id=A1BG-AS 

	Response format:
	1- If the gene_id has an approved symbol:
		{
		   "gene": [
		       "BRCA1"
		   ]
		}
	2- If the gene_id does not have an approved symbol:
	{
	   "gene": null
	}
	3-If an error occurs (400):
	{
  	   "error": "gene_id is mandatory."
	}
	
/genes-symbols
	Get a list of gene IDs in any standard and return a list with the same amount of elements with the symbols approved according to 		HGNC. In case an ID is invalid, 'null' must go in its position.
	
	Parameters:
	genes_ids <string>: List of gene identifiers from any database.

	Example:
	http://localhost:8087/genSymbols?genes_ids=A1BG-AS,BRCC1,buTTi,ENSG00000280634
	
	1- Correct answer:
	{
	    "genes": [
		[
		    "A1BG-AS1"
		],
		[
		    "BRCA1",
		    "ICE2"
		],
		null,
		[
		    "THRIL"
		]
	    ]
	}
	2- If an error occurs (400):
	{
	    "error": "genes_ids is mandatory."
	}



