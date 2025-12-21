# api/routes/alerts.py - Routes pour les alertes de prix

from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime
from typing import List
from bson import ObjectId
from bson.errors import InvalidId

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_alerts_collection
from auth import get_current_active_user
from models.alert import (
    AlertCreate,
    AlertUpdate,
    AlertResponse,
    AlertListResponse,
    AlertType
)
from services.alert_checker import check_alerts, get_alert_stats

router = APIRouter(prefix="/alerts", tags=["Alerts"])


# ===== HELPER FUNCTIONS =====

def alert_to_response(alert: dict) -> AlertResponse:
    """Convertit un document MongoDB en AlertResponse"""
    return AlertResponse(
        id=str(alert["_id"]),
        user_id=alert["user_id"],
        crypto_symbol=alert["crypto_symbol"],
        target_price=alert["target_price"],
        alert_type=alert["alert_type"],
        is_active=alert["is_active"],
        created_at=alert["created_at"],
        triggered_at=alert.get("triggered_at")
    )


# ===== ENDPOINTS =====

@router.post("", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
async def create_alert(
    alert: AlertCreate,
    current_user: dict = Depends(get_current_active_user),
    alerts_collection = Depends(get_alerts_collection)
):
    """
    🔔 Créer une nouvelle alerte de prix
    
    🔒 Route protégée - Nécessite authentification
    
    - **crypto_symbol**: Symbole de la crypto (ex: BTC, ETH)
    - **target_price**: Prix cible (doit être > 0)
    - **alert_type**: "above" ou "below"
    """
    print(f"[DEBUG] Création d'alerte pour user: {current_user['username']}")
    print(f"[DEBUG] Données: {alert.dict()}")
    
    # Créer le document alerte
    alert_doc = {
        "user_id": str(current_user["_id"]),
        "crypto_symbol": alert.crypto_symbol,
        "target_price": alert.target_price,
        "alert_type": alert.alert_type.value,
        "is_active": True,
        "created_at": datetime.utcnow(),
        "triggered_at": None
    }
    
    result = alerts_collection.insert_one(alert_doc)
    alert_doc["_id"] = result.inserted_id
    
    print(f"[DEBUG] Alerte créée avec ID: {result.inserted_id}")
    
    return alert_to_response(alert_doc)


@router.get("", response_model=AlertListResponse)
async def list_my_alerts(
    is_active: bool = None,
    crypto_symbol: str = None,
    current_user: dict = Depends(get_current_active_user),
    alerts_collection = Depends(get_alerts_collection)
):
    """
    📋 Lister mes alertes
    
    🔒 Route protégée - Nécessite authentification
    
    Filtres optionnels:
    - **is_active**: Filtrer par statut actif/inactif
    - **crypto_symbol**: Filtrer par crypto
    """
    print(f"[DEBUG] Liste des alertes pour user: {current_user['username']}")
    
    # Construire le filtre
    query = {"user_id": str(current_user["_id"])}
    
    if is_active is not None:
        query["is_active"] = is_active
    
    if crypto_symbol:
        query["crypto_symbol"] = crypto_symbol.upper()
    
    print(f"[DEBUG] Query: {query}")
    
    alerts = list(alerts_collection.find(query).sort("created_at", -1))
    
    print(f"[DEBUG] {len(alerts)} alertes trouvées")
    
    return AlertListResponse(
        alerts=[alert_to_response(a) for a in alerts],
        count=len(alerts),
        message=f"{len(alerts)} alerte(s) trouvée(s)"
    )


@router.get("/debug")
async def debug_alerts(
    current_user: dict = Depends(get_current_active_user),
    alerts_collection = Depends(get_alerts_collection)
):
    """
    🔧 Endpoint de debug pour tester les alertes
    
    🔒 Route protégée - Nécessite authentification
    """
    print(f"[DEBUG] Debug endpoint appelé par: {current_user['username']}")
    
    user_id = str(current_user["_id"])
    
    # Stats
    total_alerts = alerts_collection.count_documents({"user_id": user_id})
    active_alerts = alerts_collection.count_documents({"user_id": user_id, "is_active": True})
    triggered_alerts = alerts_collection.count_documents({"user_id": user_id, "triggered_at": {"$ne": None}})
    
    # Dernière alerte
    last_alert = alerts_collection.find_one(
        {"user_id": user_id},
        sort=[("created_at", -1)]
    )
    
    return {
        "debug": True,
        "user": {
            "username": current_user["username"],
            "user_id": user_id
        },
        "stats": {
            "total_alerts": total_alerts,
            "active_alerts": active_alerts,
            "triggered_alerts": triggered_alerts
        },
        "last_alert": alert_to_response(last_alert) if last_alert else None,
        "message": "Debug endpoint fonctionnel ✅"
    }


@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(
    alert_id: str,
    current_user: dict = Depends(get_current_active_user),
    alerts_collection = Depends(get_alerts_collection)
):
    """
    🔍 Récupérer les détails d'une alerte
    
    🔒 Route protégée - Nécessite authentification
    """
    print(f"[DEBUG] Récupération alerte {alert_id} pour user: {current_user['username']}")
    
    # Valider l'ObjectId
    try:
        obj_id = ObjectId(alert_id)
    except InvalidId:
        print(f"[DEBUG] ID invalide: {alert_id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID d'alerte invalide"
        )
    
    # Chercher l'alerte
    alert = alerts_collection.find_one({"_id": obj_id})
    
    if not alert:
        print(f"[DEBUG] Alerte non trouvée: {alert_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alerte non trouvée"
        )
    
    # Vérifier que l'utilisateur est propriétaire
    if alert["user_id"] != str(current_user["_id"]):
        print(f"[DEBUG] Accès refusé - user_id: {current_user['_id']} != alert.user_id: {alert['user_id']}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas accès à cette alerte"
        )
    
    return alert_to_response(alert)


@router.put("/{alert_id}", response_model=AlertResponse)
async def update_alert(
    alert_id: str,
    alert_update: AlertUpdate,
    current_user: dict = Depends(get_current_active_user),
    alerts_collection = Depends(get_alerts_collection)
):
    """
    ✏️ Modifier une alerte
    
    🔒 Route protégée - Nécessite authentification
    
    Champs modifiables:
    - **crypto_symbol**: Nouveau symbole
    - **target_price**: Nouveau prix cible
    - **alert_type**: Nouveau type (above/below)
    - **is_active**: Activer/désactiver l'alerte
    """
    print(f"[DEBUG] Modification alerte {alert_id} pour user: {current_user['username']}")
    print(f"[DEBUG] Données update: {alert_update.dict(exclude_unset=True)}")
    
    # Valider l'ObjectId
    try:
        obj_id = ObjectId(alert_id)
    except InvalidId:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID d'alerte invalide"
        )
    
    # Chercher l'alerte
    alert = alerts_collection.find_one({"_id": obj_id})
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alerte non trouvée"
        )
    
    # Vérifier que l'utilisateur est propriétaire
    if alert["user_id"] != str(current_user["_id"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas accès à cette alerte"
        )
    
    # Construire les données de mise à jour
    update_data = {}
    update_dict = alert_update.dict(exclude_unset=True)
    
    for field, value in update_dict.items():
        if value is not None:
            if field == "alert_type":
                update_data[field] = value.value if hasattr(value, 'value') else value
            else:
                update_data[field] = value
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Aucune donnée à mettre à jour"
        )
    
    print(f"[DEBUG] Update data: {update_data}")
    
    # Mettre à jour
    alerts_collection.update_one(
        {"_id": obj_id},
        {"$set": update_data}
    )
    
    # Récupérer l'alerte mise à jour
    updated_alert = alerts_collection.find_one({"_id": obj_id})
    
    print(f"[DEBUG] Alerte mise à jour avec succès")
    
    return alert_to_response(updated_alert)


