# 🧪 Guide des Tests - CryptoTracker

> 📚 **Documentation complète** de la suite de tests pour la plateforme de surveillance crypto.

---

## 📋 Vue d'ensemble

Ce projet contient **4 types de tests** :

| Type | Technologie | Couverture |
|------|-------------|------------|
| ✅ Tests unitaires Backend | Python/Pytest | ~75% |
| ✅ Tests unitaires Frontend | React/Jest | ~60% |
| ✅ Tests d'intégration | Docker/Pytest | API → MongoDB |
| ✅ Tests E2E | Playwright | Parcours utilisateur |

---

## 🏗️ Structure des Tests

```
cryptocurrency-monitoring-platform/
├── api/
│   ├── test_api.py                    # Tests API de base
│   ├── test_auth.py                   # Tests authentification
│   ├── test_predictions.py            # Tests prévisions
│   ├── test_technical_indicators.py   # Tests indicateurs
│   ├── test_alerts.py                 # Tests alertes
│   └── test_portfolio.py              # Tests portfolio
├── collector/
│   ├── test_collector_logic.py        # Tests logique collector
│   └── test_integration_collector.py  # Tests intégration
├── frontend/src/
│   ├── services/
│   │   ├── authService.test.js        # Tests service auth
│   │   └── cryptoService.test.js      # Tests service crypto
│   └── components/
│       └── CryptoList.test.js         # Tests composant liste
├── tests/
│   ├── e2e/
│   │   └── test_user_flow.py          # Tests E2E Playwright
│   └── api_requests.json              # Collection Postman
├── run_all_tests.sh                   # Script Bash
└── run_all_tests.ps1                  # Script PowerShell
```

---

## 📦 Tests Backend (Python/Pytest)

### Installation

```bash
pip install pytest pytest-cov pytest-mock
```

### Tests unitaires API

```bash
# Tous les tests API
cd api && pytest -v

# Tests spécifiques
pytest test_api.py -v
pytest test_predictions.py -v
pytest test_technical_indicators.py -v
pytest test_alerts.py -v
pytest test_portfolio.py -v
```

### Tests Collector

```bash
cd collector && pytest test_collector_logic.py -v
```

### Coverage

```bash
# Générer le rapport de couverture
cd api && pytest --cov=. --cov-report=html

# Voir le rapport
# Ouvrir htmlcov/index.html dans un navigateur
```

### Tests disponibles

#### `test_predictions.py`
- `test_predictions_endpoint_requires_auth` - Vérifie l'authentification
- `test_predictions_with_valid_token` - Test avec token valide
- `test_sma_basic_calculation` - Calcul SMA
- `test_ema_basic_calculation` - Calcul EMA
- `test_linear_regression_uptrend` - Régression linéaire

#### `test_technical_indicators.py`
- `test_rsi_overbought` - RSI en zone de surachat
- `test_rsi_oversold` - RSI en zone de survente
- `test_macd_bullish_crossover` - Croisement MACD haussier
- `test_bollinger_band_order` - Ordre des bandes Bollinger
- `test_combined_buy_signal` - Signal combiné d'achat

#### `test_alerts.py`
- `test_create_alert` - Création d'alerte
- `test_list_alerts` - Listage des alertes
- `test_delete_alert` - Suppression d'alerte
- `test_alert_trigger_above` - Déclenchement alerte "above"
- `test_alert_trigger_below` - Déclenchement alerte "below"

#### `test_portfolio.py`
- `test_buy_crypto` - Achat de crypto
- `test_sell_crypto` - Vente de crypto
- `test_get_balance` - Récupération du solde
- `test_pnl_calculation_profit` - Calcul P&L avec profit
- `test_average_buy_price` - Prix moyen d'achat

---

## ⚛️ Tests Frontend (React/Jest)

### Installation

```bash
cd frontend
npm install --save-dev @testing-library/react @testing-library/jest-dom
```

### Lancer les tests

```bash
cd frontend

# Tous les tests
npm test

# Mode watch
npm test -- --watch

# Tests spécifiques
npm test -- --testPathPattern=authService.test.js
npm test -- --testPathPattern=cryptoService.test.js
npm test -- --testPathPattern=CryptoList.test.js

# Coverage
npm test -- --coverage
```

### Tests disponibles

#### `authService.test.js`
- `should register a new user successfully`
- `should login successfully and store token`
- `should clear localStorage on logout`
- `should return false if no token`
- `should return Authorization header with token`

#### `cryptoService.test.js`
- `should fetch all cryptos successfully`
- `should handle 401 error and trigger logout`
- `should fetch specific crypto by symbol`
- `should fetch predictions for a crypto`
- `should fetch technical indicators`

#### `CryptoList.test.js`
- `should filter cryptos by name`
- `should filter cryptos by symbol`
- `should sort by price descending`
- `should calculate average price`
- `should format prices correctly`

