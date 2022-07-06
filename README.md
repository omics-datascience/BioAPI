# BioAPI

A powerful abstraction of gene databases.


## Requirements

- Python >= 3.6 (tested with Python 3.8). **Python 3.10 currently has an issue with PyMongo**
- MongoDB
- Docker and Docker Compose


## Preparation:

The following steps are required for both development and production sections.

1. Create a Python virtual environment to install some dependencies:
    1. `python3 -m venv venv`
    1. `source venv/bin/activate` (run only when you need to work)
    1. `pip install -r config/requirements.txt`
1. Create MongoDB Docker volumes (just the first time):
    1. `docker volume create --name=bio_api_mongo_data`
    1. `docker volume create --name=bio_api_mongo_config`
1. Import the HGNC database into MongoDB:
    1. Run the file `importacion_hgnc2mongodb.sh` that is inside the directory "BioAPI/databases/hgnc". You can edit the the file in case you want to use a different url and port for MongoDB (default: localhost:27017).


## Development

With the Python environment activated (see instructions above), follow the next steps:

1. Start up MongoDB running `docker-compose -f docker-compose.dev.yml up -d`. `docker-compose -f docker-compose.dev.yml down` to stop.
1. Run Flask app:
    1. Go inside `bio-api` folder.
    1. Run `python3 bioapi.py`
    1. To test changes, run `pytest` command. 
    

## Production

1. Run Bio-API in Docker:
    1. Make a copy of `docker-compose_dist.yml` named `docker-compose.yml` and modified the required fields.
    1. Use docker compose to get the API up: `docker-compose up -d`. By default, BioAPI runs on `localhost:8000`.


## Endpoints:

### **GET**  /gene-symbol/<*gene_id*>

Gets the identifier of a gene from different genomic databases and returns the approved symbol according to HGNC.

*gene_id*: Identifier of the gene for any database

Example: http://localhost:8000/gene-symbol/A1BG-AS 

**Response format:**

If the gene_id has an approved symbol:

```json
{
    "A1BG-AS": [
        "A1BG-AS1"
    ]
}
```

If the gene_id does not have an approved symbol:

```json
{
    "A1BG-AS": []
}
```

If an error occurs (400, 404):

```json
{
    "error": "error description."
}
```


### **POST**  /genes-symbols

Gets the identifiers of a list of genes from different genomic databases and returns the HGNC-approved symbols.

It is mandatory that the body of the request the list of genes be sent with the following Json format:  

```json
{    
    "genes_ids" : ["gen_1","gen_2", "gen_N"]    
}
```

Example: http://localhost:8000/genes-symbols  
body:
> ```json
> {    
>     "genes_ids" : ["NAP1","xyz", "FANCS"]    
> }
> ```

Correct answer:

```json
{
    "BRCC1": [
        "BRCA1",
        "ICE2"
    ],
    "FANCS": [
        "BRCA1"
    ],
    "NAP1": [
        "ACOT8",
        "AZI2",
        "CXCL8",
        "NAP1L1",
        "NAPSA",
        "NCKAP1"
    ],
    "xyz": []
}
```

If an error occurs (400, 404):

```json
{
    "error": "error description."
}
```

### **GET**  /genes-same-group/<*gene_id*>

Gets the identifier of a gene, validates it and then returns the validated gene, the group of genes to which it belongs according to HGNC, and all the other genes that belong to the same group.

*gene_id*: Identifier of the gene for any database

Example: http://localhost:8000/genes-same-group/ENSG00000146648

**Response format:**

If the gene_id has an approved symbol:

```json
{
    "gene_id": "EGFR",
    "groups": [
        {
            "gene_group": "Erb-b2 receptor tyrosine kinases",
            "gene_group_id": "1096",
            "genes": [
                "EGFR",
                "ERBB3",
                "ERBB2",
                "ERBB4"
            ]
        }
    ],
    "locus_group": "protein-coding gene",
    "locus_type": "gene with protein product"
}
```

If an error occurs (400, 404):

```json
{
    "error": "error description."
}
```

### **GET**  genes-pathways/<*source*>/<*external_id*>

Get the list of genes that are involved in a pathway for a given database.  

*source*: Database to query. Valid options: "BioCarta", "EHMN", "HumanCyc", "INOH", "KEGG", "NetPath", "PID", "Reactome", "SMPDB", "Signalink" and "Wikipathways". Using an invalid option returns an empty list of genes.      

*external_id*: Pathway identifier in the source database.

Example: http://localhost:8080/genes-pathways/KEGG/path:hsa00740 

**Response format:**

```json
{
    "genes": [
        "ACP5",
        "ACP1",
        "ACP2",
        "FLAD1",
        "ENPP3",
        "ENPP1",
        "RFK",
        "BLVRB"
    ]
}
```  

if the source or external id is not valid, or if no results are found in the query:  
```json
{
    "genes": []
}
```  

### **POST**  /genes-pathways-intersection  

Gets the common pathways for a list of genes.

It is mandatory that the body of the request the list of genes be sent with the following Json format:  

```json
{    
    "genes_ids" : ["gen_1","gen_2", "gen_N"]    
}
```  

Example: http://localhost:8000/genes-pathways-intersection  
body:  
```json
{    
    "genes_ids" : ["HLA-B" , "BRAF"]
}
```

Correct answer:

```json
{
    "pathways": [
        {
            "external_id": "path:hsa04650",
            "pathway": "Natural killer cell mediated cytotoxicity",
            "source": "KEGG"
        }
    ]
}
```

If an error occurs (400):

```json
{
    "error": "error description."
}
```