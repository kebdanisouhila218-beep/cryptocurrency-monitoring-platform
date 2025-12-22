# api/main.py - AJOUT DU FILTRE DES CRYPTOS POPULAIRES

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta, datetime, timezone
import os
import threading
import time
from database import get_collection, get_alerts_collection
from routes.alerts import router as alerts_router
from routes.profile import router as profile_router
from services.alert_checker import check_alerts
from auth import (
    authenticate_user,
    create_access_token,
    create_user,
    get_current_active_user,
    get_current_admin_user,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    UserCreate,
    UserResponse,
    Token
)

app = FastAPI(
    title="Crypto Monitoring API",
    description="API de surveillance des cryptomonnaies avec authentification JWT",
    version="2.0.0"
)

ALERT_CHECKER_ENABLED = os.getenv("ALERT_CHECKER_ENABLED", "true").lower() == "true"
ALERT_CHECK_INTERVAL_SECONDS = int(os.getenv("ALERT_CHECK_INTERVAL_SECONDS", "60"))

# ===== LISTE DES 50 CRYPTOS POPULAIRES =====
POPULAR_CRYPTO_SYMBOLS = [
    # Top 13
    "BTC", "ETH", "BNB", "SOL", "XRP", "ADA", "DOGE", 
    "DOT", "MATIC", "LTC", "AVAX", "LINK", "ATOM", "UNI", "XLM",
    
    # 35 supplémentaires
    "TRX", "ETC", "BCH", "NEAR", "LEO", "ICP", "APT", "ARB", "OP",
    "STX", "FIL", "LDO", "MNT", "IMX", "INJ", "MKR", "RUNE", "GRT",
    "AAVE", "SNX", "FTM", "ALGO", "VET", "EGLD", "AXS", "SAND", "MANA",
    "THETA", "XTZ", "FLOW", "EOS", "CHZ", "KCS", "BTT", "HBAR", "ZIL",
    "KSM", "GALA", "CRV", "QNT", "1INCH", "NEO", "COMP", "ZRX", "ENJ",
    "BAT", "LRC", "CHR",
    
    # Stablecoins
    "USDT", "USDC", "BUSD", "DAI"
]

# ===== INCLUSION DES ROUTES =====
app.include_router(alerts_router)
app.include_router(profile_router)

# ===== CORS =====
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _alert_checker_loop():
    while True:
        try:
            check_alerts()
        except Exception as e:
            print(f"[API] ⚠️ Erreur alert checker loop: {e}")
        time.sleep(max(5, ALERT_CHECK_INTERVAL_SECONDS))


@app.on_event("startup")
def start_alert_checker():
    if not ALERT_CHECKER_ENABLED:
        print("[API] ℹ️ Alert checker désactivé (ALERT_CHECKER_ENABLED=false)")
        return

    t = threading.Thread(target=_alert_checker_loop, daemon=True)
    t.start()
    print(f"[API] ✅ Alert checker démarré (interval={ALERT_CHECK_INTERVAL_SECONDS}s)")


# ===== ROUTES D'AUTHENTIFICATION =====

@app.post("/auth/register", response_model=UserResponse, tags=["Authentication"])
async def register(user: UserCreate):
    """
    📝 Inscription d'un nouvel utilisateur
    
    - **email**: Email valide
    - **username**: Nom d'utilisateur unique
    - **password**: Mot de passe (min 8 caractères recommandé)
    """
    new_user = create_user(user)
    return {
        "email": new_user["email"],
        "username": new_user["username"],
        "created_at": new_user["created_at"],
        "is_active": new_user["is_active"],
        "role": new_user["role"]
    }


