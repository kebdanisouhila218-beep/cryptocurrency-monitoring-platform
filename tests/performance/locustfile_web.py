# tests/performance/locustfile_web.py
"""
Tests de performance avec Locust pour CryptoTracker API (Version interface web)

Usage:
    locust -f locustfile_web.py --host=http://localhost:8000
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
        
        # Essayer plusieurs méthodes de login
        login_methods = [
            # Méthode 1: Form-data standard
            lambda: self.client.post("/auth/login", data={
                "username": "admin",
                "password": "MotDePasse123"
            }),
            # Méthode 2: Form-data avec headers explicites
            lambda: self.client.post("/auth/login", 
                data={
                    "username": "admin",
                    "password": "MotDePasse123"
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            ),
            # Méthode 3: Créer un utilisateur et se connecter
            self._create_and_login_user
        ]
        
        for i, method in enumerate(login_methods):
            try:
                if i == 2:  # Pour la méthode 3, c'est une fonction
                    response = method()
                else:
                    response = method()
                
                if response.status_code == 200:
                    self.token = response.json().get("access_token")
                    self.headers = {"Authorization": f"Bearer {self.token}"}
                    print(f"✅ Login réussi avec méthode {i+1}")
                    break
                else:
                    print(f"❌ Méthode {i+1} échouée: {response.status_code}")
                    if i == 2:  # Dernière méthode
                        print("❌ Toutes les méthodes de login ont échoué")
                        
            except Exception as e:
                print(f"❌ Exception méthode {i+1}: {e}")
                if i == 2:  # Dernière méthode
                    print("❌ Toutes les méthodes de login ont échoué")
    
    def _create_and_login_user(self):
        """Crée un utilisateur et se connecte"""
        username = f"testuser_{int(time.time() * 1000)}"
        
        # Créer l'utilisateur
        register_response = self.client.post("/auth/register", json={
            "username": username,
            "email": f"{username}@test.com",
            "password": "TestPassword123!"
        })
        
        if register_response.status_code == 200:
            # Se connecter
            login_response = self.client.post("/auth/login", data={
                "username": username,
                "password": "TestPassword123!"
            })
            return login_response
        else:
            # Retourner une réponse d'erreur
            class MockResponse:
                def __init__(self, status_code=500):
                    self.status_code = status_code
                    self.text = "Registration failed"
            return MockResponse()

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
        else:
            # Tenter sans authentification pour voir l'erreur
            self.client.get("/prices")

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


class AdminUser(HttpUser):
    """Simule un administrateur"""
    
    wait_time = between(2, 5)
    weight = 1  # Moins d'admins que d'utilisateurs normaux
    
    def on_start(self):
        """Login admin"""
        # Essayer plusieurs méthodes de login
        login_methods = [
            lambda: self.client.post("/auth/login", data={
                "username": "admin",
                "password": "MotDePasse123"
            }),
            lambda: self.client.post("/auth/login", 
                data={
                    "username": "admin",
                    "password": "MotDePasse123"
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
        ]
        
        for i, method in enumerate(login_methods):
            try:
                response = method()
                if response.status_code == 200:
                    self.token = response.json().get("access_token")
                    self.headers = {"Authorization": f"Bearer {self.token}"}
                    print(f"✅ Admin login réussi avec méthode {i+1}")
                    break
                else:
                    print(f"❌ Admin login méthode {i+1} échouée: {response.status_code}")
            except Exception as e:
                print(f"❌ Admin login exception {i+1}: {e}")

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