@router.delete("/{alert_id}", status_code=status.HTTP_200_OK)
async def delete_alert(
    alert_id: str,
    current_user: dict = Depends(get_current_active_user),
    alerts_collection = Depends(get_alerts_collection)
):
    """
    🗑️ Supprimer une alerte
    
    🔒 Route protégée - Nécessite authentification
    """
    print(f"[DEBUG] Suppression alerte {alert_id} pour user: {current_user['username']}")
    
    # Valider l'ObjectId
    try:
        obj_id = ObjectId(alert_id)
    except InvalidId:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID d'alerte invalide"
        )
    
    # Chercher l'alerte
    alert = alerts_collection.find_one({"_id": obj_id})
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alerte non trouvée"
        )
    
    # Vérifier que l'utilisateur est propriétaire
    if alert["user_id"] != str(current_user["_id"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas accès à cette alerte"
        )
    
    # Supprimer
    alerts_collection.delete_one({"_id": obj_id})
    
    print(f"[DEBUG] Alerte {alert_id} supprimée avec succès")
    
    return {
        "message": "Alerte supprimée avec succès",
        "alert_id": alert_id,
        "deleted": True
    }


# ===== ENDPOINTS DE VÉRIFICATION =====

@router.post("/check-now")
async def check_alerts_now(
    current_user: dict = Depends(get_current_active_user)
):
    """
    🔍 Forcer une vérification manuelle des alertes
    
    🔒 Route protégée - Nécessite authentification
    
    Vérifie toutes les alertes actives et déclenche celles qui ont atteint leur seuil.
    """
    print(f"[DEBUG] Vérification manuelle demandée par: {current_user['username']}")
    
    result = check_alerts()
    
    return {
        "message": "Vérification des alertes terminée",
        "user": current_user["username"],
        "result": result
    }


@router.get("/stats/global")
async def get_global_alert_stats(
    current_user: dict = Depends(get_current_active_user)
):
    """
    📊 Statistiques globales des alertes
    
    🔒 Route protégée - Nécessite authentification
    """
    print(f"[DEBUG] Stats globales demandées par: {current_user['username']}")
    
    stats = get_alert_stats()
    
    return {
        "message": "Statistiques des alertes",
        "stats": stats
    }
