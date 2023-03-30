# BioAPI

A powerful abstraction of genomics databases. Bioapi is a REST API that provides data related to gene nomenclature, gene expression, and metabolic pathways. All services are available through a web API accessible from a browser or any other web client. All the responses are in JSON format.

This document is focused on the **development** of the system. If you are looking for documentation for a production deployment see [DEPLOYING.md](DEPLOYING.md).


## Integrated databases

BioAPI obtains information from different bioinformatic databases. These databases were installed locally to reduce data search time. The databases currently integrated to BioAPI are:
1. Gene nomenclature: [HUGO Gene Nomenclature Committee](https://www.genenames.org/).  
HGNC is the resource for approved human gene nomenclature. Downloaded from its official website in September 2022.  
2. Gene information: [ENSEMBL](http://www.ensembl.org/biomart/martview).  
BioMart data mining tool was used to obtain a gene-related dataset from Ensembl. Ensembl is a genome browser for vertebrate genomes that supports research in comparative genomics, evolution, sequence variation and transcriptional regulation. Ensembl annotate genes, computes multiple alignments, predicts regulatory function and collects disease data. Downloaded using *BioMart data mining tool* in September 2022.  
3. Metabolic pathways: [ConsensusPathDB](http://cpdb.molgen.mpg.de/).  
ConsensusPathDB-human integrates interaction networks in Homo sapiens including binary and complex protein-protein, genetic, metabolic, signaling, gene regulatory and drug-target interactions, as well as biochemical pathways. Data originate from currently 31 public resources for interactions (listed below) and interactions that we have curated from the literature. The interaction data are integrated in a complementary manner (avoiding redundancies), resulting in a seamless interaction network containing different types of interactions. Downloaded from its official website in September 2022.          
4. Gene expression: [Genotype-Tissue Expression (GTEx)](https://gtexportal.org/home/).  
The Genotype-Tissue Expression (GTEx) project is an ongoing effort to build a comprehensive public resource to study tissue-specific gene expression and regulation. Samples were collected from 54 non-diseased tissue sites across nearly 1000 individuals, primarily for molecular assays including WGS, WES, and RNA-Seq. GTEx is being used in its version [GTEx Analysis V8 (dbGaP Accession phs000424.v8.p2)](https://gtexportal.org/home/datasets#datasetDiv1) and was downloaded from its official website in September 2022.  


## Services included in BioAPI  

### Genes symbols validator

Searches the identifier of a list of genes of different genomics databases and returns the approved symbols according to HGNC nomenclature.  

- URL: /gene-symbols
- Method: POST  
- Params: A body in Json format with the following content
    -  `gene_ids` : list of identifiers that you want to get your approved symbols  
- Success Response:
    - Code: 200
    - Content:
        - `<gene_ids>`: Returns a Json with as many keys as there are genes in the body. For each gene, the value is a list with the valid symbols.  
    - Example:
        - URL: http://localhost:8000/gene-symbols
        - body: 
        `{    "gene_ids" : ["BRCA1","F1-CAR", "BRCC1", "FANCS"]    }`
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


### Genes symbols finder

Service that takes a string of any length and returns a list of genes that contain that search criteria.  

- URL: /gene-symbols-finder
- Method: GET  
- Params: 
    - `query` : gene search string
    - `limit`: number of elements returned by the service. Default 50.
- Success Response:
    - Code: 200
    - Content: a list of gene symbols matching the search criteria.  
    - Example:
        - URL: http://localhost:8000/gene-symbols-finder/?limit=50&query=BRC
        - Response:
            ```json
            [
                "BRCA1",
                "BRCA1P1",
                "BRCA2",
                "BRCC3",
                "BRCC3P1"
            ]
            ```  


### Genes information

From a list of valid genes, obtain their descriptions, types and chromosomal coordinates for the reference human genomes GRCh37 and GRCh37.  

- URL: /gene-symbols
- Method: POST  
- Params: A body in Json format with the following content
    -  `gene_ids` : list of valid genes identifiers  
- Success Response:
    - Code: 200
    - Content:
        - `<gene_ids>`: Returns a Json with as many keys as there are genes in the body. For each gene, the value is a Json with the following format:
            -   `description` : gene description
            -   `type` : gene type (example: protein_coding)
            -   `chromosome` : chromosome where the gene is located
            -   `start` : chromosomal position of gene starts for the reference genome GRCh38
            -   `end` : chromosomal position of gene ends for the reference genome GRCh38
            -   `start_GRCh37` : chromosomal position of gene starts for the reference genome GRCh37
            -   `end_GRCh37` : chromosomal position of gene ends for the reference genome GRCh37
    - Example:
        - URL: http://localhost:8000/information-of-genes
        - body: 
        `{    "gene_ids" : ["ACTN4","ACTR3C"]    }`
        - Response:
            ```json
            {
                "ACTN4": 
                {
                    "description": "actinin alpha 4 [Source:HGNC Symbol;Acc:HGNC:166]",
                    "chromosome": "19",
                    "end": "38731589",
                    "end_GRCh37": "39222223",
                    "start": "38647649",
                    "start_GRCh37": "39138289",
                    "type": "protein_coding"
                },
                "ACTR3C": 
                {
                    "description": "actin related protein 3C [Source:HGNC Symbol;Acc:HGNC:37282]",
                    "chromosome": "7",
                    "end": "150323725",
                    "end_GRCh37": "150020814",
                    "start": "150243916",
                    "start_GRCh37": "149941005",
                    "type": "protein_coding"
                }
            }
            ```  


### Gene Groups

Gets the identifier of a gene, validates it and then returns the group of genes to which it belongs according to HGNC, and all the other genes that belong to the same group.  

- URL: /genes-of-its-group/<*gene_id*>
    - <*gene_id*> is the identifier of the gene for any database  
- Method: GET  
- Params: -  
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
        - URL: http://localhost:8000/genes-of-its-group/ENSG00000146648
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

- URL: /pathway-genes/<*source*>/<*external_id*>
    - <*source*>: Database to query. Use lowercase. Valid Options:  
       - kegg ([link](https://www.genome.jp/kegg/))
       - biocarta ([link](https://maayanlab.cloud/Harmonizome/resource/Biocarta))
       - ehmn ([link](http://allie.dbcls.jp/pair/EHMN;Edinburgh+Human+Metabolic+Network.html))
       - humancyc ([link](https://humancyc.org/))
       - inoh ([link](https://dbarchive.biosciencedbc.jp/en/inoh/desc.html))
       - netpath ([link](https://www.wikipathways.org/index.php/Portal:NetPath))
       - pid ([link](https://github.com/NCIP/pathway-interaction-database))
       - reactome ([link](https://reactome.org/))
       - smpdb ([link](https://www.smpdb.ca/))
       - signalink ([link](http://signalink.org/))
       - wikipathways ([link](https://www.wikipathways.org/index.php/WikiPathways))  
        Using an invalid option returns an empty list of genes.
    - <*external_id*>: Pathway identifier in the source database.
- Method: GET  
- Params: -  
- Success Response:
    - Code: 200
    - Content:
        - `genes`: a list of genes involved in the metabolic pathway.  
    - Example:
        - URL: http://localhost:8000/pathway-genes/kegg/hsa00740
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

- URL: /pathways-in-common
- Method: POST  
- Params: A body in Json format with the following content
    -  `gene_ids`: list of genes for which you want to get the common metabolic pathways
- Success Response:
    - Code: 200
    - Content:
        - `pathways`: list of elements of type Json. Each element corresponds to a different metabolic pathway.  
            - `source`: database of the metabolic pathway found.
            - `external_id`: pathway identifier in the source.    
            - `pathway`: name of the pathway.
    - Example:
        - URL: http://localhost:8000/pathways-in-common
        - body: 
        `{    "gene_ids" : ["HLA-B" , "BRAF"]    }`
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

- URL: /expression-of-genes
- Method: POST  
- Params: A body in Json format with the following content
    -  `gene_ids`: list of genes for which you want to get the expression.  
    -  `tissue`: healthy tissue from which you want to get the expression values.  
- Success Response:
    - Code: 200
    - Content:
        The response you get is a list. Each element of the list is a new list containing the expression values for each gene in the same sample from the GTEx database.
        - `<gene_id>`: expression value for the gene_id.
    - Example:
        - URL: http://localhost:8000/expression-of-genes
        - body: `{ "tissue": "Skin",    "gene_ids": ["BRCA1", "BRCA2"] }`
        - Response:
            ```json
            [
                [
                    {
                        "BRCA1": 1.627
                    },
                    {
                        "BRCA2": 0.2182
                    }
                ],
                [
                    {
                        "BRCA1": 1.27
                    },
                    {
                        "BRCA2": 0.4777
                    }
                ],
                [
                    {
                        "BRCA1": 1.462
                    },
                    {
                        "BRCA2": 0.4883
                    }
                ]
            ]
            ```  
            keep in mind:
            - As an example only three samples are shown. Note that in the GTEx database there may be more than 2500 samples for a given healthy tissue.
            - If one of the genes entered as a parameter corresponds to an invalid symbol, the response will omit the values for that gene. It is recommended to use the *"Genes symbols validator"* service to validate your genes before using this functionality.


### Gene Ontology terms related to a list of genes

Gets the list of related terms for a list of genes.

- URL: /genes-to-terms
- Method: POST  
- Params: A body in Json format with the following content
    -  `gene_ids`: list of genes for which you want to get the terms common (they must be a list, and have to be in HGNC gene symbol format)
    -  `filter_type`: by default "intersection", in wich case it bring all the terms that are realted to all the genes, the other option is "union" wich brings all the terms that are related to **at least** on gene
    -  `relation_type`: filters the realtion between genes and terms. By default it's ["enables","involved_in","part_of","located_in"]. It should always be a list containing any permutation of the default relations
    -  `ontology_type`: filters the ontology type of the terms in the response. By default it's ["biological_process", "molecular_function", "cellular_component"]It should always be a list containing any permutation of the default relations

******terminar
- Success Response:
    - Code: 200
    - Content:
        - `pathways`: list of elements of type Json. Each element corresponds to a different metabolic pathway.  
            - `source`: database of the metabolic pathway found.
            - `external_id`: pathway identifier in the source.    
            - `pathway`: name of the pathway.
    - Example:
        - URL: http://localhost:8000/pathways-in-common
        - body: 
        `{    "gene_ids" : ["HLA-B" , "BRAF"]    }`
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


## Error Responses

The possible error codes are 400, 404 and 500. The content of each of them is a Json with a unique key called "error" where its value is a description of the problem that produces the error. For example:  
```json
{
    "error": "404 Not Found: invalid gene identifier"
}
```


## Contributing

All kind of contribution is welcome! If you want to contribute just:

1. Fork this repository.
2. Create a new branch and introduce there your new changes.
3. Make a Pull Request!


### Run Flask dev server

1. Start up Docker services like MongoDB: `docker compose -f docker-compose.dev.yml up -d`
2. Go to the `bioapi` folder.
3. Run Flask server: `python3 bioapi.py`

**NOTE:** If you are looking for documentation for a production deployment see [DEPLOYING.md](DEPLOYING.md).


### Tests

To run all the tests:

1. Go to the `bioapi` folder.
2. Run the `pytest` command.


### Update genomic databases
For the "Metabolic pathways (ConsensusPathDB)", "Gene nomenclature (HUGO Gene Nomenclature Committee)" and "Gene information (Ensembl)" databases, it is not necessary to make any modifications to any script. This is because the datasets are automatically downloaded in their most up-to-date versions when the bash file for each database is executed as described in the **Manually import the different databases** section of the DEPLOYING.md file.  
If you need to update the "Gene expression (Genotype-Tissue Expression)" database, you should also follow the procedures in the section named above, but first you should edit the bash file as follows:  
Modify the **gtex2mongodb.sh** file. Edit the variables *"expression_url"* and *"annotation_url"*.  
In the *expession_url* variable, set the url corresponding to the GTEx "RNA-Seq Data" compressed file (gz compression). This file should contain the Gene TPMs values (Remember that Gene expression on the GTEx Portal are shown in Transcripts Per Million or TPMs).  
In the *"annotation_url"* variable, set the url corresponding to the file that contains the annotated samples and allows finding the corresponding tissue type for each sample in the database.  
By default, GTEx is being used in its version [GTEx Analysis V8 (dbGaP Accession phs000424.v8.p2)](https://gtexportal.org/home/datasets#datasetDiv1)

**NOTE:** It is NOT necessary to drop the MongoDB database before upgrading (this applies to all databases). 
