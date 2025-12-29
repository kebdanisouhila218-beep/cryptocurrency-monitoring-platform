# scripts/generate_test_data.py
# Script pour générer des données de test dans price_history

import time
import random
from datetime import datetime, timedelta
from pymongo import MongoClient

# Configuration MongoDB
MONGO_URI = "mongodb://127.0.0.1:27017/"
DB_NAME = "crypto_db"

# Cryptos populaires avec prix de base approximatifs
CRYPTOS = [
    {"symbol": "BTC", "name": "Bitcoin", "base_price": 94000},
    {"symbol": "ETH", "name": "Ethereum", "base_price": 3300},
    {"symbol": "BNB", "name": "Binance Coin", "base_price": 690},
    {"symbol": "SOL", "name": "Solana", "base_price": 185},
    {"symbol": "XRP", "name": "Ripple", "base_price": 2.1},
    {"symbol": "ADA", "name": "Cardano", "base_price": 0.87},
    {"symbol": "DOGE", "name": "Dogecoin", "base_price": 0.31},
    {"symbol": "DOT", "name": "Polkadot", "base_price": 7.0},
    {"symbol": "MATIC", "name": "Polygon", "base_price": 0.48},
    {"symbol": "LTC", "name": "Litecoin", "base_price": 102},
    {"symbol": "AVAX", "name": "Avalanche", "base_price": 38},
    {"symbol": "LINK", "name": "Chainlink", "base_price": 22},
    {"symbol": "ATOM", "name": "Cosmos", "base_price": 6.5},
    {"symbol": "UNI", "name": "Uniswap", "base_price": 13},
    {"symbol": "XLM", "name": "Stellar", "base_price": 0.35},
]

def generate_realistic_price(base_price, volatility=0.02):
    """Génère un prix réaliste avec une légère variation"""
    change = random.uniform(-volatility, volatility)
    return base_price * (1 + change)

def generate_test_data(days=30, interval_minutes=60):
    """
    Génère des données de test pour price_history
    
    Args:
        days: Nombre de jours d'historique à générer
        interval_minutes: Intervalle entre chaque point (60 = 1 point/heure)
    """
    print("="*60)
    print("🔧 GÉNÉRATION DE DONNÉES DE TEST")
    print("="*60)
    
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db["price_history"]
    
    # Calculer le nombre de points
    points_per_day = 24 * 60 // interval_minutes
    total_points = days * points_per_day
    
    print(f"📊 Configuration:")
    print(f"   - Jours d'historique: {days}")
    print(f"   - Intervalle: {interval_minutes} minutes")
    print(f"   - Points par jour: {points_per_day}")
    print(f"   - Total points par crypto: {total_points}")
    print(f"   - Cryptos: {len(CRYPTOS)}")
    print(f"   - Total documents à insérer: {total_points * len(CRYPTOS)}")
    print()
    
    # Date de départ (il y a X jours)
    start_date = datetime.utcnow() - timedelta(days=days)
    
    documents = []
    
    for crypto in CRYPTOS:
        print(f"📈 Génération pour {crypto['symbol']}...", end=" ")
        
        current_price = crypto["base_price"]
        current_time = start_date
        
        for i in range(total_points):
            # Variation réaliste du prix
            current_price = generate_realistic_price(current_price, volatility=0.005)
            
            # Créer le document
            timestamp = current_time.timestamp()
            doc = {
                "coin_id": f"{crypto['symbol'].lower()}-{crypto['name'].lower().replace(' ', '-')}",
                "symbol": crypto["symbol"],
                "name": crypto["name"],
                "price_usd": current_price,
                "volume_24h": random.uniform(1000000, 100000000),
                "market_cap": current_price * random.uniform(1000000, 100000000),
                "percent_change_1h": random.uniform(-2, 2),
                "percent_change_24h": random.uniform(-5, 5),
                "percent_change_7d": random.uniform(-10, 10),
                "timestamp": timestamp
            }
            
            documents.append(doc)
            
            # Avancer dans le temps
            current_time += timedelta(minutes=interval_minutes)
        
        print(f"✅ {total_points} points")
    
    # Insérer tous les documents
    print()
    print(f"💾 Insertion de {len(documents)} documents dans MongoDB...")
    
    # Insérer par lots de 1000
    batch_size = 1000
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i+batch_size]
        collection.insert_many(batch)
        print(f"   ✅ Lot {i//batch_size + 1}: {len(batch)} documents insérés")
    
    # Statistiques finales
    total_count = collection.count_documents({})
    
    print()
    print("="*60)
    print("✅ GÉNÉRATION TERMINÉE")
    print("="*60)
    print(f"📊 Total documents dans price_history: {total_count}")
    print()
    print("🔍 Vérification par crypto:")
    for crypto in CRYPTOS:
        count = collection.count_documents({"symbol": crypto["symbol"]})
        print(f"   - {crypto['symbol']}: {count} points")
    
    print()
    print("✅ Vous pouvez maintenant tester les prévisions sur http://localhost:3000/predictions")
    
    client.close()

if __name__ == "__main__":
    print()
    print("Ce script va générer des données de test pour price_history.")
    print()
    
    try:
        days = int(input("Nombre de jours d'historique à générer (défaut: 30): ") or "30")
        interval = int(input("Intervalle en minutes entre chaque point (défaut: 60): ") or "60")
    except ValueError:
        days = 30
        interval = 60
    
    generate_test_data(days=days, interval_minutes=interval)
