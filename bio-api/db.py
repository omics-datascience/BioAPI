import pymongo
from pymongo.database import Database
import logging
import os


def get_mongo_connection(is_debug,Config) -> Database:
    """
    Gets Mongo connection using config.txt file if DEBUG env var is 'true', or all the env variables in case of prod
    (DEBUG = 'false')
    :return: Database instance
    """
    try:
        if is_debug:
            host = Config.get('mongodb', 'host')
            mongo_port = Config.get('mongodb', 'port')
            user = Config.get('mongodb', 'user')
            password = Config.get('mongodb', 'pass')
            db = Config.get('mongodb', 'db_name')
        else:
            host = os.environ.get('MONGO_HOST')
            mongo_port = os.environ.get('MONGO_PORT')
            user = os.environ.get('MONGO_USER')
            password = os.environ.get('MONGO_PASSWORD')
            db = os.environ.get('MONGO_DB')

            if not host or not mongo_port or not db:
                logging.error(f'Host ({host}), port ({mongo_port}) or db ({db}) is invalid', exc_info=True)
                exit(-1)

        mongo_client = pymongo.MongoClient(f"mongodb://{user}:{password}@{host}:{mongo_port}/?authSource=admin")
        return mongo_client[db]
    except Exception as e:
        logging.error("Database connection error." + str(e), exc_info=True)
        exit(-1)