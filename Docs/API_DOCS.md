# 🔌 Documentation API - CryptoTracker

> 📚 **Référence complète** de l'API REST pour la plateforme de surveillance des cryptomonnaies.

---

## 🌐 Introduction

- **URL de base** : `http://localhost:8000`
- **Documentation interactive** : `http://localhost:8000/docs` (Swagger UI)
- **Format** : JSON
- **Authentification** : JWT Bearer token

---

## 🔐 Authentification

### POST /auth/register
Créer un nouveau compte utilisateur.

**Headers** : `Content-Type: application/json`

**Request Body** :
```json
{
  "username": "alice",
  "email": "alice@example.com",
  "password": "password123"
}
```

**Response 201** :
```json
{
  "username": "alice",
  "email": "alice@example.com",
  "created_at": "2024-12-29T10:00:00Z",
  "is_active": true,
  "role": "user"
}
```

---

### POST /auth/login
Se connecter et obtenir un token JWT.

**Headers** : `Content-Type: application/x-www-form-urlencoded`

**Request Body** (form-data) :
```
username: alice
password: password123
```

**Response 200** :
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

### GET /auth/me
Obtenir les informations de l'utilisateur connecté.

**Headers** : 
```
Authorization: Bearer {token}
```

**Response 200** :
```json
{
  "username": "alice",
  "email": "alice@example.com",
  "role": "user"
}
```

---

## 💰 Cryptomonnaies

### GET /prices
Obtenir la liste des prix des cryptomonnaies.

**Headers** : 
```
Authorization: Bearer {token}
```

**Query Parameters** (optionnel) :
- `only_popular=true` : Ne retourner que les cryptos populaires
- `limit=50` : Limiter le nombre de résultats

**Response 200** :
```json
{
  "prices": [
    {
      "symbol": "BTC",
      "name": "Bitcoin",
      "price_usd": 94523.45,
      "volume_24h": 28473928473,
      "market_cap": 1839284739284,
      "timestamp": "2024-12-29 10:00:00"
    },
    {
      "symbol": "ETH",
      "name": "Ethereum",
      "price_usd": 2918.23,
      "volume_24h": 1284739284,
      "market_cap": 350928473928,
      "timestamp": "2024-12-29 10:00:00"
    }
  ],
  "count": 50,
  "user": "alice"
}
```

---

### GET /prices/latest
Obtenir les derniers prix avec pagination.

**Headers** : 
```
Authorization: Bearer {token}
```

**Query Parameters** :
- `limit=10` : Nombre de résultats (défaut: 50)
- `offset=0` : Offset pour pagination

**Response 200** :
```json
{
  "prices": [...],
  "pagination": {
    "limit": 10,
    "offset": 0,
    "total": 50
  }
}
```

---

### GET /prices/{symbol}
Obtenir les détails d'une cryptomonnaie spécifique.

**Headers** : 
```
Authorization: Bearer {token}
```

**Path Parameters** :
- `symbol` : Symbole de la crypto (ex: BTC, ETH)

**Response 200** :
```json
{
  "symbol": "BTC",
  "name": "Bitcoin",
  "price_usd": 94523.45,
  "volume_24h": 28473928473,
  "market_cap": 1839284739284,
  "timestamp": "2024-12-29 10:00:00",
  "price_history": [
    {
      "date": "2024-12-28",
      "price": 94000.00
    }
  ]
}
```

---

## 🔮 Prévisions

### GET /predictions/{symbol}
Générer des prévisions pour une cryptomonnaie.

**Headers** : 
```
Authorization: Bearer {token}
```

**Path Parameters** :
- `symbol` : Symbole de la crypto (ex: BTC, ETH)

**Query Parameters** :
- `days=90` : Période de prévision en jours (30, 60, 90)

**Response 200** :
```json
{
  "symbol": "BTC",
  "predictions": {
    "sma": {
      "value": 95000,
      "confidence": 0.85,
      "description": "Moyenne Mobile Simple"
    },
    "ema": {
      "value": 94800,
      "confidence": 0.88,
      "description": "Moyenne Mobile Exponentielle"
    },
    "linear_regression": {
      "value": 96200,
      "confidence": 0.82,
      "description": "Régression Linéaire"
    },
    "optimal": {
      "value": 95300,
      "confidence": 0.87,
      "description": "Prévision optimale pondérée"
    }
  },
  "period_days": 90,
  "generated_at": "2024-12-29T10:00:00Z"
}
```

---

### GET /predictions/indicators/{symbol}
Obtenir les indicateurs techniques pour une crypto.

**Headers** : 
```
Authorization: Bearer {token}
```

