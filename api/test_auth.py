# api/test_auth.py - Tests pour l'authentification JWT

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock
from main import app
from auth import get_password_hash, users_collection

client = TestClient(app)

# Utilisateur de test
TEST_USER = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpassword123"
}

@pytest.fixture(autouse=True)
def cleanup():
    """Nettoie la DB avant/après chaque test."""
    # Avant le test
    users_collection.delete_many({"username": TEST_USER["username"]})
    yield
    # Après le test
    users_collection.delete_many({"username": TEST_USER["username"]})


# ===== TESTS INSCRIPTION =====

def test_register_new_user():
    """Test d'inscription d'un nouvel utilisateur."""
    response = client.post("/auth/register", json=TEST_USER)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == TEST_USER["username"]
    assert data["email"] == TEST_USER["email"]
    assert "created_at" in data
    assert data["is_active"] == True
    assert data["role"] == "user"


def test_register_duplicate_username():
    """Test d'inscription avec un username déjà utilisé."""
    # Première inscription
    client.post("/auth/register", json=TEST_USER)
    # Deuxième inscription avec même username
    response = client.post("/auth/register", json=TEST_USER)
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


def test_register_duplicate_email():
    """Test d'inscription avec un email déjà utilisé."""
    # Première inscription
    client.post("/auth/register", json=TEST_USER)
    # Deuxième inscription avec même email mais username différent
    duplicate_email_user = {
        "username": "different_user",
        "email": TEST_USER["email"],
        "password": "password456"
    }
    response = client.post("/auth/register", json=duplicate_email_user)
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


def test_register_invalid_email():
    """Test d'inscription avec email invalide."""
    invalid_user = {
        "username": "testuser2",
        "email": "not-an-email",
        "password": "password123"
    }
    response = client.post("/auth/register", json=invalid_user)
    assert response.status_code == 422  # Validation error


# ===== TESTS CONNEXION =====

def test_login_success():
    """Test de connexion réussie."""
    # Inscription
    client.post("/auth/register", json=TEST_USER)
    
    # Connexion
    response = client.post(
        "/auth/login",
        data={
            "username": TEST_USER["username"],
            "password": TEST_USER["password"]
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password():
    """Test de connexion avec mauvais mot de passe."""
    # Inscription
    client.post("/auth/register", json=TEST_USER)
    
    # Connexion avec mauvais password
    response = client.post(
        "/auth/login",
        data={
            "username": TEST_USER["username"],
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401
    assert "incorrect" in response.json()["detail"].lower()


def test_login_nonexistent_user():
    """Test de connexion avec utilisateur inexistant."""
    response = client.post(
        "/auth/login",
        data={
            "username": "nonexistent",
            "password": "password123"
        }
    )
    assert response.status_code == 401


# ===== TESTS ROUTES PROTÉGÉES =====

def test_access_protected_route_without_token():
    """Test d'accès à une route protégée sans token."""
    response = client.get("/prices")
    assert response.status_code == 401


def test_access_protected_route_with_token():
    """Test d'accès à une route protégée avec token valide."""
    # Inscription
    client.post("/auth/register", json=TEST_USER)
    
    # Connexion pour obtenir le token
    login_response = client.post(
        "/auth/login",
        data={
            "username": TEST_USER["username"],
            "password": TEST_USER["password"]
        }
    )
    token = login_response.json()["access_token"]
    
    # Accès à la route protégée
    response = client.get(
        "/prices",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "prices" in data


def test_get_current_user_info():
    """Test de récupération des infos de l'utilisateur connecté."""
    # Inscription
    client.post("/auth/register", json=TEST_USER)
    
    # Connexion
    login_response = client.post(
        "/auth/login",
        data={
            "username": TEST_USER["username"],
            "password": TEST_USER["password"]
        }
    )
    token = login_response.json()["access_token"]
    
    # Récupérer les infos
    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == TEST_USER["username"]
    assert data["email"] == TEST_USER["email"]


def test_access_with_invalid_token():
    """Test d'accès avec token invalide."""
    response = client.get(
        "/prices",
        headers={"Authorization": "Bearer invalid_token_here"}
    )
    assert response.status_code == 401


# ===== TESTS ROUTES ADMIN =====

def test_admin_route_as_regular_user():
    """Test d'accès à une route admin en tant qu'utilisateur normal."""
    # Inscription utilisateur normal
    client.post("/auth/register", json=TEST_USER)
    
    # Connexion
    login_response = client.post(
        "/auth/login",
        data={
            "username": TEST_USER["username"],
            "password": TEST_USER["password"]
        }
    )
    token = login_response.json()["access_token"]
    
    # Tentative d'accès à la route admin
    response = client.get(
        "/admin/users",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403  # Forbidden


# ===== TESTS ROUTES PUBLIQUES =====

def test_root_endpoint():
    """Test de l'endpoint racine (public)."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "auth" in data


def test_health_check():
    """Test du health check (public)."""
    response = client.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()


def test_public_stats():
    """Test des statistiques publiques (sans auth)."""
    # Mock MongoDB collection to avoid connection issues
    from main import get_collection
    mock_collection = Mock()
    mock_collection.count_documents.return_value = 100
    app.dependency_overrides[get_collection] = lambda: mock_collection
    
    try:
        response = client.get("/public/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_records" in data
    finally:
        app.dependency_overrides.clear()


# ===== TESTS UTILITAIRES =====

def test_password_hashing():
    """Test du hashage de mot de passe."""
    from auth import get_password_hash, verify_password
    
    password = "my_secure_password"
    hashed = get_password_hash(password)
    
    # Le hash ne doit pas être égal au mot de passe
    assert hashed != password
    
    # Vérification doit réussir
    assert verify_password(password, hashed) == True
    
    # Vérification avec mauvais password doit échouer
    assert verify_password("wrong_password", hashed) == False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])