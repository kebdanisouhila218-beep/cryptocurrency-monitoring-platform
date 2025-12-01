# collector/collector_logic.py
import requests
from typing import List, Dict

def fetch_coinpaprika_data(coin_ids: str) -> List[Dict]:
    """Récupère les données brutes de CoinPaprika (sans side-effects)."""
    url = f"https://api.coinpaprika.com/v1/tickers?ids={coin_ids}"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()

def transform_coin_data(raw_data: List[Dict]) -> List[Dict]:
    """Transforme les données brutes en format propre pour MongoDB."""
    result = []
    for coin in raw_data:
        if "quotes" not in coin or "USD" not in coin["quotes"]:
            continue
        result.append({
            "coin_id": coin["id"],
            "symbol": coin["symbol"],
            "name": coin["name"],
            "price_usd": coin["quotes"]["USD"]["price"],
            "volume_24h": coin["quotes"]["USD"]["volume_24h"],
            "market_cap": coin["quotes"]["USD"]["market_cap"],
            "timestamp": None  # ajouté plus tard
        })
    return result