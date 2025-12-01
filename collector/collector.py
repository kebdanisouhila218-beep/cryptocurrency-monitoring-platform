# collector/collector.py
import sys
import time
import requests
from pymongo import MongoClient
import logging

logging.basicConfig(level=logging.INFO)
COIN_IDS = "btc-bitcoin,eth-ethereum"
MONGO_URI = "mongodb://mongo:27017/"
DB_NAME = "crypto_db"
COLLECTION_NAME = "prices"

def fetch_and_store():
    try:
        logging.info("📡 Appel à CoinPaprika...")
        url = f"https://api.coinpaprika.com/v1/tickers?ids={COIN_IDS}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        coins = response.json()

        logging.info(f"📦 Données reçues : {len(coins)} cryptos")

        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]

        inserted = 0
        for coin in coins:
            doc = {
                "coin_id": coin["id"],
                "symbol": coin["symbol"],
                "name": coin["name"],
                "price_usd": coin["quotes"]["USD"]["price"],
                "timestamp": time.time()
            }
            collection.insert_one(doc)
            inserted += 1
            logging.info(f"✅ {coin['symbol']} = ${doc['price_usd']:.4f}")

        logging.info(f"💾 {inserted} documents insérés dans MongoDB.")
        return True

    except Exception as e:
        logging.error(f"❌ Échec : {e}")
        return False

if __name__ == "__main__":
    # Mode test : si on lance avec "test" → un seul run
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        logging.info("🧪 MODE TEST : exécution unique")
        success = fetch_and_store()
        if success:
            print("\n🟢 TEST RÉUSSI : données collectées et stockées.")
        else:
            print("\n🔴 TEST ÉCHOUÉ : voir les logs ci-dessus.")
        sys.exit(0 if success else 1)

    # Mode normal : boucle infinie
    logging.info("🚀 Collector en mode continu (toutes les 60s)...")
    while True:
        fetch_and_store()
        time.sleep(60)