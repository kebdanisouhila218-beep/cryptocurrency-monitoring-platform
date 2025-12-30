# 🚀 CI/CD Pipeline - CryptoTracker

> 📚 **Documentation complète** du pipeline CI/CD pour la plateforme de surveillance crypto.

---

## 📋 Vue d'ensemble

Notre pipeline CI/CD automatise :

| Étape | Description | Déclencheur |
|-------|-------------|-------------|
| ✅ **Tests** | Unitaires + Intégration | Chaque push/PR |
| 🐳 **Build** | Images Docker | Push main/develop |
| 🚀 **Deploy Staging** | Environnement de test | Push develop |
| 🚀 **Deploy Production** | Environnement live | Push main |
| 📬 **Notifications** | Discord/Email | Succès/Échec |
| ⏪ **Rollback** | Retour arrière auto | Échec health check |

---

## 🔄 Workflows GitHub Actions

### Structure des fichiers

```
.github/workflows/
├── test.yml                    # Tests Collector (existant)
├── test-api.yml                # Tests API (existant)
├── test-integration-collector.yml  # Tests intégration (existant)
├── build.yml                   # Build Docker images
├── deploy-staging.yml          # Déploiement staging
├── deploy-production.yml       # Déploiement production
└── pipeline.yml                # Pipeline complet
```

### Total : **7 workflows**

---

## 🧪 Workflows de Tests (1-3)

### Workflow 1 : Tests Collector
```yaml
# .github/workflows/test.yml
- Déclenchement : Push/PR
- Tests : collector/test_collector_logic.py
- Durée : ~2 minutes
```

### Workflow 2 : Tests API
```yaml
# .github/workflows/test-api.yml
- Déclenchement : Push/PR
- Tests : api/test_api.py
- Durée : ~3 minutes
```

### Workflow 3 : Tests Intégration
```yaml
# .github/workflows/test-integration-collector.yml
- Déclenchement : Push/PR
- Tests : Collector → MongoDB
- Services : MongoDB Docker
- Durée : ~5 minutes
```

---

## 🐳 Workflow Build (4)

### `.github/workflows/build.yml`

**Déclenchement :** Push sur `main` ou `develop`

**Jobs :**
1. `build-collector` - Image collector
2. `build-api` - Image API
3. `build-frontend` - Image frontend
4. `notify` - Notification Discord

**Images générées :**
```
ghcr.io/kebdanisouhila218-beep/crypto-platform-collector:TAG
ghcr.io/kebdanisouhila218-beep/crypto-platform-api:TAG
ghcr.io/kebdanisouhila218-beep/crypto-platform-frontend:TAG
```

**Tags :**
- `main` - Branche principale
- `develop` - Branche développement
- `v1.0.0` - Tags de version
- `sha-abc1234` - Commit SHA

---

## 🚀 Workflow Deploy Staging (5)

### `.github/workflows/deploy-staging.yml`

**Déclenchement :** Push sur `develop`

**Étapes :**
1. ✅ Exécuter les tests
2. 🐳 Build des images
3. 🚀 Déploiement SSH
4. 🏥 Health check
5. 📬 Notification

**Environnement :** `staging`

---

## 🚀 Workflow Deploy Production (6)

### `.github/workflows/deploy-production.yml`

**Déclenchement :** Push sur `main` ou tag `v*`

**Étapes :**
1. ✅ Suite de tests complète
2. 🐳 Build images production
3. 🚀 Déploiement zero-downtime
4. 🏥 Health check
5. ⏪ Rollback si échec
6. 📦 Création release GitHub
7. 📬 Notification

**Environnement :** `production`

**Sécurités :**
- Approbation manuelle requise
- Rollback automatique
- Health checks

---

## 🔄 Workflow Pipeline Complet (7)

### `.github/workflows/pipeline.yml`

**Déclenchement :** Push sur `main`, `develop`, ou PR

**Diagramme du Pipeline CI/CD :**

![Diagramme CI-CD Pipeline](Diagramme%20CI-CD%20Pipeline.png)

---

## 🔐 Secrets GitHub à Configurer

### Repository → Settings → Secrets → Actions

