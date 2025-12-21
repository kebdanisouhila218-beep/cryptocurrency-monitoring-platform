# api/services/alert_checker.py - Service de vérification des alertes de prix

from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pymongo import MongoClient
from bson import ObjectId
import os

# Import du service email
try:
    from services.email_service import send_alert_email
    EMAIL_SERVICE_AVAILABLE = True
except ImportError:
    try:
        from .email_service import send_alert_email
        EMAIL_SERVICE_AVAILABLE = True
    except ImportError:
        EMAIL_SERVICE_AVAILABLE = False
        print("[CHECKER] ⚠️ Service email non disponible")

# Configuration MongoDB
MONGO_HOST = os.getenv("MONGO_HOST", "127.0.0.1")
MONGO_PORT = os.getenv("MONGO_PORT", "27017")
MONGO_URI = f"mongodb://{MONGO_HOST}:{MONGO_PORT}/"
DB_NAME = "crypto_db"


def get_db_connection():
    """Retourne une connexion à la base de données"""
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    return client[DB_NAME]


def get_latest_price(db, crypto_symbol: str) -> Optional[float]:
    """
    Récupère le dernier prix d'une crypto depuis la collection prices.
    
    Args:
        db: Connexion à la base de données
        crypto_symbol: Symbole de la crypto (ex: BTC, ETH)
    
    Returns:
        Le prix en USD ou None si non trouvé
    """
    prices_collection = db["prices"]
    
    # Chercher par symbol (en majuscules)
    latest = prices_collection.find_one(
        {"symbol": crypto_symbol.upper()},
        sort=[("timestamp", -1)]
    )
    
    if latest and "price_usd" in latest:
        print(f"[CHECKER] Prix trouvé pour {crypto_symbol}: ${latest['price_usd']:.2f}")
        return latest["price_usd"]
    
    print(f"[CHECKER] ⚠️ Prix non trouvé pour {crypto_symbol}")
    return None


def get_user_email(db, user_id: str) -> Optional[str]:
    """
    Récupère l'email d'un utilisateur depuis la collection users.
    
    Args:
        db: Connexion à la base de données
        user_id: ID de l'utilisateur
    
    Returns:
        L'email de l'utilisateur ou None si non trouvé
    """
    users_collection = db["users"]
    
    try:
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        if user and "email" in user:
            return user["email"]
    except Exception as e:
        print(f"[CHECKER] ⚠️ Erreur récupération email user {user_id}: {e}")
    
    return None


def trigger_alert(db, alert: dict, current_price: float) -> bool:
    """
    Déclenche une alerte : met à jour is_active=False et triggered_at.
    Envoie également un email de notification à l'utilisateur.
    
    Args:
        db: Connexion à la base de données
        alert: Document de l'alerte
        current_price: Prix actuel qui a déclenché l'alerte
    
    Returns:
        True si l'alerte a été déclenchée avec succès
    """
    alerts_collection = db["alerts"]
    triggered_at = datetime.utcnow()
    
    try:
        result = alerts_collection.update_one(
            {"_id": alert["_id"]},
            {
                "$set": {
                    "is_active": False,
                    "triggered_at": triggered_at,
                    "triggered_price": current_price
                }
            }
        )
        
        if result.modified_count > 0:
            print(f"[CHECKER] 🔔 ALERTE DÉCLENCHÉE!")
            print(f"[CHECKER]    - Crypto: {alert['crypto_symbol']}")
            print(f"[CHECKER]    - Type: {alert['alert_type']}")
            print(f"[CHECKER]    - Prix cible: ${alert['target_price']:.2f}")
            print(f"[CHECKER]    - Prix actuel: ${current_price:.2f}")
            print(f"[CHECKER]    - User ID: {alert['user_id']}")
            
            # ===== ENVOI EMAIL DE NOTIFICATION =====
            if EMAIL_SERVICE_AVAILABLE:
                user_email = get_user_email(db, alert["user_id"])
                
                if user_email:
                    print(f"[CHECKER] 📧 Envoi email à {user_email}...")
                    
                    alert_data = {
                        "crypto_symbol": alert["crypto_symbol"],
                        "alert_type": alert["alert_type"],
                        "target_price": alert["target_price"],
                        "triggered_price": current_price,
                        "triggered_at": triggered_at
                    }
                    
                    email_result = send_alert_email(user_email, alert_data)
                    
                    if email_result.get("success"):
                        print(f"[CHECKER] ✅ Email envoyé avec succès")
                    else:
                        print(f"[CHECKER] ⚠️ Échec envoi email: {email_result.get('error')}")
                else:
                    print(f"[CHECKER] ⚠️ Email utilisateur non trouvé")
            else:
                print(f"[CHECKER] ⚠️ Service email non disponible")
            
            return True
        
        return False
        
    except Exception as e:
        print(f"[CHECKER] ❌ Erreur lors du déclenchement: {e}")
        return False


