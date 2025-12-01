# api/database.py
from pymongo import MongoClient

MONGO_URI = "mongodb://mongo:27017/"
DB_NAME = "crypto_db"
COLLECTION_NAME = "prices"

def get_collection():
    client = MongoClient(MONGO_URI)
    return client[DB_NAME][COLLECTION_NAME]