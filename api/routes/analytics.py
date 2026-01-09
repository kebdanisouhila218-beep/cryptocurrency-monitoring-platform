# api/routes/analytics.py - Routes pour visualisations avancées

from fastapi import APIRouter, Depends, Query, HTTPException
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pymongo import MongoClient
import os

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth import get_current_active_user

router = APIRouter(prefix="/analytics", tags=["Analytics"])

# Configuration MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://127.0.0.1:27017/")
DB_NAME = "crypto_db"

def get_db():
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    return client[DB_NAME]


@router.get("/available-cryptos")
async def get_available_cryptos(
    current_user: dict = Depends(get_current_active_user)
):
    """
    📋 Récupérer la liste des cryptomonnaies disponibles dans la base de données.
    
    🔒 Route protégée - Nécessite authentification
    
    **Retourne:**
    Liste des cryptos avec leur symbole et nom
    """
    print(f"[ANALYTICS] 📋 Liste des cryptos demandée")
    
    try:
        db = get_db()
        collection = db["price_history"]
        
        pipeline = [
            {"$group": {
                "_id": "$symbol",
                "name": {"$first": "$name"},
                "symbol": {"$first": "$symbol"},
                "count": {"$sum": 1}
            }},
            {"$match": {"count": {"$gte": 5}}},
            {"$sort": {"symbol": 1}},
            {"$project": {"_id": 0, "symbol": 1, "name": 1}}
        ]
        
        cryptos = list(collection.aggregate(pipeline))
        
        print(f"[ANALYTICS] ✅ {len(cryptos)} cryptos disponibles")
        
        return {
            "success": True,
            "count": len(cryptos),
            "cryptos": cryptos,
            "user": current_user["username"]
        }
    
    except Exception as e:
        print(f"[ANALYTICS] ❌ Erreur available-cryptos: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération des cryptos: {str(e)}"
        )


@router.get("/candlestick/{crypto_symbol}")
async def get_candlestick_data(
    crypto_symbol: str,
    interval: str = Query(default="1h", regex="^(5m|15m|30m|1h|4h|1d)$"),
    days: int = Query(default=7, ge=1, le=30),
    current_user: dict = Depends(get_current_active_user)
):
    """
    📈 Obtenir les données OHLC pour un graphique en chandeliers.
    
    🔒 Route protégée - Nécessite authentification
    
    **Paramètres:**
    - `crypto_symbol`: Symbole de la crypto (ex: BTC, ETH)
    - `interval`: Intervalle de temps (5m, 15m, 30m, 1h, 4h, 1d)
    - `days`: Nombre de jours d'historique (1-30, défaut: 7)
    """
    print(f"[ANALYTICS] 📊 Candlestick demandé pour {crypto_symbol} ({interval}, {days}j)")
    
    try:
        db = get_db()
        collection = db["price_history"]
        
        # Calculer la date de début
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        start_timestamp = start_date.timestamp()
        end_timestamp = end_date.timestamp()
        
        # Convertir l'intervalle en secondes
        interval_seconds = {
            "5m": 5 * 60,
            "15m": 15 * 60,
            "30m": 30 * 60,
            "1h": 60 * 60,
            "4h": 4 * 60 * 60,
            "1d": 24 * 60 * 60
        }[interval]
        
        # Récupérer les données brutes
        cursor = collection.find(
            {
                "symbol": crypto_symbol.upper(),
                "timestamp": {"$gte": start_timestamp, "$lte": end_timestamp}
            }
        ).sort("timestamp", 1)
        
        raw_data = list(cursor)
        
        if len(raw_data) < 5:
            raise HTTPException(
                status_code=400,
                detail=f"Pas assez de données pour {crypto_symbol} ({len(raw_data)} points, minimum 5 requis)"
            )
        
        # Grouper les données par intervalle pour calculer OHLC
        candles = {}
        
        for point in raw_data:
            ts = point["timestamp"]
            # Arrondir au début de l'intervalle
            interval_start = int(ts // interval_seconds) * interval_seconds
            
            if interval_start not in candles:
                candles[interval_start] = {
                    "timestamp": interval_start,
                    "open": point["price_usd"],
                    "high": point["price_usd"],
                    "low": point["price_usd"],
                    "close": point["price_usd"],
                    "volume": point.get("volume_24h", 0),
                    "count": 1
                }
            else:
                candle = candles[interval_start]
                candle["high"] = max(candle["high"], point["price_usd"])
                candle["low"] = min(candle["low"], point["price_usd"])
                candle["close"] = point["price_usd"]
                candle["volume"] = point.get("volume_24h", 0)
                candle["count"] += 1
        
        # Convertir en liste triée
        candlestick_data = []
        for ts in sorted(candles.keys()):
            candle = candles[ts]
            candlestick_data.append({
                "timestamp": datetime.utcfromtimestamp(candle["timestamp"]).isoformat() + "Z",
                "open": round(candle["open"], 2),
                "high": round(candle["high"], 2),
                "low": round(candle["low"], 2),
                "close": round(candle["close"], 2),
                "volume": round(candle["volume"], 0)
            })
        
        print(f"[ANALYTICS] ✅ {len(candlestick_data)} bougies générées pour {crypto_symbol}")
        
        return {
            "success": True,
            "crypto_symbol": crypto_symbol.upper(),
            "interval": interval,
            "days": days,
            "data_points": len(candlestick_data),
            "data": candlestick_data,
            "user": current_user["username"]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ANALYTICS] ❌ Erreur candlestick: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la génération des données OHLC: {str(e)}"
        )


