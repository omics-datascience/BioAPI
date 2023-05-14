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
    -  `gene_ids`: list of genes for which you want to get the terms in common (they must be a list, and have to be in HGNC gene symbol format)
    -  `filter_type`: by default "intersection", in wich case it bring all the terms that are realted to all the genes, the other option is "union" wich brings all the terms that are related to **at least** on gene
    -  `relation_type`: filters the relation between genes and terms. By default it's ["enables","involved_in","part_of","located_in"]. It should always be a list containing any permutation of the default relations
    -  `ontology_type`: filters the ontology type of the terms in the response. By default it's ["biological_process", "molecular_function", "cellular_component"]It should always be a list containing any permutation of the default relations

- Success Response:
    - Code: 200
    - Content:
		The response you get is a list. Each element of the list is a GO term that fulfills the conditions of the query. GO terms can contain name, definition, relations to other terms, etc.
        - `relations_to_genes`: list of elements of type Json. Each element corresponds to a to a gene and how it's related to the term.  
            - `gene`: name of the gene.
            - `relation_type`: the type of relation between the gene and the GO term.
            - `evidence`: evidence code to indicate how the annotation to a particular term is supported.    
    - Example:
        - URL: http://localhost:8000/genes-to-terms
        - body: 
		`{    "gene_ids" : ["TMCO4"],
				"relation_type": ["enables"],   
				"ontology_type" : ["molecular_function"] }`
        - Response:
         	```json
			[{
				"alt_id": [
				    "0001948",
				    "0045308"
				],
				"def": "\"Binding to a protein.\" [GOC:go_curators]",
				"go_id": "0005515",
				"is_a": "0005488",
				"name": "protein binding",
				"ontology_type": "molecular_function",
				"relations_to_genes": [
				    {
					"evidence": "IPI",
					"gene": "TMCO4",
					"relation_type": "enables"
				    }
				],
				"subset": [
				    "goslim_candida",
				    "goslim_chembl",
				    "goslim_metagenomics",
				    "goslim_pir",
				    "goslim_plant"
				],
				"synonym": [
				    "\"glycoprotein binding\" NARROW []",
				    "\"protein amino acid binding\" EXACT []"
				]
			    }]
			```  
### Gene Ontology terms related to a list of genes

Gets the list of related terms to a term.

- URL: /related-terms
- Method: POST
- Params: A body in Json format with the following content
	-  `term_id`: the term if of the term you want to search
	-  `relations`: filters the non-hierarchical relations between terms. By default it's ["part_of","regulates","has_part"]. It should always be a list 
	-`ontology_type`: filters the ontology type of the terms in the response. By default it's ["biological_process", "molecular_function", "cellular_component"]It should always be a list containing any permutation of the default relations
	-  `general_depth`: the search depth with the non-hierarchical relations
	-  `hierarchical_depth_to_children`: the search depth with the hierarchical relations in the direction of the children
	-  `llenar`:por favor llenar
- Success Response:
    - Code: 200
    - Content: The response you get is a list of GO terms related to the searched term that fulfills the conditions of the query. Each term has:
		-`go_id`: id of the GO term
		-`name`: name of the GO term
		-`ontology_type`: the ontology that the GO term belongs to
		- `relations`: dictionary of relations 
            - `relation type`: list of terms related by that relation type to the term
	- Example:
        - URL: http://localhost:8000/related-terms
         - body: 
		`{
			"term_id": "0000079",
			"general_depth" : 5
		}`
        - Response:
	```json
		[
		    {
			"go_id": "0000079",
			"name": "regulation of cyclin-dependent protein serine/threonine kinase activity",
			"ontology_type": "biological_process",
			"relations": {
			    "regulates": [
				"0004693"
			    ]
			}
		    },
		    {
			"go_id": "0004693",
			"name": "cyclin-dependent protein serine/threonine kinase activity",
			"ontology_type": "molecular_function",
			"relations": {}
		    }
		]
	```  
			
### Cancer related drugs (PharmGKB)

Gets the list of related drugs to a list of genes.

- URL: /drugs-pharm-gkb
- Method: POST
- Params: A body in Json format with the following content
	-  `gene_ids`: list of genes for whichthe related drugs
- Success Response:
    - Code: 200
    - Content: The response you get is a list of genes containing the related drug information
		-`pharmGKB_id`: Identifier assigned to this drug label by PharmGKB
		-`name`: Name assigned to the label by PharmGKB
		-`source`: The source that originally authored the label (e.g. FDA, EMA)
		-`biomarker_flag`: "On" if drug in this label appears on the FDA Biomarker list; "Off (Formerly On)" if the label was on the FDA Biomarker list at one time; "Off (Never On)" if the label was never listed on the FDA Biomarker list (to PharmGKB's knowledge)
		- `Testing Level`:  PGx testing level as annotated by PharmGKB based on definitions at https://www.pharmgkb.org/page/drugLabelLegend
		- `Chemicals`: Related chemicals
		- `Genes`: List of related genes
		- `Variants-Haplotypes`: Related variants and/or haplotypes
	- Example:
        - URL: http://localhost:8000/related-terms
         - body: 
        `{"gene_ids" : ["JAK2"]}`
        - Response:
	```json
			  {
		    "JAK2": [
			{
			    "Variants/Haplotypes": "rs77375493",
			    "biomarker_flag": "",
			    "chemicals": "ropeginterferon alfa-2b",
			    "genes": [
				"JAK2"
			    ],
			    "name": "Annotation of EMA Label for ropeginterferon alfa-2b and JAK2",
			    "pharmgkb_id": "PA166272741",
			    "source": "EMA",
			    "testing_level": "Informative PGx"
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

