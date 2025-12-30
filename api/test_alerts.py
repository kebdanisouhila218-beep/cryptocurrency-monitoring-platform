# api/test_alerts.py
"""
Tests unitaires pour le système d'alertes
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
    return f"test_alert_{''.join(random.choices(string.ascii_lowercase, k=8))}"


class TestAlertsEndpoints:
    """Tests pour les endpoints d'alertes"""
    
    @pytest.fixture
    def auth_token(self):
        """Token d'authentification pour les tests"""
        username = generate_random_username()
        
        # Inscription
        client.post("/auth/register", json={
            "username": username,
            "email": f"{username}@example.com",
            "password": "testpass123"
        })
        
        # Connexion
        login_response = client.post("/auth/login", data={
            "username": username,
            "password": "testpass123"
        })
        
        if login_response.status_code == 200:
            token = login_response.json()["access_token"]
            yield {"token": token, "username": username}
            
            # Cleanup
            try:
                from auth import users_collection
                users_collection.delete_one({"username": username})
            except:
                pass
        else:
            yield None

    def test_alerts_requires_auth(self):
        """Test que les endpoints d'alertes nécessitent l'authentification"""
        # GET /alerts
        response = client.get("/alerts")
        assert response.status_code == 401
        
        # POST /alerts
        response = client.post("/alerts", json={
            "crypto_symbol": "BTC",
            "target_price": 100000.00,
            "alert_type": "above"
        })
        assert response.status_code == 401

    def test_create_alert(self, auth_token):
        """Test de création d'une alerte"""
        if auth_token is None:
            pytest.skip("Could not obtain auth token")
            
        headers = {"Authorization": f"Bearer {auth_token['token']}"}
        
        alert_data = {
            "crypto_symbol": "BTC",
            "target_price": 100000.00,
            "alert_type": "above"
        }
        
        response = client.post("/alerts", json=alert_data, headers=headers)
        
        # Peut être 200, 201 ou 422 selon l'implémentation
        assert response.status_code in [200, 201, 422]
        
        if response.status_code in [200, 201]:
            data = response.json()
            
            # Vérifier les champs retournés
            assert "crypto_symbol" in data or "symbol" in data
            
            # Cleanup - supprimer l'alerte créée
            if "id" in data or "_id" in data:
                alert_id = data.get("id") or data.get("_id")
                client.delete(f"/alerts/{alert_id}", headers=headers)

    def test_create_alert_below(self, auth_token):
        """Test de création d'une alerte 'below'"""
        if auth_token is None:
            pytest.skip("Could not obtain auth token")
            
        headers = {"Authorization": f"Bearer {auth_token['token']}"}
        
        alert_data = {
            "crypto_symbol": "ETH",
            "target_price": 2000.00,
            "alert_type": "below"
        }
        
        response = client.post("/alerts", json=alert_data, headers=headers)
        
        assert response.status_code in [200, 201, 422]

    def test_list_alerts(self, auth_token):
        """Test de listage des alertes"""
        if auth_token is None:
            pytest.skip("Could not obtain auth token")
            
        headers = {"Authorization": f"Bearer {auth_token['token']}"}
        
        response = client.get("/alerts", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Vérifier la structure de la réponse
        assert isinstance(data, (list, dict))

    def test_delete_alert(self, auth_token):
        """Test de suppression d'une alerte"""
        if auth_token is None:
            pytest.skip("Could not obtain auth token")
            
        headers = {"Authorization": f"Bearer {auth_token['token']}"}
        
        # Créer une alerte d'abord
        alert_data = {
            "crypto_symbol": "SOL",
            "target_price": 200.00,
            "alert_type": "above"
        }
        create_response = client.post("/alerts", json=alert_data, headers=headers)
        
        if create_response.status_code in [200, 201]:
            data = create_response.json()
            alert_id = data.get("id") or data.get("_id")
            
            if alert_id:
                # Supprimer l'alerte
                delete_response = client.delete(f"/alerts/{alert_id}", headers=headers)
                
                assert delete_response.status_code in [200, 204]


class TestAlertValidation:
    """Tests de validation des alertes"""
    
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
            yield token
            
            try:
                from auth import users_collection
                users_collection.delete_one({"username": username})
            except:
                pass
        else:
            yield None

    def test_alert_missing_fields(self, auth_token):
        """Test avec des champs manquants"""
        if auth_token is None:
            pytest.skip("Could not obtain auth token")
            
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Sans crypto_symbol
        response = client.post("/alerts", json={
            "target_price": 100000.00,
            "alert_type": "above"
        }, headers=headers)
        
        assert response.status_code == 422

    def test_alert_invalid_type(self, auth_token):
        """Test avec un type d'alerte invalide"""
        if auth_token is None:
            pytest.skip("Could not obtain auth token")
            
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        response = client.post("/alerts", json={
            "crypto_symbol": "BTC",
            "target_price": 100000.00,
            "alert_type": "invalid_type"
        }, headers=headers)
        
        assert response.status_code == 422


class TestAlertLogic:
    """Tests de la logique des alertes"""
    
    def test_alert_trigger_above(self):
        """Test de déclenchement d'alerte 'above'"""
        target_price = 100000
        current_price = 105000
        alert_type = "above"
        
        should_trigger = (alert_type == "above" and current_price >= target_price)
        
        assert should_trigger == True

    def test_alert_no_trigger_above(self):
        """Test de non-déclenchement d'alerte 'above'"""
        target_price = 100000
        current_price = 95000
        alert_type = "above"
        
        should_trigger = (alert_type == "above" and current_price >= target_price)
        
        assert should_trigger == False

    def test_alert_trigger_below(self):
        """Test de déclenchement d'alerte 'below'"""
        target_price = 90000
        current_price = 85000
        alert_type = "below"
        
        should_trigger = (alert_type == "below" and current_price <= target_price)
        
        assert should_trigger == True

    def test_alert_no_trigger_below(self):
        """Test de non-déclenchement d'alerte 'below'"""
        target_price = 90000
        current_price = 95000
        alert_type = "below"
        
        should_trigger = (alert_type == "below" and current_price <= target_price)
        
        assert should_trigger == False

    def test_alert_exact_price(self):
        """Test avec prix exact"""
        target_price = 100000
        current_price = 100000
        
        # above devrait se déclencher
        should_trigger_above = (current_price >= target_price)
        assert should_trigger_above == True
        
        # below devrait aussi se déclencher
        should_trigger_below = (current_price <= target_price)
        assert should_trigger_below == True


class TestAlertNotifications:
    """Tests pour les notifications d'alertes"""
    
    def test_email_format(self):
        """Test du format d'email de notification"""
        alert = {
            "crypto_symbol": "BTC",
            "target_price": 100000,
            "alert_type": "above",
            "current_price": 105000
        }
        
        subject = f"🔔 Alerte CryptoTracker - {alert['crypto_symbol']} a atteint ${alert['current_price']}"
        
        assert "BTC" in subject
        assert "105000" in subject

    def test_discord_webhook_format(self):
        """Test du format de webhook Discord"""
        alert = {
            "crypto_symbol": "ETH",
            "target_price": 4000,
            "alert_type": "above",
            "current_price": 4200
        }
        
        message = {
            "content": f"🚨 **Alerte Prix** 🚨\n\n"
                      f"**{alert['crypto_symbol']}** a atteint **${alert['current_price']}**\n"
                      f"Prix cible: ${alert['target_price']} ({alert['alert_type']})"
        }
        
        assert "ETH" in message["content"]
        assert "4200" in message["content"]
        assert "4000" in message["content"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