@router.get("/heatmap")
async def get_heatmap_data(
    period: str = Query(default="24h", regex="^(1h|24h|7d|30d)$"),
    current_user: dict = Depends(get_current_active_user)
):
    """
    🔥 Obtenir les données pour une heatmap de performance.
    
    🔒 Route protégée - Nécessite authentification
    
    **Paramètres:**
    - `period`: Période de calcul (1h, 24h, 7d, 30d)
    """
    print(f"[ANALYTICS] 🔥 Heatmap demandée pour période: {period}")
    
    try:
        db = get_db()
        history_collection = db["price_history"]
        prices_collection = db["prices"]
        
        # Calculer la date de début selon la période
        period_hours = {
            "1h": 1,
            "24h": 24,
            "7d": 24 * 7,
            "30d": 24 * 30
        }[period]
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(hours=period_hours)
        start_timestamp = start_date.timestamp()
        
        # Récupérer toutes les cryptos avec leur prix actuel
        current_prices = list(prices_collection.find({}, {
            "_id": 0,
            "symbol": 1,
            "name": 1,
            "price_usd": 1,
            "volume_24h": 1,
            "market_cap": 1
        }))
        
        heatmap_data = []
        
        for crypto in current_prices:
            symbol = crypto["symbol"]
            current_price = crypto["price_usd"]
            
            # Récupérer le premier prix de la période
            first_price_doc = history_collection.find_one(
                {
                    "symbol": symbol,
                    "timestamp": {"$gte": start_timestamp}
                },
                sort=[("timestamp", 1)]
            )
            
            if not first_price_doc:
                # Utiliser le prix actuel si pas d'historique
                first_price = current_price
            else:
                first_price = first_price_doc["price_usd"]
            
            # Calculer la variation
            if first_price > 0:
                price_change = current_price - first_price
                price_change_percent = (price_change / first_price) * 100
            else:
                price_change = 0
                price_change_percent = 0
            
            heatmap_data.append({
                "symbol": symbol,
                "name": crypto.get("name", symbol),
                "current_price": round(current_price, 2),
                "first_price": round(first_price, 2),
                "price_change": round(price_change, 2),
                "price_change_percent": round(price_change_percent, 2),
                "volume_24h": crypto.get("volume_24h", 0),
                "market_cap": crypto.get("market_cap", 0)
            })
        
        # Trier par variation décroissante
        heatmap_data.sort(key=lambda x: x["price_change_percent"], reverse=True)
        
        print(f"[ANALYTICS] ✅ Heatmap générée avec {len(heatmap_data)} cryptos")
        
        return {
            "success": True,
            "period": period,
            "period_hours": period_hours,
            "data_points": len(heatmap_data),
            "data": heatmap_data,
            "user": current_user["username"]
        }
    
    except Exception as e:
        print(f"[ANALYTICS] ❌ Erreur heatmap: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la génération de la heatmap: {str(e)}"
        )


