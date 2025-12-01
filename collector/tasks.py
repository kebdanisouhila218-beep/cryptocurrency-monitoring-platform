# collector/tasks.py
import time
import requests
from celery import Celery
from celery.schedules import crontab
from pymongo import MongoClient
from .collector_logic import fetch_coinpaprika_data, transform_data


# Configuration Celery
app = Celery('collector', broker='redis://redis:6379/0', backend='redis://redis:6379/0')

# Configuration MongoDB
MONGO_URI = "mongodb://mongo:27017/"
DB_NAME = "crypto_db"
COLLECTION_NAME = "prices"

# Liste des cryptomonnaies à collecter
COIN_IDS = "btc-bitcoin,eth-ethereum"  # tu peux étendre

@app.task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 10})
def fetch_and_store_task(self):
    """Tâche Celery pour collecter et stocker les données de CoinPaprika."""
    try:
        # 1. Appel à CoinPaprika
        url = f"https://api.coinpaprika.com/v1/tickers?ids={COIN_IDS}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        coins = response.json()

        # 2. Connexion MongoDB
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]

        # 3. Insérer chaque pièce
        for coin in coins:
            if "quotes" not in coin or "USD" not in coin["quotes"]:
                continue  # données incomplètes
            doc = {
                "coin_id": coin["id"],
                "symbol": coin["symbol"],
                "name": coin["name"],
                "price_usd": coin["quotes"]["USD"]["price"],
                "volume_24h": coin["quotes"]["USD"]["volume_24h"],
                "market_cap": coin["quotes"]["USD"]["market_cap"],
                "percent_change_1h": coin["quotes"]["USD"]["percent_change_1h"],
                "percent_change_24h": coin["quotes"]["USD"]["percent_change_24h"],
                "percent_change_7d": coin["quotes"]["USD"]["percent_change_7d"],
                "timestamp": time.time()
            }
            collection.insert_one(doc)

        return f"✅ Succès : {len(coins)} cryptos collectées."

    except Exception as exc:
        raise self.retry(exc=exc)  # relance automatique avec backoff

# Planification : toutes les minutes
app.conf.beat_schedule = {
    'collect-every-minute': {
        'task': 'tasks.fetch_and_store_task',
        'schedule': crontab(minute='*/1'),
    },
}

# Optionnel : timezone (par défaut UTC)
app.conf.timezone = 'UTC'