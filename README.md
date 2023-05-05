# BioAPI

A powerful abstraction of genomics databases. Bioapi is a REST API that provides data related to gene nomenclature, gene expression, and metabolic pathways. All services are available through a web API accessible from a browser or any other web client. All the responses are in JSON format.

This document is focused on the **development** of the system. If you are looking for documentation for a production deployment see [DEPLOYING.md](DEPLOYING.md).


## Integrated databases

BioAPI obtains information from different bioinformatic databases. These databases were installed locally to reduce data search time. The databases currently integrated to BioAPI are:
1. Gene nomenclature: [HUGO Gene Nomenclature Committee](https://www.genenames.org/).  
HGNC is the resource for approved human gene nomenclature. Downloaded from its official website in September 2022.  
2. Gene information:  
 - [ENSEMBL](http://www.ensembl.org/biomart/martview): BioMart data mining tool was used to obtain a gene-related dataset from Ensembl. Ensembl is a genome browser for vertebrate genomes that supports research in comparative genomics, evolution, sequence variation and transcriptional regulation. Ensembl annotate genes, computes multiple alignments, predicts regulatory function and collects disease data. Downloaded using *BioMart data mining tool* in September 2022.
 - [RefSeq](https://www.ncbi.nlm.nih.gov/refseq/): The summary of each human gene was obtained from the RefSeq database. RefSeq (Reference Sequence) is the public database of annotated and curated nucleic acid (DNA and RNA) and protein sequences from the National Center for Biotechnology Information (NCBI). To obtain the summaries, the R package called [GeneSummary](https://bioconductor.org/packages/release/data/annotation/html/GeneSummary.html) was used, which obtains the abstracts from version 214 of RefSeq.
 - [CiVIC](https://civicdb.org/welcome): A description of the genes oriented to clinical interpretation in cancer was obtained from the CiVIC database, an open-source platform supporting crowdsourced and expert-moderated cancer variant curation. The database was downloaded from its official website in April 2023.  
3. Metabolic pathways: [ConsensusPathDB](http://cpdb.molgen.mpg.de/).  
ConsensusPathDB-human integrates interaction networks in Homo sapiens including binary and complex protein-protein, genetic, metabolic, signaling, gene regulatory and drug-target interactions, as well as biochemical pathways. Data originate from currently 31 public resources for interactions (listed below) and interactions that we have curated from the literature. The interaction data are integrated in a complementary manner (avoiding redundancies), resulting in a seamless interaction network containing different types of interactions. Downloaded from its official website in September 2022.          
4. Gene expression: [Genotype-Tissue Expression (GTEx)](https://gtexportal.org/home/).  
The Genotype-Tissue Expression (GTEx) project is an ongoing effort to build a comprehensive public resource to study tissue-specific gene expression and regulation. Samples were collected from 54 non-diseased tissue sites across nearly 1000 individuals, primarily for molecular assays including WGS, WES, and RNA-Seq. GTEx is being used in its version [GTEx Analysis V8 (dbGaP Accession phs000424.v8.p2)](https://gtexportal.org/home/datasets#datasetDiv1) and was downloaded from its official website in September 2022.  
5. Actionable and Cancer genes: [OncoKB](https://www.oncokb.org/).  
OncoKB™ is a precision oncology knowledge base developed at Memorial Sloan Kettering Cancer Center that contains biological and clinical information about genomic alterations in cancer. Alteration- and tumor type-specific therapeutic implications are classified using the OncoKB™ [Levels of Evidence system](https://www.oncokb.org/levels), which assigns clinical actionability to individual mutational events. Downloaded from its official website in April 2023.  


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

From a list of valid genes, it obtains different information for the human reference genomes GRCh38 and GRCh37.  

- URL: /information-of-genes
- Method: POST  
- Params: A body in Json format with the following content
    -  `gene_ids` : list of valid genes identifiers  
- Success Response:
    - Code: 200
    - Content:
        - `<gene_ids>`: Returns a Json with as many keys as there are valid genes in the body. For each gene, the value is a Json with the following format:
            - `description` : Very brief description of the gene according to the Ensembl database
            - `refseq_summary` : More complete description of the gene according to the RefSeq database (RefSeq : NCBI Reference Sequences)
            - `civic_description` : Description of the clinical relevance of the gene according to the CiVIC (Clinical Interpretation of Variants in Cancer) database
            - `gene_biotype` : gene type (example: protein_coding)
            - `chromosome` : chromosome where the gene is located
            - `start` : chromosomal position of gene starts for the reference genome GRCh38
            - `end` : chromosomal position of gene ends for the reference genome GRCh38
            - `start_GRCh37` : chromosomal position of gene starts for the reference genome GRCh37
            - `end_GRCh37` : chromosomal position of gene ends for the reference genome GRCh37
            - `percentage_gene_gc_content` : Ratio of guanine and cytosine nucleotides in the DNA sequence of the gene
            - `strand` : DNA strand containing the coding sequence for the gene
            - `band` : cytoband or specific location in the genome
            - `oncokb_cancer_gene` : return "Oncogene" or "Tumor Suppressor Gene" only if the gene has this information in the OncoKB database 
            - `ensembl_gene_id` : Gene identifier in the Ensembl database
            - `entrezgene_id` : Gene identifier in the NCBI Entrez database
                    
    - Example:
        - URL: http://localhost:8000/information-of-genes
        - body: 
        `{    "gene_ids" : ["INVALIDGENE","MC1R", "ALK"]    }`
        - Response:
            ```json
            {
                "ALK": {
                    "band": "p23.1", 
                    "chromosome": "2", 
                    "civic_description": "ALK amplifications, fusions and mutations have been shown to be driving events in non-small cell lung cancer. While crizontinib has ...", 
                    "end_GRCh37": 30144432, 
                    "end_position": 29921586, 
                    "ensembl_gene_id": "ENSG00000171094", 
                    "entrezgene_id": 238, 
                    "gene_biotype": "protein_coding", 
                    "hgnc_symbol": "ALK", 
                    "oncokb_cancer_gene": "Oncogene", 
                    "percentage_gene_gc_content": 43.51, 
                    "refseq_summary": "This gene encodes a receptor tyrosine kinase, which belongs to the insulin receptor superfamily. This protein comprises...", 
                    "start_GRCh37": 29415640, 
                    "start_position": 29192774, 
                    "strand": -1
                }, 
                "MC1R": {
                    "band": "q24.3", 
                    "chromosome": "16", 
                    "description": "melanocortin 1 receptor", 
                    "end_GRCh37": 89987385, 
                    "end_position": 89920973, 
                    "ensembl_gene_id": "ENSG00000258839", 
                    "entrezgene_id": 4157, 
                    "gene_biotype": "protein_coding", 
                    "percentage_gene_gc_content": 58.17, 
                    "refseq_summary": "This intronless gene encodes the receptor protein for melanocyte-stimulating hormone (MSH). The encoded protein...", 
                    "start_GRCh37": 89978527, 
                    "start_position": 89912119, 
                    "strand": 1
                }
            }
            ```  
            Keep in mind: 
             - If a gene passed in the body is not found in the database (invalid gene symbol), it will not appear in the response.
             - If one of the fields for a gene has no value, it will not appear in the response.


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


### Actionable and Cancer genes
This service retrieves information of actionable genes and drugs obtained from the OncoKB database, at a therapeutic, diagnostic and prognostic level.  

- URL: /information-of-oncokb
- Method: POST  
- Params: A body in Json format with the following content
    -  `gene_ids`: list of genes for which you want to get the information from OncoKB database.  
- Success Response:
    - Code: 200
    - Content:
        The response you get is a dict. Each key of the list is a gene with information in OncoKB. For each key gene, the value is a list. Each item in the list is a Dict containing the following information obtained from OncoKB.  
        - `<drugs>`: drug associated with specific gene alteration.
        - `<alterations>`: specific cancer gene alterations.
        - `<cancer_types>`: type of cancer according to OncoTree [nomenclature](http://oncotree.mskcc.org/).
        - `<classification>`: clinical implications of the drug (therapeutic, diagnostic, and prognostic).
        - `<level_of_evidence>`: [Level of evidence](https://www.oncokb.org/levels#version=V2) of the drug or gene according to OncoKB version 2.
    - Example:
        - URL: http://localhost:8000/information-of-oncokb
        - body: `{ "gene_ids": ["ATM"] }`
        - Response:
            ```json
            {
                "ATM": [
                    {
                        "alterations": "Oncogenic Mutations",
                        "cancer_types": "Prostate Cancer, NOS, Prostate Cancer",
                        "classification": "Therapeutic",
                        "drugs": "Olaparib",
                        "level_of_evidence": "1"
                    }
                ]
            }
            ```  
            Keep in mind: 
             - If a gene passed in the body is not found in the database, it will not appear in the response.
             - If one of the fields for a gene has no value in the database, it will not appear in the response.


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
