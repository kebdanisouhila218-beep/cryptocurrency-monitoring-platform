# 🔧 SETUP - Configuration du Projet CryptoTracker

> 📚 Guide de configuration pour le développement et le déploiement.

---

## 📋 Table des matières

1. [Prérequis](#prérequis)
2. [Configuration locale](#configuration-locale)
3. [Secrets GitHub](#secrets-github)
4. [Services externes](#services-externes)
5. [Tests](#tests)
6. [Déploiement](#déploiement)

---

## 🔧 Prérequis

### Logiciels requis

| Logiciel | Version | Installation |
|----------|---------|--------------|
| **Python** | 3.10+ | [python.org](https://python.org) |
| **Node.js** | 18+ | [nodejs.org](https://nodejs.org) |
| **Docker** | 20+ | [docker.com](https://docker.com) |
| **Git** | 2.30+ | [git-scm.com](https://git-scm.com) |

### Vérification

```bash
python --version   # Python 3.10+
node --version     # v18+
docker --version   # Docker 20+
git --version      # git 2.30+
```

---

## 🏠 Configuration locale

### 1. Cloner le projet

```bash
git clone https://github.com/kebdanisouhila218-beep/cryptocurrency-monitoring-platform.git
cd cryptocurrency-monitoring-platform
```

### 2. Configurer les variables d'environnement

```bash
# Copier le template
cp .env.example .env

# Éditer avec vos valeurs
# Windows: notepad .env
# Linux/Mac: nano .env
```

### 3. Variables d'environnement requises

```bash
# .env - Configuration minimale

# MongoDB
MONGO_HOST=localhost
MONGO_PORT=27017
MONGO_URI=mongodb://localhost:27017/

# JWT (générer une clé secrète)
SECRET_KEY=votre_cle_secrete_longue_et_aleatoire

# API
API_HOST=0.0.0.0
API_PORT=8000
```

### 4. Démarrer avec Docker Compose

```bash
# Démarrer tous les services
docker-compose up -d

# Vérifier l'état
docker-compose ps

# Voir les logs
docker-compose logs -f
```

### 5. Accéder à l'application

| Service | URL |
|---------|-----|
| **Frontend** | http://localhost:3000 |
| **API** | http://localhost:8000 |
| **API Docs** | http://localhost:8000/docs |
| **MongoDB** | localhost:27017 |

---

## 🔐 Secrets GitHub

Pour les déploiements CI/CD, configurer ces secrets dans GitHub :

**Repository → Settings → Secrets and variables → Actions**

### Secrets obligatoires

| Secret | Description | Exemple |
|--------|-------------|---------|
| `SSH_PRIVATE_KEY` | Clé SSH pour staging | Contenu de `~/.ssh/id_rsa` |
| `SSH_PRIVATE_KEY_PROD` | Clé SSH pour production | Contenu de `~/.ssh/id_rsa_prod` |
| `STAGING_HOST` | IP serveur staging | `192.168.1.100` |
| `STAGING_USER` | User SSH staging | `deploy` |
| `PRODUCTION_HOST` | IP serveur production | `10.0.0.50` |
| `PRODUCTION_USER` | User SSH production | `deploy` |

### Secrets optionnels

| Secret | Description |
|--------|-------------|
| `DISCORD_WEBHOOK_URL` | Webhook Discord pour notifications |
| `STAGING_API_URL` | URL API staging pour health check |
| `PRODUCTION_API_URL` | URL API production pour health check |

### Générer une clé SSH

```bash
# Générer une nouvelle clé
ssh-keygen -t rsa -b 4096 -C "github-actions@crypto-platform.com" -f ~/.ssh/id_rsa_deploy

# Copier la clé publique sur le serveur
ssh-copy-id -i ~/.ssh/id_rsa_deploy.pub user@server

# Afficher la clé privée (à copier dans GitHub Secrets)
cat ~/.ssh/id_rsa_deploy
```

---

## 🌐 Services externes

### MongoDB

**Option 1 : Docker (local)**
```bash
docker run -d -p 27017:27017 --name mongodb mongo:6
```

**Option 2 : MongoDB Atlas (cloud)**
1. Créer un compte sur [mongodb.com/atlas](https://mongodb.com/atlas)
2. Créer un cluster gratuit (M0)
3. Récupérer la connection string
4. Configurer dans `.env` :
   ```bash
   MONGO_URI=mongodb+srv://user:password@cluster.mongodb.net/crypto_db
   ```

### Redis (optionnel)

**Docker :**
```bash
docker run -d -p 6379:6379 --name redis redis:7-alpine
```

**Configuration :**
```bash
REDIS_HOST=localhost
REDIS_PORT=6379
```

### API CoinPaprika

- **Gratuit** : 25,000 requêtes/mois
- **Pas de clé requise** pour l'usage basique
- Documentation : [api.coinpaprika.com](https://api.coinpaprika.com)

---

## 🧪 Tests

### Tests Backend (Python/Pytest)

```bash
# Installer les dépendances
cd api
pip install -r requirements.txt
pip install pytest pytest-cov

# Lancer les tests
pytest -v

# Avec couverture
pytest --cov=. --cov-report=html
```

### Tests Frontend (Jest)

```bash
# Installer les dépendances
cd frontend
npm install

# Lancer les tests
npm test

# Avec couverture
npm run test:coverage
```

### Tests d'intégration

```bash
# Démarrer MongoDB
docker run -d -p 27017:27017 mongo:6

# Lancer les tests d'intégration
cd collector
pytest test_integration_collector.py -v
```

### Tous les tests

```powershell
# Windows
.\run_all_tests.ps1

# Linux/Mac
./run_all_tests.sh
```

---

## 🚀 Déploiement

### Déploiement Docker local

```bash
# Build des images
docker-compose build

# Démarrer
docker-compose up -d

# Vérifier
docker-compose ps
```

### Déploiement staging (develop)

Le déploiement staging est automatique sur push vers `develop` :

```bash
git checkout develop
git push origin develop
# → GitHub Actions déploie automatiquement
```

### Déploiement production (main)

Le déploiement production est automatique sur push vers `main` :

```bash
git checkout main
git merge develop
git push origin main
# → GitHub Actions déploie automatiquement
```

### Déploiement manuel

```bash
# Sur le serveur
cd ~/crypto-platform

# Pull les images
docker-compose pull

# Redémarrer
docker-compose up -d

# Vérifier
docker-compose ps
```

---

## 📊 Monitoring

### Health checks

```bash
# API
curl http://localhost:8000/health

# Frontend
curl http://localhost:3000
```

### Logs

```bash
# Tous les services
docker-compose logs -f

# Service spécifique
docker-compose logs -f api
docker-compose logs -f frontend
docker-compose logs -f collector
```

### Métriques

- **GitHub Actions** : https://github.com/REPO/actions
- **Docker** : `docker stats`

---

## 🔧 Dépannage

### MongoDB ne démarre pas

```bash
# Vérifier les logs
docker-compose logs mongo

# Supprimer les données et redémarrer
docker-compose down -v
docker-compose up -d
```

### API ne répond pas

```bash
# Vérifier les logs
docker-compose logs api

# Redémarrer
docker-compose restart api
```

### Tests échouent

```bash
# Backend - vérifier les dépendances
cd api && pip install -r requirements.txt

# Frontend - réinstaller node_modules
cd frontend && rm -rf node_modules && npm install
```

---

## 📚 Ressources

- [Pydantic V2 Migration](https://docs.pydantic.dev/latest/migration/)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [React Testing Library](https://testing-library.com/docs/react-testing-library/intro/)
- [GitHub Actions](https://docs.github.com/en/actions)
- [Docker Compose](https://docs.docker.com/compose/)

---

<div align="center">

**CryptoTracker Setup Guide** 🚀

[🏠 README](README.md) | [📖 Installation](docs/INSTALLATION.md) | [🧪 Tests](docs/TESTING.md)

</div>
