# api/routes/predictions.py
from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_collection, get_price_history_collection
from auth import get_current_active_user
from services.prediction_service import (
    calculate_all_smas,
    calculate_all_emas,
    calculate_linear_regression,
    calculate_weighted_prediction,
    get_price_change_percent,
    get_volatility
)
from services.technical_indicators import calculate_all_indicators

router = APIRouter(prefix="/predictions", tags=["Prévisions"])


@router.get("")
async def list_available_predictions(
    current_user: dict = Depends(get_current_active_user)
):
    """
    📋 Liste des cryptos disponibles pour les prévisions.
    
    🔒 Route protégée - Nécessite authentification
    """
    available_cryptos = [
        {"symbol": "BTC", "name": "Bitcoin"},
        {"symbol": "ETH", "name": "Ethereum"},
        {"symbol": "BNB", "name": "Binance Coin"},
        {"symbol": "SOL", "name": "Solana"},
        {"symbol": "XRP", "name": "Ripple"},
        {"symbol": "ADA", "name": "Cardano"},
        {"symbol": "DOGE", "name": "Dogecoin"},
        {"symbol": "DOT", "name": "Polkadot"},
        {"symbol": "MATIC", "name": "Polygon"},
        {"symbol": "LTC", "name": "Litecoin"},
        {"symbol": "AVAX", "name": "Avalanche"},
        {"symbol": "LINK", "name": "Chainlink"},
        {"symbol": "ATOM", "name": "Cosmos"},
        {"symbol": "UNI", "name": "Uniswap"},
        {"symbol": "XLM", "name": "Stellar"}
    ]
    
    return {
        "success": True,
        "available_cryptos": available_cryptos,
        "user": current_user["username"]
    }


