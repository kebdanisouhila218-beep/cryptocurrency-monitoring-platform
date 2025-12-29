# api/services/prediction_service.py
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import numpy as np
from scipy import stats

# ===== CACHE POUR PERFORMANCE =====
_cache = {}
CACHE_DURATION = 300  # 5 minutes


def calculate_sma(prices: List[float], period: int) -> Optional[float]:
    """
    Calcule la moyenne mobile simple (SMA)
    
    Args:
        prices: Liste des prix (du plus ancien au plus récent)
        period: Période de la moyenne (ex: 7, 30, 90)
    
    Returns:
        Moyenne mobile ou None si pas assez de données
    """
    if len(prices) < period:
        return None
    
    recent_prices = prices[-period:]
    return sum(recent_prices) / period


def calculate_ema(prices: List[float], period: int) -> Optional[float]:
    """
    Calcule la moyenne mobile exponentielle (EMA)
    
    L'EMA donne plus de poids aux prix récents.
    
    Args:
        prices: Liste des prix (du plus ancien au plus récent)
        period: Période de la moyenne (ex: 7, 20, 50)
    
    Returns:
        EMA ou None si pas assez de données
    """
    if len(prices) < period:
        return None
    
    # Multiplicateur de lissage
    multiplier = 2 / (period + 1)
    
    # Commencer avec la SMA comme première valeur EMA
    ema = sum(prices[:period]) / period
    
    # Calculer l'EMA pour chaque prix suivant
    for price in prices[period:]:
        ema = (price * multiplier) + (ema * (1 - multiplier))
    
    return ema


def calculate_all_smas(prices: List[float]) -> Dict[str, Optional[float]]:
    """
    Calcule toutes les moyennes mobiles (7, 30, 90 jours)
    
    Returns:
        Dict avec sma_7, sma_30, sma_90
    """
    return {
        "sma_7": calculate_sma(prices, 7),
        "sma_30": calculate_sma(prices, 30),
        "sma_90": calculate_sma(prices, 90)
    }


def calculate_all_emas(prices: List[float]) -> Dict[str, Optional[float]]:
    """
    Calcule toutes les moyennes mobiles exponentielles (7, 20, 50 périodes)
    
    Returns:
        Dict avec ema_7, ema_20, ema_50
    """
    return {
        "ema_7": calculate_ema(prices, 7),
        "ema_20": calculate_ema(prices, 20),
        "ema_50": calculate_ema(prices, 50)
    }


def calculate_linear_regression(prices: List[float], days: int = 30) -> Dict:
    """
    Calcule la régression linéaire pour prédire la tendance
    
    Args:
        prices: Liste des prix historiques
        days: Nombre de jours à utiliser pour le calcul
    
    Returns:
        Dict avec pente, intercept, prévision 7j, 30j
    """
    if len(prices) < days:
        return {
            "error": "Pas assez de données",
            "slope": None,
            "trend": "unknown",
            "prediction_7d": 0,
            "prediction_30d": 0,
            "confidence": "low"
        }
    
    # Prendre les N derniers jours
    recent_prices = prices[-days:]
    
    # X = jours (0, 1, 2, ..., N-1)
    x = np.arange(len(recent_prices))
    y = np.array(recent_prices)
    
    # Calcul de la régression linéaire
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    
    # Prédiction pour les 7 et 30 prochains jours
    next_7_days = intercept + slope * (len(recent_prices) + 7)
    next_30_days = intercept + slope * (len(recent_prices) + 30)
    
    # Déterminer la tendance basée sur le pourcentage de changement
    current_price = recent_prices[-1]
    if current_price > 0:
        slope_percent = (slope / current_price) * 100
        if slope_percent > 0.5:
            trend = "bullish"  # Haussière
        elif slope_percent < -0.5:
            trend = "bearish"  # Baissière
        else:
            trend = "neutral"  # Neutre
    else:
        trend = "unknown"
    
    return {
        "slope": float(slope),
        "intercept": float(intercept),
        "r_squared": float(r_value ** 2),
        "trend": trend,
        "prediction_7d": float(max(0, next_7_days)),
        "prediction_30d": float(max(0, next_30_days)),
        "confidence": "high" if r_value ** 2 > 0.7 else "medium" if r_value ** 2 > 0.4 else "low"
    }


def calculate_weighted_prediction(prices: List[float], sma: Optional[float], ema: Optional[float], lr_prediction: float) -> float:
    """
    Calcule une prédiction pondérée combinant SMA, EMA et régression linéaire.
    
    Pondération: EMA 40%, LR 40%, SMA 20%
    """
    current_price = prices[-1] if prices else 0
    
    predictions = []
    weights = []
    
    if sma is not None:
        predictions.append(sma)
        weights.append(0.2)
    
    if ema is not None:
        predictions.append(ema)
        weights.append(0.4)
    
    if lr_prediction > 0:
        predictions.append(lr_prediction)
        weights.append(0.4)
    
    if not predictions:
        return current_price
    
    # Normaliser les poids
    total_weight = sum(weights)
    weights = [w / total_weight for w in weights]
    
    # Calculer la moyenne pondérée
    weighted_avg = sum(p * w for p, w in zip(predictions, weights))
    
    return weighted_avg


def get_price_change_percent(prices: List[float], period: int) -> Optional[float]:
    """
    Calcule le changement de prix en % sur une période
    
    Args:
        prices: Liste des prix
        period: Période (ex: 7, 30)
    
    Returns:
        Pourcentage de changement ou None
    """
    if len(prices) < period + 1:
        return None
    
    old_price = prices[-(period + 1)]
    current_price = prices[-1]
    
    if old_price == 0:
        return None
    
    return ((current_price - old_price) / old_price) * 100


def get_volatility(prices: List[float], period: int = 30) -> Optional[float]:
    """
    Calcule la volatilité (écart-type) des prix sur une période.
    
    Args:
        prices: Liste des prix
        period: Période de calcul
    
    Returns:
        Volatilité en pourcentage ou None
    """
    if len(prices) < period:
        return None
    
    recent_prices = prices[-period:]
    mean_price = sum(recent_prices) / len(recent_prices)
    
    if mean_price == 0:
        return None
    
    # Calculer les rendements quotidiens
    returns = []
    for i in range(1, len(recent_prices)):
        if recent_prices[i-1] != 0:
            daily_return = (recent_prices[i] - recent_prices[i-1]) / recent_prices[i-1]
            returns.append(daily_return)
    
    if not returns:
        return None
    
    # Écart-type des rendements * 100 pour avoir en %
    volatility = np.std(returns) * 100
    
    return float(volatility)
