# Deploy

Below are the steps to perform a production deploy of BioAPI.


## Requirements

BioAPI deployment was configured to be simple from the Docker Compose tool. So you need to install:
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
        - `MONGO_INITDB_ROOT_USERNAME` and `MONGO_INITDB_ROOT_PASSWORD`: These variables are the username and password that will be created in MongoDB for the "*bio_api*" database.  
        - `deploy.resources.limits.memory`: By default, 12GB of memory is allocated for MongoDB. Modify this value if you need it.  
    - BioAPI Server:
        - `MONGO_USER` and `MONGO_PASSWORD`: These variables are the username and password for BioAPI to access MongoDB. These credentials must be the same ones that were set for the MongoDB server.
3. Edit the BioAPI configuration file. It is found in *config/bioapi_conf/config.txt*. As in the previous step, set the MongoDB credentials in the corresponding variables.  
4. Import genomics databases. BioAPI uses three genomic databases for its operation. These databases must be loaded in MongoDB. To import all databases in MongoDB:
    1. Download this file: **LINK**
    1. Use Mongorestore to import into MongoDB:
    ```
    mongorestore --username <user> --password <pass> --authenticationDatabase admin --host <url> --port <port> --gzip <path_to_dump>
    ```
    Where *\<user\>*, *\<pass\>*, *\<url\>* and *\<port\>* are the preconfigured credentials to MongoDB. *\<path_to_dump\>* is the path to the folder downloaded in the first step.

    Alternatively (but not recommended due to high computational demands) you can run a separate ETL process to download, process and import the databases into MongoDB. The ETL process is simplified for the user in a single bash script for each database and is shown below:  

    First, you must install the necessary requirements. They can be installed using
    ```python
    pip install -r config/genomic_db_conf/requirements.txt
    ```

    1. Metabolic pathways: [ConsensusPathDB](http://cpdb.molgen.mpg.de/)  
        - Go to the path "databases/cpdb"
        - Edit the empty variables `user` and `password` with the credentials configured in step 2. 
        - Run the bash script:  
            ```bash
            bash cpdb2mongodb.sh
            ```
    2. Gene nomenclature: [HUGO Gene Nomenclature Committee](https://www.genenames.org/)
        - Go to the path "databases/hgnc"
        - Edit the empty variables `user` and `password` with the credentials configured in step 2. 
        - Run the bash script:  
            ```bash
            bash hgnc2mongodb.sh
            ```             
    3. Gene expression: [Genotype-Tissue Expression (GTEx)](https://gtexportal.org/home/)
        - Go to the path "databases/gtex"
        - Edit the empty variables `user` and `password` with the credentials configured in step 2. 
        - Run the bash script:  
            ```bash
            bash gtex2mongodb.sh
            ```
## Build and run BioAPI

To build the Docker image use:  
```bash
docker image build -t omicsdatascience/bio-api:0.1.0 .
```

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