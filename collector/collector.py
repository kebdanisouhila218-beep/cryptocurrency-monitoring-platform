# collector/collector.py - VERSION CORRIGÉE
import sys
import time
import requests
from pymongo import MongoClient
import logging

logging.basicConfig(level=logging.INFO)

# ===== CORRECTION: Liste complète de cryptos populaires =====
CRYPTO_LIST = [
    "btc-bitcoin",
    "eth-ethereum",
    "bnb-binance-coin",
    "xrp-ripple",
    "ada-cardano",
    "sol-solana",
    "doge-dogecoin",
    "dot-polkadot",
    "matic-polygon",
    "ltc-litecoin"
]

COIN_IDS = ",".join(CRYPTO_LIST)  # btc-bitcoin,eth-ethereum,...
MONGO_URI = "mongodb://mongo:27017/"
DB_NAME = "crypto_db"
COLLECTION_NAME = "prices"

def fetch_and_store():
    try:
        logging.info("📡 Appel à CoinPaprika...")
        logging.info(f"📋 Cryptos demandées: {COIN_IDS[:100]}...")
        
        url = f"https://api.coinpaprika.com/v1/tickers"
        
        # ✅ CHANGEMENT: On récupère TOUTES les cryptos, puis on filtre
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        all_coins = response.json()
        
        logging.info(f"📦 Total de cryptos reçues : {len(all_coins)}")
        
        # Filtrer pour garder seulement nos cryptos
        coins = [c for c in all_coins if c['id'] in CRYPTO_LIST]
        
        logging.info(f"✅ Cryptos filtrées : {len(coins)}")

        if len(coins) == 0:
            logging.warning("⚠️ Aucune crypto trouvée dans le filtre!")
            logging.info("🔍 Essai sans filtre...")
            coins = all_coins[:10]  # Prendre les 10 premières

        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]

        inserted = 0
        for coin in coins:
            try:
                # Vérifier que les données sont complètes
                if "quotes" not in coin or "USD" not in coin.get("quotes", {}):
                    logging.warning(f"⚠️ Données incomplètes pour {coin.get('id', 'unknown')}")
                    continue
                
                doc = {
                    "coin_id": coin["id"],
                    "symbol": coin["symbol"],
                    "name": coin["name"],
                    "price_usd": coin["quotes"]["USD"]["price"],
                    "volume_24h": coin["quotes"]["USD"].get("volume_24h", 0),
                    "market_cap": coin["quotes"]["USD"].get("market_cap", 0),
                    "timestamp": time.time()
                }
                collection.insert_one(doc)
                inserted += 1
                logging.info(f"✅ {coin['symbol']:6s} = ${doc['price_usd']:>12.4f}")
            except Exception as e:
                logging.error(f"❌ Erreur pour {coin.get('symbol', 'unknown')}: {e}")

        logging.info(f"💾 {inserted} documents insérés dans MongoDB.")
        
        # Afficher un résumé
        total_docs = collection.count_documents({})
        logging.info(f"📊 Total de documents dans la DB: {total_docs}")
        
        return True

    except Exception as e:
        logging.error(f"❌ Échec : {e}")
        import traceback
        traceback.print_exc()
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