@app.post("/auth/login", response_model=Token, tags=["Authentication"])
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    🔐 Connexion et obtention du JWT token
    
    - **username**: Nom d'utilisateur
    - **password**: Mot de passe
    
    Retourne un access_token JWT valide 30 minutes.
    """
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/auth/me", response_model=UserResponse, tags=["Authentication"])
async def read_users_me(current_user: dict = Depends(get_current_active_user)):
    """
    👤 Récupère les informations de l'utilisateur connecté
    
    Nécessite un token JWT valide dans le header Authorization.
    """
    return {
        "email": current_user["email"],
        "username": current_user["username"],
        "created_at": current_user["created_at"],
        "is_active": current_user["is_active"],
        "role": current_user["role"]
    }


# ===== ROUTES CRYPTOS (PROTÉGÉES) =====

@app.get("/prices", tags=["Crypto Data"])
async def get_prices(
    only_popular: bool = True,  # ✅ NOUVEAU: Filtre par défaut
    collection=Depends(get_collection),
    current_user: dict = Depends(get_current_active_user)
):
    """
    💰 Récupère les prix des cryptomonnaies
    
    🔒 Route protégée - Nécessite authentification
    
    **Paramètres:**
    - `only_popular`: Si True (par défaut), retourne seulement les cryptos populaires (BTC, ETH, etc.)
    """
    try:
        # ✅ NOUVEAU: Filtrer par symboles populaires
        if only_popular:
            query = {"symbol": {"$in": POPULAR_CRYPTO_SYMBOLS}}
            print(f"[API] 🔍 Filtre activé: seulement cryptos populaires")
        else:
            query = {}
            print(f"[API] 📊 Pas de filtre: toutes les cryptos")
        
        # Récupérer les dernières entrées pour chaque crypto (éviter les doublons)
        pipeline = [
            {"$match": query},
            {"$sort": {"timestamp": -1}},
            # Grouper par symbol pour avoir seulement la dernière valeur
            {"$group": {
                "_id": "$symbol",
                "coin_id": {"$first": "$coin_id"},
                "symbol": {"$first": "$symbol"},
                "name": {"$first": "$name"},
                "price_usd": {"$first": "$price_usd"},
                "volume_24h": {"$first": "$volume_24h"},
                "market_cap": {"$first": "$market_cap"},
                "timestamp": {"$first": "$timestamp"}
            }},
            {"$sort": {"price_usd": -1}},  # Trier par prix décroissant
            {"$limit": 50}
        ]
        
        prices = list(collection.aggregate(pipeline))
        
        # Formater les données avec fuseau horaire UTC+1 (Europe/Paris)
        for p in prices:
            if "timestamp" in p:
                # Convertir timestamp UTC vers UTC+1
                utc_dt = datetime.utcfromtimestamp(p["timestamp"])
                local_dt = utc_dt + timedelta(hours=1)  # UTC+1
                p["timestamp"] = local_dt.strftime("%Y-%m-%d %H:%M:%S")
            # Supprimer le _id MongoDB
            if "_id" in p:
                del p["_id"]
        
        print(f"[API] ✅ {len(prices)} cryptos retournées")
        
        # Afficher les 5 premières pour debug
        if len(prices) > 0:
            print(f"[API] 📊 Top 5 cryptos:")
            for i, p in enumerate(prices[:5]):
                print(f"[API]   {i+1}. {p['symbol']:6s} - ${p['price_usd']:.2f}")
        
        return {"prices": prices, "user": current_user["username"], "count": len(prices)}
    except Exception as e:
        print(f"[API] ❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e), "prices": []}


@app.get("/prices/latest", tags=["Crypto Data"])
async def get_latest_prices(
    limit: int = 10,
    only_popular: bool = True,
    collection=Depends(get_collection),
    current_user: dict = Depends(get_current_active_user)
):
    """
    📊 Récupère les derniers prix (limité)
    
    🔒 Route protégée - Nécessite authentification
    """
    try:
        query = {"symbol": {"$in": POPULAR_CRYPTO_SYMBOLS}} if only_popular else {}
        prices = list(collection.find(query, {"_id": 0}).sort("timestamp", -1).limit(limit))
        return {"prices": prices, "count": len(prices)}
    except Exception as e:
        return {"error": str(e), "prices": []}


# ===== ROUTES ADMIN =====

@app.get("/admin/users", tags=["Admin"])
async def list_users(current_user: dict = Depends(get_current_admin_user)):
    """
    👥 Liste tous les utilisateurs (ADMIN uniquement)
    
    🔒 Route protégée - Nécessite rôle admin
    """
    from auth import users_collection
    users = list(users_collection.find({}, {"_id": 0, "hashed_password": 0}))
    return {"users": users, "count": len(users)}


@app.delete("/admin/users/{username}", tags=["Admin"])
async def delete_user(
    username: str,
    current_user: dict = Depends(get_current_admin_user)
):
    """
    🗑️ Supprime un utilisateur (ADMIN uniquement)
    
    🔒 Route protégée - Nécessite rôle admin
    """
    from auth import users_collection
    result = users_collection.delete_one({"username": username})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": f"User {username} deleted successfully"}


# ===== ROUTES PUBLIQUES =====

@app.get("/", tags=["Public"])
async def root():
    """
    🏠 Page d'accueil de l'API
    """
    return {
        "message": "🚀 Crypto Monitoring API v2.0",
        "docs": "/docs",
        "auth": {
            "register": "/auth/register",
            "login": "/auth/login",
            "me": "/auth/me"
        },
        "endpoints": {
            "prices": "/prices (🔒 protected)",
            "latest": "/prices/latest (🔒 protected)",
            "admin": "/admin/users (🔒 admin only)",
            "alerts": "/alerts (🔒 protected)"
        }
    }


@app.get("/health", tags=["Public"])
async def health_check():
    """
    ✅ Health check de l'API
    """
    return {"status": "✅ API is healthy", "version": "2.0.0"}


@app.get("/public/stats", tags=["Public"])
async def public_stats(collection=Depends(get_collection)):
    """
    📈 Statistiques publiques (sans authentification)
    """
    try:
        count = collection.count_documents({})
        popular_count = collection.count_documents({"symbol": {"$in": POPULAR_CRYPTO_SYMBOLS}})
        return {
            "total_records": count,
            "popular_cryptos": popular_count,
            "message": "Login required for detailed data",
            "register_url": "/auth/register"
        }
    except Exception as e:
        return {"error": str(e)}