---

## 🔗 Tests d'Intégration

### Avec Docker

```bash
# Lancer les tests d'intégration
docker-compose run --rm test-integration

# Ou manuellement
docker-compose up -d mongo redis
cd collector && pytest test_integration_collector.py -v
```

### Sans Docker (MongoDB local requis)

```bash
# S'assurer que MongoDB tourne
mongod --dbpath /data/db

# Lancer les tests
cd collector && pytest test_integration_collector.py -v
```

---

## 🌐 Tests E2E (Playwright)

### Installation

```bash
pip install pytest-playwright
playwright install
```

### Lancer les tests

```bash
# Mode headless (sans navigateur visible)
pytest tests/e2e/ -v

# Mode headed (avec navigateur visible)
pytest tests/e2e/ -v --headed

# Test spécifique
pytest tests/e2e/test_user_flow.py -v
```

### Tests disponibles

- `test_registration_page_loads` - Page d'inscription
- `test_login_page_loads` - Page de connexion
- `test_user_registration_flow` - Flux d'inscription
- `test_navigation_menu_exists` - Menu de navigation
- `test_theme_toggle` - Changement de thème
- `test_mobile_viewport` - Responsive mobile
- `test_page_load_time` - Performance

---

## 📬 Tests API (Postman)

### Importer la collection

1. Ouvrir Postman
2. **File → Import**
3. Sélectionner `tests/api_requests.json`

### Utilisation

1. **Login User** - Obtenir un token
2. Copier `access_token` dans les variables
3. Tester les autres endpoints

### Endpoints testés

- **Authentication** : Register, Login, Get Current User
- **Cryptos** : Get All Prices, Get Latest, Get by Symbol
- **Predictions** : Get Predictions, Get Indicators
- **Alerts** : Create, List, Update, Delete
- **Portfolio** : Buy, Sell, Balance, Transactions
- **Analytics** : Candlestick, Heatmap, Compare

---

## 🚀 Lancer tous les tests

### Windows (PowerShell)

```powershell
.\run_all_tests.ps1
```

### Linux/Mac (Bash)

```bash
chmod +x run_all_tests.sh
./run_all_tests.sh
```

---

## 📊 Métriques de Qualité

| Métrique | Valeur |
|----------|--------|
| **Coverage Backend** | ~75% |
| **Coverage Frontend** | ~60% |
| **Tests Total** | ~50 tests |
| **Temps d'exécution** | ~3-4 minutes |

---

## 🔄 CI/CD (GitHub Actions)

Les tests s'exécutent automatiquement sur chaque push via 3 workflows :

### `.github/workflows/test.yml`
- Tests unitaires Collector
- Déclenché sur push/PR

### `.github/workflows/test-api.yml`
- Tests unitaires API
- Déclenché sur push/PR

### `.github/workflows/test-integration-collector.yml`
- Tests d'intégration
- Utilise Docker MongoDB

---

## 🛠️ Dépannage

### Erreur "Module not found"

```bash
# Backend
pip install -r requirements.txt

# Frontend
cd frontend && npm install
```

### Erreur "MongoDB connection failed"

```bash
# Vérifier que MongoDB tourne
docker-compose ps

# Redémarrer
docker-compose restart mongo
```

### Tests E2E échouent

```bash
# Vérifier que le frontend tourne
curl http://localhost:3000

# Vérifier que l'API tourne
curl http://localhost:8000/health

# Réinstaller Playwright
playwright install --force
```

### Tests Frontend timeout

```bash
# Augmenter le timeout
npm test -- --testTimeout=30000
```

---

## 📝 Bonnes Pratiques

### Écrire de nouveaux tests

1. **Nommer clairement** : `test_<fonction>_<cas>`
2. **Un assert par test** (idéalement)
3. **Utiliser des fixtures** pour le setup
4. **Nettoyer après** (cleanup)

### Exemple de test

```python
def test_create_alert_with_valid_data(auth_token):
    """Test de création d'alerte avec données valides"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    alert_data = {
        "crypto_symbol": "BTC",
        "target_price": 100000.00,
        "alert_type": "above"
    }
    
    response = client.post("/alerts", json=alert_data, headers=headers)
    
    assert response.status_code == 201
    assert response.json()["crypto_symbol"] == "BTC"
```

---

## 📞 Support

Si vous rencontrez des problèmes avec les tests :

1. Vérifiez les logs avec `pytest -v --tb=long`
2. Consultez la [documentation API](API_DOCS.md)
3. Ouvrez une [issue sur GitHub](https://github.com/kebdanisouhila218-beep/cryptocurrency-monitoring-platform/issues)

---

<div align="center">

**Tests CryptoTracker v1.0** 🧪

[🏠 Retour à l'accueil](../README.md) | [📖 Documentation API](API_DOCS.md) | [👥 Guide utilisateur](USER_GUIDE.md)

</div>
