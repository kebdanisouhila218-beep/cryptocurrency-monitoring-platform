# CryptoTracker — Plateforme de Surveillance des Cryptomonnaies

Plateforme complete de surveillance des cryptomonnaies permettant de suivre les prix en temps reel, generer des previsions, configurer des alertes automatiques et gerer un portfolio virtuel. Developpee avec FastAPI et React.

Projet realise dans le cadre du module AMS Application GLA (Genie Logiciel Avance), Master ILSEN, Universite d'Avignon, annee universitaire 2025-2026.

Documentation complete : [`Docs/`](Docs/) — Deploiement Kubernetes : [`Docs/KUBERNETES_DEPLOYMENT.md`](Docs/KUBERNETES_DEPLOYMENT.md)

## Vue d'ensemble

CryptoTracker suit 50 cryptomonnaies en temps reel (prix, volume, capitalisation), genere des previsions (moyennes mobiles SMA/EMA, regression lineaire) et calcule des indicateurs techniques (RSI, MACD, Bollinger Bands) avec signaux d'achat et de vente.

![Dashboard](docs/screenshots/dashboard.png)

## Fonctionnalites principales

**Surveillance et analyse**
- Suivi de 50 cryptomonnaies en temps reel
- Previsions (SMA, EMA, regression lineaire) avec niveaux de confiance
- Indicateurs techniques (RSI, MACD, Bollinger Bands)
- Graphiques chandeliers OHLC, heatmap de performance du marche

**Alertes et notifications**
- Alertes de prix personnalisees (seuil, pourcentage)
- Notifications par email et webhook Discord

**Portfolio**
- Portfolio virtuel avec calcul automatique des gains/pertes
- Simulation d'achat/vente, historique des transactions

**Utilisateurs et administration**
- Authentification JWT avec hachage Argon2
- Panel d'administration : gestion des utilisateurs, statistiques, logs
- Deux roles : utilisateur et administrateur

**Interface**
- Mode sombre, design responsive (mobile et desktop)

**DevOps et monitoring**
- Docker Compose (services API, frontend, base de donnees, monitoring)
- Deploiement Kubernetes (Minikube / Kind)
- Monitoring Prometheus + Grafana, logs centralises via Loki
- Tests de securite automatises (Trivy, Snyk, OWASP ZAP) et de performance (Locust, k6)

## Architecture technique

**Backend (Python)**
FastAPI pour l'API REST, MongoDB pour le stockage, Redis et Celery pour les taches asynchrones, Pydantic pour la validation des donnees, authentification JWT avec hachage Argon2, client Prometheus pour les metriques.

**Frontend (React)**
React avec hooks, Recharts pour les graphiques interactifs, Axios pour les appels API, theme clair/sombre, panel d'administration complet.

**DevOps et infrastructure**
Docker Compose, orchestration Kubernetes (Minikube/Kind), pipeline CI/CD via GitHub Actions, monitoring Prometheus + Grafana, logs centralises Loki + Promtail, alertes systeme via AlertManager.

![Diagramme d'Architecture](Docs/Diagramme%20d'Architecture.png)

## Installation rapide

```bash
# Cloner le projet
git clone https://github.com/kebdanisouhila218-beep/cryptocurrency-monitoring-platform.git
cd cryptocurrency-monitoring-platform

# Configurer l'environnement
cp .env.example .env
# Editer .env avec vos propres cles (SMTP, Discord, SECRET_KEY)

# Lancer avec Docker
docker-compose up -d
```

Acces une fois demarre :
- Frontend : http://localhost:3000
- API : http://localhost:8000
- Documentation API (Swagger) : http://localhost:8000/docs

## Methodologie et sprints

Projet developpe en 14 sprints selon une methodologie Agile :

| Sprints | Fonctionnalite |
|---|---|
| 1-2 | Collecte de donnees, API, frontend React |
| 3-4 | Tests, authentification JWT |
| 5-7 | Alertes, portfolio virtuel |
| 8-10 | Previsions, indicateurs techniques, visualisations |
| 11 | Documentation et diagrammes |
| 12 | Panel d'administration, gestion des roles |
| 13 | Kubernetes, monitoring avance |
| 14 | CI/CD, tests de securite et de performance |

## Documentation

- [Guide d'installation](Docs/INSTALLATION.md)
- [Documentation API](Docs/API_DOCS.md)
- [Guide utilisateur](Docs/USER_GUIDE.md)
- [Pipeline CI/CD](Docs/CICD.md)
- [Deploiement Kubernetes](Docs/KUBERNETES_DEPLOYMENT.md)
- [Monitoring](Docs/MONITORING.md)
- [Tests de performance et de securite](Docs/PERFORMANCE_SECURITY_TESTS.md)

Diagrammes UML disponibles dans `Docs/` : architecture, deploiement, cas d'utilisation, classes, sequences (authentification, creation d'alerte, trading virtuel), activite, etats, pipeline CI/CD.

## Tests

```bash
# Tests backend
cd api && python -m pytest -v

# Tests collector
cd collector && python -m pytest -v

# Tests frontend
cd frontend && npm test

# Tests de performance (Locust)
locust -f tests/performance/locustfile_web.py --host=http://localhost:8000

# Tests de securite
python tests/security/zap_scan.py --target http://localhost:8000
```

| Type | Outils | Description |
|---|---|---|
| Unitaires | Pytest | API, collector, services |
| Integration | Pytest + Docker | MongoDB, Redis |
| Performance | Locust, k6 | Tests de charge et de stress |
| Securite | Trivy, Snyk, OWASP ZAP | Vulnerabilites, dependances |
| End-to-end | Playwright | Parcours utilisateur complets |

Couverture de tests : environ 75%, avec 12 workflows CI/CD (tests, build, securite, performance, deploiement).

## Securite

**Authentification et autorisation**
JWT avec expiration des tokens (30 minutes), hachage des mots de passe (Argon2/Bcrypt), controle d'acces par role (utilisateur/administrateur).

**Protection des donnees**
Validation des entrees via Pydantic, configuration stricte de CORS, secrets geres via variables d'environnement (non commitees).

**Tests de securite automatises**
Trivy pour le scan des images Docker, Snyk pour les vulnerabilites des dependances, OWASP ZAP pour les tests de penetration.

## Competences mobilisees

Python, FastAPI, React, MongoDB, Redis, Celery, JWT, Argon2, Docker, Kubernetes, GitHub Actions, Prometheus, Grafana, Loki, Pytest, Playwright, Locust, OWASP ZAP, Trivy, Snyk, methodologie Agile, architecture microservices.

## Contact

Souhila Aicha Kebdani — kebdanisouhila218@gmail.com — Master 1 ILSEN, Universite d'Avignon, 2025/2026

## Licence

Ce projet est sous licence MIT — voir le fichier [LICENSE](LICENSE).
