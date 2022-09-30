# Deploy

Below are the steps to perform a production deploy of BioAPI.


## Requirements

- BioAPI deployment was configured to be simple from the Docker Compose tool. So you need to install:
    - [docker](https://docs.docker.com/desktop/#download-and-install)
    - [docker-compose](https://docs.docker.com/compose/install/)
- To incorporate the genomic databases that BioAPI needs, the mongodb tools are required. Install them using:
    ```
    apt-get install mongodb-org-tools
    ```
## Instructions

1. Create MongoDB Docker volumes:
    ```bash
    docker volume create --name=bio_api_mongo_data
    docker volume create --name=bio_api_mongo_config
    ```
2. Make a copy of `docker-compose_dist.yml` with the name `docker-compose.yml` and set the environment variables that are empty with data. They are listed below by category:
    - MongoDB Server:
        - `MONGO_INITDB_ROOT_USERNAME` and `MONGO_INITDB_ROOT_PASSWORD`: These variables are the username and password that will be created in MongoDB for the "*admin*" database.  
        - `deploy.resources.limits.memory`: By default, 12GB of memory is allocated for MongoDB. Modify this value if you need it.  
    - BioAPI Server:
        - `MONGO_USER` and `MONGO_PASSWORD`: These variables are the username and password for BioAPI to access MongoDB. These credentials must be the same ones that were set for the MongoDB server.
3. Import genomics databases. BioAPI uses three genomic databases for its operation. These databases must be loaded in MongoDB. To import all databases in MongoDB:
    1. Download the "bioapi_db.gz" from **[here](https://ipfs.io/ipfs/QmaDAw6tD1BWGoMXPBRNTYWmRPYPq9QMebaLCC4uCECA4k?filename=bioapi_db.gz)**
    1. Use Mongorestore to import it into MongoDB:
   ```
   mongorestore --username <user> --password <pass> --authenticationDatabase admin --host <url> --port <port> --gzip --archive=bioapi_db.gz
    ```
    Where *\<user\>*, *\<pass\>*, *\<url\>* and *\<port\>* are the preconfigured credentials to MongoDB. *bioapi_db.gz* is the file downloaded in the previous step. Keep in mind that this loading process will import approximately *45 GB* of information into MongoDB, so it may take a while.

    Alternatively (but **not recommended** due to high computational demands) you can run a separate ETL process to download from source, process and import the databases into MongoDB. The ETL process is programmed in a single bash script for each database and is shown below:  

    First, you must install the necessary requirements. They can be installed using
    ```python
    pip install -r config/genomic_db_conf/requirements.txt
    ```

    1. Metabolic pathways: [ConsensusPathDB](http://cpdb.molgen.mpg.de/)  
        - Go to the path "databases/cpdb"
        - Edit the empty variables `user` and `password` with the credentials configured in step 2. 
        - Run the bash script:  
            ```
            bash cpdb2mongodb.sh
            ```
    2. Gene nomenclature: [HUGO Gene Nomenclature Committee](https://www.genenames.org/)
        - Go to the path "databases/hgnc"
        - Edit the empty variables `user` and `password` with the credentials configured in step 2. 
        - Run the bash script:  
            ```
            bash hgnc2mongodb.sh
            ```             
    3. Gene expression: [Genotype-Tissue Expression (GTEx)](https://gtexportal.org/home/)
        - Go to the path "databases/gtex"
        - Edit the empty variables `user` and `password` with the credentials configured in step 2. 
        - Run the bash script:  
            ```
            bash gtex2mongodb.sh
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