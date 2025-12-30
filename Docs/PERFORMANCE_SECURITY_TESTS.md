# 🔒 Tests de Performance et Sécurité

## Vue d'ensemble

Ce document décrit les outils de tests de performance et de sécurité implémentés pour CryptoTracker.

---

## 📊 Tests de Performance

### 1. Locust (Python)

**Locust** est un outil de test de charge open-source écrit en Python.

#### Installation

```bash
pip install locust
```

#### Utilisation

```bash
# Depuis le dossier tests/performance
cd tests/performance

# Lancer Locust avec interface web
locust -f locustfile.py --host=http://localhost:8000

# Ouvrir http://localhost:8089 dans le navigateur
```

#### Configuration

- **Utilisateurs simulés** : Configurables via l'interface web
- **Taux de spawn** : Nombre d'utilisateurs créés par seconde
- **Durée** : Configurable

#### Scénarios testés

| Scénario | Fréquence | Description |
|----------|-----------|-------------|
| Health Check | Haute | Vérification santé API |
| Get Prices | Très haute | Récupération des prix |
| Get Alerts | Moyenne | Liste des alertes |
| Create Alert | Basse | Création d'alerte |
| Admin Stats | Basse | Statistiques admin |

---

### 2. k6 (JavaScript)

**k6** est un outil moderne de test de charge avec scripts JavaScript.

#### Installation

```bash
# Windows (avec Chocolatey)
choco install k6

# Ou télécharger depuis https://k6.io/docs/getting-started/installation/
```

#### Utilisation

```bash
# Test basique
k6 run tests/performance/k6_load_test.js

# Test avec paramètres
k6 run --vus 50 --duration 30s k6_load_test.js

# Export des résultats
k6 run --out json=results.json k6_load_test.js
```

#### Seuils de performance

| Métrique | Seuil |
|----------|-------|
| Temps de réponse P95 | < 500ms |
| Temps de réponse P99 | < 1000ms |
| Taux d'erreur | < 5% |
| Durée login | < 1000ms |

#### Scénarios de charge

```
Montée progressive:
0 → 10 utilisateurs (30s)
Maintien 10 utilisateurs (1min)
10 → 50 utilisateurs (30s)
Maintien 50 utilisateurs (1min)
50 → 0 utilisateurs (30s)
```

---

## 🔒 Tests de Sécurité

### 1. OWASP ZAP

**OWASP ZAP** (Zed Attack Proxy) est un scanner de sécurité web.

#### Installation

```bash
# Docker (recommandé)
docker pull owasp/zap2docker-stable

# Lancer ZAP en mode daemon
docker run -u zap -p 8080:8080 -i owasp/zap2docker-stable zap.sh -daemon -host 0.0.0.0 -port 8080
```

#### Utilisation

```bash
# Installer les dépendances Python
pip install python-owasp-zap-v2.4

# Lancer le scan
cd tests/security
python zap_scan.py --target http://localhost:8000

# Scan actif (plus approfondi)
python zap_scan.py --target http://localhost:8000 --active

# Tests basiques sans ZAP
python zap_scan.py --no-zap
```

#### Types de scans

| Type | Description | Durée |
|------|-------------|-------|
| Spider | Découverte des URLs | ~1min |
| Passif | Analyse du trafic | ~2min |
| Actif | Tests d'intrusion | ~10min |

#### Vulnérabilités détectées

- SQL Injection
- XSS (Cross-Site Scripting)
- CSRF (Cross-Site Request Forgery)
- Headers de sécurité manquants
- Exposition d'informations sensibles

---

### 2. Snyk

**Snyk** analyse les vulnérabilités dans les dépendances.

#### Installation

```bash
# Installation globale
npm install -g snyk

# Authentification
snyk auth
```

#### Utilisation

```powershell
# Windows PowerShell
cd tests/security
.\run_snyk.ps1
```

```bash
# Linux/Mac
cd tests/security
chmod +x run_snyk.sh
./run_snyk.sh
```

#### Analyses effectuées

| Cible | Fichier | Type |
|-------|---------|------|
| Python API | api/requirements.txt | Dépendances pip |
| Frontend | frontend/package.json | Dépendances npm |
| Docker | Dockerfiles | Images containers |
| Code | Tout le projet | SAST (analyse statique) |

#### Intégration CI/CD

```yaml
# .github/workflows/security.yml
- name: Run Snyk
  uses: snyk/actions/python@master
  env:
    SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
```

---

## 📁 Structure des fichiers

```
tests/
├── performance/
│   ├── locustfile.py        # Tests Locust
│   ├── k6_load_test.js      # Tests k6
│   └── requirements.txt     # Dépendances
│
├── security/
│   ├── zap_scan.py          # Scanner OWASP ZAP
│   ├── run_snyk.ps1         # Script Snyk (Windows)
│   ├── run_snyk.sh          # Script Snyk (Linux/Mac)
│   ├── snyk_config.json     # Configuration Snyk
│   └── requirements.txt     # Dépendances
│
└── results/                 # Résultats des tests
    ├── k6_summary.json
    ├── zap_report.json
    └── snyk_*.json
```

---

## 🚀 Exécution rapide

### Tests de performance

```bash
# Locust (interface web)
pip install locust
locust -f tests/performance/locustfile.py --host=http://localhost:8000

# k6 (ligne de commande)
k6 run tests/performance/k6_load_test.js
```

### Tests de sécurité

```bash
# Tests basiques (sans outils externes)
python tests/security/zap_scan.py --no-zap

# Snyk (nécessite authentification)
cd tests/security && .\run_snyk.ps1
```

---

## 📊 Interprétation des résultats

### Performance

| Métrique | Bon | Acceptable | Mauvais |
|----------|-----|------------|---------|
| Temps réponse P95 | < 200ms | < 500ms | > 500ms |
| Taux d'erreur | < 1% | < 5% | > 5% |
| Requêtes/sec | > 100 | > 50 | < 50 |

### Sécurité

| Niveau | Action |
|--------|--------|
| 🔴 Critique | Corriger immédiatement |
| 🟠 Haute | Corriger avant production |
| 🟡 Moyenne | Planifier correction |
| 🔵 Info | À évaluer |

---

## ✅ Checklist avant production

- [ ] Tests Locust passés (> 100 req/s)
- [ ] Tests k6 passés (P95 < 500ms)
- [ ] Scan ZAP sans vulnérabilités critiques
- [ ] Snyk sans vulnérabilités high/critical
- [ ] Headers de sécurité configurés
- [ ] HTTPS activé
- [ ] Rate limiting configuré
