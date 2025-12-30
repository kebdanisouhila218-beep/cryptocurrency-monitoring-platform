# 🚀 CryptoTracker - Plateforme de Surveillance des Cryptomonnaies

[![Tests Collector](https://github.com/kebdanisouhila218-beep/cryptocurrency-monitoring-platform/actions/workflows/test.yml/badge.svg)](https://github.com/kebdanisouhila218-beep/cryptocurrency-monitoring-platform/actions/workflows/test.yml)
[![Tests API](https://github.com/kebdanisouhila218-beep/cryptocurrency-monitoring-platform/actions/workflows/test-api.yml/badge.svg)](https://github.com/kebdanisouhila218-beep/cryptocurrency-monitoring-platform/actions/workflows/test-api.yml)
[![Tests Integration](https://github.com/kebdanisouhila218-beep/cryptocurrency-monitoring-platform/actions/workflows/test-integration-collector.yml/badge.svg)](https://github.com/kebdanisouhila218-beep/cryptocurrency-monitoring-platform/actions/workflows/test-integration-collector.yml)
[![Build](https://github.com/kebdanisouhila218-beep/cryptocurrency-monitoring-platform/actions/workflows/build.yml/badge.svg)](https://github.com/kebdanisouhila218-beep/cryptocurrency-monitoring-platform/actions/workflows/build.yml)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![React](https://img.shields.io/badge/React-19+-61DAFB.svg)](https://reactjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688.svg)](https://fastapi.tiangolo.com)
[![MongoDB](https://img.shields.io/badge/MongoDB-6.0+-green.svg)](https://mongodb.com)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> 📊 **Surveillance intelligente des cryptomonnaies en temps réel avec prévisions, alertes et portfolio virtuel.**

[🔴 Démo Live](https://demo.example.com) | [📖 Documentation](docs/) | [🚀 Installation](#installation-rapide)

---

## 📖 Vue d'ensemble

**CryptoTracker** est une plateforme complète de surveillance des cryptomonnaies qui permet de suivre **50 cryptos en temps réel**, générer des **prévisions intelligentes**, configurer des **alertes automatiques** et gérer un **portfolio virtuel**. Développée avec **FastAPI** et **React**, elle utilise des algorithmes de **moyennes mobiles (SMA/EMA)** et **régression linéaire** pour fournir des analyses pertinentes.

![Dashboard](docs/screenshots/dashboard.png)

---

## ✨ Fonctionnalités principales

- 📊 **Surveillance 50 cryptos** en temps réel (prix, volume, market cap)
- 🔮 **Prévisions avancées** : SMA, EMA, Régression Linéaire avec niveaux de confiance
- 🔬 **Indicateurs techniques** : RSI, MACD, Bollinger Bands avec signaux ACHAT/VENTE
- 📈 **Graphiques chandeliers** OHLC avec intervalles configurables
- 🔥 **Heatmap de performance** du marché (top gainers/losers)
- 🔔 **Alertes de prix** personnalisées (Email + Discord)
- 💼 **Portfolio virtuel** avec calcul P&L automatique
- 👤 **Authentification sécurisée** JWT avec hash Argon2
- 🌙 **Mode sombre** avec thème complet
- 📱 **Responsive design** pour mobile/desktop

---

## 🏗️ Architecture technique

### Backend
- **Python 3.11+** avec **FastAPI** pour l'API REST
- **MongoDB** pour le stockage des prix et données utilisateur
- **Redis** + **Celery** pour les tâches asynchrones (collecte, alertes)
- **Pydantic** pour la validation des données
- **JWT** pour l'authentification

### Frontend
- **React 19** avec hooks modernes
- **Recharts** pour les graphiques interactifs
- **Axios** pour les appels API
- **CSS variables** pour le thème clair/sombre

### DevOps
- **Docker Compose** pour le déploiement
- **GitHub Actions** pour la CI/CD
- **Tests unitaires** et d'intégration

```
┌─────────────┐
│ CoinPaprika │
└──────┬──────┘
       ↓
┌─────────────┐    ┌─────────────┐
│  Collector  │ → │   MongoDB   │
└─────────────┘    └──────┬──────┘
                          ↓
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Redis +   │ ← │ API FastAPI │ → │ React Front │
│   Celery    │    └─────────────┘    └─────────────┘
└─────────────┘
```

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
| 11 | Documentation | ✅ | 1 sem |

---

## 📊 Statistiques du projet

- **Total lignes de code** : ~16,800
- **Backend (Python)** : ~6,500 lignes
- **Frontend (JS/JSX/CSS)** : ~9,800 lignes
- **Tests** : ~500 lignes
- **Fichiers** : ~100
- **Collections MongoDB** : 6
- **Endpoints API** : 25+

---

## 📚 Documentation

- 📖 [Guide d'installation](docs/INSTALLATION.md)
- 🔌 [Documentation API](docs/API_DOCS.md)
- 👥 [Guide utilisateur](docs/USER_GUIDE.md)
- 🎓 [Présentation soutenance](docs/PRESENTATION_SOUTENANCE.pptx)
- 📄 [Rapport final](docs/RAPPORT_FINAL.docx)

---

## 🧪 Tests

```bash
# Tests backend
cd api && python -m pytest

# Tests collector
cd collector && python -m pytest

# Tests frontend
cd frontend && npm test

# CI/CD automatique sur GitHub Actions
```

- **Tests unitaires** : Collector, API, Utils
- **Tests d'intégration** : MongoDB, Redis
- **Coverage** : ~75%
- **Workflows CI/CD** : 3 (tests, build, deploy)

---

## 🛡️ Sécurité

- 🔐 **Authentification JWT** avec tokens expirants
- 🔒 **Hash mots de passe** Argon2/Bcrypt
- ✅ **Validation des entrées** avec Pydantic
- 🌐 **CORS configuré** pour le frontend
- 🚫 **Pas de secrets** dans le code (variables .env)

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
- **Formation** : Master 1 ILSEN - 2024/2025

---

## 📜 Licence

Ce projet est sous licence **MIT** - voir le fichier [LICENSE](LICENSE) pour les détails.

---

<div align="center">

**Merci d'utiliser CryptoTracker ! 🚀**

[⭐ Give a star](https://github.com/kebdanisouhila218-beep/cryptocurrency-monitoring-platform) | [🐛 Report a bug](issues) | [💡 Suggest a feature](issues)

</div>
