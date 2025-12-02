# collector/test_integration_collector.py
import pytest
import requests
from pymongo import MongoClient
import time

# ✅ Correction ici
MONGO_URI = "mongodb://mongo:27017/"  # ← Nom du service Docker
DB_NAME = "crypto_db"
COLLECTION_NAME = "prices"
COIN_IDS = "btc-bitcoin"

def test_collect_and_store_in_mongodb():
    """Teste que le collector insère bien des données dans MongoDB."""
    # 1. Appel à CoinPaprika
    url = f"https://api.coinpaprika.com/v1/tickers?ids={COIN_IDS}"
    response = requests.get(url)
    assert response.status_code == 200
    coins = response.json()
    assert len(coins) >= 1

    # 2. Connexion à MongoDB (dans Docker)
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]

    # 3. Insérer une donnée
    doc = {
        "coin_id": coins[0]["id"],
        "symbol": coins[0]["symbol"],
        "price_usd": coins[0]["quotes"]["USD"]["price"],
        "timestamp": time.time()
    }
    result = collection.insert_one(doc)
    assert result.inserted_id is not None

    # 4. Vérifier la lecture
    found = collection.find_one({"_id": result.inserted_id})
    assert found is not None
    assert found["symbol"] == "BTC"

    # 5. Nettoyer
    collection.delete_one({"_id": result.inserted_id})