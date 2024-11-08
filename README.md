# BioAPI

A powerful abstraction of genomics databases. Bioapi is a REST API that provides data related to gene nomenclature, gene expression, and metabolic pathways. All services are available through a web API accessible from a browser or any other web client. All the responses are in JSON format.

This document is focused on the **development** of the system. If you are looking for documentation for a production deployment see [DEPLOYING.md](DEPLOYING.md).

- [BioAPI](#bioapi)
  - [Integrated databases](#integrated-databases)
  - [Services included in BioAPI](#services-included-in-bioapi)
    - [Genes symbols validator](#genes-symbols-validator)
    - [Genes symbols finder](#genes-symbols-finder)
    - [Genes information](#genes-information)
    - [Gene Groups](#gene-groups)
    - [Genes of a metabolic pathway](#genes-of-a-metabolic-pathway)
    - [Metabolic pathways from different genes](#metabolic-pathways-from-different-genes)
    - [Gene expression](#gene-expression)
    - [Therapies and actionable genes in cancer](#therapies-and-actionable-genes-in-cancer)
    - [Gene Ontology terms related to a list of genes](#gene-ontology-terms-related-to-a-list-of-genes)
    - [Gene Ontology terms related to another specific term](#gene-ontology-terms-related-to-another-specific-term)
    - [Cancer related drugs](#cancer-related-drugs)
    - [Predicted functional associations network](#predicted-functional-associations-network)
    - [Drugs that regulate a gene](#drugs-that-regulate-a-gene)
  - [Error Responses](#error-responses)
  - [Contributing](#contributing)
    - [Run Flask dev server](#run-flask-dev-server)
    - [Tests](#tests)

## Integrated databases

BioAPI obtains information from different bioinformatics databases. These databases were installed locally to reduce data search time. The databases currently integrated to BioAPI are:

1. Gene nomenclature: [HUGO Gene Nomenclature Committee](https://www.genenames.org/).  
HGNC is the resource for approved human gene nomenclature. Downloaded from its official website in September 2022.  
2. Gene information:  

   - [ENSEMBL](http://www.ensembl.org/biomart/martview): BioMart data mining tool was used to obtain a gene-related dataset from Ensembl. Ensembl is a genome browser for vertebrate genomes that supports comparative genomics, evolution, sequence variation and transcriptional regulation research. Ensembl annotates genes, computes multiple alignments, predicts regulatory function, and collects disease data. Downloaded using *BioMart data mining tool* in September 2022.
   - [RefSeq](https://www.ncbi.nlm.nih.gov/refseq/): the summary of each human gene was obtained from the RefSeq database. RefSeq (Reference Sequence) is the public database of annotated and curated nucleic acid (DNA and RNA) and protein sequences from the National Center for Biotechnology Information (NCBI). To obtain the summaries, the R package called [GeneSummary](https://bioconductor.org/packages/release/data/annotation/html/GeneSummary.html) was used, which obtains the abstracts from version 214 of RefSeq.
   - [CIViC](https://civicdb.org/welcome): A description of the genes oriented to clinical interpretation in cancer was obtained from the CIViC database, an open-source platform supporting crowd-sourced and expert-moderated cancer variant curation. The database was downloaded from its official website in April 2023.  

3. Metabolic pathways: [ConsensusPathDB](http://cpdb.molgen.mpg.de/).  
ConsensusPathDB-human integrates interaction networks in Homo sapiens including binary and complex protein-protein, genetic, metabolic, signaling, gene regulatory, and drug-target interactions, as well as biochemical pathways. Data originate from currently 31 public resources for interactions (listed below) and interactions that we have curated from the literature. The interaction data are integrated in a complementary manner (avoiding redundancies), resulting in a seamless interaction network containing different types of interactions. Downloaded from its official website in September 2022.
4. Gene expression: [Genotype-Tissue Expression (GTEx)](https://gtexportal.org/home/).  
The Genotype-Tissue Expression (GTEx) project is an ongoing effort to build a comprehensive public resource to study tissue-specific gene expression and regulation. Samples were collected from 54 non-diseased tissue sites across nearly 1000 individuals, primarily for molecular assays including WGS, WES, and RNA-Seq. GTEx is being used in its version [GTEx Analysis V8 (dbGaP Accession phs000424.v8.p2)](https://gtexportal.org/home/datasets#datasetDiv1) and was downloaded from its official website in September 2022.
5. Therapies and actionable genes in cancer: [OncoKB](https://www.oncokb.org/).  
OncoKB™ is a precision oncology knowledge base developed at Memorial Sloan Kettering Cancer Center that contains biological and clinical information about cancer-related genomic alterations. Alterations and tumor-type-specific therapeutic implications are classified using the OncoKB™ [Levels of Evidence system](https://www.oncokb.org/levels), which assigns clinical actionability to individual mutational events. Downloaded from its official website in November 2023.  
6. Gene Ontology [Gene Ontology (GO)](http://geneontology.org/).
It is a project to develop an up-to-date, comprehensive, computational model of biological systems, from the molecular level to larger pathways, cellular and organism-level systems. It provides structured and standardized annotations of gene products, in a hierarchical system of terms and relationships that describes the molecular functions, biological processes, and cellular components associated with genes and gene products. Downloaded from its official website in June 2023
7. Cancer-related drugs [Pharmacogenomics Knowledge Base (PharmGKB)](https://www.pharmgkb.org/).
It is a resource that provides information about how human genetic variation affects response to medications. PharmGKB collects, curates, and disseminates knowledge about clinically actionable gene-drug associations and genotype-phenotype relationships. Downloaded from its official website in February 2024
8. Predicted functional associations network [STRING](https://string-db.org/)
It is a database of known and predicted protein-protein interactions. The interactions include direct (physical) and indirect (functional) associations; they stem from computational prediction, knowledge transfer between organisms, and interactions aggregated from other (primary) databases. String is being used in its version 12.0.
9. Pharmaco-transcriptomics [DrugBank](https://go.drugbank.com/)
It is a comprehensive, free-to-access, online database containing information on drugs and drug targets. BioAPI only generates access links to the Drugbank website, it does not contain your data.  

## Services included in BioAPI  

### Genes symbols validator

Searches the identifier of a list of genes of different genomics databases and returns the approved symbols according to HGNC nomenclature.  

- URL: /gene-symbols
- Method: POST  
- Params: A body in JSON format with the following content
  - `gene_ids`: list of identifiers that you want to get your approved symbols.  
- Success Response:
  - Code: 200
  - Content:
    - `gene_ids`: Returns a JSON with as many keys as there are genes in the body. For each gene, the value is a list with the valid symbols.  
  - Example:
    - URL: <https://bioapi.multiomix.org/gene-symbols>
    - body:
            `{
                "gene_ids":[
                    "BRCA1",
                    "F1-CAR",
                    "BRCC1",
                    "FANCS"
                ]
            }`
    - Response:

        ```json
        {
            "BRCA1":[
                "BRCA1"
            ],
            "BRCC1":[
                "BRCA1",
                "ICE2"
            ],
            "F1-CAR":[
                
            ],
            "FANCS":[
                "BRCA1"
            ]
        }
        ```  

### Genes symbols finder

Service that takes a string of any length and returns a list of genes that contain that search criteria.  

- URL: /gene-symbols-finder
- Method: GET  
- Params:
  - `query`: gene search string.
  - `limit`: number of elements returned by the service. Default 50.
- Success Response:
  - Code: 200
  - Content: a list of gene symbols matching the search criteria.  
  - Example:
    - URL: <https://bioapi.multiomix.org/gene-symbols-finder/?limit=50&query=BRC>
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
- Params: A body in JSON format with the following content
  - `gene_ids`: list of valid genes identifiers.  
- Success Response:
  - Code: 200
  - Content:
    - `gene_ids`: Returns a JSON with as many keys as there are valid genes in the body. For each gene, the value is a JSON with the following format:
      - `alias_symbol`: alternative symbols for a known gene.
      - `percentage_gene_gc_content`: Ratio of guanine and cytosine nucleotides in the DNA sequence of the gene.
      - `oncokb_cancer_gene`: return `Oncogene` or `Tumor Suppressor Gene` only if the gene has this information in the OncoKB database.
      - `name`: gene name according to the HGNC database.
      - `band`: cytoband or specific location in the genome.
      - `chromosome`: chromosome where the gene is located (Chromosome without *chr* prefix).
      - `start_position`: chromosomal position of gene starts for the reference genome GRCh38.
      - `end_position`: chromosomal position of gene ends for the reference genome GRCh38.
      - `start_GRCh37`: chromosomal position of gene starts for the reference genome GRCh37.
      - `end_GRCh37`: chromosomal position of gene ends for the reference genome GRCh37.
      - `strand`: DNA strand containing the coding sequence for the gene. Possible values are 1 for the positive strand or -1 for the negative strand.
      - `gene_biotype`: A gene or transcript classification (examples: protein_coding or miRNA). The different possibilities for this field can be found in the [Biotype section of the Ensembl documentation](https://vega.archive.ensembl.org/info/about/gene_and_transcript_types.html).
      - `refseq_summary`: complete description of the gene according to the RefSeq database (RefSeq : NCBI Reference Sequences).
      - `civic_description`: Description of the clinical relevance of the gene according to the CIViC (Clinical Interpretation of Variants in Cancer) database.
      - `hgnc_id`: Gene identifier in the HGNC database.
      - `uniprot_ids`: Gene identifier in the Uniprot database.
      - `omim_id`: Gene identifier in the OMIM database.
      - `ensembl_gene_id`: Gene identifier in the Ensembl database.
      - `entrez_id`: Gene identifier in the NCBI Entrez database.
  - Example:
    - URL: <https://bioapi.multiomix.org/information-of-genes>
    - body:
            `{
                "gene_ids":[
                    "INVALIDGENE",
                    "MC1R",
                    "ALK"
                ]
            }`
    - Response:

      ```json
      {
          "ALK":{
              "alias_symbol":[
                  "CD246",
                  "ALK1"
              ],
              "band":"p23.1",
              "chromosome":"2",
              "civic_description":"ALK amplifications, fusions and mutations have been shown to be driving ...",
              "end_GRCh37":30144432,
              "end_position":29921586,
              "ensembl_gene_id":"ENSG00000171094",
              "entrez_id":"238",
              "gene_biotype":"protein_coding",
              "hgnc_id":"HGNC:427",
              "name":"ALK receptor tyrosine kinase",
              "omim_id":"105590",
              "oncokb_cancer_gene":"Oncogene",
              "percentage_gene_gc_content":43.51,
              "refseq_summary":"This gene encodes a receptor tyrosine kinase, which belongs to the insulin receptor superfamily. This protein ...",
              "start_GRCh37":29415640,
              "start_position":29192774,
              "strand":-1,
              "uniprot_ids":"Q9UM73"
          },
          "MC1R":{
              "alias_symbol":"MSH-R",
              "band":"q24.3",
              "chromosome":"16",
              "civic_description":"",
              "end_GRCh37":89987385,
              "end_position":89920973,
              "ensembl_gene_id":"ENSG00000258839",
              "entrez_id":"4157",
              "gene_biotype":"protein_coding",
              "hgnc_id":"HGNC:6929",
              "name":"melanocortin 1 receptor",
              "omim_id":"155555",
              "percentage_gene_gc_content":58.17,
              "refseq_summary":"This intronless gene encodes the receptor protein for melanocyte-stimulating hormone (MSH). The encoded protein...",
              "start_GRCh37":89978527,
              "start_position":89912119,
              "strand":1,
              "uniprot_ids":"Q01726"
          }
      }
      ```  

    Keep in mind:
        - If a gene passed in the body is not found in the database (invalid gene symbol), it will not appear in the response.
        - If one of the fields for a gene has no value, it will not appear in the response.

### Gene Groups

Gets the identifier of a gene, validates it and then returns the group of genes to which it belongs according to HGNC, and all the other genes that belong to the same group.  

- URL: /genes-of-its-group/*gene_id*
  - `gene_id` is the identifier of the gene for any database.  
- Method: GET  
- Params: -  
- Success Response:
  - Code: 200
  - Content:
    - `gene_id`: HGNC approved gene symbol.  
    - `locus_group`: Groups locus types together into related sets. The different options for this field can be: `protein-coding gene`, `pseudogene`, `phenotype` or `other`.
    - `locus_type`: Specifies the genetic class of each gene entry. All locus types and locus groups can be found in the [HGNC documentation](https://www.genenames.org/download/statistics-and-files/).
    - `groups`:
      - `gene_group`: Gene group name.
      - `gene_group_id`: Gene group identifier.
      - `genes`: All others genes for this group.  
        For a description of the gene groups and IDs you can access the [HUGO Gene Nomenclature Committee website](https://www.genenames.org/data/genegroup/#!/).
  - Example:
    - URL: <https://bioapi.multiomix.org/genes-of-its-group/ENSG00000146648>
    - Response:

        ```json
        {
            "gene_id":"EGFR",
            "groups":[
                {
                    "gene_group":"Erb-b2 receptor tyrosine kinases",
                    "gene_group_id":"1096",
                    "genes":[
                        "EGFR",
                        "ERBB3",
                        "ERBB4",
                        "ERBB2"
                    ]
                }
            ],
            "locus_group":"protein-coding gene",
            "locus_type":"gene with protein product"
        }
        ```

### Genes of a metabolic pathway

Get the list of genes that are involved in a pathway for a given database.

- URL: /pathway-genes/*source*/*external_id*
  - `source`: Database to query. Use lowercase. Valid Options:  
    - [kegg](https://www.genome.jp/kegg/).
    - [biocarta](https://maayanlab.cloud/Harmonizome/resource/Biocarta).
    - [ehmn](https://allie.dbcls.jp/pair/EHMN;Edinburgh+Human+Metabolic+Network.html).
    - [humancyc](https://humancyc.org/).
    - [inoh](https://dbarchive.biosciencedbc.jp/en/inoh/desc.html).
    - [netpath](https://classic.wikipathways.org/index.php/Portal:NetPath).
    - [pid](https://github.com/NCIP/pathway-interaction-database).
    - [reactome](https://reactome.org/).
    - [smpdb](https://www.smpdb.ca/).
    - [signalink](http://signalink.org/).
    - [wikipathways](https://www.wikipathways.org/index.php/WikiPathways).  
    Using an invalid option returns an empty list of genes.
  - `external_id`: Pathway identifier in the source database.
- Method: GET  
- Params: -  
- Success Response:
  - Code: 200
  - Content:
    - `genes`: a list of genes involved in the metabolic pathway.  
  - Example:
    - URL: <https://bioapi.multiomix.org/pathway-genes/kegg/hsa00740>
    - Response:

      ```json
      {
          "genes":[
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
- Params: A body in JSON format with the following content
  - `gene_ids`: list of genes for which you want to get the common metabolic pathways. If you use a list with a single gene, then you will get all the pathways for that gene.
- Success Response:
  - Code: 200
  - Content:
    - `pathways`: list of elements of type JSON. Each element corresponds to a different metabolic pathway.  
      - `source`: database of the metabolic pathway found. Possible values can be found in [Genes of a metabolic pathway](#genes-of-a-metabolic-pathway) service.
      - `external_id`: pathway identifier in the source.
      - `pathway`: name of the pathway.
  - Example:
    - URL: <https://bioapi.multiomix.org/pathways-in-common>
    - body:
            `{
                "gene_ids":[
                    "HLA-B",
                    "BRAF"
                ]
            }`
    - Response:

      ```json
      {
          "pathways":[
              {
                  "external_id":"hsa04650",
                  "pathway":"Natural killer cell mediated cytotoxicity",
                  "source":"KEGG"
              }
          ]
      }
      ```  

### Gene expression

This service gets gene expression in healthy tissue

- URL: /expression-of-genes
- Method: POST  
- Params: A body in JSON format with the following content
  - `gene_ids`: list of genes for which you want to get the expression.  
  - `tissue`: healthy tissue from which you want to get the expression values. The different options for this parameter are: `Adipose Tissue`, `Adrenal Gland`, `Bladder`, `Blood`, `Blood Vessel`, `Brain`, `Breast`, `Cervix Uteri`, `Colon`, `Esophagus`, `Fallopian Tube`, `Heart`, `Kidney`, `Liver`, `Lung`, `Muscle`, `Nerve`, `Ovary`, `Pancreas`, `Pituitary`, `Prostate`, `Salivary Gland`, `Skin`, `Small Intestine`, `Spleen`, `Stomach`, `Testis`, `Thyroid`, `Uterus` or `Vagina`. Any other value will cause the response to have no results.
  - `type`: Type of response format: `json` or `gzip`. Default: json.
- Success Response:
  - Code: 200
  - Content:
        The response you get is a list. Each element of the list is a new list containing the expression values for each gene in the same sample from the GTEx database.
    - `gene_id`: expression value for the gene_id.
  - Example:
    - URL: <https://bioapi.multiomix.org/expression-of-genes>
    - body:
            `{
                "tissue":"Skin",
                "gene_ids":[
                    "BRCA1",
                    "BRCA2"
                ]
            }`
    - Response:

      ```json
      [
          [
              {
                  "BRCA1":1.627
              },
              {
                  "BRCA2":0.2182
              }
          ],
          [
              {
                  "BRCA1":1.27
              },
              {
                  "BRCA2":0.4777
              }
          ],
          [
              {
                  "BRCA1":1.462
              },
              {
                  "BRCA2":0.4883
              }
          ]
      ]
      ```  

    keep in mind:
  - As an example only three samples are shown. Note that in the GTEx database there may be more than 2500 samples for a given healthy tissue.
  - If one of the genes entered as a parameter corresponds to an invalid symbol, the response will omit the values for that gene. It is recommended to use the *"Genes symbols validator"* service to validate your genes before using this functionality.

### Therapies and actionable genes in cancer

This service retrieves information on FDA-approved precision oncology therapies, actionable genes, and drugs obtained from the OncoKB database, at a therapeutic, diagnostic, and prognostic level.  

- URL: /information-of-oncokb
- Method: POST  
- Params: A body in JSON format with the following content
  - `gene_ids`: list of genes for which you want to get the information from the OncoKB database.  
  - `query`: Optional. Parameter used to show only the results that match it. The query is used to find matches within the information offered by OncoKB for the fields `precision_oncology_therapy`, `cancer_types`, `method_of_biomarker_detection`, or `drugs`.  
- Success Response:
  - Code: 200
  - Content:
    - `gene_ids`: Returns a JSON with as many keys as there are valid genes in the body. For each gene, the value is a JSON with the following format:  
      - `therapeutic`: Evidence of the gene for therapeutic. The value is a list of elements of the JSON type, where each element is a different evidence with the following structure:  
        - `drugs`: therapeutic drug.  
        - `level_of_evidence`: level of therapeutic evidence. The different values for the levels of evidence can be found in the [documentation of the OncoKB database](https://www.oncokb.org/therapeutic-levels).
        - `alterations`: specific cancer gene alterations.
        - `cancer_types`: type of cancer. Cancer types use the [OncoTree nomenclature](http://oncotree.mskcc.org/).
      - `diagnostic`: Evidence of the gene for diagnosis (for hematologic malignancies only). The value is a list of elements of the JSON type, where each element is a different evidence with the following structure:  
        - `level_of_evidence`: level of diagnostic evidence. The different values for the levels of evidence can be found in the [documentation of the OncoKB database](https://www.oncokb.org/diagnostic-levels).
        - `alterations`: specific cancer gene alterations.
        - `cancer_types`: type of cancer. Cancer types use the [OncoTree nomenclature](http://oncotree.mskcc.org/).
      - `prognostic`: Evidence of the gene for prognostic (for hematologic malignancies only). The value is a list of elements of the JSON type, where each element is a different evidence with the following structure:  
        - `level_of_evidence`: level of prognostic evidence. The different values for the levels of evidence can be found in the [documentation of the OncoKB database](https://www.oncokb.org/prognostic-levels).
        - `alterations`: specific cancer gene alterations.
        - `cancer_types`: type of cancer. Cancer types use the [OncoTree nomenclature](http://oncotree.mskcc.org/).
      - `oncokb_cancer_gene`: type of cancer gene. `Oncogene` and/or `Tumor Suppressor Gene`.  
      - `refseq_transcript`: gene transcript according to the RefSeq database.  
      - `sources`: list of sources where there is evidence of the relationship of the gene with cancer. These may be different sequencing panels, the [Sanger Cancer Gene Census](https://www.sanger.ac.uk/data/cancer-gene-census/), or [Vogelstein et al. (2013)](http://science.sciencemag.org/content/339/6127/1546.full).
      - `precision_therapies`: FDA-approved therapies that are considered precision oncology therapies by OncoKB™. The value is a list of elements of the JSON type, where each element is a different precision oncology therapy with the following structure:  
        - `precision_oncology_therapy`: A drug that is most effective in a molecularly defined subset of patients and for which pre-treatment molecular profiling is required for optimal patient selection.
        - `fda_first_approval`: Year of drug’s first FDA-approval. The first year the drug received FDA-approval in any indication, irrespective of whether the biomarker was included in the FDA-drug at that time.
        - `drug_classification`: Possible classifications are `first-in-class`, `mechanistically-distinct`, `follow-on`, or `resistance` based on [Suehnholz et al. Cancer Discovery 2023](https://aacrjournals.org/cancerdiscovery/article/doi/10.1158/2159-8290.CD-23-0467/729589/Quantifying-the-Expanding-Landscape-of-Clinical). Only drugs with an FDA-specified biomarker that can be detected by a DNA/NGS-based detection method are classified.
        - `fda_recognized_biomarkers`: Biomarkers related to therapy according to the FDA. Includes pathognomonic and indication-specific biomarkers, that while not specifically listed in the Indications and Usage section of the FDA drug label, are targeted by the precision oncology drug.
        - `method_of_biomarker_detection`: Biomarker detection method. If there is a corresponding FDA-cleared or -approved companion diagnostic device for biomarker identification, the detection method associated with this device is listed; if the biomarker can be detected by a DNA/NGS-based detection method this is listed first.  

  - Example:
    - URL: <https://bioapi.multiomix.org/information-of-oncokb>
    - body:
            `{
                "gene_ids":[
                    "ATM"
                ],
                "query": "Olaparib"
            }`
    - Response:

      ```json
      {
        "ATM":{
            "oncokb_cancer_gene":[
                "Tumor Suppressor Gene"
            ],
            "precision_therapies":[
                {
                    "drug_classification":"First-in-class",
                    "fda_first_approval":"2014",
                    "fda_recognized_biomarkers":"ATM, BARD1, BRCA1/2, BRIP1, CDK12, CHEK1/2, FANCL, PALB2, RAD51B, RAD51C, RAD51D, RAD54 Oncogenic Mutations",
                    "method_of_biomarker_detection":"DNA/NGS-based detection",
                    "precision_oncology_therapy":"Olaparib"
                }
            ],
            "refseq_transcript":"NM_000051.3",
            "sources":[
                "oncokb_annotated",
                "msk_impact",
                "msk_impact_heme",
                "foundation_one_cdx",
                "foundation_one_heme",
                "vogelstein",
                "sanger_cgc"
            ],
            "therapeutic":[
                {
                    "alterations":"Oncogenic Mutations",
                    "cancer_types":"Prostate Cancer, NOS, Prostate Cancer",
                    "drugs":"Olaparib",
                    "level_of_evidence":"1"
                }
            ]
        }
      }
      ```  

    Keep in mind:
    - If a gene passed in the body is not found in the database, it will not appear in the response.
    - If one of the fields for a gene has no value in the database, it will not appear in the response.

### Gene Ontology terms related to a list of genes

Gets the list of related terms for a list of genes.

- URL: /genes-to-terms
- Method: POST  
- Params: A body in JSON format with the following content
  - `gene_ids`: list of genes for which you want to get the terms in common (they must be a list, and have to be in HGNC gene symbol format).
  - `filter_type`: by default `intersection`, in which case it bring all the terms that are related to all the genes, another option is `union` which brings all the terms that are related to **at least** on gene. The third option is `enrichment`, it does a gene enrichment analysis on the input of genes with [g:Profiler library](https://biit.cs.ut.ee/gprofiler/page/docs). This filter type has 2 extra parameters:
    - `p_value_threshold`: 0.05 by default. It's the p-value threshold for significance, results with smaller p-value are tagged as significant. Must be a float. Not recommended to set it higher than 0.05.
    - `correction_method`:  The enrichment default correction method is `analytical` which uses multiple testing correction and applies g:Profiler tailor-made algorithm [g:SCS](https://biit.cs.ut.ee/gprofiler/page/docs#significance_threhshold) for reducing significance scores. Alternatively, one may select `bonferroni` correction or `false_discovery_rate` (Benjamini-Hochberg FDR).
  - `relation_type`: filters the relation between genes and terms. By default it's `["enables","involved_in","part_of","located_in"]`. It should always be a list containing any permutation of the allowed relations. Only valid on `filter_type` intersection and union. should not be present on `enrichment`.
  - `ontology_type`: filters the ontology type of the terms in the response. By default it's `["biological_process", "molecular_function", "cellular_component"]`. It should always be a list containing any permutation of the 3 ontologies.

- Success Response:
  - Code: 200
  - Content:
  The response you get is a list. Each element of the list is a GO term that fulfills the conditions of the query. GO terms can contain name, definition, relations to other terms, etc.
    - `go_id`: Unique identifier.
    - `name`: human-readable term name.
    - `ontology_type`: Denotes which of the three sub-ontologies (`biological_process`", `molecular_function`, `cellular_component`) the term belongs to.
    - `definition`: A textual description of what the term represents, plus reference(s) to the source of the information.
    - `synonyms`: Alternative words or phrases closely related in meaning to the term name, with indication of the relationship between the name and synonym given by the synonym scope.
    - `subset`: This field refers to an additional categorization of terms within the ontology. It allows terms that share specific characteristics or properties to be grouped into smaller, more specific subsets.
    - `is_a`: Refers to a semantic relationship between terms within the ontology. Indicates that a term is a subtype or subclass of another more general term.
    - `alt_id`: Refers to alternative or secondary identifiers for a specific term in the ontology.
    - `synonym`: Synonyms are alternative words or phrases closely related in meaning to the term name.
    - `definition_reference`: This field provides bibliographic references or sources from which the definition of the term in question is obtained.
    - `relations_to_genes`: list of elements of type JSON. Each element corresponds to a gene and how it's related to the term.  
      - `gene`: name of the gene.
      - `relation_type`: the type of relation between the gene and the GO term. They can be `enables`, `involved_in`, `part_of` or `located_in`. When `filter_type` is enrichment, extra relation will be gather from g:Profiler database. These relations will be shown as "relation obtained from gProfiler".
      - `evidence`: evidence code to indicate how the annotation to a particular term is supported.
    - `enrichment_metrics`:  
      - `p_value`: Hypergeometric p-value after correction for multiple testing.
      - `intersection_size`: The number of genes in the query that are annotated to the corresponding term.
      - `effective_domain_size`: The total number of genes "in the universe" which is used as one of the four parameters for the hypergeometric probability function of statistical significance.  
      - `query_size`: The number of genes that were included in the query.
      - `term_size`: The number of genes that are annotated to the term.
      - `precision`: The proportion of genes in the input list that are annotated to the function. Defined as intersection_size/query_size.
      - `recall`: The proportion of functionally annotated genes that the query recovers. Defined as intersection_size/term_size.
  - Example:
    - URL: <https://bioapi.multiomix.org/genes-to-terms>
    - body:
            `{
                "gene_ids":[
                    "TMCO4"
                ],
                "relation_type":[
                    "enables"
                ],
                "ontology_type":[
                    "molecular_function"
                ]
            }`
    - Response:

      ```json
        [
          {
              "alt_id":[
                  "0001948",
                  "0045308"
              ],
              "definition":"Binding to a protein.",
              "definition_reference":"GOC:go_curators",
              "go_id":"0005515",
              "is_a":"0005488",
              "name":"protein binding",
              "ontology_type":"molecular_function",
              "relations_to_genes":[
                  {
                      "evidence":"IPI",
                      "gene":"TMCO4",
                      "relation_type":"enables"
                  }
              ],
              "subset":[
                  "goslim_candida",
                  "goslim_chembl",
                  "goslim_metagenomics",
                  "goslim_pir",
                  "goslim_plant"
              ],
              "synonym":[
                  "\"glycoprotein binding\" NARROW []",
                  "\"protein amino acid binding\" EXACT []"
              ]
          }
        ]
        ```  

### Gene Ontology terms related to another specific term

Gets the list of related terms to a term.

- URL: /related-terms
- Method: POST
- Params: A body in JSON format with the following content
  - `term_id`: The term ID of the term you want to search.
  - `relations`: Filters the non-hierarchical relations between terms. By default it's `["part_of","regulates","has_part"]`. It should always be a list.
  - `ontology_type`: Filters the ontology type of the terms in the response. By default it's `["biological_process", "molecular_function", "cellular_component"]`. It should always be a list containing any permutation of the 3 ontologies.
  - `general_depth`: The search depth for the non-hierarchical relations.
  - `hierarchical_depth_to_children`: The search depth for the hierarchical relations in the direction of the children.
  - `to_root`: `0` for false `1` fot true. If true get all the terms in the hierarchical relations in the direction of the root.
- Success Response:
  - Code: 200
  - Content: The response you get is a list of GO terms related to the searched term that fulfills the conditions of the query. Each term has:
    - `go_id`: ID of the GO term.
    - `name`: Name of the GO term.
    - `ontology_type`: Denotes which of the three sub-ontologies (`cellular_component`, `biological_process` or `molecular_function`) the term belongs to.
    - `relations`: Dictionary of relations. Possible keys within this dictionary are `part_of`, `regulates` or `has_part`, and their values are lists of terms with Gene Ontology identifiers.  
  - Example:
    - URL: <https://bioapi.multiomix.org/related-terms>
    - body:
            `{
                "term_id":"0000079",
                "general_depth":5,
                "to_root":0
            }`
    - Response:

      ```json
      [
          {
              "go_id":"0000079",
              "name":"regulation of cyclin-dependent protein serine/threonine kinase activity",
              "ontology_type":"biological_process",
              "relations":{
                  "regulates":[
                      "0004693"
                  ]
              }
          },
          {
              "go_id":"0004693",
              "name":"cyclin-dependent protein serine/threonine kinase activity",
              "ontology_type":"molecular_function",
              "relations":{ }
          }
      ]
      ```  

### Cancer related drugs

Gets a list of drugs from the PharmGKB database related to a list of genes.  

- URL: /drugs-pharm-gkb
- Method: POST
- Params: A body in JSON format with the following content:
  - `gene_ids`: list of genes for which the related drugs.
- Success Response:
  - Code: 200
  - Content: The response you get is a dictionary where the genes are the keys and the values are a list of all the related drug information
    - `pharmgkb_id`: Identifier assigned to this drug label by PharmGKB.
    - `name`: Name assigned to the label by PharmGKB.
    - `source`: The source that originally authored the label. Valid options are `EMA`, `FDA`, `HCSC` or `PMDA`. For a detailed description of each value, review the [PharmGKB documentation](https://www.pharmgkb.org/page/drugLabelLegend#drug-label-sources).
    - `biomarker_flag`: `On` if drug in this label appears on the FDA Biomarker list; `Off (Formerly On)` if the label was on the FDA Biomarker list at one time; `Off (Never On)` if the label was never listed on the FDA Biomarker list (to PharmGKB's knowledge).
    - `testing_level`:  PGx testing level as annotated by PharmGKB. Possible values are: `Testing Required`, `Testing Recommended`, `Actionable PGx`, `Informative PGx` or `Criteria Not Met`. For a detailed description of each value, review the [PharmGKB documentation](https://www.pharmgkb.org/page/drugLabelLegend).
    - `chemicals`: Related chemicals.
    - `genes`: List of related genes.
    - `variants_haplotypes`: Related variants and/or haplotypes.
  - Example:
    - URL: <https://bioapi.multiomix.org/drugs-pharm-gkb>
    - body:
            `{
                "gene_ids":[
                    "JAK2"
                ]
            }`
    - Response:

      ```json
      {
          "JAK2":[
              {
                  "variants_haplotypes":"rs77375493",
                  "biomarker_flag":"",
                  "chemicals":"ropeginterferon alfa-2b",
                  "genes":[
                      "JAK2"
                  ],
                  "name":"Annotation of EMA Label for ropeginterferon alfa-2b and JAK2",
                  "pharmgkb_id":"PA166272741",
                  "source":"EMA",
                  "testing_level":"Informative PGx"
              }
          ]
      }
      ```

### Predicted functional associations network

For a given gene, this service gets from the String database a list of genes and their relationships to it.  

- URL: /string-relations
- Method: POST
- Params: A body in JSON format with the following content
  - `gene_id`: target gene.
  - `min_combined_score`: the minimum combined scored allowed int the relations. Possible scores go from 1 to 1000.
- Success Response:
  - Code: 200
  - Content: The response you get is a list of relations containing the targeted gene. More information about each field in the response and how the different scores are calculated can be found in the [scientific publication](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9825434/) of the STRING database. Unless otherwise indicated in this documentation, values for fields are scores in the range 1-1000.  
    - `gene_1`: Gene 1 in the bidirectional relationship.
    - `gene_2`: Gene 2 in the bidirectional relationship.
    - `neighborhood_transferred`: score  reflecting the strength of supporting evidence from neighborhood done in other organisms.
    - `fusion`: score that is derived from fused proteins in other species.
    - `cooccurence`: is a type of score that is derived from similar absence/presence patterns of genes in different species.
    - `homology`: is a measure of the degree of homology between the interactors in a protein interaction.
    - `coexpression`: is a measure of the degree of coexpression of two genes based on their similar patterns of mRNA expression measured by DNA arrays and similar technologies
    - `coexpression_transferred`: is a measure of the degree of coexpression of two genes based on their similar patterns of mRNA expression measured by DNA arrays and similar technologies, transferred from other species based on homology.
    - `experiments`: is a score that represents the confidence level of a protein interaction based on experimental evidence.
    - `experiments_transferred`: score that is computed from experimental data transferred from other species based on homology.
    - `database`: score derived from curated data of various databases. It represents the confidence level of protein interactions based on this curated data.
    - `database_transferred`: score derived from curated data of various databases, transferred from other species based on homology.
    - `textmining`: is a score derived from the co-occurrence of gene/protein names in scientific publications.
    - `textmining_transferred`: is a score derived from the co-occurrence of gene/protein names in scientific publications, transferred from other species based on homology.
    - `combined_score`: is a measure of the confidence level of a protein-protein interaction. It is calculated by combining the scores of all the evidence channels, including transferred scores from other species based on homology.
  - Example:
    - URL: <https://bioapi.multiomix.org/string-relations>
    - body:
            `{
                "gene_id":"MX2",
                "min_combined_score":976
            }`
    - Response:

      ```json
          [
              {
                  "coexpression": 774,
                  "coexpression_transferred": 76,
                  "combined_score": 979,
                  "cooccurence": 60,
                  "database": 900,
                  "database_transferred": null,
                  "experiments": null,
                  "experiments_transferred": null,
                  "fusion": null,
                  "gene_1": "MX2",
                  "gene_2": "MX1",
                  "homology": 961,
                  "neighborhood_transferred": null,
                  "textmining": 77,
                  "textmining_transferred": 102
              },
              {
                  "coexpression": 538,
                  "coexpression_transferred": 304,
                  "combined_score": 979,
                  "cooccurence": null,
                  "database": 500,
                  "database_transferred": null,
                  "experiments": null,
                  "experiments_transferred": 104,
                  "fusion": null,
                  "gene_1": "MX2",
                  "gene_2": "ISG15",
                  "homology": null,
                  "neighborhood_transferred": null,
                  "textmining": 862,
                  "textmining_transferred": 162
              }
          ]
      ```

### Drugs that regulate a gene

Service that takes gene symbol and returns a link to <https://go.drugbank.com> with all the drugs that upregulate and down regulate its expresion. Useful for embeding.

- URL: /drugs-regulating-gene/*gene_id*
  - `gene_id` is the identifier of the gene.
- Method: GET
- Params: -
- Success Response:
  - Code: 200
  - Content: The response you get is a dictionary with a single key called `link` where its value is a URL that points to the information on the DrugBank website.
    - `link`: Link to DrugBank website.
  - Example:
    - URL: <https://bioapi.multiomix.org/drugs-regulating-gene/TP53>
    - Response:

      ```json
      {
          "link": "https://go.drugbank.com/pharmaco/transcriptomics?q%5Bg%5B0%5D%5D%5Bm%5D=or&q%5Bg%5B0%5D%5D%5Bdrug_approved_true%5D=all&q%5Bg%5B0%5D%5D%5Bdrug_nutraceutical_true%5D=all&q%5Bg%5B0%5D%5D%5Bdrug_illicit_true%5D=all&q%5Bg%5B0%5D%5D%5Bdrug_investigational_true%5D=all&q%5Bg%5B0%5D%5D%5Bdrug_withdrawn_true%5D=all&q%5Bg%5B0%5D%5D%5Bdrug_experimental_true%5D=all&q%5Bg%5B1%5D%5D%5Bm%5D=or&q%5Bg%5B1%5D%5D%5Bdrug_available_in_us_true%5D=all&q%5Bg%5B1%5D%5D%5Bdrug_available_in_ca_true%5D=all&q%5Bg%5B1%5D%5D%5Bdrug_available_in_eu_true%5D=all&commit=Apply+Filter&q%5Bdrug_precise_names_name_cont%5D=&q%5Bgene_symbol_eq%5D=TP53&q%5Bgene_id_eq%5D=&q%5Bchange_eq%5D=&q%5Binteraction_cont%5D=&q%5Bchromosome_location_cont%5D="
      }
      ```  

## Error Responses

The possible error codes are 400, 404 and 500. The content of each of them is a JSON with a unique key called `error` where its value is a description of the problem that produces the error. For example:  

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

1. Start up Docker services like MongoDB: `docker compose -f docker-compose.dev.yml up -d`.
2. Go to the `bio-api` folder.
3. Run Flask server: `python3 bioapi.py`.

**NOTE:** If you are looking for documentation for a production deployment see [DEPLOYING.md](DEPLOYING.md).

### Tests

To run all the tests:

1. Go to the `bioapi` folder.
2. Run the `pytest` command.
