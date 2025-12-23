# collector/test_collector_logic.py
import pytest
requests_mock = pytest.importorskip("requests_mock")
from collector_logic import fetch_coinpaprika_data, transform_coin_data

MOCK_API_RESPONSE = [
    {
        "id": "btc-bitcoin",
        "symbol": "BTC",
        "name": "Bitcoin",
        "quotes": {
            "USD": {
                "price": 93421.56,
                "volume_24h": 28473928473,
                "market_cap": 1839284739284
            }
        }
    }
]

def test_fetch_coinpaprika_data():
    with requests_mock.Mocker() as m:
        m.get("https://api.coinpaprika.com/v1/tickers?ids=btc-bitcoin", json=MOCK_API_RESPONSE)
        result = fetch_coinpaprika_data("btc-bitcoin")
    
    assert len(result) == 1
    assert result[0]["symbol"] == "BTC"
    assert result[0]["quotes"]["USD"]["price"] == 93421.56

def test_transform_coin_data():
    transformed = transform_coin_data(MOCK_API_RESPONSE)
    coin = transformed[0]
    assert coin["symbol"] == "BTC"
    assert coin["price_usd"] == 93421.56
    assert coin["market_cap"] == 1839284739284