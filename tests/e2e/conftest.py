# tests/e2e/conftest.py
"""
Configuration pytest pour les tests E2E avec Playwright
"""
import pytest


def pytest_configure(config):
    """Configuration pytest"""
    config.addinivalue_line(
        "markers", "e2e: mark test as end-to-end test"
    )


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Arguments pour le contexte du navigateur"""
    return {
        **browser_context_args,
        "viewport": {"width": 1920, "height": 1080},
        "ignore_https_errors": True,
    }


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    """Arguments pour le lancement du navigateur"""
    return {
        **browser_type_launch_args,
        "headless": True,
        "slow_mo": 100,  # Ralentir pour voir les actions
    }


# Configuration des URLs
BASE_URL = "http://localhost:3000"
API_URL = "http://localhost:8000"


@pytest.fixture
def base_url():
    """URL de base du frontend"""
    return BASE_URL


@pytest.fixture
def api_url():
    """URL de base de l'API"""
    return API_URL
