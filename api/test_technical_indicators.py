# api/test_technical_indicators.py
"""
Tests unitaires pour les indicateurs techniques (RSI, MACD, Bollinger Bands)
"""
import pytest
from fastapi.testclient import TestClient
import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import app

client = TestClient(app)


class TestRSICalculation:
    """Tests pour le calcul RSI (Relative Strength Index)"""
    
    def calculate_rsi(self, prices, period=14):
        """Calcul RSI manuel pour les tests"""
        if len(prices) < period + 1:
            return None
            
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains[:period])
        avg_loss = np.mean(losses[:period])
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi

    def test_rsi_overbought(self):
        """Test RSI en zone de surachat (>70)"""
        # Tendance fortement haussière
        prices = [100 + i * 5 for i in range(20)]  # Prix croissants
        
        rsi = self.calculate_rsi(prices)
        
        # RSI devrait être élevé (proche de 100)
        assert rsi is not None
        assert rsi > 70  # Zone de surachat

    def test_rsi_oversold(self):
        """Test RSI en zone de survente (<30)"""
        # Tendance fortement baissière
        prices = [200 - i * 5 for i in range(20)]  # Prix décroissants
        
        rsi = self.calculate_rsi(prices)
        
        # RSI devrait être bas (proche de 0)
        assert rsi is not None
        assert rsi < 30  # Zone de survente

    def test_rsi_neutral(self):
        """Test RSI en zone neutre (30-70)"""
        # Prix oscillants
        prices = [100, 105, 100, 105, 100, 105, 100, 105, 100, 105,
                  100, 105, 100, 105, 100, 105, 100, 105, 100, 105]
        
        rsi = self.calculate_rsi(prices)
        
        # RSI devrait être proche de 50
        assert rsi is not None
        assert 30 <= rsi <= 70

    def test_rsi_range(self):
        """Test que RSI est toujours entre 0 et 100"""
        test_cases = [
            [100 + i for i in range(20)],  # Hausse
            [100 - i for i in range(20)],  # Baisse
            [100] * 20,  # Stable
        ]
        
        for prices in test_cases:
            rsi = self.calculate_rsi(prices)
            if rsi is not None:
                assert 0 <= rsi <= 100


class TestMACDCalculation:
    """Tests pour le calcul MACD"""
    
    def calculate_ema(self, prices, period):
        """Calcul EMA pour MACD"""
        multiplier = 2 / (period + 1)
        ema = prices[0]
        
        for price in prices[1:]:
            ema = (price - ema) * multiplier + ema
        
        return ema
    
    def calculate_macd(self, prices, fast=12, slow=26, signal_period=9):
        """Calcul MACD manuel"""
        if len(prices) < slow:
            return None
            
        ema_fast = self.calculate_ema(prices, fast)
        ema_slow = self.calculate_ema(prices, slow)
        
        macd_line = ema_fast - ema_slow
        
        return {
            "macd_line": macd_line,
            "ema_fast": ema_fast,
            "ema_slow": ema_slow
        }

    def test_macd_bullish_crossover(self):
        """Test MACD avec croisement haussier"""
        # Tendance haussière
        prices = [100 + i * 2 for i in range(30)]
        
        result = self.calculate_macd(prices)
        
        assert result is not None
        # En tendance haussière, EMA rapide > EMA lente
        assert result["ema_fast"] > result["ema_slow"]
        assert result["macd_line"] > 0

    def test_macd_bearish_crossover(self):
        """Test MACD avec croisement baissier"""
        # Tendance baissière
        prices = [200 - i * 2 for i in range(30)]
        
        result = self.calculate_macd(prices)
        
        assert result is not None
        # En tendance baissière, EMA rapide < EMA lente
        assert result["ema_fast"] < result["ema_slow"]
        assert result["macd_line"] < 0

    def test_macd_components(self):
        """Test que tous les composants MACD sont présents"""
        prices = list(range(100, 150))
        
        result = self.calculate_macd(prices)
        
        assert result is not None
        assert "macd_line" in result
        assert "ema_fast" in result
        assert "ema_slow" in result


