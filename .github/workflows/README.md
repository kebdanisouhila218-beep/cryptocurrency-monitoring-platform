# GitHub Actions Workflows

Ce dossier contient les workflows GitHub Actions pour l'automatisation du CI/CD, des tests de performance et de sécurité.

---

## 📁 Workflows disponibles

| Workflow | Description | Déclenchement |
|----------|-------------|---------------|
| `ci-cd.yml` | Pipeline CI/CD complet | Push sur main/develop |
| `performance-tests.yml` | Tests de performance (Locust, k6) | Push, PR, quotidien |
| `security-tests.yml` | Tests de sécurité (Snyk, ZAP, Trivy) | Push, PR, quotidien |

---

## 🚀 CI/CD Pipeline (`ci-cd.yml`)

### Jobs

1. **test** - Tests unitaires et build
   - Tests API Python avec pytest
   - Tests frontend avec Jest
   - Build frontend
   - Couverture de code

2. **sonarqube** - Analyse qualité code
   - Analyse SonarCloud
   - Métriques de qualité
   - Détection de bugs et code smells

3. **build-and-push** - Build Docker
   - Build images API et Collector
   - Push vers GitHub Container Registry
   - Multi-arch support

4. **deploy** - Déploiement
   - Déploiement en production
   - Health checks
   - Notifications

5. **performance-security-gate** - Gates de qualité
   - Vérification des seuils
   - Validation avant déploiement

6. **notify** - Notifications
   - Statut du déploiement
   - Notifications équipe

---

## ⚡ Tests de Performance (`performance-tests.yml`)

### Locust Tests

```yaml
locust -f tests/performance/locustfile.py \
  --host=http://localhost:8000 \
  --users 10 \
  --spawn-rate 2 \
  --run-time 60s \
  --headless
```

**Seuils :**
- Temps réponse moyen < 500ms
- Taux d'erreur < 5%

### k6 Tests

```bash
k6 run tests/performance/k6_load_test.js \
  --out json=results/k6_results.json
```

**Seuils :**
- P95 < 500ms
- P99 < 1000ms
- Erreurs < 5%

---

## 🔒 Tests de Sécurité (`security-tests.yml`)

### Tests basiques
- Headers de sécurité
- SQL Injection
- XSS basique
- Endpoints sensibles

### Snyk Scans
- Dépendances Python
- Dépendances Node.js
- Analyse code source (SAST)

### Docker Security
- Scan images avec Trivy
- Vulnérabilités containers
- SARIF export

### OWASP ZAP
- Scan baseline
- Analyse dynamique
- Rapport détaillé

---

## 🔧 Configuration requise

### Secrets GitHub

| Secret | Description | Requis pour |
|--------|-------------|--------------|
| `SONAR_TOKEN` | Token SonarCloud | SonarQube scan |
| `SNYK_TOKEN` | Token Snyk | Snyk scans |
| `GITHUB_TOKEN` | Token GitHub | Docker push |

### Variables d'environnement

| Variable | Valeur | Description |
|----------|--------|-------------|
| `REGISTRY` | `ghcr.io` | Container Registry |
| `IMAGE_NAME` | `${{ github.repository }}` | Nom des images |

---

## 📊 Rapports et Artifacts

### Artifacts générés

| Artifact | Contenu | Rétention |
|----------|---------|-----------|
| `locust-results` | Rapport Locust HTML/CSV | 30 jours |
| `k6-results` | Résultats k6 JSON | 30 jours |
| `security-results` | Rapports Snyk/ZAP | 30 jours |
| `trivy-results` | Scan Trivy SARIF | 30 jours |
| `performance-report` | Rapport performance | 30 jours |
| `security-report` | Rapport sécurité | 30 jours |

### Rapports disponibles

- **Performance** : HTML, JSON, CSV
- **Sécurité** : JSON, SARIF, HTML
- **Qualité** : SonarCloud dashboard

---

## 🚀 Utilisation locale

### Lancer les tests manuellement

```bash
# Tests de performance
pip install locust
locust -f tests/performance/locustfile.py --host=http://localhost:8000

# Tests de sécurité
python tests/security/zap_scan.py --no-zap

# Snyk (nécessite authentification)
npm install -g snyk
snyk auth
cd tests/security && ./run_snyk.sh
```

### Débogage des workflows

```bash
# Activer le debug mode
act -j performance-tests -v

# Lancer un job spécifique
act -j security-tests
```

---

## 📈 Monitoring

### Métriques collectées

- **Performance** : Temps réponse, débit, erreurs
- **Sécurité** : Vulnérabilités, scores de risque
- **Qualité** : Couverture, debt, bugs

### Alertes

- Échec des tests de performance
- Vulnérabilités critiques
- Déploiement échoué

---

## 🔄 Maintenance

### Mises à jour recommandées

1. **Mettre à jour les dépendances** des workflows
2. **Revoir les seuils** de performance
3. **Ajouter de nouveaux tests** de sécurité
4. **Optimiser les temps** d'exécution

### Bonnes pratiques

- **Versionner les workflows**
- **Documenter les changements**
- **Tester en local** avant merge
- **Surveiller les coûts** GitHub Actions

---

## 🚨 Dépannage

### Problèmes courants

| Problème | Solution |
|----------|----------|
| Tests timeout | Augmenter les timeouts dans les workflows |
| Secrets manquants | Ajouter les secrets dans GitHub Settings |
| Échec Docker build | Vérifier le Dockerfile et les dépendances |
| SonarQube échoue | Vérifier le token et la configuration |

### Logs et debug

```bash
# Activer les logs détaillés
echo "::set-output name=debug::true"

# Voir les logs d'exécution
act --list
```