def check_single_alert(db, alert: dict) -> Tuple[bool, Optional[str]]:
    """
    Vérifie une seule alerte.
    
    Args:
        db: Connexion à la base de données
        alert: Document de l'alerte à vérifier
    
    Returns:
        Tuple (triggered: bool, message: str ou None)
    """
    crypto_symbol = alert["crypto_symbol"]
    target_price = alert["target_price"]
    alert_type = alert["alert_type"]
    
    # Récupérer le prix actuel
    current_price = get_latest_price(db, crypto_symbol)
    
    if current_price is None:
        return False, f"Prix non disponible pour {crypto_symbol}"
    
    # Vérifier selon le type d'alerte
    triggered = False
    
    if alert_type == "above" and current_price >= target_price:
        triggered = True
        message = f"{crypto_symbol} >= ${target_price:.2f} (actuel: ${current_price:.2f})"
    elif alert_type == "below" and current_price <= target_price:
        triggered = True
        message = f"{crypto_symbol} <= ${target_price:.2f} (actuel: ${current_price:.2f})"
    else:
        message = None
    
    if triggered:
        trigger_alert(db, alert, current_price)
        return True, message
    
    return False, None


def check_alerts() -> Dict:
    """
    Vérifie toutes les alertes actives et déclenche celles qui ont atteint leur seuil.
    
    Returns:
        Dictionnaire avec les statistiques de la vérification
    """
    print("\n" + "="*60)
    print("[CHECKER] 🔍 Début de la vérification des alertes...")
    print("="*60)
    
    start_time = datetime.utcnow()
    
    result = {
        "checked_at": start_time.isoformat(),
        "total_active_alerts": 0,
        "alerts_checked": 0,
        "alerts_triggered": 0,
        "alerts_skipped": 0,
        "triggered_details": [],
        "errors": []
    }
    
    try:
        db = get_db_connection()
        alerts_collection = db["alerts"]
        
        # Récupérer toutes les alertes actives
        active_alerts = list(alerts_collection.find({"is_active": True}))
        result["total_active_alerts"] = len(active_alerts)
        
        print(f"[CHECKER] 📊 {len(active_alerts)} alerte(s) active(s) à vérifier")
        
        if len(active_alerts) == 0:
            print("[CHECKER] ℹ️ Aucune alerte active à vérifier")
            return result
        
        # Vérifier chaque alerte
        for alert in active_alerts:
            result["alerts_checked"] += 1
            alert_id = str(alert["_id"])
            
            print(f"\n[CHECKER] Vérification alerte {alert_id}:")
            print(f"[CHECKER]    - Crypto: {alert['crypto_symbol']}")
            print(f"[CHECKER]    - Type: {alert['alert_type']}")
            print(f"[CHECKER]    - Prix cible: ${alert['target_price']:.2f}")
            
            try:
                triggered, message = check_single_alert(db, alert)
                
                if triggered:
                    result["alerts_triggered"] += 1
                    result["triggered_details"].append({
                        "alert_id": alert_id,
                        "crypto_symbol": alert["crypto_symbol"],
                        "alert_type": alert["alert_type"],
                        "target_price": alert["target_price"],
                        "message": message
                    })
                elif message:
                    # Erreur (prix non trouvé)
                    result["alerts_skipped"] += 1
                    result["errors"].append({
                        "alert_id": alert_id,
                        "error": message
                    })
                    
            except Exception as e:
                result["errors"].append({
                    "alert_id": alert_id,
                    "error": str(e)
                })
                print(f"[CHECKER] ❌ Erreur: {e}")
        
        # Résumé
        duration = (datetime.utcnow() - start_time).total_seconds()
        result["duration_seconds"] = duration
        
        print("\n" + "="*60)
        print(f"[CHECKER] ✅ Vérification terminée en {duration:.2f}s")
        print(f"[CHECKER] 📊 Résumé:")
        print(f"[CHECKER]    - Alertes vérifiées: {result['alerts_checked']}")
        print(f"[CHECKER]    - Alertes déclenchées: {result['alerts_triggered']}")
        print(f"[CHECKER]    - Alertes ignorées: {result['alerts_skipped']}")
        print(f"[CHECKER]    - Erreurs: {len(result['errors'])}")
        print("="*60 + "\n")
        
        return result
        
    except Exception as e:
        print(f"[CHECKER] ❌ Erreur critique: {e}")
        result["errors"].append({"error": str(e)})
        return result


def get_alert_stats() -> Dict:
    """
    Retourne les statistiques des alertes.
    
    Returns:
        Dictionnaire avec les stats
    """
    try:
        db = get_db_connection()
        alerts_collection = db["alerts"]
        
        total = alerts_collection.count_documents({})
        active = alerts_collection.count_documents({"is_active": True})
        triggered = alerts_collection.count_documents({"triggered_at": {"$ne": None}})
        
        # Dernière alerte déclenchée
        last_triggered = alerts_collection.find_one(
            {"triggered_at": {"$ne": None}},
            sort=[("triggered_at", -1)]
        )
        
        return {
            "total_alerts": total,
            "active_alerts": active,
            "triggered_alerts": triggered,
            "inactive_alerts": total - active,
            "last_triggered": {
                "alert_id": str(last_triggered["_id"]),
                "crypto_symbol": last_triggered["crypto_symbol"],
                "triggered_at": last_triggered["triggered_at"].isoformat()
            } if last_triggered else None
        }
        
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    # Test manuel
    print("Test du service alert_checker...")
    result = check_alerts()
    print(f"\nRésultat: {result}")