**Path Parameters** :
- `symbol` : Symbole de la crypto

**Query Parameters** :
- `days=90` : Période d'analyse

**Response 200** :
```json
{
  "symbol": "BTC",
  "indicators": {
    "rsi": {
      "value": 65.4,
      "signal": "NEUTRAL",
      "description": "RSI (Relative Strength Index)"
    },
    "macd": {
      "macd": 125.3,
      "signal": 98.7,
      "histogram": 26.6,
      "signal_type": "BUY",
      "description": "MACD (Moving Average Convergence Divergence)"
    },
    "bollinger_bands": {
      "upper": 96000,
      "middle": 94500,
      "lower": 93000,
      "signal": "NEUTRAL",
      "description": "Bollinger Bands"
    },
    "combined_signal": "BUY"
  },
  "period_days": 90
}
```

---

## 🔔 Alertes

### POST /alerts
Créer une nouvelle alerte de prix.

**Headers** : 
```
Authorization: Bearer {token}
Content-Type: application/json
```

**Request Body** :
```json
{
  "crypto_symbol": "BTC",
  "target_price": 100000.00,
  "alert_type": "above"
}
```

**Response 201** :
```json
{
  "id": "507f1f77bcf86cd799439011",
  "crypto_symbol": "BTC",
  "target_price": 100000.00,
  "alert_type": "above",
  "is_active": true,
  "created_at": "2024-12-29T10:00:00Z",
  "user": "alice"
}
```

---

### GET /alerts
Lister toutes les alertes de l'utilisateur.

**Headers** : 
```
Authorization: Bearer {token}
```

**Query Parameters** (optionnel) :
- `active=true` : Filtrer les alertes actives uniquement
- `crypto=BTC` : Filtrer par cryptomonnaie

**Response 200** :
```json
{
  "alerts": [
    {
      "id": "507f1f77bcf86cd799439011",
      "crypto_symbol": "BTC",
      "target_price": 100000.00,
      "alert_type": "above",
      "is_active": true,
      "created_at": "2024-12-29T10:00:00Z",
      "triggered_at": null
    }
  ],
  "count": 1
}
```

---

### PUT /alerts/{id}
Modifier une alerte existante.

**Headers** : 
```
Authorization: Bearer {token}
Content-Type: application/json
```

**Request Body** :
```json
{
  "target_price": 95000.00,
  "is_active": false
}
```

**Response 200** :
```json
{
  "id": "507f1f77bcf86cd799439011",
  "crypto_symbol": "BTC",
  "target_price": 95000.00,
  "alert_type": "above",
  "is_active": false,
  "updated_at": "2024-12-29T11:00:00Z"
}
```

---

### DELETE /alerts/{id}
Supprimer une alerte.

**Headers** : 
```
Authorization: Bearer {token}
```

**Response 204** : No Content

---

## 💼 Portfolio

### POST /portfolio/buy
Acheter une cryptomonnaie (simulation).

**Headers** : 
```
Authorization: Bearer {token}
Content-Type: application/json
```

**Request Body** :
```json
{
  "crypto_symbol": "BTC",
  "quantity": 0.5,
  "price": 94000.00
}
```

**Response 201** :
```json
{
  "transaction_id": "507f1f77bcf86cd799439012",
  "type": "buy",
  "crypto_symbol": "BTC",
  "quantity": 0.5,
  "price": 94000.00,
  "total_amount": 47000.00,
  "timestamp": "2024-12-29T10:00:00Z"
}
```

---

### POST /portfolio/sell
Vendre une cryptomonnaie (simulation).

**Headers** : 
```
Authorization: Bearer {token}
Content-Type: application/json
```

**Request Body** :
```json
{
  "crypto_symbol": "BTC",
  "quantity": 0.2,
  "price": 95000.00
}
```

**Response 201** :
```json
{
  "transaction_id": "507f1f77bcf86cd799439013",
  "type": "sell",
  "crypto_symbol": "BTC",
  "quantity": 0.2,
  "price": 95000.00,
  "total_amount": 19000.00,
  "timestamp": "2024-12-29T10:05:00Z"
}
```

---

### GET /portfolio/balance
Obtenir le solde et positions du portfolio.

**Headers** : 
```
Authorization: Bearer {token}
```

**Response 200** :
```json
{
  "balance": {
    "total_value": 125000.00,
    "total_invested": 100000.00,
    "pnl": 25000.00,
    "pnl_percent": 25.0,
    "available_cash": 5000.00
  },
  "positions": [
    {
      "crypto_symbol": "BTC",
      "quantity": 1.0,
      "avg_buy_price": 90000.00,
      "current_price": 94523.45,
      "value": 94523.45,
      "pnl": 4523.45,
      "pnl_percent": 5.03
    }
  ]
}
```

