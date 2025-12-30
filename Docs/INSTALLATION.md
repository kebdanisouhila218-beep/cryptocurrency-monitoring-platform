# 📖 Guide d'Installation - CryptoTracker

> 🚀 **Instructions complètes** pour installer et lancer la plateforme de surveillance des cryptomonnaies en développement ou production.

---

## 📋 Prérequis

Avant de commencer, assurez-vous d'avoir installé :

- **Docker** & **Docker Compose** (recommandé)
- **Python 3.11+** (si installation manuelle)
- **Node.js 18+** (si installation manuelle)
- **Git**
- **MongoDB** (si pas Docker)
- **Redis** (si pas Docker)

---

## 🐳 Installation avec Docker (RECOMMANDÉ)

### Étape 1 : Cloner le projet

```bash
git clone https://github.com/kebdanisouhila218-beep/cryptocurrency-monitoring-platform.git
cd cryptocurrency-monitoring-platform
```

### Étape 2 : Configuration

```bash
# Copier le fichier d'environnement exemple
cp .env.example .env

# Éditer .env avec vos configurations
nano .env  # ou votre éditeur préféré
```

**Variables à configurer dans `.env` :**

```env
# Clé secrète JWT (générez une longue chaîne aléatoire)
SECRET_KEY=votre-cle-secrete-tres-longue-ici

# Base de données MongoDB
MONGO_URI=mongodb://localhost:27017/
DB_NAME=crypto_db

# Redis
REDIS_URL=redis://localhost:6379/0

# Configuration Email (pour alertes)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=votre-email@gmail.com
SMTP_PASSWORD=votre-mot-de-passe-app

# Webhook Discord (optionnel)
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...

# API CoinPaprika (gratuit)
COINPAPRIKA_API_KEY=votre-api-key-coinpaprika
```

### Étape 3 : Lancement

```bash
# Démarrer tous les services
docker-compose up -d

# Vérifier que tout tourne
docker-compose ps
```

### Étape 4 : Vérification

```bash
# Vérifier l'API
curl http://localhost:8000/health

# Vérifier le frontend
# Ouvrir http://localhost:3000 dans votre navigateur
```

> ✅ **Félicitations !** CryptoTracker est maintenant accessible.

---

## 💻 Installation Développement (sans Docker)

### Backend API

```bash
# 1. Aller dans le dossier API
cd api

# 2. Créer un environnement virtuel
python -m venv venv

# 3. Activer l'environnement
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 4. Installer les dépendances
pip install -r requirements.txt

# 5. Créer le fichier .env (voir configuration ci-dessus)
cp .env.example .env
# Éditer .env

# 6. Démarrer l'API
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend React

```bash
# 1. Aller dans le dossier frontend
cd frontend

# 2. Installer les dépendances
npm install

# 3. Démarrer le serveur de développement
npm start
```

### Collector (tâches de fond)

```bash
# 1. Aller dans le dossier collector
cd collector

# 2. Créer un environnement virtuel
python -m venv venv

# 3. Activer l'environnement
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 4. Installer les dépendances
pip install -r requirements.txt

# 5. Créer le fichier .env (même configuration que l'API)
cp .env.example .env
# Éditer .env

# 6. Terminal 1 : Démarrer le worker Celery
celery -A tasks worker --loglevel=info

# 7. Terminal 2 : Démarrer le scheduler Celery Beat
celery -A tasks beat --loglevel=info
```

---

## 🗄️ Configuration MongoDB

### Si MongoDB n'est pas dans Docker

```bash
# Installer MongoDB (suivre la doc officielle pour votre OS)
# Démarrer MongoDB
mongod --dbpath /data/db

# Importer des données de test (optionnel)
cd api
python scripts/import_test_data.py
```

### Vérification MongoDB

```bash
# Se connecter à MongoDB
mongosh

# Vérifier la base de données
use crypto_db
db.prices.find().limit(5)
db.users.find().limit(5)
```

---

## 🔴 Configuration Redis

### Si Redis n'est pas dans Docker

```bash
# Installer Redis
# Démarrer Redis
redis-server

