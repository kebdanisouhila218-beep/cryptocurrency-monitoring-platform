# 🧪 Guide de Test CI/CD - Étape par Étape

> 📚 **Guide progressif** pour tester le pipeline CI/CD de CryptoTracker.

**Durée totale : 2-3 heures**

---

## 📋 Table des matières

1. [Vérifier l'état actuel](#étape-1--vérifier-létat-actuel)
2. [Tester les workflows existants](#étape-2--tester-les-workflows-existants)
3. [Ajouter le workflow Build](#étape-3--tester-le-workflow-build)
4. [Activer le push des images](#étape-4--activer-le-push-des-images)
5. [Tester le workflow complet](#étape-5--tester-le-workflow-complet)
6. [Merger dans main](#étape-6--merger-dans-main)
7. [Vérification finale](#étape-7--vérification-finale)

---

## ✅ ÉTAPE 1 : Vérifier l'état actuel (5 min)

### 1.1 Vérifier les workflows existants

```powershell
# Aller dans votre projet
cd C:\Users\etudiant\Documents\GitHub\cryptocurrency-monitoring-platform

# Vérifier les workflows actuels
Get-ChildItem .github\workflows\

# Vous devriez voir :
# - test.yml
# - test-api.yml
# - test-integration-collector.yml
# - build.yml
# - deploy-staging.yml
# - deploy-production.yml
# - pipeline.yml
```

### 1.2 Vérifier Git

```powershell
# Vérifier le statut
git status

# Vérifier la branche actuelle
git branch

# Vous devriez être sur : main ou develop
```

### 1.3 Vérifier que les services fonctionnent

```powershell
# Lancer Docker
docker-compose up -d

# Vérifier
docker-compose ps

# Tester l'API
curl http://localhost:8000/health

# Résultat attendu :
# {"status":"✅ API is healthy","version":"2.0.0"}
```

**✅ Si tout fonctionne, passez à l'étape 2**

---

## 🧪 ÉTAPE 2 : Tester les workflows existants (10 min)

### 2.1 Créer une branche de test

```powershell
# Créer une branche de test
git checkout -b test/ci-cd-step-by-step

# Faire un petit changement (trigger le workflow)
Add-Content -Path README.md -Value "`n<!-- Test CI/CD -->"

# Commit
git add README.md
git commit -m "test: trigger CI/CD workflows"

# Pousser sur GitHub
git push origin test/ci-cd-step-by-step
```

### 2.2 Vérifier sur GitHub

1. Aller sur : `https://github.com/kebdanisouhila218-beep/cryptocurrency-monitoring-platform/actions`
2. Vous devriez voir les workflows qui se lancent :
   - ✅ Tests Collector
   - ✅ Tests API
   - ✅ Tests Integration
   - ✅ Build Docker Images
3. Attendre qu'ils deviennent verts ✅

**✅ Si tous verts → Passez à l'étape 3**
**❌ Si rouge → Voir section [DÉPANNAGE](#-dépannage)**

---

## 🐳 ÉTAPE 3 : Tester le workflow Build (15 min)

### 3.1 Vérifier le Dockerfile Frontend

```powershell
# Vérifier si le Dockerfile existe
Test-Path frontend\Dockerfile

# Devrait retourner : True
```

### 3.2 Tester le build localement

```powershell
# Tester le build du frontend
cd frontend
docker build -t crypto-frontend-test .

# Si succès, nettoyer
docker rmi crypto-frontend-test
cd ..
```

### 3.3 Vérifier le workflow build.yml

Le workflow `build.yml` est configuré pour :
- Se déclencher sur `main`, `develop`, et `test/**`
- Construire 3 images Docker (Collector, API, Frontend)
- Pousser vers GitHub Container Registry (GHCR)

**📊 Vérifier sur GitHub Actions :**
1. Aller sur : `https://github.com/kebdanisouhila218-beep/cryptocurrency-monitoring-platform/actions`
2. Cliquer sur "Build Docker Images"
3. Vérifier que les 3 jobs passent :
   - ✅ Build Collector Image
   - ✅ Build API Image
   - ✅ Build Frontend Image

---

## 🚀 ÉTAPE 4 : Activer le push des images (10 min)

### 4.1 Configurer les permissions GitHub

1. Aller sur GitHub → Repository → **Settings**
2. **Actions** → **General**
3. **Workflow permissions** → Cocher **"Read and write permissions"**
4. **Sauvegarder**

### 4.2 Vérifier les images sur GitHub Packages

Après un push réussi :
1. Aller sur : `https://github.com/kebdanisouhila218-beep?tab=packages`
2. Vous devriez voir 3 packages :
   - `crypto-platform-collector`
   - `crypto-platform-api`
   - `crypto-platform-frontend`

### 4.3 Tester un pull local

```powershell
# Se connecter à GitHub Container Registry
# (Remplacer VOTRE_TOKEN par un Personal Access Token)
echo VOTRE_TOKEN | docker login ghcr.io -u kebdanisouhila218-beep --password-stdin

# Pull une image
docker pull ghcr.io/kebdanisouhila218-beep/crypto-platform-api:main

# Vérifier
docker images | Select-String crypto-platform
```

---

## 🌿 ÉTAPE 5 : Tester le workflow complet (15 min)

### 5.1 Merger dans develop

```powershell
# Revenir sur develop
git checkout develop

# Merger votre branche de test
git merge test/ci-cd-step-by-step

# Pousser
git push origin develop
```

### 5.2 Vérifier sur GitHub

1. Tous les workflows devraient se lancer :
   - ✅ Tests Collector
   - ✅ Tests API
   - ✅ Tests Integration
   - ✅ Build Docker Images
   - ✅ Deploy to Staging (si configuré)
2. Attendre que TOUT soit vert

---

## ✅ ÉTAPE 6 : Merger dans main (5 min)

### 6.1 Merger develop dans main

```powershell
# Aller sur main
git checkout main

# Merger develop
git merge develop

# Pousser
git push origin main
```

### 6.2 Vérifier sur GitHub

1. Tous les workflows se lancent sur main
2. Build des images avec tag "main"
3. (Optionnel) Déploiement production

---

## 📊 ÉTAPE 7 : Vérification finale (5 min)

### 7.1 Checklist

- [ ] ✅ Tous les workflows sur main sont verts
- [ ] ✅ 3 images Docker visibles dans Packages
- [ ] ✅ Badges dans README.md
- [ ] ✅ Documentation CICD.md créée
- [ ] ✅ Tests locaux passent
- [ ] ✅ `docker-compose up -d` fonctionne

### 7.2 Badges dans README

Les badges sont déjà configurés dans le README.md :

```markdown
[![Tests Collector](https://github.com/kebdanisouhila218-beep/cryptocurrency-monitoring-platform/actions/workflows/test.yml/badge.svg)]
[![Tests API](https://github.com/kebdanisouhila218-beep/cryptocurrency-monitoring-platform/actions/workflows/test-api.yml/badge.svg)]
[![Tests Integration](https://github.com/kebdanisouhila218-beep/cryptocurrency-monitoring-platform/actions/workflows/test-integration-collector.yml/badge.svg)]
[![Build](https://github.com/kebdanisouhila218-beep/cryptocurrency-monitoring-platform/actions/workflows/build.yml/badge.svg)]
```

---

## 🎓 Pour la Soutenance

### Démo CI/CD en 2 minutes

1. **Montrer GitHub Actions** (30 sec)
   ```
   → https://github.com/kebdanisouhila218-beep/cryptocurrency-monitoring-platform/actions
   → Montrer tous les workflows verts ✅
   ```

2. **Montrer les images Docker** (30 sec)
   ```
   → https://github.com/kebdanisouhila218-beep?tab=packages
   → Montrer les 3 packages
   ```

3. **Expliquer le pipeline** (1 min)
   ```
   "Sur chaque push :
   1. Tests automatiques (3 workflows)
   2. Build des images Docker
   3. Push vers GitHub Container Registry
   4. (Optionnel) Déploiement staging/production"
   ```

---

## 🔧 DÉPANNAGE

### ❌ Problème 1 : Workflow rouge - Tests échouent

```powershell
# Lancer les tests localement d'abord
cd api
python -m pytest test_api.py -v

# Si ça passe localement, le problème est dans GitHub Actions
# → Vérifier la configuration du workflow
```

**Erreurs communes :**
- MongoDB non démarré → Attendre 10 secondes de plus
- Imports manquants → Vérifier requirements.txt
- Tests obsolètes → Mettre à jour les tests

---

### ❌ Problème 2 : Build échoue - Docker

```powershell
# Erreur commune : "Dockerfile not found"

# Vérifier :
Test-Path frontend\Dockerfile
Test-Path api\Dockerfile
Test-Path collector\Dockerfile
```

---

### ❌ Problème 3 : Permission denied - GitHub Packages

**Solution :**
1. Aller sur GitHub → Settings → Actions → General
2. Workflow permissions → Cocher "Read and write permissions"
3. Sauvegarder
4. Re-run le workflow

---

### ❌ Problème 4 : Images non visibles dans Packages

**Vérifier :**
1. Le workflow build.yml a bien `push: true` (ou condition correcte)
2. Les permissions GitHub Actions (voir Problème 3)
3. Le workflow est bien terminé (vert ✅)

**Si toujours pas visible :**
- Aller sur le repo → Settings → Actions → General
- Package permissions → Cocher "Inherit from organization"

---

## 📋 Résumé des commandes

```powershell
# ÉTAPE 1 : Vérifier l'état
git status
docker-compose up -d
docker-compose ps

# ÉTAPE 2 : Tester workflows existants
git checkout -b test/ci-cd-step-by-step
git push origin test/ci-cd-step-by-step

# ÉTAPE 3 : Tester build localement
cd frontend
docker build -t crypto-frontend-test .
cd ..

# ÉTAPE 5 : Merger dans develop
git checkout develop
git merge test/ci-cd-step-by-step
git push origin develop

# ÉTAPE 6 : Merger dans main
git checkout main
git merge develop
git push origin main

# Vérifier les images
docker images | Select-String crypto-platform
```

---

## 📊 Workflows GitHub Actions

| Workflow | Fichier | Déclencheur | Description |
|----------|---------|-------------|-------------|
| Tests Collector | `test.yml` | Push/PR | Tests unitaires collector |
| Tests API | `test-api.yml` | Push/PR | Tests unitaires API |
| Tests Integration | `test-integration-collector.yml` | Push/PR | Tests Collector → MongoDB |
| Build | `build.yml` | Push main/develop | Build images Docker |
| Deploy Staging | `deploy-staging.yml` | Push develop | Déploiement staging |
| Deploy Production | `deploy-production.yml` | Push main | Déploiement production |
| Pipeline | `pipeline.yml` | Push/PR | Pipeline complet |

**Total : 7 workflows**

---

<div align="center">

**Guide CI/CD CryptoTracker** 🚀

[🏠 Retour à l'accueil](../README.md) | [📖 CI/CD](CICD.md) | [🧪 Tests](TESTING.md)

</div>
