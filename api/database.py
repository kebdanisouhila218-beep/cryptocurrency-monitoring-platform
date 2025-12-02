# api/database.py

from pymongo import MongoClient
import os

# ✅ Utiliser 127.0.0.1 pour la connexion locale
# Utiliser "mongo" si dans Docker
MONGO_HOST = os.getenv("MONGO_HOST", "127.0.0.1")
MONGO_PORT = os.getenv("MONGO_PORT", "27017")
MONGO_URI = f"mongodb://{MONGO_HOST}:{MONGO_PORT}/"

DB_NAME = "crypto_db"
COLLECTION_NAME = "prices"

def get_collection():
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        # Tester la connexion
        client.server_info()
        return client[DB_NAME][COLLECTION_NAME]
    except Exception as e:
        print(f"❌ Erreur de connexion MongoDB: {e}")
        raise