# Vérifier Redis
redis-cli ping
# Doit répondre : PONG
```

---

## 🔧 Variables d'Environnement

| Variable | Description | Exemple |
|----------|-------------|---------|
| `SECRET_KEY` | Clé secrète pour JWT | `"votre-cle-secrete-256bits"` |
| `MONGO_URI` | URI de connexion MongoDB | `"mongodb://localhost:27017/"` |
| `DB_NAME` | Nom de la base de données | `"crypto_db"` |
| `REDIS_URL` | URL de connexion Redis | `"redis://localhost:6379/0"` |
| `SMTP_HOST` | Serveur SMTP | `"smtp.gmail.com"` |
| `SMTP_PORT` | Port SMTP | `587` |
| `SMTP_USER` | Email SMTP | `"votre@email.com"` |
| `SMTP_PASSWORD` | Mot de passe SMTP | `"votre-mot-de-passe-app"` |
| `DISCORD_WEBHOOK_URL` | Webhook Discord notifications | `"https://discord.com/api/webhooks/..."` |
| `COINPAPRIKA_API_KEY` | Clé API CoinPaprika | `"votre-api-key"` |

---

## ✅ Vérification que tout fonctionne

### 1. API Backend

```bash
curl http://localhost:8000/health
# Réponse attendue : {"status": "healthy"}
```

### 2. Frontend

- Ouvrir `http://localhost:3000` dans votre navigateur
- Vous devriez voir la page de connexion

### 3. MongoDB

```bash
# Si Docker
docker exec -it mongo mongosh

# Si local
mongosh

> use crypto_db
> db.prices.find().limit(5)
> db.users.find().limit(5)
```

### 4. Redis

```bash
# Si Docker
docker exec -it redis redis-cli ping

# Si local
redis-cli ping
# Réponse : PONG
```

### 5. Collector

```bash
# Vérifier les logs Celery
# Dans le terminal du worker, vous devriez voir :
# [INFO] Starting collection...
# [INFO] Collected 50 prices
```

---

## 🚨 Troubleshooting

### Port 3000 déjà utilisé

```bash
# Trouver le processus
lsof -ti:3000

# Tuer le processus
lsof -ti:3000 | xargs kill -9
```

### Erreur de connexion MongoDB

```bash
# Vérifier que MongoDB tourne
docker-compose ps  # ou ps aux | grep mongod

# Redémarrer MongoDB
docker-compose restart mongo
```

### Celery ne fonctionne pas

```bash
# Vérifier Redis
redis-cli ping

# Redémarrer Redis
docker-compose restart redis

# Redémarrer Celery
docker-compose restart collector
```

### Erreur JWT

```bash
# Vérifier que SECRET_KEY est défini dans .env
grep SECRET_KEY .env

# Régénérer une clé si nécessaire
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Frontend ne se connecte pas à l'API

```bash
# Vérifier que l'API tourne
curl http://localhost:8000/health

# Vérifier la configuration CORS dans api/main.py
# Assurez-vous que localhost:3000 est autorisé
```

---

## 🚀 Déployment en Production (optionnel)

### Avec Kubernetes

```bash
# Utiliser les manifests dans k8s/
kubectl apply -f k8s/
```

### Configuration HTTPS avec Nginx

```bash
# Installer Certbot
sudo apt install certbot python3-certbot-nginx

# Obtenir un certificat SSL
sudo certbot --nginx -d votredomaine.com
```

### Sécuriser MongoDB

```bash
# Créer un utilisateur MongoDB
mongo
> use admin
> db.createUser({user: "admin", pwd: "password", roles: ["root"]})

# Activer l'authentification dans mongod.conf
security:
  authorization: enabled
```

### Monitoring avec Prometheus + Grafana

```bash
# Ajouter Prometheus et Grafana à docker-compose.yml
# Configurer les dashboards de monitoring
```

---

## 📞 Aide

Si vous rencontrez des problèmes :

1. Vérifiez les logs avec `docker-compose logs [service]`
2. Consultez la [documentation API](API_DOCS.md)
3. Ouvrez une [issue sur GitHub](https://github.com/kebdanisouhila218-beep/cryptocurrency-monitoring-platform/issues)

---

<div align="center">

**Installation terminée ! 🎉**

[🏠 Retour à l'accueil](../README.md) | [📚 Documentation API](API_DOCS.md) | [👥 Guide utilisateur](USER_GUIDE.md)

</div>
