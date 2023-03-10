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

Alternatively (but **not recommended** due to high computational demands) you can run a separate ETL process to download from source, process and import the databases into MongoDB. The ETL process is programmed in a single bash script for each database and is shown below:  

First, you must install the necessary requirements.  
- [R languaje](https://www.r-project.org/). Version 4.1.2 or later.
- Some python packages. They can be installed using
    ```bash
    pip install -r config/genomic_db_conf/requirements.txt
    ```

1. Metabolic pathways: [ConsensusPathDB](http://cpdb.molgen.mpg.de/)  
    - Go to the path "databases/cpdb"
    - Edit the empty variables `user` and `password` with the credentials configured in step 2. 
   - Run the bash script:  
   ```bash
   ./cpdb2mongodb.sh
   ```
2. Gene nomenclature: [HUGO Gene Nomenclature Committee](https://www.genenames.org/)
    - Go to the path "databases/hgnc"
    - Edit the empty variables `user` and `password` with the credentials configured in step 2. 
    - Run the bash script:  
    ```bash
    ./hgnc2mongodb.sh
    ```
3. Gene expression: [Genotype-Tissue Expression (GTEx)](https://gtexportal.org/home/)
    - Go to the path "databases/gtex"
    - Edit the empty variables `user` and `password` with the credentials configured in step 2. 
    - Run the bash script:  
    ```bash
    ./gtex2mongodb.sh
    ```
4. Gene information: [Ensembl (Biomart tool)](https://www.ensembl.org/biomart/martview/)
    - Go to the path "databases/ensembl_gene"
    - Edit the empty variables `user` and `password` with the credentials configured in step 2. 
    - Run the bash script:  
    ```bash
    ./ensembl_gene2mongodb.sh
    ```
5. Gene ontology: [Gene Ontology (GO)](http://geneontology.org/)
	**This import needs the "Gene nomenclature" databases (2) already imported to properly process the gene ontology databases
    - Go to the path "databases/gene_ontology"
    - Edit the empty variables `user` and `password` with the credentials configured in step 2. 
    - Run the python script:  
    ```python
    python ./go2mongodb.py
    ```


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
