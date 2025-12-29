# collector/tasks.py - VERSION FINALE AVEC UPSERT

import time
import requests
from celery import Celery
from celery.schedules import crontab
from pymongo import MongoClient

# Import absolu
import collector_logic

# Configuration Celery
app = Celery('collector', broker='redis://redis:6379/0', backend='redis://redis:6379/0')

# Configuration MongoDB
MONGO_URI = "mongodb://mongo:27017/"
DB_NAME = "crypto_db"
COLLECTION_NAME = "prices"

# ✅ LISTE ÉTENDUE : 50 CRYPTOS POPULAIRES
CRYPTO_LIST = [
    # Top 13 (déjà présentes)
    "btc-bitcoin",
    "eth-ethereum",
    "bnb-binance-coin",
    "sol-solana",
    "xrp-ripple",
    "ada-cardano",
    "doge-dogecoin",
    "dot-polkadot",
    "matic-polygon",
    "ltc-litecoin",
    "avax-avalanche",
    "link-chainlink",
    "atom-cosmos",
    "uni-uniswap",
    "xlm-stellar",
    
    # 35 cryptos supplémentaires pour atteindre 50
    "trx-tron",
    "etc-ethereum-classic",
    "bch-bitcoin-cash",
    "near-near-protocol",
    "leo-unus-sed-leo",
    "icp-internet-computer",
    "apt-aptos",
    "arb-arbitrum",
    "op-optimism",
    "stx-stacks",
    "fil-filecoin",
    "ldo-lido-dao",
    "mnt-mantle",
    "imx-immutable-x",
    "inj-injective-protocol",
    "mkr-maker",
    "rune-thorchain",
    "grt-the-graph",
    "aave-aave",
    "snx-synthetix-network-token",
    "ftm-fantom",
    "algo-algorand",
    "vet-vechain",
    "egld-elrond",
    "axs-axie-infinity",
    "sand-the-sandbox",
    "mana-decentraland",
    "theta-theta-network",
    "xtz-tezos",
    "flow-flow",
    "eos-eos",
    "chz-chiliz",
    "kcs-kucoin-shares",
    "btt-bittorrent",
    "hbar-hedera-hashgraph",
    "zil-zilliqa",
    "ksm-kusama",
    "gala-gala",
    "crv-curve-dao-token",
    "qnt-quant",
    "1inch-1inch",
    "neo-neo",
    "comp-compound",
    "zrx-0x",
    "enj-enjin-coin",
    "bat-basic-attention-token",
    "lrc-loopring",
    "chr-chromia"
]

COIN_IDS = ",".join(CRYPTO_LIST)


@app.task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 10})
def fetch_and_store_task(self):
    """
    Tâche Celery pour collecter et stocker les données de CoinPaprika.
    
    ✅ AMÉLIORATION : Utilise UPSERT pour remplacer les anciennes valeurs
    au lieu de les accumuler.
    """
    print("\n" + "="*60)
    print("[CELERY] 📡 Début de la collecte des cryptos...")
    print("="*60)
    
    try:
        # 1. Appel à CoinPaprika avec filtre strict
        url = f"https://api.coinpaprika.com/v1/tickers?ids={COIN_IDS}"
        print(f"[CELERY] 📋 Cryptos demandées: {len(CRYPTO_LIST)}")
        print(f"[CELERY] 🔗 URL: {url[:80]}...")
        
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        coins = response.json()
        
        print(f"[CELERY] ✅ {len(coins)} cryptos reçues depuis l'API")
        
        # Vérifier qu'on a bien nos cryptos
        if len(coins) == 0:
            print("[CELERY] ⚠️ Aucune crypto reçue avec le filtre, méthode alternative...")
            
            # Méthode alternative: récupérer toutes et filtrer
            all_url = "https://api.coinpaprika.com/v1/tickers"
            all_response = requests.get(all_url, timeout=15)
            all_coins = all_response.json()
            
            coins = [c for c in all_coins if c['id'] in CRYPTO_LIST]
            print(f"[CELERY] ✅ {len(coins)} cryptos filtrées")
        
        # ✅ VALIDATION : Vérifier qu'on n'a QUE nos cryptos populaires
        received_ids = [c['id'] for c in coins]
        unexpected = [c_id for c_id in received_ids if c_id not in CRYPTO_LIST]
        
        if unexpected:
            print(f"[CELERY] ⚠️ ATTENTION : Cryptos inattendues reçues : {unexpected}")
            # Filtrer pour garder seulement nos cryptos
            coins = [c for c in coins if c['id'] in CRYPTO_LIST]
            print(f"[CELERY] 🔧 Filtrage appliqué : {len(coins)} cryptos conservées")
        
        # Afficher les cryptos qu'on va insérer
        print("\n[CELERY] 📊 CRYPTOS À INSÉRER/METTRE À JOUR:")
        for coin in coins:
            print(f"[CELERY]   ✅ {coin.get('symbol', 'N/A'):6s} - {coin.get('name', 'N/A')}")
        print("")

        # 2. Connexion MongoDB
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
        
        # ✅ NOUVELLE : Collection historique pour les prévisions
        history_collection = db["price_history"]

        # 3. ✅ UPSERT : Remplacer au lieu d'accumuler
        inserted_count = 0
        updated_count = 0
        history_count = 0
        current_timestamp = time.time()
        
        for coin in coins:
            if "quotes" not in coin or "USD" not in coin["quotes"]:
                print(f"[CELERY] ⚠️ Données incomplètes pour {coin.get('id', 'unknown')}")
                continue
            
            doc = {
                "coin_id": coin["id"],
                "symbol": coin["symbol"],
                "name": coin["name"],
                "price_usd": coin["quotes"]["USD"]["price"],
                "volume_24h": coin["quotes"]["USD"].get("volume_24h", 0),
                "market_cap": coin["quotes"]["USD"].get("market_cap", 0),
                "percent_change_1h": coin["quotes"]["USD"].get("percent_change_1h", 0),
                "percent_change_24h": coin["quotes"]["USD"].get("percent_change_24h", 0),
                "percent_change_7d": coin["quotes"]["USD"].get("percent_change_7d", 0),
                "timestamp": current_timestamp
            }
            
            # ✅ UPSERT : update_one avec upsert=True
            # Cherche par symbol, remplace si existe, insère si n'existe pas
            result = collection.update_one(
                {"symbol": coin["symbol"]},  # Critère de recherche
                {"$set": doc},                # Données à mettre à jour
                upsert=True                   # Insère si n'existe pas
            )
            
            if result.upserted_id:
                inserted_count += 1
                print(f"[CELERY] ➕ {coin['symbol']:6s} = ${doc['price_usd']:>12.4f} (NOUVEAU)")
            else:
                updated_count += 1
                print(f"[CELERY] 🔄 {coin['symbol']:6s} = ${doc['price_usd']:>12.4f} (MIS À JOUR)")
            
            # ✅ NOUVEAU : INSERT dans price_history (historique complet)
            history_collection.insert_one(doc.copy())
            history_count += 1

        # 4. Statistiques finales
        total_docs = collection.count_documents({})
        total_history = history_collection.count_documents({})
        
        print("\n" + "="*60)
        print("[CELERY] Collecte terminée avec succès!")
        print("[CELERY] Résumé:")
        print(f"[CELERY]    - Nouvelles cryptos: {inserted_count}")
        print(f"[CELERY]    - Cryptos mises à jour: {updated_count}")
        print(f"[CELERY]    - Total en DB (prices): {total_docs}")
        print(f"[CELERY]    - Total historique (price_history): {total_history}")
        print("="*60 + "\n")

        return f"Succès : {inserted_count} nouvelles, {updated_count} mises à jour, {history_count} historique"

    except Exception as exc:
        print(f"[CELERY] Erreur: {exc}")
        import traceback
        traceback.print_exc()
        raise self.retry(exc=exc)


