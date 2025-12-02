# api/test_integration_api.py
import pytest
from fastapi.testclient import TestClient
from main import app
import requests
from pymongo import MongoClient
import time

MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "crypto_db"
COLLECTION_NAME = "prices"

@pytest.fixture(scope="module", autouse=True)
def setup_test_data():
    """Insère une donnée de test avant les tests."""
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    
    # Insère une donnée réelle
    collection.insert_one({
        "coin_id": "btc-bitcoin",
        "symbol": "BTC",
        "price_usd": 93421.56,
        "timestamp": time.time()
    })
    yield
    # Nettoyage après
    collection.delete_many({"symbol": "BTC"})

def test_api_returns_data_from_mongodb():
    """Teste que l'API lit bien les données depuis MongoDB réelle."""
    client = TestClient(app)
    response = client.get("/prices")
    
    assert response.status_code == 200
    data = response.json()
    assert "prices" in data
    assert len(data["prices"]) >= 1
    assert data["prices"][0]["symbol"] == "BTC"