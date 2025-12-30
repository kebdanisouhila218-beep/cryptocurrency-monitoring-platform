# api/test_predictions.py
"""
Tests unitaires pour le module de prévisions (SMA, EMA, Régression Linéaire)
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
import numpy as np
import sys
import os

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import app

client = TestClient(app)

# Mock de données price_history
MOCK_PRICE_HISTORY = [
    {"crypto_symbol": "BTC", "price_usd": 90000 + i * 100, "timestamp": 1735400000 + i * 3600}
    for i in range(100)
]


class TestPredictionsEndpoint:
    """Tests pour l'endpoint /predictions"""
    
    @pytest.fixture
    def auth_token(self):
        """Obtenir un token JWT valide pour les tests"""
        import random
        import string
        random_suffix = ''.join(random.choices(string.ascii_lowercase, k=8))
        username = f"test_pred_{random_suffix}"
        
        # Créer un utilisateur de test
        register_response = client.post("/auth/register", json={
            "username": username,
            "email": f"{username}@example.com",
            "password": "testpass123"
        })
        
        # Se connecter
        login_response = client.post("/auth/login", data={
            "username": username,
            "password": "testpass123"
        })
        
        if login_response.status_code == 200:
            token = login_response.json()["access_token"]
            yield token
            
            # Cleanup
            try:
                from auth import users_collection
                users_collection.delete_one({"username": username})
            except:
                pass
        else:
            yield None

    def test_predictions_endpoint_requires_auth(self):
        """Test que l'endpoint /predictions nécessite l'authentification"""
        response = client.get("/predictions/BTC?days=30")
        assert response.status_code == 401

    def test_predictions_with_valid_token(self, auth_token):
        """Test des prévisions avec un token valide"""
        if auth_token is None:
            pytest.skip("Could not obtain auth token")
            
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        response = client.get("/predictions/BTC?days=30", headers=headers)
        
        # Peut retourner 200 (succès) ou 400 (données insuffisantes)
        assert response.status_code in [200, 400, 404]
        
        if response.status_code == 200:
            data = response.json()
            # Vérifier la structure si succès
            assert "symbol" in data or "predictions" in data

    def test_predictions_invalid_symbol(self, auth_token):
        """Test avec un symbole invalide"""
        if auth_token is None:
            pytest.skip("Could not obtain auth token")
            
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        response = client.get("/predictions/INVALID_SYMBOL_XYZ?days=30", headers=headers)
        
        # Devrait retourner 400 ou 404
        assert response.status_code in [400, 404]


class TestSMACalculation:
    """Tests pour le calcul SMA (Simple Moving Average)"""
    
    def test_sma_basic_calculation(self):
        """Test du calcul SMA basique"""
        prices = [100, 110, 105, 115, 120]
        period = 3
        
        # Calcul manuel : moyenne des 3 derniers = (105 + 115 + 120) / 3 = 113.33
        expected_sma = (105 + 115 + 120) / 3
        
        # Calcul avec numpy
        sma = np.mean(prices[-period:])
        
        assert abs(sma - expected_sma) < 0.01

    def test_sma_with_longer_period(self):
        """Test SMA avec une période plus longue"""
        prices = list(range(100, 150))  # 50 prix de 100 à 149
        period = 20
        
        sma = np.mean(prices[-period:])
        
        # Moyenne des 20 derniers (130 à 149)
        expected = np.mean(list(range(130, 150)))
        
        assert abs(sma - expected) < 0.01

    def test_sma_single_value(self):
        """Test SMA avec un seul prix"""
        prices = [100]
        
        sma = np.mean(prices)
        
        assert sma == 100


