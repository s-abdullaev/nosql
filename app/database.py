from pymongo import MongoClient

from config import MONGO_URI, MONGO_DB_NAME


def get_client() -> MongoClient:
    return MongoClient(MONGO_URI)


def get_db():
    return get_client()[MONGO_DB_NAME]
