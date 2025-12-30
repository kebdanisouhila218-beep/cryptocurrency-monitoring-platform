# api/metrics.py - Métriques Prometheus pour FastAPI

from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time

# Compteurs
REQUESTS_TOTAL = Counter(
    'fastapi_requests_total',
    'Total number of requests',
    ['method', 'endpoint', 'status_code']
)

ALERTS_TRIGGERED = Counter(
    'alerts_triggered_total',
    'Total number of alerts triggered',
    ['crypto', 'type']
)

CRYPTO_PRICES_COLLECTED = Counter(
    'crypto_prices_collected_total',
    'Total number of crypto prices collected',
    ['crypto']
)

EMAILS_SENT = Counter(
    'emails_sent_total',
    'Total number of emails sent',
    ['status']
)

# Histogrammes
REQUEST_DURATION = Histogram(
    'fastapi_request_duration_seconds',
    'Request duration in seconds',
    ['method', 'endpoint'],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

# Jauges
ACTIVE_USERS = Gauge(
    'active_users_total',
    'Number of active users'
)

ACTIVE_ALERTS = Gauge(
    'active_alerts_total',
    'Number of active alerts'
)

CRYPTO_COUNT = Gauge(
    'crypto_count_total',
    'Number of tracked cryptocurrencies'
)


class PrometheusMiddleware(BaseHTTPMiddleware):
    """Middleware pour collecter les métriques des requêtes"""
    
    async def dispatch(self, request: Request, call_next):
        # Ne pas mesurer les métriques elles-mêmes
        if request.url.path == "/metrics":
            return await call_next(request)
        
        method = request.method
        endpoint = request.url.path
        
        # Mesurer le temps de réponse
        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time
        
        # Enregistrer les métriques
        status_code = response.status_code
        REQUESTS_TOTAL.labels(method=method, endpoint=endpoint, status_code=status_code).inc()
        REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)
        
        return response


def get_metrics():
    """Retourne les métriques au format Prometheus"""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


def update_system_metrics(db):
    """Met à jour les métriques système depuis MongoDB"""
    try:
        # Compter les utilisateurs actifs
        users_count = db.users.count_documents({"is_active": True})
        ACTIVE_USERS.set(users_count)
        
        # Compter les alertes actives
        alerts_count = db.alerts.count_documents({"is_active": True})
        ACTIVE_ALERTS.set(alerts_count)
        
        # Compter les cryptos
        crypto_count = db.prices.distinct("symbol")
        CRYPTO_COUNT.set(len(crypto_count) if crypto_count else 0)
        
    except Exception as e:
        print(f"[METRICS] Erreur mise à jour métriques: {e}")


def record_alert_triggered(crypto: str, alert_type: str):
    """Enregistre une alerte déclenchée"""
    ALERTS_TRIGGERED.labels(crypto=crypto, type=alert_type).inc()


def record_price_collected(crypto: str):
    """Enregistre une collecte de prix"""
    CRYPTO_PRICES_COLLECTED.labels(crypto=crypto).inc()


def record_email_sent(success: bool):
    """Enregistre un envoi d'email"""
    status = "success" if success else "failure"
    EMAILS_SENT.labels(status=status).inc()