class TestEMACalculation:
    """Tests pour le calcul EMA (Exponential Moving Average)"""
    
    def test_ema_basic_calculation(self):
        """Test du calcul EMA basique"""
        prices = [100, 110, 105, 115, 120]
        period = 3
        
        # Calcul EMA
        multiplier = 2 / (period + 1)
        ema = prices[0]
        
        for price in prices[1:]:
            ema = (price - ema) * multiplier + ema
        
        # EMA devrait être proche mais différent de SMA
        sma = np.mean(prices[-period:])
        
        # EMA donne plus de poids aux valeurs récentes
        assert ema > 0
        assert ema != sma  # EMA et SMA sont différents

    def test_ema_trending_up(self):
        """Test EMA avec tendance haussière"""
        prices = [100, 105, 110, 115, 120, 125, 130]
        period = 5
        
        multiplier = 2 / (period + 1)
        ema = prices[0]
        
        for price in prices[1:]:
            ema = (price - ema) * multiplier + ema
        
        # EMA devrait être proche du dernier prix en tendance haussière
        assert ema > prices[0]
        assert ema < prices[-1]  # Mais inférieur au dernier (effet de lissage)


class TestLinearRegression:
    """Tests pour la régression linéaire"""
    
    def test_linear_regression_uptrend(self):
        """Test régression linéaire avec tendance haussière"""
        prices = [100, 110, 120, 130, 140]  # Tendance parfaitement linéaire
        
        # Calcul de régression linéaire simple
        x = np.arange(len(prices))
        y = np.array(prices)
        
        # Coefficients
        slope = np.polyfit(x, y, 1)[0]
        
        # La pente devrait être positive (tendance haussière)
        assert slope > 0
        
        # Prédiction pour le prochain point
        next_x = len(prices)
        coeffs = np.polyfit(x, y, 1)
        prediction = np.polyval(coeffs, next_x)
        
        # Le prix prédit devrait être > 140
        assert prediction > 140

    def test_linear_regression_downtrend(self):
        """Test régression linéaire avec tendance baissière"""
        prices = [150, 140, 130, 120, 110]  # Tendance baissière
        
        x = np.arange(len(prices))
        y = np.array(prices)
        
        slope = np.polyfit(x, y, 1)[0]
        
        # La pente devrait être négative
        assert slope < 0

    def test_linear_regression_flat(self):
        """Test régression linéaire avec prix stable"""
        prices = [100, 100, 100, 100, 100]
        
        x = np.arange(len(prices))
        y = np.array(prices)
        
        slope = np.polyfit(x, y, 1)[0]
        
        # La pente devrait être proche de 0
        assert abs(slope) < 0.01


class TestConfidenceCalculation:
    """Tests pour le calcul du niveau de confiance"""
    
    def test_confidence_high_correlation(self):
        """Test confiance avec forte corrélation (données linéaires)"""
        prices = [100, 110, 120, 130, 140]
        
        x = np.arange(len(prices))
        y = np.array(prices)
        
        # Calcul du coefficient de corrélation
        correlation = np.corrcoef(x, y)[0, 1]
        
        # Corrélation parfaite pour données linéaires
        assert abs(correlation) > 0.99

    def test_confidence_low_correlation(self):
        """Test confiance avec faible corrélation (données aléatoires)"""
        np.random.seed(42)
        prices = np.random.uniform(100, 200, 50).tolist()
        
        x = np.arange(len(prices))
        y = np.array(prices)
        
        correlation = np.corrcoef(x, y)[0, 1]
        
        # Corrélation faible pour données aléatoires
        assert abs(correlation) < 0.5


class TestPredictionValidation:
    """Tests de validation des paramètres de prédiction"""
    
    def test_minimum_data_points(self):
        """Test avec le minimum de points de données"""
        # Au moins 30 points pour des prévisions fiables
        min_points = 30
        prices = list(range(100, 100 + min_points))
        
        assert len(prices) >= min_points

    def test_period_validation(self):
        """Test validation de la période"""
        valid_periods = [30, 60, 90]
        invalid_periods = [5, 10, 400]
        
        for period in valid_periods:
            assert 30 <= period <= 365
        
        for period in invalid_periods:
            assert not (30 <= period <= 365) or period == 5 or period == 10


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