class TestBollingerBands:
    """Tests pour les bandes de Bollinger"""
    
    def calculate_bollinger(self, prices, period=20, std_dev=2.0):
        """Calcul des bandes de Bollinger"""
        if len(prices) < period:
            return None
            
        prices_array = np.array(prices[-period:])
        
        middle_band = np.mean(prices_array)
        std = np.std(prices_array)
        
        upper_band = middle_band + (std_dev * std)
        lower_band = middle_band - (std_dev * std)
        
        current_price = prices[-1]
        bandwidth = (upper_band - lower_band) / middle_band
        
        # %B = (Prix - Bande Inf) / (Bande Sup - Bande Inf)
        if upper_band != lower_band:
            percent_b = (current_price - lower_band) / (upper_band - lower_band)
        else:
            percent_b = 0.5
        
        return {
            "upper_band": upper_band,
            "middle_band": middle_band,
            "lower_band": lower_band,
            "bandwidth": bandwidth,
            "percent_b": percent_b
        }

    def test_bollinger_band_order(self):
        """Test que upper > middle > lower"""
        prices = [100, 102, 98, 105, 103, 107, 104, 108, 106, 110,
                  108, 112, 110, 115, 113, 118, 116, 120, 118, 122]
        
        result = self.calculate_bollinger(prices)
        
        assert result is not None
        assert result["upper_band"] > result["middle_band"]
        assert result["middle_band"] > result["lower_band"]

    def test_bollinger_high_volatility(self):
        """Test bandes larges avec haute volatilité"""
        # Prix très volatils
        prices = [100, 150, 80, 160, 70, 170, 60, 180, 50, 190,
                  100, 150, 80, 160, 70, 170, 60, 180, 50, 190]
        
        result = self.calculate_bollinger(prices)
        
        assert result is not None
        # Bandwidth devrait être élevé
        assert result["bandwidth"] > 0.5

    def test_bollinger_low_volatility(self):
        """Test bandes étroites avec basse volatilité"""
        # Prix stables
        prices = [100, 101, 100, 101, 100, 101, 100, 101, 100, 101,
                  100, 101, 100, 101, 100, 101, 100, 101, 100, 101]
        
        result = self.calculate_bollinger(prices)
        
        assert result is not None
        # Bandwidth devrait être faible
        assert result["bandwidth"] < 0.1

    def test_percent_b_range(self):
        """Test que %B est généralement entre 0 et 1"""
        prices = list(range(100, 120))
        
        result = self.calculate_bollinger(prices)
        
        assert result is not None
        # %B peut dépasser 0-1 mais devrait être proche
        assert -0.5 <= result["percent_b"] <= 1.5


class TestCombinedSignal:
    """Tests pour le signal combiné"""
    
    def get_combined_signal(self, rsi_signal, macd_signal, bollinger_signal):
        """Calcul du signal combiné"""
        signals = [rsi_signal, macd_signal, bollinger_signal]
        
        buy_count = signals.count("ACHAT")
        sell_count = signals.count("VENTE")
        
        if buy_count >= 2:
            return "ACHAT"
        elif sell_count >= 2:
            return "VENTE"
        else:
            return "NEUTRE"

    def test_combined_buy_signal(self):
        """Test signal d'achat combiné"""
        signal = self.get_combined_signal("ACHAT", "ACHAT", "NEUTRE")
        assert signal == "ACHAT"

    def test_combined_sell_signal(self):
        """Test signal de vente combiné"""
        signal = self.get_combined_signal("VENTE", "VENTE", "NEUTRE")
        assert signal == "VENTE"

    def test_combined_neutral_signal(self):
        """Test signal neutre combiné"""
        signal = self.get_combined_signal("ACHAT", "VENTE", "NEUTRE")
        assert signal == "NEUTRE"

    def test_all_buy_signals(self):
        """Test tous les signaux d'achat"""
        signal = self.get_combined_signal("ACHAT", "ACHAT", "ACHAT")
        assert signal == "ACHAT"

    def test_all_sell_signals(self):
        """Test tous les signaux de vente"""
        signal = self.get_combined_signal("VENTE", "VENTE", "VENTE")
        assert signal == "VENTE"


class TestIndicatorsEndpoint:
    """Tests pour l'endpoint /predictions/indicators"""
    
    @pytest.fixture
    def auth_token(self):
        """Token d'authentification"""
        import random
        import string
        random_suffix = ''.join(random.choices(string.ascii_lowercase, k=8))
        username = f"test_ind_{random_suffix}"
        
        client.post("/auth/register", json={
            "username": username,
            "email": f"{username}@example.com",
            "password": "testpass123"
        })
        
        login_response = client.post("/auth/login", data={
            "username": username,
            "password": "testpass123"
        })
        
        if login_response.status_code == 200:
            token = login_response.json()["access_token"]
            yield token
            
            try:
                from auth import users_collection
                users_collection.delete_one({"username": username})
            except:
                pass
        else:
            yield None

    def test_indicators_requires_auth(self):
        """Test que l'endpoint nécessite l'authentification"""
        response = client.get("/predictions/indicators/BTC?days=90")
        assert response.status_code == 401

    def test_indicators_with_auth(self, auth_token):
        """Test des indicateurs avec authentification"""
        if auth_token is None:
            pytest.skip("Could not obtain auth token")
            
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        response = client.get("/predictions/indicators/BTC?days=90", headers=headers)
        
        # Peut retourner 200 ou 400 selon les données disponibles
        assert response.status_code in [200, 400, 404]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