@router.post("/compare")
async def compare_cryptos(
    symbols: List[str],
    days: int = Query(default=7, ge=1, le=30),
    current_user: dict = Depends(get_current_active_user)
):
    """
    📊 Comparer plusieurs cryptos sur un même graphique.
    
    🔒 Route protégée - Nécessite authentification
    
    **Body:**
    ```json
    ["BTC", "ETH", "BNB"]
    ```
    
    **Retourne:**
    Données normalisées pour comparaison (base 100 au début)
    """
    print(f"[ANALYTICS] 📊 Comparaison de {len(symbols)} cryptos: {symbols}")
    
    try:
        db = get_db()
        collection = db["price_history"]
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        start_timestamp = start_date.timestamp()
        end_timestamp = end_date.timestamp()
        
        comparison_data = {}
        
        for symbol in symbols:
            cursor = collection.find(
                {
                    "symbol": symbol.upper(),
                    "timestamp": {"$gte": start_timestamp, "$lte": end_timestamp}
                },
                sort=[("timestamp", 1)]
            )
            
            data = list(cursor)
            
            if len(data) < 5:
                print(f"[ANALYTICS] ⚠️ Pas assez de données pour {symbol}")
                continue
            
            # Normaliser à base 100
            first_price = data[0]["price_usd"]
            
            normalized = []
            for point in data:
                normalized.append({
                    "timestamp": datetime.utcfromtimestamp(point["timestamp"]).isoformat() + "Z",
                    "value": round((point["price_usd"] / first_price) * 100, 2),
                    "price": round(point["price_usd"], 2)
                })
            
            comparison_data[symbol.upper()] = normalized
        
        print(f"[ANALYTICS] ✅ {len(comparison_data)} cryptos comparées")
        
        return {
            "success": True,
            "symbols": list(comparison_data.keys()),
            "days": days,
            "data": comparison_data,
            "user": current_user["username"]
        }
    
    except Exception as e:
        print(f"[ANALYTICS] ❌ Erreur comparaison: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la comparaison: {str(e)}"
        )


@router.get("/market-overview")
async def get_market_overview(
    current_user: dict = Depends(get_current_active_user)
):
    """
    📊 Vue d'ensemble du marché crypto.
    
    🔒 Route protégée - Nécessite authentification
    
    **Retourne:**
    - Total market cap
    - Nombre de cryptos en hausse/baisse
    - Top gainers et losers
    """
    print(f"[ANALYTICS] 📊 Market overview demandé")
    
    try:
        db = get_db()
        prices_collection = db["prices"]
        history_collection = db["price_history"]
        
        # Récupérer tous les prix actuels
        current_prices = list(prices_collection.find({}, {"_id": 0}))
        
        # Calculer les statistiques
        total_market_cap = sum(c.get("market_cap", 0) for c in current_prices)
        total_volume_24h = sum(c.get("volume_24h", 0) for c in current_prices)
        
        # Calculer les variations 24h
        start_timestamp = (datetime.utcnow() - timedelta(hours=24)).timestamp()
        
        gainers = 0
        losers = 0
        unchanged = 0
        
        for crypto in current_prices:
            symbol = crypto["symbol"]
            current_price = crypto["price_usd"]
            
            # Récupérer le prix il y a 24h
            old_price_doc = history_collection.find_one(
                {"symbol": symbol, "timestamp": {"$gte": start_timestamp}},
                sort=[("timestamp", 1)]
            )
            
            if old_price_doc:
                old_price = old_price_doc["price_usd"]
                if current_price > old_price:
                    gainers += 1
                elif current_price < old_price:
                    losers += 1
                else:
                    unchanged += 1
            else:
                unchanged += 1
        
        print(f"[ANALYTICS] ✅ Market overview: {gainers} gainers, {losers} losers")
        
        return {
            "success": True,
            "total_cryptos": len(current_prices),
            "total_market_cap": round(total_market_cap, 0),
            "total_volume_24h": round(total_volume_24h, 0),
            "gainers": gainers,
            "losers": losers,
            "unchanged": unchanged,
            "market_sentiment": "bullish" if gainers > losers else "bearish" if losers > gainers else "neutral",
            "user": current_user["username"]
        }
    
    except Exception as e:
        print(f"[ANALYTICS] ❌ Erreur market overview: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération de l'overview: {str(e)}"
        )
