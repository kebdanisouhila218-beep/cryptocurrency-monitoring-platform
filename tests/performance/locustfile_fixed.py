# tests/performance/locustfile_fixed.py
"""
Tests de performance avec Locust pour CryptoTracker API (Version corrigée)

Usage:
    locust -f locustfile_fixed.py --host=http://localhost:8000
"""

from locust import HttpUser, task, between
import time


class CryptoTrackerUser(HttpUser):
    """Simule un utilisateur de l'application CryptoTracker"""
    
    wait_time = between(1, 3)
    
    def on_start(self):
        """Login au démarrage"""
        self.token = None
        self.headers = {}
        
        # Utiliser le compte admin existant
        login_response = self.client.post("/auth/login", 
            data={
                "username": "admin",
                "password": "MotDePasse123"
            })
        
        if login_response.status_code == 200:
            self.token = login_response.json().get("access_token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
            print("✅ Login admin réussi")
        else:
            print("❌ Login admin échoué")
            print(f"Status: {login_response.status_code}")
            print(f"Response: {login_response.text}")

    @task(10)
    def health_check(self):
        """Test endpoint health"""
        self.client.get("/health")

    @task(5)
    def get_root(self):
        """Test page d'accueil API"""
        self.client.get("/")

    @task(20)
    def get_prices(self):
        """Test récupération des prix"""
        if self.token:
            self.client.get("/prices", headers=self.headers)

    @task(10)
    def get_latest_prices(self):
        """Test derniers prix"""
        if self.token:
            self.client.get("/prices/latest?limit=10", headers=self.headers)

    @task(5)
    def get_user_info(self):
        """Test info utilisateur"""
        if self.token:
            self.client.get("/auth/me", headers=self.headers)

    @task(8)
    def get_alerts(self):
        """Test récupération des alertes"""
        if self.token:
            self.client.get("/alerts", headers=self.headers)

    @task(5)
    def get_portfolios(self):
        """Test récupération des portfolios virtuels"""
        if self.token:
            self.client.get("/virtual-portfolio", headers=self.headers)

    @task(3)
    def get_predictions(self):
        """Test prédictions BTC"""
        if self.token:
            self.client.get("/predictions/indicators/BTC", headers=self.headers)

    @task(3)
    def get_analytics_heatmap(self):
        """Test heatmap analytics"""
        if self.token:
            self.client.get("/analytics/heatmap", headers=self.headers)

    @task(2)
    def get_candlestick(self):
        """Test données candlestick"""
        if self.token:
            self.client.get("/analytics/candlestick/BTC", headers=self.headers)

    @task(1)
    def create_and_delete_alert(self):
        """Test création et suppression d'alerte"""
        if self.token:
            # Créer une alerte
            response = self.client.post("/alerts", 
                headers=self.headers,
                json={
                    "crypto_symbol": "BTC",
                    "target_price": 100000,
                    "alert_type": "above"
                }
            )
            
            if response.status_code == 200:
                alert_id = response.json().get("alert", {}).get("id")
                if alert_id:
                    # Supprimer l'alerte
                    self.client.delete(f"/alerts/{alert_id}", headers=self.headers)


class AdminUser(HttpUser):
    """Simule un administrateur"""
    
    wait_time = between(2, 5)
    weight = 1  # Moins d'admins que d'utilisateurs normaux
    
    def on_start(self):
        """Login admin"""
        login_response = self.client.post("/auth/login", data={
            "username": "admin",
            "password": "MotDePasse123"
        })
        
        if login_response.status_code == 200:
            self.token = login_response.json().get("access_token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            self.headers = {}
            self.token = None

    @task(5)
    def get_admin_stats(self):
        """Test statistiques admin"""
        if self.token:
            self.client.get("/admin/stats", headers=self.headers)

    @task(3)
    def get_admin_users(self):
        """Test liste utilisateurs"""
        if self.token:
            self.client.get("/admin/users", headers=self.headers)

    @task(2)
    def get_system_health(self):
        """Test santé système"""
        if self.token:
            self.client.get("/admin/system/health", headers=self.headers)

    @task(2)
    def get_admin_alerts(self):
        """Test alertes admin"""
        if self.token:
            self.client.get("/admin/alerts", headers=self.headers)