| Secret | Description | Obligatoire |
|--------|-------------|-------------|
| `SSH_PRIVATE_KEY` | Clé SSH staging | Oui (deploy) |
| `SSH_PRIVATE_KEY_PROD` | Clé SSH production | Oui (deploy) |
| `STAGING_HOST` | IP serveur staging | Oui (deploy) |
| `STAGING_USER` | User SSH staging | Oui (deploy) |
| `PRODUCTION_HOST` | IP serveur production | Oui (deploy) |
| `PRODUCTION_USER` | User SSH production | Oui (deploy) |
| `DISCORD_WEBHOOK_URL` | Webhook Discord | Non |
| `STAGING_API_URL` | URL API staging | Non |
| `PRODUCTION_API_URL` | URL API production | Non |

### Générer une clé SSH

```bash
# Générer la clé
ssh-keygen -t rsa -b 4096 -C "github-actions@crypto-platform.com"

# Copier la clé publique sur le serveur
ssh-copy-id user@your-server.com

# Copier la clé PRIVÉE dans les secrets GitHub
cat ~/.ssh/id_rsa
```

---

## 🌿 Stratégie de Branches

```
main        → Production (déploiement auto)
develop     → Staging (déploiement auto)
feature/*   → Tests seulement (PR vers develop)
hotfix/*    → Tests + PR vers main
```

### Workflow de développement

```bash
# 1. Créer une feature
git checkout develop
git checkout -b feature/nouvelle-fonction

# 2. Développer et commiter
git add .
git commit -m "feat: nouvelle fonction"

# 3. Pousser et créer PR
git push origin feature/nouvelle-fonction
# → Créer PR vers develop sur GitHub
# → Tests automatiques

# 4. Merger dans develop
# → Déploiement staging automatique

# 5. Merger develop dans main
git checkout main
git merge develop
git push origin main
# → Déploiement production automatique
```

---

## ⏪ Rollback

### Automatique (production)

En cas d'échec du health check :
1. ❌ Health check échoue
2. ⚠️ Workflow détecte l'échec
3. ⏪ Rollback vers dernière version stable
4. 📬 Notification d'alerte

### Manuel

```bash
# Via SSH
ssh user@production-server
cd ~/crypto-platform

# Trouver le dernier backup
ls -la backup-*.yml

# Restaurer
cp backup-YYYYMMDD-HHMMSS.yml docker-compose.yml
docker-compose up -d
```

---

## 📊 Monitoring

### URLs de monitoring

| Environnement | URL |
|---------------|-----|
| GitHub Actions | `github.com/REPO/actions` |
| Staging Health | `https://staging-api.example.com/health` |
| Production Health | `https://api.example.com/health` |
| Docker Packages | `github.com/REPO/packages` |

### Vérifier l'état

```bash
# Santé de l'API
curl https://api.crypto-platform.com/health

# Logs Docker
docker-compose logs -f api

# État des conteneurs
docker-compose ps
```

---

## 🎓 Pour la Soutenance

### Ce que vous pouvez dire :

> "Le projet inclut un **pipeline CI/CD complet** avec **7 workflows GitHub Actions** :
> 
> 1. **3 workflows de tests** : Collector, API, Intégration
> 2. **1 workflow de build** : Construction des images Docker
> 3. **2 workflows de déploiement** : Staging et Production
> 4. **1 workflow pipeline** : Orchestration complète
> 
> Le tout avec **zero-downtime deployment**, **rollback automatique**, et **notifications Discord**."

### Démo en live :

```bash
# 1. Montrer les workflows sur GitHub
→ github.com/YOUR_REPO/actions

# 2. Montrer les images Docker
→ github.com/YOUR_REPO/packages

# 3. Déclencher un build (optionnel)
git commit --allow-empty -m "demo: trigger CI/CD"
git push origin main
```

---

## 📝 Commandes utiles

```bash
# Voir les workflows en cours
gh run list

# Voir les logs d'un workflow
gh run view <run-id> --log

# Déclencher manuellement
gh workflow run pipeline.yml

# Voir les images Docker
docker images | grep crypto-platform
```

---

## 🔧 Dépannage

### Build échoue

```bash
# Vérifier les logs GitHub Actions
# → Actions → Workflow → Job → Step

# Tester localement
docker build -t test ./api
```

### Déploiement échoue

```bash
# Vérifier la connexion SSH
ssh user@server "echo OK"

# Vérifier les secrets GitHub
# → Settings → Secrets → Vérifier les noms
```

### Health check échoue

```bash
# Vérifier l'API
curl -v https://api.example.com/health

# Vérifier les logs
docker-compose logs api
```

---

<div align="center">

**Pipeline CI/CD CryptoTracker** 🚀

[🏠 Retour à l'accueil](../README.md) | [🧪 Tests](TESTING.md) | [📖 Installation](INSTALLATION.md)

</div>
