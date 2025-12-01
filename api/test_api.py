# api/test_api.py
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock
from main import app, get_collection

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

def test_root():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "🚀 API Crypto fonctionnelle !"

def test_prices():
    # Mock MongoDB
    mock_collection = Mock()
    mock_cursor = Mock()
    mock_cursor.sort.return_value.limit.return_value = MOCK_PRICES
    mock_collection.find.return_value = mock_cursor

    # Injecter le mock
    app.dependency_overrides[get_collection] = lambda: mock_collection

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