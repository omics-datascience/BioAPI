# BioAPI

A powerful abstraction of genomics databases. Bioapi is a REST API that provides data related to gene nomenclature, gene expression, and metabolic pathways.   
All services are available through a web API accessible from a browser or any other web client. All the responses are in JSON format.

## Services

### Gene symbol validator
Searches the identifier of a gene of **different genomic databases** and returns the approved symbol according to HGNC.  

- URL: /gene-symbol/<*gene_id*>
    - <*gene_id*> is the identifier from which you want to obtain the symbol in HGNC nomenclature  

- Method: GET  

- Required query params: -  

- Success Response:
    - Code: 200
    - Content:
        - `<gene_id>`: list of valid identifiers for the gene_id
    - Example:
        - URL: http://localhost:8000/gene-symbol/A1BG-AS
        - Response:
            ```json
            {
                "A1BG-AS": [
                    "A1BG-AS1"
                ]
            }
            ```


### Genes symbols validator
Searches the identifier of a list of genes of **differents genomics databases** and returns the approved symbols according to HGNC nomenclature.  

- URL: /genes-symbols

- Method: POST  

- Required query params: A body in Json format with the following content
    -  `genes_ids` : list of identifiers that you want to get your approved symbols  

- Success Response:
    - Code: 200
    - Content:
        - `<genes_ids>`: Returns a Json with as many keys as there are genes in the body. For each gene, the value is a list with the valid symbols.  
    - Example:
        - URL: http://localhost:8000/genes-symbols
        - body: 
        `{    "genes_ids" : ["BRCA1","F1-CAR", "BRCC1", "FANCS"]    }`
        - Response:
            ```json
            {
                "BRCA1": [
                    "BRCA1"
                ],
                "BRCC1": [
                    "BRCA1",
                    "ICE2"
                ],
                "F1-CAR": [],
                "FANCS": [
                    "BRCA1"
                ]
            }
            ```  

### Gene Groups
Gets the identifier of a gene, validates it and then returns the group of genes to which it belongs according to HGNC, and all the other genes that belong to the same group.  

- URL: /genes-same-group/<*gene_id*>
    - <*gene_id*> is the dentifier of the gene for any database  

- Method: GET  

- Required query params: -  

- Success Response:
    - Code: 200
    - Content:
        - `gene_id`: HGNC approved gene symbol.  
        - `locus_group`:
        - `locus_type`:
        - `groups`:
            - `gene_group`:
            - `gene_group_id`:
            - `genes`:
            
    - Example:
        - URL: http://localhost:8000/genes-same-group/ENSG00000146648
        - Response:
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
                            "ERBB4",
                            "ERBB2"
                        ]
                    }
                ],
                "locus_group": "protein-coding gene",
                "locus_type": "gene with protein product"
            }
            ```  

### Genes of a metabolic pathway
Get the list of genes that are involved in a pathway for a given database.

- URL: /genes-pathways/<*source*>/<*external_id*>
    - <*source*>: Database to query. Valid options:  
       - KEGG
       - BioCarta
       - EHMN
       - HumanCyc
       - INOH
       - NetPath
       - PID
       - Reactome
       - SMPDB
       - Signalink
       - Wikipathways  
        Using an invalid option returns an empty list of genes.
    - <*external_id*>: Pathway identifier in the source database.

- Method: GET  

- Required query params: -  

- Success Response:
    - Code: 200
    - Content:
        - `genes`: a list of genes involved in the metabolic pathway.  
            
    - Example:
        - URL: http://localhost:8000/genes-pathways/KEGG/hsa00740
        - Response:
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

### Metabolic pathways from different genes  
Gets the common pathways for a list of genes.

- URL: /genes-pathways-intersection
    
- Method: POST  

- Required query params: A body in Json format with the following content
    -  `genes_ids`: list of genes for which you want to get the common metabolic pathways  

- Success Response:
    - Code: 200
    - Content:
        - `pathways`: list of elements of type Json. Each element corresponds to a different metabolic pathway.  
            - `source`: database of the metabolic pathway found.
            - `external_id`: pathway identifier in the source.    
            - `pathway`: name of the pathway.

    - Example:
        - URL: http://localhost:8000/genes-pathways-intersection
        - body: 
        `{    "genes_ids" : ["HLA-B" , "BRAF"]    }`
        - Response:
            ```json
            {
                "pathways": [
                    {
                        "external_id": "hsa04650",
                        "pathway": "Natural killer cell mediated cytotoxicity",
                        "source": "KEGG"
                    }
                ]
            }
            ```  

### Gene expression  
This service gets gene expression in healthy tissue

- URL: /genes-expression
    
- Method: POST  

- Required query params: A body in Json format with the following content
    -  `genes_ids`: list of genes for which you want to get the expression.  
    -  `tissue`: healthy tissue from which you want to get the expression values.  

- Success Response:
    - Code: 200
    - Content:
        The response you get is a list. Each element of the list is a new list containing the expression values for each gene in the same sample from the GTEx database.
        - `<gene_id>`: expression value for the gene_id.

    - Example:
        - URL: http://localhost:8000/genes-expression
        - body: 
        `{    "tissue": "Skin",    "genes_ids": ["BRCA1", "BRCA2"]  }`
        - Response:
            ```json
            [
                [
                    {
                        "BRCA1": 1.627,
                    },
                    {
                        "BRCA2": 0.2182,
                    }
                ],
                [
                    {
                        "BRCA1": 1.27,
                    },
                    {
                        "BRCA2": 0.4777,
                    }
                ],
                [
                    {
                        "BRCA1": 1.462,
                    },
                    {
                        "BRCA2": 0.4883,
                    }
                ]
            ]
            ```  
            *As an example only three samples are shown. Note that in the GTEx database there may be more than 2500 samples for a given healthy tissue.

## Error Responses  
The possible error codes are 400, 404 and 500. The content of each of them is a Json with a unique key called "error" where its value is a description of the problem that produces the error. For example:  
```json
{
    "error": "404 Not Found: invalid gene identifier"
}
```