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

# ===== TÂCHE DE VÉRIFICATION DES ALERTES =====

@app.task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 30})
def check_alerts_task(self):
    """
    Tâche Celery pour vérifier les alertes de prix.
    Compare les prix actuels avec les seuils d'alerte et déclenche les alertes.
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
        
        # Récupérer les alertes actives
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
            
            # Vérifier si l'alerte doit être déclenchée
            should_trigger = False
            
            if alert_type == "above" and current_price >= target_price:
                should_trigger = True
            elif alert_type == "below" and current_price <= target_price:
                should_trigger = True
            
            if should_trigger:
                # Déclencher l'alerte
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
        return f"✅ Vérification terminée: {triggered_count}/{len(active_alerts)} alertes déclenchées"
        
    except Exception as exc:
        print(f"[CELERY] ❌ Erreur: {exc}")
        raise self.retry(exc=exc)


# Planification : toutes les minutes
app.conf.beat_schedule = {
    'collect-every-minute': {
        'task': 'tasks.fetch_and_store_task',
        'schedule': crontab(minute='*/1'),
    },
    'check-alerts-every-5-minutes': {
        'task': 'tasks.check_alerts_task',
        'schedule': crontab(minute='*/5'),
    },
}

# Optionnel : timezone (par défaut UTC)
app.conf.timezone = 'UTC'