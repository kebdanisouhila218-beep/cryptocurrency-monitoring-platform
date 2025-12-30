# 🔍 SonarQube - Analyse de Qualité du Code

## Vue d'ensemble

SonarQube analyse automatiquement la qualité du code et détecte :
- 🐛 **Bugs** - Erreurs potentielles
- 🔒 **Vulnérabilités** - Problèmes de sécurité
- 🧹 **Code Smells** - Mauvaises pratiques
- 📊 **Couverture de tests** - Pourcentage de code testé
- 📝 **Duplications** - Code dupliqué

## 🚀 Démarrage rapide

### 1. Lancer SonarQube

```bash
docker-compose up -d sonarqube
```

### 2. Accéder à l'interface

- **URL** : http://localhost:9000
- **Login** : `admin`
- **Mot de passe** : `admin` (à changer au premier login)

### 3. Créer un projet

1. Connectez-vous à SonarQube
2. Cliquez sur **"Create Project"**
3. Choisissez **"Manually"**
4. Entrez :
   - Project key : `cryptocurrency-monitoring-platform`
   - Display name : `CryptoTracker`
5. Cliquez sur **"Set Up"**
6. Choisissez **"Locally"**
7. Générez un **token** et copiez-le

### 4. Installer SonarScanner

#### Windows (PowerShell)
```powershell
# Télécharger SonarScanner
Invoke-WebRequest -Uri "https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-5.0.1.3006-windows.zip" -OutFile "sonar-scanner.zip"

# Extraire
Expand-Archive -Path "sonar-scanner.zip" -DestinationPath "C:\sonar-scanner"

# Ajouter au PATH
$env:PATH += ";C:\sonar-scanner\sonar-scanner-5.0.1.3006-windows\bin"
```

#### Ou avec npm (plus simple)
```bash
npm install -g sonarqube-scanner
```

### 5. Lancer l'analyse

```bash
# Depuis la racine du projet
sonar-scanner -Dsonar.login=VOTRE_TOKEN
```

Ou avec npm :
```bash
npx sonarqube-scanner -Dsonar.login=VOTRE_TOKEN
```

## 📊 Configuration

Le fichier `sonar-project.properties` à la racine configure l'analyse :

```properties
sonar.projectKey=cryptocurrency-monitoring-platform
sonar.projectName=CryptoTracker
sonar.sources=api,frontend/src,collector
sonar.exclusions=**/node_modules/**,**/__pycache__/**
sonar.python.version=3.11
```

## 🎯 Métriques analysées

| Métrique | Description |
|----------|-------------|
| **Reliability** | Bugs et erreurs |
| **Security** | Vulnérabilités |
| **Maintainability** | Code smells, dette technique |
| **Coverage** | Couverture de tests |
| **Duplications** | Code dupliqué |

## 🔧 Intégration CI/CD

### GitHub Actions

Ajoutez à `.github/workflows/sonar.yml` :

```yaml
name: SonarQube Analysis

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  sonarqube:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: SonarQube Scan
        uses: sonarsource/sonarqube-scan-action@master
        env:
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
          SONAR_HOST_URL: ${{ secrets.SONAR_HOST_URL }}
```

## 📈 Quality Gates

SonarQube définit des seuils de qualité :

| Condition | Seuil par défaut |
|-----------|------------------|
| Coverage | > 80% |
| Duplications | < 3% |
| Maintainability Rating | A |
| Reliability Rating | A |
| Security Rating | A |

## 🛠️ Dépannage

### SonarQube ne démarre pas

```bash
# Vérifier les logs
docker logs sonarqube

# Augmenter la mémoire si nécessaire
docker-compose down sonarqube
# Modifier docker-compose.yml pour ajouter :
# environment:
#   - SONAR_ES_BOOTSTRAP_CHECKS_DISABLE=true
docker-compose up -d sonarqube
```

### Erreur "Elasticsearch bootstrap checks failed"

C'est normal sur Windows/WSL. La variable `SONAR_ES_BOOTSTRAP_CHECKS_DISABLE=true` est déjà configurée.

### Scanner ne trouve pas les fichiers

Vérifiez que `sonar.sources` pointe vers les bons dossiers dans `sonar-project.properties`.