@router.get("/{crypto_symbol}")
async def get_predictions(
    crypto_symbol: str,
    days: int = Query(default=90, ge=1, le=365, description="Nombre de jours d'historique (1-365)"),
    current_user: dict = Depends(get_current_active_user),
    prices_collection = Depends(get_collection)
):
    """
    🔮 Prévisions complètes pour une crypto donnée.
    
    🔒 Route protégée - Nécessite authentification
    
    **Algorithmes utilisés:**
    - SMA (Simple Moving Average) - 7, 30, 90 jours
    - EMA (Exponential Moving Average) - 7, 20, 50 périodes
    - Régression Linéaire - prédiction 7j et 30j
    - Prédiction Pondérée (combinaison des 3 algorithmes)
    """
    try:
        symbol = crypto_symbol.upper()
        print(f"[PREDICTIONS] 🔮 Calcul des prévisions pour {symbol} ({days} jours)")
        
        # Récupérer l'historique depuis prices (données UPSERT)
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # D'abord essayer price_history si disponible
        try:
            history_collection = get_price_history_collection()
            historical_data = list(history_collection.find(
                {
                    "symbol": symbol,
                    "timestamp": {"$gte": cutoff_date.timestamp()}
                },
                {"price_usd": 1, "timestamp": 1, "_id": 0}
            ).sort("timestamp", 1))
            
            if historical_data:
                print(f"[PREDICTIONS] ✅ {len(historical_data)} points depuis price_history")
        except Exception as e:
            print(f"[PREDICTIONS] ⚠️ price_history non disponible: {e}")
            historical_data = []
        
        # Fallback sur prices si pas assez de données
        if len(historical_data) < 10:
            historical_data = list(prices_collection.find(
                {
                    "symbol": symbol,
                    "timestamp": {"$gte": cutoff_date.timestamp()}
                },
                {"price_usd": 1, "timestamp": 1, "_id": 0}
            ).sort("timestamp", 1))
            print(f"[PREDICTIONS] 📊 {len(historical_data)} points depuis prices")
        
        if not historical_data:
            raise HTTPException(status_code=404, detail=f"Aucune donnée pour {symbol}")
        
        # Extraire les prix
        prices = [float(d["price_usd"]) for d in historical_data]
        current_price = prices[-1]
        
        # Calculs SMA
        smas = calculate_all_smas(prices)
        
        # Calculs EMA
        emas = calculate_all_emas(prices)
        
        # Régression linéaire
        regression = calculate_linear_regression(prices, min(30, len(prices)))
        
        # Prédiction pondérée
        weighted_pred = calculate_weighted_prediction(
            prices,
            smas.get("sma_30"),
            emas.get("ema_20"),
            regression.get("prediction_7d", 0)
        )
        
        # Changements de prix
        changes = {
            "change_7d": get_price_change_percent(prices, 7),
            "change_30d": get_price_change_percent(prices, 30),
            "change_90d": get_price_change_percent(prices, 90)
        }
        
        # Volatilité
        volatility = get_volatility(prices, min(30, len(prices)))
        
        print(f"[PREDICTIONS] ✅ Prévisions calculées pour {symbol}")
        
        return {
            "success": True,
            "crypto_symbol": symbol,
            "current_price": round(current_price, 2),
            "data_points": len(prices),
            "days_analyzed": days,
            "moving_averages": {
                "sma_7": round(smas["sma_7"], 2) if smas["sma_7"] else None,
                "sma_30": round(smas["sma_30"], 2) if smas["sma_30"] else None,
                "sma_90": round(smas["sma_90"], 2) if smas["sma_90"] else None
            },
            "exponential_averages": {
                "ema_7": round(emas["ema_7"], 2) if emas["ema_7"] else None,
                "ema_20": round(emas["ema_20"], 2) if emas["ema_20"] else None,
                "ema_50": round(emas["ema_50"], 2) if emas["ema_50"] else None
            },
            "trend_analysis": {
                "trend": regression.get("trend", "unknown"),
                "confidence": regression.get("confidence", "low"),
                "r_squared": round(regression.get("r_squared", 0), 4),
                "prediction_7d": round(regression.get("prediction_7d", 0), 2),
                "prediction_30d": round(regression.get("prediction_30d", 0), 2)
            },
            "weighted_prediction": {
                "value": round(weighted_pred, 2),
                "algorithm": "Weighted Average (SMA: 20%, EMA: 40%, LR: 40%)",
                "confidence": regression.get("confidence", "low")
            },
            "volatility": round(volatility, 2) if volatility else None,
            "price_changes": {
                "7_days": round(changes["change_7d"], 2) if changes["change_7d"] else None,
                "30_days": round(changes["change_30d"], 2) if changes["change_30d"] else None,
                "90_days": round(changes["change_90d"], 2) if changes["change_90d"] else None
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[PREDICTIONS] ❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/indicators/{crypto_symbol}")
async def get_technical_indicators(
    crypto_symbol: str,
    days: int = Query(default=90, ge=30, le=365, description="Nombre de jours d'historique (30-365)"),
    current_user: dict = Depends(get_current_active_user)
):
    """
    🔬 Calcule les indicateurs techniques avancés (RSI, MACD, Bollinger Bands)
    
    🔒 Route protégée - Nécessite authentification
    
    **Indicateurs calculés:**
    - RSI (Relative Strength Index) - 14 périodes
    - MACD (Moving Average Convergence Divergence) - 12/26/9 périodes
    - Bollinger Bands - 20 périodes, 2 écarts-types
    - Signal combiné basé sur les 3 indicateurs
    """
    try:
        symbol = crypto_symbol.upper()
        print(f"[INDICATORS] 🔬 Calcul des indicateurs pour {symbol} ({days}j)...")
        
        # Récupérer l'historique
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        cutoff_timestamp = cutoff_date.timestamp()
        
        # Essayer price_history d'abord
        try:
            history_collection = get_price_history_collection()
            historical_data = list(history_collection.find(
                {
                    "symbol": symbol,
                    "timestamp": {"$gte": cutoff_timestamp}
                },
                {"price_usd": 1, "timestamp": 1, "_id": 0}
            ).sort("timestamp", 1))
            
            if historical_data:
                print(f"[INDICATORS] ✅ {len(historical_data)} points depuis price_history")
        except Exception as e:
            print(f"[INDICATORS] ⚠️ price_history non disponible: {e}")
            historical_data = []
        
        # Fallback sur prices
        if len(historical_data) < 50:
            prices_collection = get_collection()
            historical_data = list(prices_collection.find(
                {
                    "symbol": symbol,
                    "timestamp": {"$gte": cutoff_timestamp}
                },
                {"price_usd": 1, "timestamp": 1, "_id": 0}
            ).sort("timestamp", 1))
            print(f"[INDICATORS] 📊 {len(historical_data)} points depuis prices")
        
        if len(historical_data) < 50:
            return {
                "error": f"Données insuffisantes pour {symbol}",
                "message": f"Minimum 50 points requis, {len(historical_data)} disponibles",
                "crypto_symbol": symbol
            }
        
        # Extraire les prix
        prices = [float(h["price_usd"]) for h in historical_data]
        
        # Calculer tous les indicateurs
        indicators = calculate_all_indicators(prices)
        
        # Ajouter les métadonnées
        indicators["crypto_symbol"] = symbol
        indicators["current_price"] = round(prices[-1], 2)
        indicators["num_points"] = len(prices)
        indicators["period_days"] = days
        
        print(f"[INDICATORS] ✅ Indicateurs calculés pour {symbol}")
        print(f"[INDICATORS]    - RSI: {indicators['rsi']['value']} ({indicators['rsi']['signal']})")
        print(f"[INDICATORS]    - MACD: {indicators['macd']['trading_signal']}")
        print(f"[INDICATORS]    - BB: {indicators['bollinger_bands']['trading_signal']}")
        print(f"[INDICATORS]    - Signal combiné: {indicators['combined_signal']['signal']}")
        
        return indicators
    
    except Exception as e:
        print(f"[INDICATORS] ❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return {
            "error": str(e),
            "crypto_symbol": crypto_symbol.upper()
        }
