# api/routes/admin.py - Routes d'administration

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from auth import get_current_admin_user, users_collection, get_password_hash
from database import (
    get_collection, 
    get_alerts_collection, 
    get_portfolios_collection,
    get_transactions_collection,
    get_price_history_collection
)

router = APIRouter(prefix="/admin", tags=["Admin"])


# ===== MODÈLES =====

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    role: Optional[str] = None  # "user" ou "admin"

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str = "user"

class StatsResponse(BaseModel):
    total_users: int
    active_users: int
    admin_users: int
    total_alerts: int
    active_alerts: int
    total_portfolios: int
    total_transactions: int
    total_price_records: int


# ===== ROUTES UTILISATEURS =====

@router.get("/users", summary="Liste tous les utilisateurs")
async def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_admin_user)
):
    """
    👥 Liste tous les utilisateurs (ADMIN uniquement)
    
    - **skip**: Nombre d'utilisateurs à sauter (pagination)
    - **limit**: Nombre maximum d'utilisateurs à retourner
    """
    users = list(users_collection.find(
        {}, 
        {"_id": 0, "hashed_password": 0}
    ).skip(skip).limit(limit))
    
    total = users_collection.count_documents({})
    
    return {
        "users": users,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/users/{username}", summary="Détails d'un utilisateur")
async def get_user(
    username: str,
    current_user: dict = Depends(get_current_admin_user)
):
    """
    👤 Récupère les détails d'un utilisateur spécifique
    """
    user = users_collection.find_one(
        {"username": username},
        {"_id": 0, "hashed_password": 0}
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Ajouter les statistiques de l'utilisateur
    alerts_collection = get_alerts_collection()
    portfolios_collection = get_portfolios_collection()
    
    user_stats = {
        "alerts_count": alerts_collection.count_documents({"user_id": username}),
        "portfolios_count": portfolios_collection.count_documents({"user_id": username})
    }
    
    return {**user, "stats": user_stats}


@router.post("/users", summary="Créer un utilisateur (admin)")
async def create_user_admin(
    user_data: UserCreate,
    current_user: dict = Depends(get_current_admin_user)
):
    """
    ➕ Crée un nouvel utilisateur avec un rôle spécifique (ADMIN uniquement)
    
    Permet de créer des utilisateurs admin directement.
    """
    # Vérifier si l'utilisateur existe
    if users_collection.find_one({"username": user_data.username}):
        raise HTTPException(status_code=400, detail="Username already exists")
    
    if users_collection.find_one({"email": user_data.email}):
        raise HTTPException(status_code=400, detail="Email already exists")
    
    # Valider le rôle
    if user_data.role not in ["user", "admin"]:
        raise HTTPException(status_code=400, detail="Role must be 'user' or 'admin'")
    
    # Créer l'utilisateur
    new_user = {
        "username": user_data.username,
        "email": user_data.email,
        "hashed_password": get_password_hash(user_data.password),
        "created_at": datetime.utcnow(),
        "is_active": True,
        "role": user_data.role
    }
    
    users_collection.insert_one(new_user)
    
    return {
        "message": f"User {user_data.username} created successfully",
        "username": user_data.username,
        "role": user_data.role
    }


@router.put("/users/{username}", summary="Modifier un utilisateur")
async def update_user(
    username: str,
    user_update: UserUpdate,
    current_user: dict = Depends(get_current_admin_user)
):
    """
    ✏️ Modifie un utilisateur (ADMIN uniquement)
    
    Permet de modifier l'email, le statut actif et le rôle.
    """
    user = users_collection.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Empêcher l'admin de se désactiver lui-même
    if username == current_user["username"] and user_update.is_active == False:
        raise HTTPException(status_code=400, detail="Cannot deactivate yourself")
    
    # Empêcher l'admin de se retirer le rôle admin
    if username == current_user["username"] and user_update.role == "user":
        raise HTTPException(status_code=400, detail="Cannot remove your own admin role")
    
    # Valider le rôle
    if user_update.role and user_update.role not in ["user", "admin"]:
        raise HTTPException(status_code=400, detail="Role must be 'user' or 'admin'")
    
    # Construire la mise à jour
    update_data = {}
    if user_update.email is not None:
        update_data["email"] = user_update.email
    if user_update.is_active is not None:
        update_data["is_active"] = user_update.is_active
    if user_update.role is not None:
        update_data["role"] = user_update.role
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    users_collection.update_one(
        {"username": username},
        {"$set": update_data}
    )
    
    return {"message": f"User {username} updated successfully", "updated_fields": list(update_data.keys())}


@router.delete("/users/{username}", summary="Supprimer un utilisateur")
async def delete_user(
    username: str,
    current_user: dict = Depends(get_current_admin_user)
):
    """
    🗑️ Supprime un utilisateur (ADMIN uniquement)
    
    ⚠️ Cette action est irréversible et supprime aussi les alertes et portfolios de l'utilisateur.
    """
    # Empêcher l'admin de se supprimer lui-même
    if username == current_user["username"]:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    
    user = users_collection.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Supprimer les données associées
    alerts_collection = get_alerts_collection()
    portfolios_collection = get_portfolios_collection()
    transactions_collection = get_transactions_collection()
    
    deleted_alerts = alerts_collection.delete_many({"user_id": username}).deleted_count
    deleted_portfolios = portfolios_collection.delete_many({"user_id": username}).deleted_count
    deleted_transactions = transactions_collection.delete_many({"user_id": username}).deleted_count
    
    # Supprimer l'utilisateur
    users_collection.delete_one({"username": username})
    
    return {
        "message": f"User {username} deleted successfully",
        "deleted_data": {
            "alerts": deleted_alerts,
            "portfolios": deleted_portfolios,
            "transactions": deleted_transactions
        }
    }


@router.post("/users/{username}/promote", summary="Promouvoir en admin")
async def promote_to_admin(
    username: str,
    current_user: dict = Depends(get_current_admin_user)
):
    """
    ⬆️ Promouvoir un utilisateur au rôle admin
    """
    result = users_collection.update_one(
        {"username": username},
        {"$set": {"role": "admin"}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": f"User {username} promoted to admin"}


@router.post("/users/{username}/demote", summary="Rétrograder en user")
async def demote_to_user(
    username: str,
    current_user: dict = Depends(get_current_admin_user)
):
    """
    ⬇️ Rétrograder un admin au rôle utilisateur standard
    """
    if username == current_user["username"]:
        raise HTTPException(status_code=400, detail="Cannot demote yourself")
    
    result = users_collection.update_one(
        {"username": username},
        {"$set": {"role": "user"}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": f"User {username} demoted to user"}


# ===== ROUTES STATISTIQUES =====

@router.get("/stats", summary="Statistiques globales")
async def get_stats(current_user: dict = Depends(get_current_admin_user)):
    """
    📊 Récupère les statistiques globales de la plateforme (ADMIN uniquement)
    """
    alerts_collection = get_alerts_collection()
    portfolios_collection = get_portfolios_collection()
    transactions_collection = get_transactions_collection()
    prices_collection = get_collection()
    
    stats = {
        "users": {
            "total": users_collection.count_documents({}),
            "active": users_collection.count_documents({"is_active": True}),
            "admins": users_collection.count_documents({"role": "admin"}),
            "standard": users_collection.count_documents({"role": "user"})
        },
        "alerts": {
            "total": alerts_collection.count_documents({}),
            "active": alerts_collection.count_documents({"is_active": True}),
            "triggered": alerts_collection.count_documents({"triggered_at": {"$ne": None}})
        },
        "portfolios": {
            "total": portfolios_collection.count_documents({}),
            "transactions": transactions_collection.count_documents({})
        },
        "data": {
            "price_records": prices_collection.count_documents({})
        },
        "generated_at": datetime.utcnow().isoformat()
    }
    
    return stats


# ===== ROUTES DONNÉES =====

@router.delete("/data/prices/old", summary="Supprimer anciennes données")
async def delete_old_prices(
    days: int = 30,
    current_user: dict = Depends(get_current_admin_user)
):
    """
    🗑️ Supprime les données de prix plus anciennes que X jours
    
    Utile pour nettoyer la base de données.
    """
    from datetime import timedelta
    import time
    
    cutoff_timestamp = time.time() - (days * 24 * 60 * 60)
    
    prices_collection = get_collection()
    result = prices_collection.delete_many({"timestamp": {"$lt": cutoff_timestamp}})
    
    return {
        "message": f"Deleted {result.deleted_count} price records older than {days} days",
        "deleted_count": result.deleted_count
    }


@router.get("/data/collections", summary="Info collections MongoDB")
async def get_collections_info(current_user: dict = Depends(get_current_admin_user)):
    """
    📁 Récupère les informations sur les collections MongoDB
    """
    from pymongo import MongoClient
    import os
    
    MONGO_HOST = os.getenv("MONGO_HOST", "127.0.0.1")
    client = MongoClient(f"mongodb://{MONGO_HOST}:27017/")
    db = client["crypto_db"]
    
    collections_info = []
    for name in db.list_collection_names():
        collection = db[name]
        stats = {
            "name": name,
            "count": collection.count_documents({}),
            "indexes": list(collection.index_information().keys())
        }
        collections_info.append(stats)
    
    return {"collections": collections_info}


# ===== ROUTES ALERTES ADMIN =====

@router.get("/alerts", summary="Toutes les alertes")
async def get_all_alerts(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False,
    current_user: dict = Depends(get_current_admin_user)
):
    """
    🔔 Liste toutes les alertes de tous les utilisateurs (ADMIN uniquement)
    """
    alerts_collection = get_alerts_collection()
    
    query = {"is_active": True} if active_only else {}
    alerts = list(alerts_collection.find(query, {"_id": 0}).skip(skip).limit(limit))
    total = alerts_collection.count_documents(query)
    
    return {
        "alerts": alerts,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.post("/alerts/disable-all", summary="Désactiver toutes les alertes")
async def disable_all_alerts(
    current_user: dict = Depends(get_current_admin_user)
):
    """
    🔕 Désactive toutes les alertes actives (ADMIN uniquement)
    
    Utile en cas de problème système.
    """
    alerts_collection = get_alerts_collection()
    result = alerts_collection.update_many(
        {"is_active": True},
        {"$set": {"is_active": False}}
    )
    
    return {
        "message": f"Disabled {result.modified_count} alerts",
        "disabled_count": result.modified_count
    }


@router.delete("/alerts/{alert_id}", summary="Supprimer une alerte")
async def delete_alert_admin(
    alert_id: str,
    current_user: dict = Depends(get_current_admin_user)
):
    """
    🗑️ Supprime une alerte spécifique (ADMIN uniquement)
    """
    alerts_collection = get_alerts_collection()
    result = alerts_collection.delete_one({"id": alert_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    return {"message": f"Alert {alert_id} deleted"}


# ===== ROUTES NOTIFICATIONS =====

@router.get("/notifications/logs", summary="Logs des notifications")
async def get_notification_logs(
    skip: int = 0,
    limit: int = 50,
    current_user: dict = Depends(get_current_admin_user)
):
    """
    📧 Récupère les logs des notifications envoyées
    """
    from pymongo import MongoClient
    import os
    
    MONGO_HOST = os.getenv("MONGO_HOST", "127.0.0.1")
    client = MongoClient(f"mongodb://{MONGO_HOST}:27017/")
    db = client["crypto_db"]
    
    # Créer la collection si elle n'existe pas
    if "notification_logs" not in db.list_collection_names():
        return {"logs": [], "total": 0}
    
    logs_collection = db["notification_logs"]
    logs = list(logs_collection.find({}, {"_id": 0}).sort("timestamp", -1).skip(skip).limit(limit))
    total = logs_collection.count_documents({})
    
    return {
        "logs": logs,
        "total": total,
        "skip": skip,
        "limit": limit
    }


class BroadcastMessage(BaseModel):
    subject: str
    message: str
    send_email: bool = True
    send_discord: bool = True

@router.post("/notifications/broadcast", summary="Envoyer message à tous")
async def broadcast_notification(
    broadcast: BroadcastMessage,
    current_user: dict = Depends(get_current_admin_user)
):
    """
    📢 Envoie une notification à tous les utilisateurs (ADMIN uniquement)
    """
    from pymongo import MongoClient
    import os
    
    MONGO_HOST = os.getenv("MONGO_HOST", "127.0.0.1")
    client = MongoClient(f"mongodb://{MONGO_HOST}:27017/")
    db = client["crypto_db"]
    logs_collection = db["notification_logs"]
    
    # Récupérer tous les utilisateurs actifs
    users = list(users_collection.find({"is_active": True}))
    
    sent_count = 0
    errors = []
    
    for user in users:
        try:
            # Envoyer email (mode simulation si pas configuré)
            if broadcast.send_email and user.get("email"):
                try:
                    from services.email_service import send_email
                    send_email(
                        to_email=user["email"],
                        subject=f"[CryptoTracker] {broadcast.subject}",
                        body=broadcast.message
                    )
                    sent_count += 1
                except Exception as e:
                    errors.append(f"Email to {user['username']}: {str(e)}")
            
            # Envoyer Discord
            if broadcast.send_discord and user.get("discord_webhook_url"):
                try:
                    from services.discord_service import send_discord_notification
                    send_discord_notification(
                        webhook_url=user["discord_webhook_url"],
                        title=broadcast.subject,
                        message=broadcast.message
                    )
                except Exception as e:
                    errors.append(f"Discord to {user['username']}: {str(e)}")
                    
        except Exception as e:
            errors.append(f"User {user.get('username', 'unknown')}: {str(e)}")
    
    # Logger la notification
    log_entry = {
        "type": "broadcast",
        "subject": broadcast.subject,
        "message": broadcast.message,
        "sent_by": current_user["username"],
        "recipients_count": len(users),
        "sent_count": sent_count,
        "errors": errors if errors else [],
        "timestamp": datetime.utcnow()
    }
    logs_collection.insert_one(log_entry)
    
    return {
        "message": "Broadcast sent",
        "recipients": len(users),
        "sent": sent_count,
        "errors": errors if errors else None
    }


# ===== ROUTES MONITORING SYSTÈME =====

@router.get("/system/health", summary="État des services")
async def get_system_health(current_user: dict = Depends(get_current_admin_user)):
    """
    🏥 Vérifie l'état de tous les services (ADMIN uniquement)
    """
    import os
    from pymongo import MongoClient
    
    health = {
        "api": {"status": "healthy", "message": "API is running"},
        "mongodb": {"status": "unknown", "message": ""},
        "redis": {"status": "unknown", "message": ""},
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Test MongoDB
    try:
        MONGO_HOST = os.getenv("MONGO_HOST", "127.0.0.1")
        client = MongoClient(f"mongodb://{MONGO_HOST}:27017/", serverSelectionTimeoutMS=2000)
        client.server_info()
        health["mongodb"] = {"status": "healthy", "message": "Connected"}
    except Exception as e:
        health["mongodb"] = {"status": "unhealthy", "message": str(e)}
    
    # Test Redis (optionnel - ne pas bloquer si redis n'est pas installé)
    try:
        import redis
        REDIS_HOST = os.getenv("REDIS_HOST", "127.0.0.1")
        r = redis.Redis(host=REDIS_HOST, port=6379, socket_timeout=2)
        r.ping()
        health["redis"] = {"status": "healthy", "message": "Connected"}
    except ImportError:
        health["redis"] = {"status": "unavailable", "message": "Redis module not installed"}
    except Exception as e:
        health["redis"] = {"status": "unhealthy", "message": str(e)}
    
    # Status global (ignorer redis pour le status global)
    mongodb_healthy = health["mongodb"]["status"] == "healthy"
    health["overall"] = "healthy" if mongodb_healthy else "degraded"
    
    return health


@router.get("/system/activity", summary="Activité récente")
async def get_activity(
    days: int = 7,
    current_user: dict = Depends(get_current_admin_user)
):
    """
    📈 Récupère l'activité des derniers jours (inscriptions, alertes)
    """
    from datetime import timedelta
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Inscriptions par jour
    users_by_day = {}
    users = list(users_collection.find({"created_at": {"$gte": cutoff_date}}))
    for user in users:
        day = user["created_at"].strftime("%Y-%m-%d")
        users_by_day[day] = users_by_day.get(day, 0) + 1
    
    # Alertes déclenchées par jour
    alerts_collection = get_alerts_collection()
    alerts_by_day = {}
    alerts = list(alerts_collection.find({"triggered_at": {"$gte": cutoff_date}}))
    for alert in alerts:
        if alert.get("triggered_at"):
            day = alert["triggered_at"].strftime("%Y-%m-%d")
            alerts_by_day[day] = alerts_by_day.get(day, 0) + 1
    
    # Transactions par jour
    transactions_collection = get_transactions_collection()
    transactions_by_day = {}
    transactions = list(transactions_collection.find({"timestamp": {"$gte": cutoff_date}}))
    for tx in transactions:
        if tx.get("timestamp"):
            if isinstance(tx["timestamp"], datetime):
                day = tx["timestamp"].strftime("%Y-%m-%d")
            else:
                day = str(tx["timestamp"])[:10]
            transactions_by_day[day] = transactions_by_day.get(day, 0) + 1
    
    return {
        "period_days": days,
        "registrations": users_by_day,
        "alerts_triggered": alerts_by_day,
        "transactions": transactions_by_day,
        "totals": {
            "new_users": len(users),
            "alerts_triggered": len(alerts),
            "transactions": len(transactions)
        }
    }
