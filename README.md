# 🚀 CryptoTracker - Plateforme de Surveillance des Cryptomonnaies

[![CI/CD Pipeline](https://github.com/kebdanisouhila218-beep/cryptocurrency-monitoring-platform/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/kebdanisouhila218-beep/cryptocurrency-monitoring-platform/actions/workflows/ci-cd.yml)
[![Security Tests](https://github.com/kebdanisouhila218-beep/cryptocurrency-monitoring-platform/actions/workflows/security-tests.yml/badge.svg)](https://github.com/kebdanisouhila218-beep/cryptocurrency-monitoring-platform/actions/workflows/security-tests.yml)
[![Performance Tests](https://github.com/kebdanisouhila218-beep/cryptocurrency-monitoring-platform/actions/workflows/performance-tests.yml/badge.svg)](https://github.com/kebdanisouhila218-beep/cryptocurrency-monitoring-platform/actions/workflows/performance-tests.yml)
[![Tests API](https://github.com/kebdanisouhila218-beep/cryptocurrency-monitoring-platform/actions/workflows/test-api.yml/badge.svg)](https://github.com/kebdanisouhila218-beep/cryptocurrency-monitoring-platform/actions/workflows/test-api.yml)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![React](https://img.shields.io/badge/React-19+-61DAFB.svg)](https://reactjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688.svg)](https://fastapi.tiangolo.com)
[![MongoDB](https://img.shields.io/badge/MongoDB-6.0+-green.svg)](https://mongodb.com)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg)](https://docker.com)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-Ready-326CE5.svg)](https://kubernetes.io)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> 📊 **Surveillance intelligente des cryptomonnaies en temps réel avec prévisions, alertes, portfolio virtuel et panel d'administration.**

[🔴 Démo Live](https://demo.example.com) | [📖 Documentation](Docs/) | [🚀 Installation](#installation-rapide) | [☸️ Kubernetes](Docs/KUBERNETES_DEPLOYMENT.md)

---

## 📖 Vue d'ensemble

**CryptoTracker** est une plateforme complète de surveillance des cryptomonnaies qui permet de suivre **50 cryptos en temps réel**, générer des **prévisions intelligentes**, configurer des **alertes automatiques** et gérer un **portfolio virtuel**. Développée avec **FastAPI** et **React**, elle utilise des algorithmes de **moyennes mobiles (SMA/EMA)** et **régression linéaire** pour fournir des analyses pertinentes.

![Dashboard](docs/screenshots/dashboard.png)

---

## ✨ Fonctionnalités principales

### 📊 Surveillance & Analytics
- 📊 **Surveillance 50 cryptos** en temps réel (prix, volume, market cap)
- 🔮 **Prévisions avancées** : SMA, EMA, Régression Linéaire avec niveaux de confiance
- 🔬 **Indicateurs techniques** : RSI, MACD, Bollinger Bands avec signaux ACHAT/VENTE
- 📈 **Graphiques chandeliers** OHLC avec intervalles configurables
- 🔥 **Heatmap de performance** du marché (top gainers/losers)

### 🔔 Alertes & Notifications
- 🔔 **Alertes de prix** personnalisées (seuil, pourcentage)
- 📧 **Notifications Email** automatiques
- 💬 **Webhooks Discord** pour alertes instantanées

### 💼 Portfolio
- 💼 **Portfolio virtuel** avec calcul P&L automatique
- 📈 **Simulation trading** achat/vente sans risque
- 📊 **Historique transactions** complet

### 👤 Utilisateurs & Admin
- 👤 **Authentification sécurisée** JWT avec hash Argon2
- 🛡️ **Panel Admin** : gestion utilisateurs, statistiques, logs système
- 👥 **Rôles** : Utilisateur et Administrateur

### 🎨 Interface
- 🌙 **Mode sombre** avec thème complet
- 📱 **Responsive design** pour mobile/desktop

### ☸️ DevOps & Monitoring
- 🐳 **Docker Compose** avec 15 services
- ☸️ **Kubernetes** ready (Minikube/Kind)
- 📈 **Prometheus + Grafana** pour le monitoring
- 📝 **Loki** pour les logs centralisés
- 🔒 **Tests sécurité** : Trivy, Snyk, OWASP ZAP
- ⚡ **Tests performance** : Locust, k6

---

## 🏗️ Architecture technique

### Backend (Python)
- **FastAPI** pour l'API REST haute performance
- **MongoDB** pour le stockage des prix et données utilisateur
- **Redis** + **Celery** pour les tâches asynchrones
- **Pydantic** pour la validation des données
- **JWT** + **Argon2** pour l'authentification sécurisée
- **Prometheus client** pour les métriques

### Frontend (React)
- **React 19** avec hooks modernes
- **Recharts** pour les graphiques interactifs
- **Axios** pour les appels API
- **CSS variables** pour le thème clair/sombre
- **Panel Admin** complet

### DevOps & Infrastructure
- **Docker Compose** avec 15 services
- **Kubernetes** (Minikube/Kind) pour l'orchestration
- **GitHub Actions** avec 12 workflows CI/CD
- **Prometheus + Grafana** pour le monitoring
- **Loki + Promtail** pour les logs centralisés
- **AlertManager** pour les alertes système

### Diagramme d'Architecture

![Diagramme d'Architecture](Docs/Diagramme%20d'Architecture.png)

---

## 🚀 Installation rapide

```bash
# 1. Cloner le projet
git clone https://github.com/kebdanisouhila218-beep/cryptocurrency-monitoring-platform.git
cd cryptocurrency-monitoring-platform

# 2. Configurer l'environnement
cp .env.example .env
# Éditer .env avec vos clés (SMTP, Discord, SECRET_KEY)

# 3. Lancer avec Docker
docker-compose up -d

# 4. Accéder à l'application
# Frontend : http://localhost:3000
# API : http://localhost:8000
# Documentation API : http://localhost:8000/docs
```

> ⚡ **Prêt en 2 minutes !** Tous les services démarreront automatiquement.

---

## 📅 Sprints réalisés

| Sprint | Fonctionnalité | Status | Durée |
|--------|----------------|--------|-------|
| 1-2 | Collecte + API + React | ✅ | 2 sem |
| 3-4 | Tests + JWT Auth | ✅ | 1.5 sem |
| 5-7 | Alertes + Portfolio | ✅ | 2 sem |
| 8-10 | Prévisions + Indicators + Viz | ✅ | 3 sem |
| 11 | Documentation + Diagrammes | ✅ | 1 sem |
| 12 | Panel Admin + Rôles | ✅ | 1 sem |
| 13 | Kubernetes + Monitoring avancé | ✅ | 1.5 sem |
| 14 | CI/CD + Tests Sécurité/Performance | ✅ | 1 sem |

---

## 📊 Statistiques du projet

| Métrique | Valeur |
|----------|--------|
| **Total lignes de code** | ~20,000+ |
| **Backend (Python)** | ~8,500 lignes |
| **Frontend (JS/JSX/CSS)** | ~11,000 lignes |
| **Tests** | ~1,500 lignes |
| **Fichiers** | ~150+ |
| **Collections MongoDB** | 6 |
| **Endpoints API** | **35+** |
| **Workflows CI/CD** | **12** |
| **Services Docker** | **15** |
| **Diagrammes UML** | **10** |

---

## 📚 Documentation

### Guides
- 📖 [Guide d'installation](Docs/INSTALLATION.md)
- 🔌 [Documentation API](Docs/API_DOCS.md)
- 👥 [Guide utilisateur](Docs/USER_GUIDE.md)
- 🎓 [Présentation soutenance](Docs/PRESENTATION_SOUTENANCE.md)

### DevOps
- 🛠️ [CI/CD Pipeline](Docs/CICD.md)
- ☸️ [Déploiement Kubernetes](Docs/KUBERNETES_DEPLOYMENT.md)
- 📈 [Monitoring](Docs/MONITORING.md)
- 🧪 [Tests Performance & Sécurité](Docs/PERFORMANCE_SECURITY_TESTS.md)

### 📊 Diagrammes UML

| Diagramme | Description |
|-----------|-------------|
| [🏗️ Architecture](Docs/Diagramme%20d'Architecture.png) | Vue des composants du système |
| [🚀 Déploiement](Docs/Diagramme%20de%20Déploiement.png) | Infrastructure Docker/Cloud |
| [👤 Cas d'utilisation](Docs/Diagramme%20de%20Cas%20d'Utilisation.png) | Fonctionnalités utilisateur |
| [📊 Classes](Docs/Diagramme%20de%20Classes%20(Modèles).png) | Modèles de données |
| [🔐 Séquence Auth](Docs/Diagramme%20de%20Séquence%20-%20Authentification.png) | Flux d'authentification |
| [🔔 Séquence Alerte](Docs/Diagramme%20de%20Séquence%20-%20Création%20d'Alerte.png) | Création et déclenchement |
| [💱 Séquence Trading](Docs/Diagramme%20de%20Séquence%20-%20Trading%20Virtuel.png) | Simulation d'achat/vente |
| [📊 Activité Trading](Docs/Diagramme%20d'Activité%20-%20Flux%20de%20Trading.png) | Flux de trading |
| [🔄 État Alerte](Docs/Diagramme%20d'État%20-%20Cycle%20de%20Vie%20d'une%20Alerte.png) | Cycle de vie alerte |
| [⚙️ CI/CD Pipeline](Docs/Diagramme%20CI-CD%20Pipeline.png) | Pipeline GitHub Actions |

---

## 🧪 Tests

```bash
# Tests backend
cd api && python -m pytest -v

# Tests collector
cd collector && python -m pytest -v

# Tests frontend
cd frontend && npm test

# Tests de performance (Locust)
locust -f tests/performance/locustfile_web.py --host=http://localhost:8000

# Tests de sécurité
python tests/security/zap_scan.py --target http://localhost:8000
```

### Types de tests
| Type | Outils | Description |
|------|--------|-------------|
| **Unitaires** | pytest | API, Collector, Services |
| **Intégration** | pytest + Docker | MongoDB, Redis |
| **Performance** | Locust, k6 | Load testing, stress testing |
| **Sécurité** | Trivy, Snyk, ZAP | Vulnérabilités, dépendances |
| **E2E** | Playwright | Tests end-to-end |

- **Coverage** : ~75%
- **Workflows CI/CD** : 12 (tests, build, security, performance, deploy)

---

## 🛡️ Sécurité

### Authentification & Autorisation
- 🔐 **JWT** avec tokens expirants (30 min)
- 🔒 **Hash mots de passe** Argon2/Bcrypt
- 👥 **Rôles** : User et Admin avec guards

### Protection des données
- ✅ **Validation** avec Pydantic
- 🌐 **CORS** configuré strictement
- 🚫 **Secrets** en variables d'environnement

### Tests de sécurité automatisés
- 🔍 **Trivy** : Scan des images Docker
- 📦 **Snyk** : Vulnérabilités des dépendances
- 🕷️ **OWASP ZAP** : Tests de pénétration

---

## 🤝 Contribuer

1. Fork le projet
2. Créer une branche (`git checkout -b feature/nouvelle-fonction`)
3. Commit (`git commit -m 'Ajout nouvelle fonction'`)
4. Push (`git push origin feature/nouvelle-fonction`)
5. Ouvrir une Pull Request

---

## 📞 Contact

- **Nom** : Souhila Aicha Kebdani
- **Email** : kebdanisouhila218@gmail.com
- **GitHub** : [@kebdanisouhila218-beep](https://github.com/kebdanisouhila218-beep)
- **Formation** : Master 1 ILSEN - 2025/2026

---

## 📜 Licence

Ce projet est sous licence **MIT** - voir le fichier [LICENSE](LICENSE) pour les détails.

---

<div align="center">

**Merci d'utiliser CryptoTracker ! 🚀**

[⭐ Give a star](https://github.com/kebdanisouhila218-beep/cryptocurrency-monitoring-platform) | [🐛 Report a bug](issues) | [💡 Suggest a feature](issues)

</div>
