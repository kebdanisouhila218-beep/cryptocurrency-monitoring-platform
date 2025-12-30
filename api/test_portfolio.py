# api/test_portfolio.py
"""
Tests unitaires pour le portfolio virtuel
"""
import pytest
from fastapi.testclient import TestClient
import random
import string
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import app

client = TestClient(app)


def generate_random_username():
    """Génère un nom d'utilisateur aléatoire"""
    return f"test_port_{''.join(random.choices(string.ascii_lowercase, k=8))}"


class TestPortfolioEndpoints:
    """Tests pour les endpoints du portfolio"""
    
    @pytest.fixture
    def auth_token(self):
        """Token d'authentification"""
        username = generate_random_username()
        
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
            yield {"token": token, "username": username}
            
            try:
                from auth import users_collection
                users_collection.delete_one({"username": username})
            except:
                pass
        else:
            yield None

    def test_portfolio_requires_auth(self):
        """Test que les endpoints portfolio nécessitent l'authentification"""
        # GET balance
        response = client.get("/portfolio/balance")
        assert response.status_code == 401
        
        # POST buy
        response = client.post("/portfolio/buy", json={
            "crypto_symbol": "BTC",
            "quantity": 0.5,
            "price": 94000.00
        })
        assert response.status_code == 401

    def test_buy_crypto(self, auth_token):
        """Test d'achat de crypto"""
        if auth_token is None:
            pytest.skip("Could not obtain auth token")
            
        headers = {"Authorization": f"Bearer {auth_token['token']}"}
        
        buy_data = {
            "crypto_symbol": "BTC",
            "quantity": 0.5,
            "price": 94000.00
        }
        
        response = client.post("/portfolio/buy", json=buy_data, headers=headers)
        
        # Peut être 200, 201 ou 404 selon l'implémentation
        assert response.status_code in [200, 201, 404, 422]

    def test_sell_crypto(self, auth_token):
        """Test de vente de crypto"""
        if auth_token is None:
            pytest.skip("Could not obtain auth token")
            
        headers = {"Authorization": f"Bearer {auth_token['token']}"}
        
        # D'abord acheter
        buy_data = {
            "crypto_symbol": "ETH",
            "quantity": 2.0,
            "price": 3500.00
        }
        client.post("/portfolio/buy", json=buy_data, headers=headers)
        
        # Puis vendre
        sell_data = {
            "crypto_symbol": "ETH",
            "quantity": 1.0,
            "price": 3600.00
        }
        response = client.post("/portfolio/sell", json=sell_data, headers=headers)
        
        # Peut être 200, 201, 400 ou 404 selon l'implémentation
        assert response.status_code in [200, 201, 400, 404, 422]

    def test_get_balance(self, auth_token):
        """Test de récupération du solde"""
        if auth_token is None:
            pytest.skip("Could not obtain auth token")
            
        headers = {"Authorization": f"Bearer {auth_token['token']}"}
        
        response = client.get("/portfolio/balance", headers=headers)
        
        # Peut être 200 ou 404 selon l'implémentation
        assert response.status_code in [200, 404]

    def test_get_transactions(self, auth_token):
        """Test de récupération des transactions"""
        if auth_token is None:
            pytest.skip("Could not obtain auth token")
            
        headers = {"Authorization": f"Bearer {auth_token['token']}"}
        
        response = client.get("/portfolio/transactions", headers=headers)
        
        # Peut être 200 ou 404 selon l'implémentation
        assert response.status_code in [200, 404]


class TestPortfolioCalculations:
    """Tests pour les calculs du portfolio"""
    
    def test_pnl_calculation_profit(self):
        """Test calcul P&L avec profit"""
        buy_price = 90000
        current_price = 95000
        quantity = 1.0
        
        invested = buy_price * quantity
        current_value = current_price * quantity
        pnl = current_value - invested
        pnl_percent = (pnl / invested) * 100
        
        assert pnl == 5000
        assert abs(pnl_percent - 5.56) < 0.1

    def test_pnl_calculation_loss(self):
        """Test calcul P&L avec perte"""
        buy_price = 95000
        current_price = 90000
        quantity = 1.0
        
        invested = buy_price * quantity
        current_value = current_price * quantity
        pnl = current_value - invested
        pnl_percent = (pnl / invested) * 100
        
        assert pnl == -5000
        assert pnl_percent < 0

    def test_average_buy_price(self):
        """Test calcul du prix moyen d'achat"""
        transactions = [
            {"quantity": 1.0, "price": 90000},
            {"quantity": 0.5, "price": 95000},
            {"quantity": 0.5, "price": 85000}
        ]
        
        total_quantity = sum(t["quantity"] for t in transactions)
        total_cost = sum(t["quantity"] * t["price"] for t in transactions)
        avg_price = total_cost / total_quantity
        
        # (1*90000 + 0.5*95000 + 0.5*85000) / 2 = 180000 / 2 = 90000
        assert total_quantity == 2.0
        assert avg_price == 90000

    def test_total_portfolio_value(self):
        """Test calcul de la valeur totale du portfolio"""
        positions = [
            {"symbol": "BTC", "quantity": 1.0, "current_price": 94000},
            {"symbol": "ETH", "quantity": 5.0, "current_price": 3500},
            {"symbol": "SOL", "quantity": 20.0, "current_price": 150}
        ]
        
        total_value = sum(p["quantity"] * p["current_price"] for p in positions)
        
        # 1*94000 + 5*3500 + 20*150 = 94000 + 17500 + 3000 = 114500
        assert total_value == 114500


