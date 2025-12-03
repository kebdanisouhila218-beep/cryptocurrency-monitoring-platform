# 🚀 Cryptocurrency Monitoring Platform

[![Tests Collector](https://github.com/kebdanisouhila218-beep/cryptocurrency-monitoring-platform/actions/workflows/test.yml/badge.svg)](https://github.com/kebdanisouhila218-beep/cryptocurrency-monitoring-platform/actions/workflows/test.yml)
[![Tests API](https://github.com/kebdanisouhila218-beep/cryptocurrency-monitoring-platform/actions/workflows/test-api.yml/badge.svg)](https://github.com/kebdanisouhila218-beep/cryptocurrency-monitoring-platform/actions/workflows/test-api.yml)
[![Tests Integration](https://github.com/kebdanisouhila218-beep/cryptocurrency-monitoring-platform/actions/workflows/test-integration-collector.yml/badge.svg)](https://github.com/kebdanisouhila218-beep/cryptocurrency-monitoring-platform/actions/workflows/test-integration-collector.yml)

## 📊 Statut du Projet

**Sprint 1 terminé ✅** | **Sprint 2 en cours 🔄**

---

## 📝 Description

Plateforme complète de **surveillance, d'analyse et de prévision** des marchés de cryptomonnaies. Le système collecte automatiquement les données de prix, volumes et capitalisations depuis des APIs publiques, les stocke dans une base de données, et les expose via une API REST et une interface web interactive.

### ✅ Fonctionnalités Actuelles (Sprint 1 - TERMINÉ)

- ✅ **Collecte automatique des données** depuis CoinPaprika API
- ✅ **Stockage persistant** dans MongoDB
- ✅ **API REST** pour consulter les prix (FastAPI)
- ✅ **Interface web React** avec tableaux et graphiques
- ✅ **Planification automatique** avec Celery + Redis
- ✅ **Tests unitaires** et **tests d'intégration**
- ✅ **Pipeline CI/CD** avec GitHub Actions (3 workflows)
- ✅ **Conteneurisation** complète avec Docker Compose

### 🔄 En Développement (Sprint 2 - EN COURS)

- 🔄 Authentification JWT
- 🔄 Dashboard avancé avec graphiques interactifs
- 🔄 Filtres et recherche améliorés

### 📋 Roadmap (Sprints 3-5)

**Sprint 3 - Alertes & Notifications**
- Système d'alertes personnalisées (seuils de prix)
- Notifications par email
- Webhooks Discord

**Sprint 4 - Portfolio & Prévisions**
- Portfolio virtuel (simulation achats/ventes)
- Module de prévision (moyennes mobiles, régression)
- Calcul de performances (P&L)

**Sprint 5 - DevOps & Production**
- Déploiement Kubernetes
- Monitoring Prometheus + Grafana
- Tests de performance (Locust)
- Tests de sécurité (OWASP ZAP)

---

## 🏗️ Architecture

```
┌─────────────────┐
│  CoinPaprika    │
│      API        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌─────────────────┐
│   Collector     │─────▶│    MongoDB      │
│   (Python)      │      │    (NoSQL)      │
└────────┬────────┘      └────────┬────────┘
         │                        │
         ▼                        │
┌─────────────────┐              │
│ Redis + Celery  │              │
│  (Queue/Beat)   │              │
└─────────────────┘              │
                                 ▼
                        ┌─────────────────┐
                        │   API FastAPI   │
                        │   (REST API)    │
                        └────────┬────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │  React Frontend │
                        │   (Dashboard)   │
                        └────────┬────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │  Utilisateurs   │
                        └─────────────────┘
```

**Voir le diagramme complet :** [docs/architecture-diagram.png](docs/architecture-diagram.png)

---

## 🛠️ Technologies Utilisées

| Composant | Technologie | Version |
|-----------|-------------|---------|
| **Langage** | Python | 3.11 |
| **Framework Backend** | FastAPI | 0.104+ |
| **Base de données** | MongoDB | 6.0 |
| **Cache/Queue** | Redis | 7.0 |
| **Task Queue** | Celery | 5.3+ |
| **Frontend** | React | 18.x |
| **Graphiques** | Recharts | 2.x |
| **Conteneurisation** | Docker & Docker Compose | - |
| **CI/CD** | GitHub Actions | - |
| **Tests** | pytest | 7.x |
| **Gestion de projet** | GitHub Projects | - |

---

## 🚀 Démarrage Rapide

### Prérequis

- Docker & Docker Compose installés
- Python 3.11+ (pour développement local)
- Node.js 18+ (pour le frontend)

### Installation

```bash
# 1. Cloner le repository
git clone https://github.com/kebdanisouhila218-beep/cryptocurrency-monitoring-platform.git
cd cryptocurrency-monitoring-platform

# 2. Lancer tous les services avec Docker Compose
docker-compose up -d

# 3. Vérifier que les services sont actifs
docker-compose ps
```

### Accès aux Services

- **API REST :** http://localhost:8000
- **Documentation API :** http://localhost:8000/docs
- **Frontend React :** http://localhost:3000 (après `npm start` dans `frontend/`)
- **MongoDB :** localhost:27017
- **Redis :** localhost:6379

### Tester l'API

```bash
# Endpoint racine
curl http://localhost:8000/

# Récupérer les prix
curl http://localhost:8000/prices

# Health check
curl http://localhost:8000/health
```

---

## 🧪 Tests

Le projet inclut des tests unitaires et d'intégration avec une couverture complète.

### Lancer Tous les Tests

```bash
# Tests unitaires - Collector
pytest collector/test_collector_logic.py -v

# Tests unitaires - API
cd api && pytest test_api.py -v

# Tests d'intégration
docker-compose up test-integration
```

### Tests via Docker Compose

```bash
# Test du collector (mode unique)
docker-compose up collector-test

# Tests unitaires API
docker-compose up test-unit-api

# Tests d'intégration collector-MongoDB
docker-compose up test-integration
```

### CI/CD - GitHub Actions

Le projet utilise 3 workflows automatisés :

1. **test.yml** - Tests unitaires du collector
2. **test-api.yml** - Tests unitaires de l'API
3. **test-integration-collector.yml** - Tests d'intégration

Tous les tests s'exécutent automatiquement sur chaque `push` et `pull request`.

---

## 📁 Structure du Projet

```
cryptocurrency-monitoring-platform/
├── .github/
│   └── workflows/              # Pipelines CI/CD
│       ├── test.yml
│       ├── test-api.yml
│       └── test-integration-collector.yml
├── api/                        # Backend API FastAPI
│   ├── main.py                 # Application principale
│   ├── database.py             # Connexion MongoDB
│   ├── test_api.py             # Tests unitaires
│   ├── Dockerfile
│   └── requirements.txt
├── collector/                  # Service de collecte
│   ├── collector.py            # Script principal
│   ├── collector_logic.py      # Logique métier
│   ├── tasks.py                # Tâches Celery
│   ├── test_collector_logic.py # Tests unitaires
│   ├── test_integration_collector.py
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                   # Application React
│   ├── src/
│   │   ├── components/         # Composants React
│   │   │   ├── CryptoList.js
│   │   │   ├── Dashboard.js
│   │   │   └── Navigation.js
│   │   ├── api/
│   │   │   └── cryptoService.js
│   │   └── App.js
│   └── package.json
├── docs/                       # Documentation
│   ├── architecture-diagram.png
│   ├── use-case-diagram.png
│   ├── class-diagram.png
│   └── sequence-diagram.png
├── docker-compose.yml          # Orchestration des services
└── README.md                   # Ce fichier
```

---

## 🔧 Développement Local

### Backend API

```bash
cd api
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend React

```bash
cd frontend
npm install
npm start
```

### Collector (mode test unique)

```bash
cd collector
pip install -r requirements.txt
python collector.py test
```

---

## 📊 Métriques & Qualité

- **Couverture des tests :** Tests unitaires + intégration sur composants critiques
- **CI/CD :** 3 workflows automatisés avec GitHub Actions
- **Conteneurisation :** 100% des services dockerisés
- **Documentation :** README complet + diagrammes UML

### Tests de Qualité (À venir - Sprint 5)

- Tests de performance avec Locust
- Tests de sécurité avec OWASP ZAP
- Analyse qualité avec SonarQube

---

## 🤝 Contribution

Ce projet est développé selon une **méthodologie Agile** (Scrum/Kanban).

### Gestion de Projet

- **Issues GitHub :** Suivi des tâches et bugs
- **GitHub Projects :** Board Kanban avec sprints
- **Milestones :** Organisation par sprints

Voir le board : [Projects](https://github.com/kebdanisouhila218-beep/cryptocurrency-monitoring-platform/projects)

---

## 📚 Documentation Complémentaire

- **Diagramme d'architecture :** [docs/architecture-diagram.png](docs/architecture-diagram.png)
- **Diagramme de cas d'utilisation :** [docs/use-case-diagram.png](docs/use-case-diagram.png)
- **Diagramme de classes :** [docs/class-diagram.png](docs/class-diagram.png)
- **Diagramme de séquence :** [docs/sequence-diagram.png](docs/sequence-diagram.png)

---

## 🐛 Problèmes Connus

- Aucun problème majeur actuellement
- Pour signaler un bug : [Ouvrir une issue](https://github.com/kebdanisouhila218-beep/cryptocurrency-monitoring-platform/issues)

---

## 📄 Licence

Ce projet est développé dans un cadre académique - Master 1 ILSEN (2025)

---

## 👨‍💻 Auteur

**Souhila Aicha Kebdani**  
Master 1 ILSEN - Projet de développement logiciel  
📧 [Contact](mailto:kebdanisouhila218@example.com)  
🔗 [GitHub](https://github.com/kebdanisouhila218-beep)

