# api/services/technical_indicators.py
"""
Service de calcul des indicateurs techniques avancés pour l'analyse crypto.

Indicateurs implémentés :
- RSI (Relative Strength Index) - 14 périodes
- MACD (Moving Average Convergence Divergence) - 12/26/9 périodes
- Bollinger Bands - 20 périodes, 2 écarts-types
- Signaux d'achat/vente automatiques
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta


def calculate_rsi(prices: List[float], period: int = 14) -> Tuple[float, str, List[float]]:
    """
    Calcule le RSI (Relative Strength Index).
    
    Formule :
    RSI = 100 - (100 / (1 + RS))
    où RS = Moyenne des gains / Moyenne des pertes
    
    Args:
        prices: Liste des prix (du plus ancien au plus récent)
        period: Période de calcul (défaut: 14)
    
    Returns:
        Tuple (RSI actuel, Signal, Série complète RSI)
        
    Interprétation :
        RSI > 70 → Surachat (Signal VENTE)
        RSI < 30 → Survente (Signal ACHAT)
        30 ≤ RSI ≤ 70 → Neutre
    """
    if len(prices) < period + 1:
        return 50.0, "NEUTRE", []
    
    # Convertir en pandas Series pour faciliter les calculs
    prices_series = pd.Series(prices)
    
    # Calculer les variations de prix
    delta = prices_series.diff()
    
    # Séparer les gains et les pertes
    gains = delta.where(delta > 0, 0.0)
    losses = -delta.where(delta < 0, 0.0)
    
    # Calculer les moyennes mobiles exponentielles
    avg_gains = gains.ewm(span=period, adjust=False).mean()
    avg_losses = losses.ewm(span=period, adjust=False).mean()
    
    # Calculer le RS (Relative Strength)
    rs = avg_gains / avg_losses.replace(0, np.nan)
    rs = rs.fillna(0)
    
    # Calculer le RSI
    rsi_series = 100 - (100 / (1 + rs))
    rsi_series = rsi_series.fillna(50)
    
    # Valeur actuelle
    current_rsi = float(rsi_series.iloc[-1])
    
    # Déterminer le signal
    if current_rsi > 70:
        signal = "VENTE"  # Surachat
    elif current_rsi < 30:
        signal = "ACHAT"  # Survente
    else:
        signal = "NEUTRE"
    
    return current_rsi, signal, rsi_series.tolist()


def calculate_macd(
    prices: List[float],
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9
) -> Dict:
    """
    Calcule le MACD (Moving Average Convergence Divergence).
    
    Composants :
    - MACD Line = EMA(12) - EMA(26)
    - Signal Line = EMA(9) du MACD
    - Histogramme = MACD - Signal
    
    Args:
        prices: Liste des prix
        fast_period: Période EMA rapide (défaut: 12)
        slow_period: Période EMA lente (défaut: 26)
        signal_period: Période Signal (défaut: 9)
    
    Returns:
        Dict avec macd, signal, histogram, et signal d'achat/vente
        
    Interprétation :
        MACD > Signal → Signal ACHAT (momentum haussier)
        MACD < Signal → Signal VENTE (momentum baissier)
        Histogramme > 0 → Force haussière
        Histogramme < 0 → Force baissière
    """
    if len(prices) < slow_period + signal_period:
        return {
            "macd": 0.0,
            "signal": 0.0,
            "histogram": 0.0,
            "trading_signal": "NEUTRE",
            "macd_series": [],
            "signal_series": [],
            "histogram_series": []
        }
    
    prices_series = pd.Series(prices)
    
    # Calculer les EMA rapide et lente
    ema_fast = prices_series.ewm(span=fast_period, adjust=False).mean()
    ema_slow = prices_series.ewm(span=slow_period, adjust=False).mean()
    
    # Calculer la ligne MACD
    macd_line = ema_fast - ema_slow
    
    # Calculer la ligne de signal (EMA du MACD)
    signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
    
    # Calculer l'histogramme
    histogram = macd_line - signal_line
    
    # Valeurs actuelles
    current_macd = float(macd_line.iloc[-1])
    current_signal = float(signal_line.iloc[-1])
    current_histogram = float(histogram.iloc[-1])
    
    # Déterminer le signal de trading
    if current_macd > current_signal and current_histogram > 0:
        trading_signal = "ACHAT"  # Croisement haussier
    elif current_macd < current_signal and current_histogram < 0:
        trading_signal = "VENTE"  # Croisement baissier
    else:
        trading_signal = "NEUTRE"
    
    return {
        "macd": current_macd,
        "signal": current_signal,
        "histogram": current_histogram,
        "trading_signal": trading_signal,
        "macd_series": macd_line.tolist(),
        "signal_series": signal_line.tolist(),
        "histogram_series": histogram.tolist()
    }


def calculate_bollinger_bands(
    prices: List[float],
    period: int = 20,
    num_std: float = 2.0
) -> Dict:
    """
    Calcule les Bandes de Bollinger.
    
    Composants :
    - Bande du milieu = SMA(20)
    - Bande supérieure = SMA(20) + 2 × σ
    - Bande inférieure = SMA(20) - 2 × σ
    
    Args:
        prices: Liste des prix
        period: Période de calcul (défaut: 20)
        num_std: Nombre d'écarts-types (défaut: 2.0)
    
    Returns:
        Dict avec upper, middle, lower, largeur, et signal
        
    Interprétation :
        Prix proche bande supérieure → Surachat (Signal VENTE)
        Prix proche bande inférieure → Survente (Signal ACHAT)
        Largeur faible → Faible volatilité (consolidation)
        Largeur élevée → Forte volatilité (breakout possible)
    """
    if len(prices) < period:
        return {
            "upper": 0.0,
            "middle": 0.0,
            "lower": 0.0,
            "width": 0.0,
            "width_percent": 0.0,
            "percent_b": 0.5,
            "trading_signal": "NEUTRE",
            "upper_series": [],
            "middle_series": [],
            "lower_series": []
        }
    
    prices_series = pd.Series(prices)
    
    # Calculer la bande du milieu (SMA)
    middle_band = prices_series.rolling(window=period).mean()
    
    # Calculer l'écart-type
    std_dev = prices_series.rolling(window=period).std()
    
    # Calculer les bandes supérieure et inférieure
    upper_band = middle_band + (num_std * std_dev)
    lower_band = middle_band - (num_std * std_dev)
    
    # Valeurs actuelles
    current_price = prices[-1]
    current_upper = float(upper_band.iloc[-1])
    current_middle = float(middle_band.iloc[-1])
    current_lower = float(lower_band.iloc[-1])
    
    # Largeur des bandes (indicateur de volatilité)
    width = current_upper - current_lower
    width_percent = (width / current_middle) * 100 if current_middle > 0 else 0
    
    # %B : Position du prix dans les bandes (0 = bande inf, 1 = bande sup)
    band_range = current_upper - current_lower
    percent_b = (current_price - current_lower) / band_range if band_range > 0 else 0.5
    
    # Déterminer le signal de trading
    if percent_b > 0.9:
        trading_signal = "VENTE"  # Prix proche de la bande supérieure
    elif percent_b < 0.1:
        trading_signal = "ACHAT"  # Prix proche de la bande inférieure
    else:
        trading_signal = "NEUTRE"
    
    return {
        "upper": current_upper,
        "middle": current_middle,
        "lower": current_lower,
        "width": width,
        "width_percent": width_percent,
        "percent_b": percent_b,
        "trading_signal": trading_signal,
        "upper_series": upper_band.fillna(0).tolist(),
        "middle_series": middle_band.fillna(0).tolist(),
        "lower_series": lower_band.fillna(0).tolist()
    }


def generate_combined_signal(rsi_signal: str, macd_signal: str, bb_signal: str) -> Dict:
    """
    Génère un signal combiné basé sur les 3 indicateurs.
    
    Logique :
    - ACHAT FORT : 3 indicateurs disent ACHAT
    - ACHAT : 2 indicateurs disent ACHAT
    - VENTE FORTE : 3 indicateurs disent VENTE
    - VENTE : 2 indicateurs disent VENTE
    - NEUTRE : Signaux contradictoires
    
    Args:
        rsi_signal: Signal du RSI
        macd_signal: Signal du MACD
        bb_signal: Signal des Bollinger Bands
    
    Returns:
        Dict avec signal combiné et force
    """
    signals = [rsi_signal, macd_signal, bb_signal]
    
    achat_count = signals.count("ACHAT")
    vente_count = signals.count("VENTE")
    
    if achat_count == 3:
        return {
            "signal": "ACHAT FORT",
            "force": 100,
            "emoji": "🟢🟢🟢",
            "description": "Les 3 indicateurs confirment un signal d'achat"
        }
    elif achat_count == 2:
        return {
            "signal": "ACHAT",
            "force": 70,
            "emoji": "🟢🟢",
            "description": "2 indicateurs sur 3 suggèrent un achat"
        }
    elif vente_count == 3:
        return {
            "signal": "VENTE FORTE",
            "force": 100,
            "emoji": "🔴🔴🔴",
            "description": "Les 3 indicateurs confirment un signal de vente"
        }
    elif vente_count == 2:
        return {
            "signal": "VENTE",
            "force": 70,
            "emoji": "🔴🔴",
            "description": "2 indicateurs sur 3 suggèrent une vente"
        }
    else:
        return {
            "signal": "NEUTRE",
            "force": 50,
            "emoji": "🟡",
            "description": "Signaux contradictoires, attendre confirmation"
        }


def calculate_all_indicators(prices: List[float]) -> Dict:
    """
    Calcule tous les indicateurs techniques.
    
    Args:
        prices: Liste des prix (du plus ancien au plus récent)
    
    Returns:
        Dict complet avec tous les indicateurs et signaux
    """
    # RSI
    rsi_value, rsi_signal, rsi_series = calculate_rsi(prices, period=14)
    
    # MACD
    macd_data = calculate_macd(prices, fast_period=12, slow_period=26, signal_period=9)
    
    # Bollinger Bands
    bb_data = calculate_bollinger_bands(prices, period=20, num_std=2.0)
    
    # Signal combiné
    combined = generate_combined_signal(rsi_signal, macd_data["trading_signal"], bb_data["trading_signal"])
    
    return {
        "rsi": {
            "value": round(rsi_value, 2),
            "signal": rsi_signal,
            "series": rsi_series[-100:] if len(rsi_series) > 100 else rsi_series,  # Limiter pour performance
            "interpretation": get_rsi_interpretation(rsi_value)
        },
        "macd": {
            "macd": round(macd_data["macd"], 4),
            "signal": round(macd_data["signal"], 4),
            "histogram": round(macd_data["histogram"], 4),
            "trading_signal": macd_data["trading_signal"],
            "macd_series": macd_data["macd_series"][-100:] if len(macd_data["macd_series"]) > 100 else macd_data["macd_series"],
            "signal_series": macd_data["signal_series"][-100:] if len(macd_data["signal_series"]) > 100 else macd_data["signal_series"],
            "histogram_series": macd_data["histogram_series"][-100:] if len(macd_data["histogram_series"]) > 100 else macd_data["histogram_series"],
            "interpretation": get_macd_interpretation(macd_data)
        },
        "bollinger_bands": {
            "upper": round(bb_data["upper"], 2),
            "middle": round(bb_data["middle"], 2),
            "lower": round(bb_data["lower"], 2),
            "width": round(bb_data["width"], 2),
            "width_percent": round(bb_data["width_percent"], 2),
            "percent_b": round(bb_data["percent_b"], 4),
            "trading_signal": bb_data["trading_signal"],
            "upper_series": bb_data["upper_series"][-100:] if len(bb_data["upper_series"]) > 100 else bb_data["upper_series"],
            "middle_series": bb_data["middle_series"][-100:] if len(bb_data["middle_series"]) > 100 else bb_data["middle_series"],
            "lower_series": bb_data["lower_series"][-100:] if len(bb_data["lower_series"]) > 100 else bb_data["lower_series"],
            "interpretation": get_bb_interpretation(bb_data)
        },
        "combined_signal": combined
    }


def get_rsi_interpretation(rsi: float) -> str:
    """Retourne une interprétation textuelle du RSI"""
    if rsi > 70:
        return f"Surachat ({rsi:.1f} > 70) - Possible correction baissière"
    elif rsi < 30:
        return f"Survente ({rsi:.1f} < 30) - Possible rebond haussier"
    elif rsi > 50:
        return f"Zone neutre ({rsi:.1f}) - Légère force haussière"
    else:
        return f"Zone neutre ({rsi:.1f}) - Légère faiblesse"


def get_macd_interpretation(macd_data: Dict) -> str:
    """Retourne une interprétation textuelle du MACD"""
    if macd_data["histogram"] > 0 and macd_data["trading_signal"] == "ACHAT":
        return "Momentum haussier fort - MACD > Signal"
    elif macd_data["histogram"] < 0 and macd_data["trading_signal"] == "VENTE":
        return "Momentum baissier fort - MACD < Signal"
    elif macd_data["histogram"] > 0:
        return "Momentum haussier - En attente de confirmation"
    else:
        return "Momentum baissier - En attente de confirmation"


def get_bb_interpretation(bb_data: Dict) -> str:
    """Retourne une interprétation textuelle des Bollinger Bands"""
    percent_b = bb_data["percent_b"]
    width_percent = bb_data["width_percent"]
    
    if percent_b > 0.9:
        return f"Prix proche bande sup ({percent_b:.1%}) - Surachat possible"
    elif percent_b < 0.1:
        return f"Prix proche bande inf ({percent_b:.1%}) - Survente possible"
    elif width_percent < 5:
        return f"Bandes étroites ({width_percent:.1f}%) - Faible volatilité, breakout imminent"
    elif width_percent > 15:
        return f"Bandes larges ({width_percent:.1f}%) - Forte volatilité"
    else:
        return f"Prix au milieu des bandes ({percent_b:.1%}) - Volatilité normale"
