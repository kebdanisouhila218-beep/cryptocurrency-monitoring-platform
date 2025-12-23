# api/test_api.py
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock
from main import app, get_collection, get_current_active_user

MOCK_PRICES = [
    {
        "coin_id": "btc-bitcoin",
        "symbol": "BTC",
        "name": "Bitcoin",
        "price_usd": 93421.56,
        "volume_24h": 28473928473,
        "market_cap": 1839284739284,
        "timestamp": 1700000000
    }
]

def test_root_returns_json():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Crypto" in data["message"]
    
def test_prices():
    # Mock MongoDB
    mock_collection = Mock()
    # Make the mock return an iterable result for aggregation
    mock_collection.aggregate.return_value = MOCK_PRICES

    # Mock authentication
    mock_user = {"username": "testuser", "email": "test@example.com"}
    
    # Injecter les mocks
    app.dependency_overrides[get_collection] = lambda: mock_collection
    app.dependency_overrides[get_current_active_user] = lambda: mock_user

    # Tester
    client = TestClient(app)
    response = client.get("/prices")

    # Vérifier
    assert response.status_code == 200
    data = response.json()
    assert "prices" in data
    assert len(data["prices"]) == 1
    assert data["prices"][0]["symbol"] == "BTC"

    # Nettoyer
    app.dependency_overrides.clear()