# ===== TÂCHE DE VÉRIFICATION DES ALERTES =====

@app.task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 30})
def check_alerts_task(self):
    """
    Tâche Celery pour vérifier les alertes de prix.
    """
    from datetime import datetime
    
    print("\n" + "="*60)
    print("[CELERY] 🔔 Début de la vérification des alertes...")
    print("="*60)
    
    try:
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        alerts_collection = db["alerts"]
        prices_collection = db["prices"]
        
        active_alerts = list(alerts_collection.find({"is_active": True}))
        
        print(f"[CELERY] 📊 {len(active_alerts)} alerte(s) active(s) à vérifier")
        
        if len(active_alerts) == 0:
            return "ℹ️ Aucune alerte active à vérifier"
        
        triggered_count = 0
        
        for alert in active_alerts:
            crypto_symbol = alert["crypto_symbol"]
            target_price = alert["target_price"]
            alert_type = alert["alert_type"]
            
            # Récupérer le dernier prix
            latest_price_doc = prices_collection.find_one(
                {"symbol": crypto_symbol.upper()},
                sort=[("timestamp", -1)]
            )
            
            if not latest_price_doc or "price_usd" not in latest_price_doc:
                print(f"[CELERY] ⚠️ Prix non trouvé pour {crypto_symbol}")
                continue
            
            current_price = latest_price_doc["price_usd"]
            
            should_trigger = False
            
            if alert_type == "above" and current_price >= target_price:
                should_trigger = True
            elif alert_type == "below" and current_price <= target_price:
                should_trigger = True
            
            if should_trigger:
                alerts_collection.update_one(
                    {"_id": alert["_id"]},
                    {
                        "$set": {
                            "is_active": False,
                            "triggered_at": datetime.utcnow(),
                            "triggered_price": current_price
                        }
                    }
                )
                
                triggered_count += 1
                print(f"[CELERY] 🔔 ALERTE DÉCLENCHÉE!")
                print(f"[CELERY]    - Crypto: {crypto_symbol}")
                print(f"[CELERY]    - Type: {alert_type}")
                print(f"[CELERY]    - Prix cible: ${target_price:.2f}")
                print(f"[CELERY]    - Prix actuel: ${current_price:.2f}")
        
        print(f"\n[CELERY] ✅ Vérification terminée: {triggered_count} alerte(s) déclenchée(s)")
        return f"✅ {triggered_count}/{len(active_alerts)} alertes déclenchées"
        
    except Exception as exc:
        print(f"[CELERY] ❌ Erreur: {exc}")
        raise self.retry(exc=exc)


# ===== PLANIFICATION DES TÂCHES =====

app.conf.beat_schedule = {
    'collect-every-minute': {
        'task': 'tasks.fetch_and_store_task',
        'schedule': crontab(minute='*/1'),  # Toutes les minutes
    },
    'check-alerts-every-5-minutes': {
        'task': 'tasks.check_alerts_task',
        'schedule': crontab(minute='*/5'),  # Toutes les 5 minutes
    },
}

app.conf.timezone = 'UTC'

app.conf.update(
    result_expires=3600,
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    enable_utc=True,
)