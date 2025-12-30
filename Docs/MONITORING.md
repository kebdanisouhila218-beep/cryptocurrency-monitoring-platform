# 📊 Monitoring avec Prometheus + Grafana

## Vue d'ensemble

La plateforme CryptoTracker intègre un système de monitoring complet avec :
- **Prometheus** : Collecte et stockage des métriques
- **Grafana** : Visualisation et dashboards
- **Exporters** : MongoDB, Redis, Node (système)

## 🚀 Démarrage rapide

### Lancer le monitoring

```bash
# Démarrer tous les services de monitoring
docker-compose up -d prometheus grafana mongodb-exporter redis-exporter node-exporter
```

### Accès aux interfaces

| Service | URL | Identifiants |
|---------|-----|--------------|
| **Grafana** | http://localhost:3001 | admin / admin123 |
| **Prometheus** | http://localhost:9090 | - |
| **API Metrics** | http://localhost:8000/metrics | - |

## 📈 Métriques disponibles

### API FastAPI

| Métrique | Description |
|----------|-------------|
| `fastapi_requests_total` | Nombre total de requêtes |
| `fastapi_request_duration_seconds` | Durée des requêtes (histogramme) |
| `alerts_triggered_total` | Alertes déclenchées |
| `crypto_prices_collected_total` | Prix collectés |
| `emails_sent_total` | Emails envoyés |
| `active_users_total` | Utilisateurs actifs |
| `active_alerts_total` | Alertes actives |

### MongoDB

| Métrique | Description |
|----------|-------------|
| `mongodb_connections` | Connexions actives |
| `mongodb_op_counters_total` | Opérations (insert, query, update, delete) |
| `mongodb_memory_usage_bytes` | Utilisation mémoire |

### Redis

| Métrique | Description |
|----------|-------------|
| `redis_connected_clients` | Clients connectés |
| `redis_commands_processed_total` | Commandes traitées |
| `redis_memory_used_bytes` | Mémoire utilisée |

### Système (Node Exporter)

| Métrique | Description |
|----------|-------------|
| `node_cpu_seconds_total` | Utilisation CPU |
| `node_memory_MemTotal_bytes` | Mémoire totale |
| `node_memory_MemAvailable_bytes` | Mémoire disponible |
| `node_filesystem_size_bytes` | Espace disque |

## 📊 Dashboard Grafana

Un dashboard pré-configuré est disponible avec :

1. **Vue d'ensemble**
   - Total des requêtes API
   - Temps de réponse (p95)
   - Prix crypto collectés
   - Alertes déclenchées

2. **Performance API**
   - Taux de requêtes par endpoint
   - Distribution des temps de réponse

3. **Infrastructure**
   - Utilisation CPU
   - Utilisation mémoire
   - Métriques Redis

## 🔧 Configuration

### Prometheus (`monitoring/prometheus/prometheus.yml`)

```yaml
scrape_configs:
  - job_name: 'fastapi'
    static_configs:
      - targets: ['api:8000']
    metrics_path: /metrics

  - job_name: 'mongodb'
    static_configs:
      - targets: ['mongodb-exporter:9216']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']
```

### Grafana

- **Datasources** : Configurés automatiquement via provisioning
- **Dashboards** : Importés automatiquement au démarrage

## 🔍 Requêtes PromQL utiles

```promql
# Taux de requêtes par seconde
rate(fastapi_requests_total[5m])

# Temps de réponse moyen
histogram_quantile(0.95, rate(fastapi_request_duration_seconds_bucket[5m]))

# Erreurs HTTP 5xx
sum(rate(fastapi_requests_total{status_code=~"5.."}[5m]))

# Utilisation CPU
100 - (avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# Mémoire utilisée
node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes
```

## 🚨 Alertes (optionnel)

Pour configurer des alertes, créez un fichier `monitoring/prometheus/alerts.yml` :

```yaml
groups:
  - name: crypto-alerts
    rules:
      - alert: HighErrorRate
        expr: sum(rate(fastapi_requests_total{status_code=~"5.."}[5m])) > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Taux d'erreur élevé"

      - alert: APIDown
        expr: up{job="fastapi"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "API non disponible"
```

## 📁 Structure des fichiers

```
monitoring/
├── prometheus/
│   └── prometheus.yml          # Configuration Prometheus
├── grafana/
│   └── provisioning/
│       ├── datasources/
│       │   └── datasources.yml # Sources de données
│       └── dashboards/
│           ├── dashboards.yml  # Configuration dashboards
│           └── crypto-dashboard.json  # Dashboard principal
```

## 🛠️ Dépannage

### Prometheus ne collecte pas les métriques

1. Vérifier que l'API est accessible : `curl http://localhost:8000/metrics`
2. Vérifier les targets dans Prometheus : http://localhost:9090/targets

### Grafana ne montre pas de données

1. Vérifier la connexion à Prometheus dans Grafana
2. Vérifier que Prometheus collecte bien les données
3. Ajuster la plage de temps dans Grafana

### Les exporters ne démarrent pas

```bash
# Vérifier les logs
docker-compose logs mongodb-exporter
docker-compose logs redis-exporter
```
