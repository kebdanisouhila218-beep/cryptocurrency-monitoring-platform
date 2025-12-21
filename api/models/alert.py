# api/models/alert.py - Modèles Pydantic pour les alertes de prix

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, validator
from enum import Enum


class AlertType(str, Enum):
    """Type d'alerte: au-dessus ou en-dessous du prix cible"""
    ABOVE = "above"
    BELOW = "below"


class AlertBase(BaseModel):
    """Modèle de base pour les alertes"""
    crypto_symbol: str = Field(..., description="Symbole de la crypto (ex: BTC, ETH)")
    target_price: float = Field(..., gt=0, description="Prix cible (doit être > 0)")
    alert_type: AlertType = Field(..., description="Type d'alerte: above ou below")
    
    @validator('crypto_symbol')
    def crypto_symbol_uppercase(cls, v):
        """Convertit le symbole en majuscules"""
        return v.upper().strip()
    
    @validator('target_price')
    def validate_price(cls, v):
        """Valide que le prix est positif"""
        if v <= 0:
            raise ValueError('Le prix cible doit être supérieur à 0')
        return round(v, 8)  # Arrondi à 8 décimales pour les cryptos


class AlertCreate(AlertBase):
    """Modèle pour la création d'une alerte"""
    pass


class AlertUpdate(BaseModel):
    """Modèle pour la mise à jour d'une alerte"""
    crypto_symbol: Optional[str] = Field(None, description="Symbole de la crypto")
    target_price: Optional[float] = Field(None, gt=0, description="Prix cible")
    alert_type: Optional[AlertType] = Field(None, description="Type d'alerte")
    is_active: Optional[bool] = Field(None, description="Alerte active ou non")
    
    @validator('crypto_symbol')
    def crypto_symbol_uppercase(cls, v):
        """Convertit le symbole en majuscules"""
        if v is not None:
            return v.upper().strip()
        return v
    
    @validator('target_price')
    def validate_price(cls, v):
        """Valide que le prix est positif"""
        if v is not None and v <= 0:
            raise ValueError('Le prix cible doit être supérieur à 0')
        if v is not None:
            return round(v, 8)
        return v


class AlertInDB(AlertBase):
    """Modèle complet d'une alerte en base de données"""
    id: str = Field(..., description="ID unique de l'alerte")
    user_id: str = Field(..., description="ID de l'utilisateur propriétaire")
    is_active: bool = Field(default=True, description="Alerte active ou non")
    created_at: datetime = Field(..., description="Date de création")
    triggered_at: Optional[datetime] = Field(None, description="Date de déclenchement")
    
    class Config:
        from_attributes = True


class AlertResponse(AlertBase):
    """Modèle de réponse pour une alerte"""
    id: str
    user_id: str
    is_active: bool
    created_at: datetime
    triggered_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class AlertListResponse(BaseModel):
    """Modèle de réponse pour une liste d'alertes"""
    alerts: list[AlertResponse]
    count: int
    message: str = "Alertes récupérées avec succès"