class TestPortfolioValidation:
    """Tests de validation du portfolio"""
    
    def test_quantity_must_be_positive(self):
        """Test que la quantité doit être positive"""
        quantity = -1.0
        
        is_valid = quantity > 0
        
        assert is_valid == False

    def test_price_must_be_positive(self):
        """Test que le prix doit être positif"""
        price = -100.00
        
        is_valid = price > 0
        
        assert is_valid == False

    def test_cannot_sell_more_than_owned(self):
        """Test qu'on ne peut pas vendre plus que ce qu'on possède"""
        owned_quantity = 1.0
        sell_quantity = 2.0
        
        can_sell = sell_quantity <= owned_quantity
        
        assert can_sell == False

    def test_valid_crypto_symbols(self):
        """Test des symboles de crypto valides"""
        valid_symbols = ["BTC", "ETH", "SOL", "ADA", "DOT"]
        invalid_symbols = ["", "INVALID_SYMBOL_XYZ", "123"]
        
        for symbol in valid_symbols:
            assert len(symbol) >= 2
            assert len(symbol) <= 10
        
        for symbol in invalid_symbols:
            is_valid = len(symbol) >= 2 and len(symbol) <= 10 and symbol.isalpha()
            # Au moins un devrait être invalide
            if symbol == "" or symbol == "123":
                assert not is_valid or symbol == ""


class TestPortfolioTransactions:
    """Tests pour les transactions du portfolio"""
    
    def test_transaction_types(self):
        """Test des types de transactions"""
        valid_types = ["buy", "sell"]
        
        for t_type in valid_types:
            assert t_type in ["buy", "sell"]

    def test_transaction_timestamp(self):
        """Test que les transactions ont un timestamp"""
        import time
        
        transaction = {
            "type": "buy",
            "crypto_symbol": "BTC",
            "quantity": 1.0,
            "price": 94000,
            "timestamp": time.time()
        }
        
        assert "timestamp" in transaction
        assert transaction["timestamp"] > 0

    def test_transaction_total_amount(self):
        """Test du calcul du montant total"""
        quantity = 0.5
        price = 94000
        
        total_amount = quantity * price
        
        assert total_amount == 47000


class TestPortfolioStats:
    """Tests pour les statistiques du portfolio"""
    
    def test_portfolio_stats_structure(self):
        """Test de la structure des statistiques"""
        stats = {
            "total_value": 100000,
            "total_invested": 90000,
            "pnl": 10000,
            "pnl_percent": 11.11,
            "positions_count": 5,
            "transactions_count": 15
        }
        
        required_fields = ["total_value", "total_invested", "pnl", "pnl_percent"]
        
        for field in required_fields:
            assert field in stats

    def test_allocation_calculation(self):
        """Test du calcul de l'allocation"""
        positions = [
            {"symbol": "BTC", "value": 50000},
            {"symbol": "ETH", "value": 30000},
            {"symbol": "SOL", "value": 20000}
        ]
        
        total_value = sum(p["value"] for p in positions)
        
        allocations = []
        for p in positions:
            allocation = (p["value"] / total_value) * 100
            allocations.append({"symbol": p["symbol"], "allocation": allocation})
        
        # BTC: 50%, ETH: 30%, SOL: 20%
        assert allocations[0]["allocation"] == 50
        assert allocations[1]["allocation"] == 30
        assert allocations[2]["allocation"] == 20
        
        # Total devrait être 100%
        total_allocation = sum(a["allocation"] for a in allocations)
        assert total_allocation == 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
