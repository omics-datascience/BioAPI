# Deploy

Below are the steps to perform a production deploy of BioAPI.


## Requirements

- BioAPI deployment was configured to be simple from the Docker Compose tool. So you need to install:
    - [docker](https://docs.docker.com/desktop/#download-and-install)
    - [docker-compose](https://docs.docker.com/compose/install/)


## Instructions

1. Create MongoDB Docker volumes:
    ```bash
    docker volume create --name=bio_api_mongo_data
    docker volume create --name=bio_api_mongo_config
    ```
2. Make a copy of `docker-compose_dist.yml` with the name `docker-compose.yml` and set the environment variables that are empty with data. They are listed below by category:
    - MongoDB Server:
        - `MONGO_INITDB_ROOT_USERNAME` and `MONGO_INITDB_ROOT_PASSWORD`: These variables are the username and password that will be created in MongoDB for the "*admin*" database.  
        - `deploy.resources.limits.memory`: By default, 6GB of memory is allocated for MongoDB. Modify this value if you need it.  
    - BioAPI Server:
        - `MONGO_USER` and `MONGO_PASSWORD`: These variables are the username and password for BioAPI to access MongoDB. These credentials must be the same ones that were set for the MongoDB server.
3. (Optional) Optimize Mongo by changing the configuration in the `config/mongo/mongod.conf` file and uncommenting the reference in the `docker-compose.yml` and/or `docker-compose.dev.yml`.
4. Start up all the services with Docker Compose running `docker compose up -d` to check that It's all working, and read the instructions in the following section to import the genomics databases.


## Importing genomic data

BioAPI uses three genomic databases for its operation. These databases must be loaded in MongoDB. You can import all the databases in two ways:


### Import using public DB backup (recommended)

To import all databases in MongoDB:
 
1. Download the "bioapi_db.gz" from **[here](https://drive.google.com/file/d/1lI3A98N-GhnffkSOWjB_gx_ieq3pEjFP/view?usp=sharing)**
2. Shutdown all the services running `docker compose down`
3. Edit the `docker-compose.yml` file to include the downloaded file inside the container:
    ```yml
    # ...
        mongo:
            image: mongo:6.0.2
            # ...
            volumes:
                # ...
                - /path/to/bioapi_db.gz:/bioapi_db.gz
    # ...
    ```
	Where "/path/to/" is the absolute path of the "bioapi_db.gz" file downloaded on step 1.
4. Start up the services again running `docker compose up -d`
5. Go inside the container `docker container exec -it bio_api_mongo_db bash`
6. Use Mongorestore to import it into MongoDB:
    ```bash
    mongorestore --username <user> --password <pass> --authenticationDatabase admin --gzip --archive=/bioapi_db.gz
    ```
   Where *\<user\>*, *\<pass\>* are the preconfigured credentials to MongoDB in the `docker-compose.yml` file. *bioapi_db.gz* is the file downloaded in the previous step. **Keep in mind that this loading process will import approximately *47 GB* of information into MongoDB, so it may take a while**.
7. Rollup the changes in `docker-compose.yml` file to remove the backup file from the `volumes` section. Restart all the services again.


### Manually import the different databases

Alternatively (but **not recommended** due to high computational demands) you can run a separate ETL process to download from source, process and import the databases into MongoDB. 

1. Install the necessary requirements:  
    - [R languaje](https://www.r-project.org/). Version 4.1.2 or later (Only necessary if you want to update the Gene information database from Ensembl)
    - Some python packages. They can be installed using:  
        `pip install -r config/genomic_db_conf/requirements.txt`  
2. The ETL process is programmed in a single bash script for each database. Edit in the bash file of the database that you want to update the **user** and **password** parameters, using the same values that you set in the `docker-compose.yml` file. Bash files can be found in the *'databases'* folder, within the corresponding directories for each database:  
    - For Metabolic pathways ([ConsensusPathDB](http://cpdb.molgen.mpg.de/)) use "databases/cpdb" directory and the *cpdb2mongodb.sh* file.
    - For Gene nomenclature ([HUGO Gene Nomenclature Committee](https://www.genenames.org/)) use "databases/hgnc" directory and the *hgnc2mongodb.sh* file.
    - For Gene expression ([Genotype-Tissue Expression (GTEx)](https://gtexportal.org/home/)) use "databases/gtex" directory and the *gtex2mongodb.sh*.
    - For Gene information ([Ensembl (Biomart tool)](https://www.ensembl.org/biomart/martview/)) use "databases/ensembl_gene" directory and the *ensembl_gene2mongodb.sh* file.  
    - For Oncokb Drug information, it is necessary that you download the dataset from Therapeutic, Diagnostic and Prognostic datasets of Actionable Genes from its [official site](https://www.oncokb.org/actionableGenes) and place it within the directory "databases/oncokb" with the Name "oncokb_biomarker_drug_associations.tsv". Then use the same directory as before and the script oncokb2mongodb.sh to load.  
3. Run bash files.  
    `./<file.sh>`  
    where file.sh can be *cpdb2mongodb.sh*, *hgnc2mongodb.sh*, *gtex2mongodb.sh*, or *ensembl_gene2mongodb.sh*, as appropriate.  

## Run BioAPI
Use docker compose to get the BioAPI up:

```bash
docker-compose up -d
```

By default, BioAPI runs on `localhost:8000`.  

If you want to stop all services, you can execute:

```bash
docker-compose down
```


### See container status

To check the different services' status you can run:

```bash
docker-compose logs <service>
```

Where  *\<service\>* could be `nginx`, `web` or `mongo`.


## Update genomic databases
If new versions are released for the genomic databases included in BioAPI, you can update them by following the instructions below:  
- For the "Metabolic pathways (ConsensusPathDB)", "Gene nomenclature (HUGO Gene Nomenclature Committee)", "Gene information (Ensembl)" and Drugs (OncoKB) databases, it is not necessary to make any modifications to any script. This is because the datasets are automatically downloaded in their most up-to-date versions when the bash file for each database is executed as described in the **Manually import the different databases** section of this file.  
- If you need to update the "Gene expression (Genotype-Tissue Expression)" database, you should also follow the procedures in the section named above, but first you should edit the bash file as follows:  
    1. Modify the **gtex2mongodb.sh** file. Edit the variables *"expression_url"* and *"annotation_url"*.
    1. In the *expession_url* variable, set the url corresponding to the GTEx "RNA-Seq Data" compressed file (gz compression). This file should contain the Gene TPMs values (Remember that Gene expression on the GTEx Portal are shown in Transcripts Per Million or TPMs).
    1. In the *"annotation_url"* variable, set the url corresponding to the file that contains the annotated samples and allows finding the corresponding tissue type for each sample in the database.
  By default, GTEx is being used in its version [GTEx Analysis V8 (dbGaP Accession phs000424.v8.p2)](https://gtexportal.org/home/datasets#datasetDiv1)

**NOTE:** It is NOT necessary to drop the MongoDB database before upgrading (this applies to all databases). 