---

### GET /portfolio/transactions
Obtenir l'historique des transactions.

**Headers** : 
```
Authorization: Bearer {token}
```

**Query Parameters** (optionnel) :
- `limit=50` : Limiter le nombre de résultats
- `type=buy` : Filtrer par type (buy/sell)

**Response 200** :
```json
{
  "transactions": [
    {
      "transaction_id": "507f1f77bcf86cd799439012",
      "type": "buy",
      "crypto_symbol": "BTC",
      "quantity": 0.5,
      "price": 94000.00,
      "total_amount": 47000.00,
      "timestamp": "2024-12-29T10:00:00Z"
    }
  ],
  "count": 1
}
```

---

## 📊 Analytics

### GET /analytics/candlestick/{symbol}
Obtenir les données OHLC pour graphiques chandeliers.

**Headers** : 
```
Authorization: Bearer {token}
```

**Path Parameters** :
- `symbol` : Symbole de la crypto

**Query Parameters** :
- `interval=1h` : Intervalle (5m, 15m, 1h, 4h, 1d)
- `days=7` : Période (1, 3, 7, 14, 30)

**Response 200** :
```json
{
  "symbol": "BTC",
  "interval": "1h",
  "data": [
    {
      "timestamp": "2024-12-29T09:00:00Z",
      "open": 94000.00,
      "high": 94500.00,
      "low": 93800.00,
      "close": 94300.00,
      "volume": 1284739
    }
  ],
  "period_days": 7,
  "stats_24h": {
    "high": 95000.00,
    "low": 93000.00,
    "volume": 28473928473
  }
}
```

---

### GET /analytics/heatmap
Obtenir la heatmap de performance du marché.

**Headers** : 
```
Authorization: Bearer {token}
```

**Query Parameters** :
- `period=24h` : Période (1h, 24h, 7d, 30d)

**Response 200** :
```json
{
  "period": "24h",
  "data": [
    {
      "symbol": "BTC",
      "name": "Bitcoin",
      "price": 94523.45,
      "change_24h": 2.5,
      "change_percent": 2.7
    }
  ],
  "top_gainers": [
    {
      "symbol": "SOL",
      "change_percent": 8.5
    }
  ],
  "top_losers": [
    {
      "symbol": "ADA",
      "change_percent": -3.2
    }
  ]
}
```

---

### POST /analytics/compare
Comparer plusieurs cryptomonnaies.

**Headers** : 
```
Authorization: Bearer {token}
Content-Type: application/json
```

**Request Body** :
```json
{
  "symbols": ["BTC", "ETH", "SOL"],
  "period": "7d"
}
```

**Response 200** :
```json
{
  "period": "7d",
  "comparison": [
    {
      "symbol": "BTC",
      "price": 94523.45,
      "change_7d": 5.2,
      "change_percent": 5.8
    }
  ]
}
```

---

## 🚨 Codes d'erreur

| Code | Description | Solution |
|------|-------------|----------|
| **200** | OK | Requête réussie |
| **201** | Created | Ressource créée avec succès |
| **204** | No Content | Ressource supprimée avec succès |
| **400** | Bad Request | Données invalides dans la requête |
| **401** | Unauthorized | Token manquant ou expiré |
| **403** | Forbidden | Permissions insuffisantes |
| **404** | Not Found | Ressource non trouvée |
| **422** | Validation Error | Données invalides (Pydantic) |
| **500** | Internal Server Error | Erreur serveur |

---

## 🔧 Utilisation avec curl

### Authentification

```bash
# Login
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=alice&password=password123"

# Récupérer le token et l'utiliser
TOKEN="eyJhbGciOiJIUzI1NiIs..."

# Obtenir les prix
curl -X GET "http://localhost:8000/prices" \
  -H "Authorization: Bearer $TOKEN"
```

### Créer une alerte

```bash
curl -X POST "http://localhost:8000/alerts" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"crypto_symbol": "BTC", "target_price": 100000.00, "alert_type": "above"}'
```

---

## 📚 Ressources additionnelles

- [Documentation interactive Swagger](http://localhost:8000/docs)
- [Guide d'installation](INSTALLATION.md)
- [Guide utilisateur](USER_GUIDE.md)

---

<div align="center">

**API CryptoTracker v1.0** 🚀

[🏠 Retour à l'accueil](../README.md) | [📖 Guide utilisateur](USER_GUIDE.md) | [⚙️ Installation](INSTALLATION.md)

</div>
