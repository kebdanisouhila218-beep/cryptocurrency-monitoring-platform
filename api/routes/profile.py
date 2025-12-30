# api/routes/profile.py - Routes pour la gestion du profil utilisateur

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, HttpUrl, field_validator
from typing import Optional
from pymongo import MongoClient
from bson import ObjectId
import os

from auth import get_current_active_user

# Import du service Discord pour la validation et le test
try:
    from services.discord_service import validate_discord_webhook_url, test_discord_webhook
except ImportError:
    from ..services.discord_service import validate_discord_webhook_url, test_discord_webhook

router = APIRouter(prefix="/profile", tags=["Profile"])

# Configuration MongoDB
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    MONGO_HOST = os.getenv("MONGO_HOST", "127.0.0.1")
    MONGO_PORT = os.getenv("MONGO_PORT", "27017")
    MONGO_URI = f"mongodb://{MONGO_HOST}:{MONGO_PORT}/"
DB_NAME = "crypto_db"


def get_users_collection():
    """Retourne la collection users"""
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    return client[DB_NAME]["users"]


# ===== MODÈLES PYDANTIC =====

class DiscordWebhookUpdate(BaseModel):
    """Modèle pour la mise à jour du webhook Discord"""
    discord_webhook_url: Optional[str] = None
    
    @field_validator('discord_webhook_url')
    @classmethod
    def validate_webhook(cls, v: Optional[str]) -> Optional[str]:
        if v is None or v == "":
            return None
        if not validate_discord_webhook_url(v):
            raise ValueError("URL de webhook Discord invalide. Format attendu: https://discord.com/api/webhooks/...")
        return v.strip()


class DiscordWebhookResponse(BaseModel):
    """Réponse pour le webhook Discord"""
    discord_webhook_url: Optional[str] = None
    is_configured: bool = False


class DiscordTestResponse(BaseModel):
    """Réponse pour le test du webhook Discord"""
    success: bool
    message: str


class ProfileResponse(BaseModel):
    """Réponse complète du profil utilisateur"""
    username: str
    email: str
    discord_webhook_url: Optional[str] = None
    discord_configured: bool = False
    notifications_email: bool = True
    notifications_discord: bool = False


# ===== ROUTES =====

@router.get("/", response_model=ProfileResponse)
async def get_profile(current_user: dict = Depends(get_current_active_user)):
    """
    👤 Récupère le profil complet de l'utilisateur connecté
    """
    discord_webhook = current_user.get("discord_webhook_url", "")
    
    return {
        "username": current_user["username"],
        "email": current_user["email"],
        "discord_webhook_url": discord_webhook if discord_webhook else None,
        "discord_configured": bool(discord_webhook),
        "notifications_email": current_user.get("notifications_email", True),
        "notifications_discord": current_user.get("notifications_discord", bool(discord_webhook))
    }


@router.get("/discord", response_model=DiscordWebhookResponse)
async def get_discord_webhook(current_user: dict = Depends(get_current_active_user)):
    """
    📱 Récupère la configuration du webhook Discord de l'utilisateur
    """
    webhook_url = current_user.get("discord_webhook_url", "")
    
    # Masquer partiellement l'URL pour la sécurité
    masked_url = None
    if webhook_url:
        # Afficher seulement les 20 premiers et 10 derniers caractères
        if len(webhook_url) > 40:
            masked_url = webhook_url[:30] + "..." + webhook_url[-10:]
        else:
            masked_url = webhook_url
    
    return {
        "discord_webhook_url": masked_url,
        "is_configured": bool(webhook_url)
    }


@router.put("/discord", response_model=DiscordWebhookResponse)
async def update_discord_webhook(
    webhook_data: DiscordWebhookUpdate,
    current_user: dict = Depends(get_current_active_user)
):
    """
    📱 Met à jour le webhook Discord de l'utilisateur
    
    - **discord_webhook_url**: URL du webhook Discord (ou null pour supprimer)
    
    Format attendu: https://discord.com/api/webhooks/{id}/{token}
    """
    users_collection = get_users_collection()
    
    try:
        user_id = current_user["_id"]
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        
        new_webhook = webhook_data.discord_webhook_url
        
        # Mettre à jour le webhook
        result = users_collection.update_one(
            {"_id": user_id},
            {
                "$set": {
                    "discord_webhook_url": new_webhook,
                    "notifications_discord": bool(new_webhook)
                }
            }
        )
        
        if result.modified_count == 0 and result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utilisateur non trouvé"
            )
        
        # Masquer l'URL pour la réponse
        masked_url = None
        if new_webhook:
            if len(new_webhook) > 40:
                masked_url = new_webhook[:30] + "..." + new_webhook[-10:]
            else:
                masked_url = new_webhook
        
        return {
            "discord_webhook_url": masked_url,
            "is_configured": bool(new_webhook)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la mise à jour: {str(e)}"
        )


@router.delete("/discord", response_model=DiscordWebhookResponse)
async def delete_discord_webhook(current_user: dict = Depends(get_current_active_user)):
    """
    🗑️ Supprime le webhook Discord de l'utilisateur
    """
    users_collection = get_users_collection()
    
    try:
        user_id = current_user["_id"]
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        
        result = users_collection.update_one(
            {"_id": user_id},
            {
                "$set": {
                    "discord_webhook_url": None,
                    "notifications_discord": False
                }
            }
        )
        
        return {
            "discord_webhook_url": None,
            "is_configured": False
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la suppression: {str(e)}"
        )


@router.post("/discord/test", response_model=DiscordTestResponse)
async def test_discord_webhook_endpoint(current_user: dict = Depends(get_current_active_user)):
    """
    🧪 Teste le webhook Discord configuré en envoyant un message de test
    """
    webhook_url = current_user.get("discord_webhook_url", "")
    
    if not webhook_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Aucun webhook Discord configuré. Configurez d'abord un webhook via PUT /profile/discord"
        )
    
    result = test_discord_webhook(webhook_url)
    
    if result["success"]:
        return {
            "success": True,
            "message": "Message de test envoyé avec succès ! Vérifiez votre canal Discord."
        }
    else:
        return {
            "success": False,
            "message": f"Échec de l'envoi: {result.get('error', 'Erreur inconnue')}"
        }
