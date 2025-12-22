# api/services/discord_service.py - Service de notifications Discord pour les alertes

import os
from typing import Dict, Optional
from datetime import datetime

import requests


# Webhook par défaut (pour les tests ou si l'utilisateur n'en a pas configuré)
DEFAULT_DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "").strip()

# Couleurs pour les embeds Discord (en décimal)
COLOR_GREEN = 0x00FF00  # Pour "au-dessus de"
COLOR_RED = 0xFF0000    # Pour "en-dessous de"
COLOR_BLUE = 0x3498DB   # Couleur par défaut


def validate_discord_webhook_url(url: str) -> bool:
    """
    Valide le format d'une URL de webhook Discord.
    
    Args:
        url: URL du webhook à valider
    
    Returns:
        True si l'URL est valide, False sinon
    """
    if not url:
        return False
    
    # Format attendu: https://discord.com/api/webhooks/{id}/{token}
    # ou https://discordapp.com/api/webhooks/{id}/{token}
    valid_prefixes = [
        "https://discord.com/api/webhooks/",
        "https://discordapp.com/api/webhooks/",
        "https://canary.discord.com/api/webhooks/",
        "https://ptb.discord.com/api/webhooks/"
    ]
    
    return any(url.startswith(prefix) for prefix in valid_prefixes)


def create_alert_embed(alert_data: Dict) -> Dict:
    """
    Crée un embed Discord formaté pour une alerte.
    
    Args:
        alert_data: Données de l'alerte
    
    Returns:
        Dictionnaire représentant l'embed Discord
    """
    crypto_symbol = alert_data.get("crypto_symbol", "N/A")
    alert_type = alert_data.get("alert_type", "N/A")
    target_price_raw = alert_data.get("target_price", 0)
    triggered_price_raw = alert_data.get("triggered_price", 0)
    triggered_at = alert_data.get("triggered_at")

    try:
        target_price = float(target_price_raw)
    except Exception:
        target_price = 0.0

    try:
        triggered_price = float(triggered_price_raw)
    except Exception:
        triggered_price = 0.0
    
    # Déterminer l'emoji et la couleur selon le type d'alerte
    if alert_type == "above":
        emoji = "📈"
        color = COLOR_GREEN
        type_label = "Au-dessus de"
    else:
        emoji = "📉"
        color = COLOR_RED
        type_label = "En-dessous de"
    
    # Formater la date
    if isinstance(triggered_at, datetime):
        timestamp_str = triggered_at.strftime("%d/%m/%Y à %H:%M:%S")
        iso_timestamp = triggered_at.isoformat()
    else:
        timestamp_str = str(triggered_at) if triggered_at else "N/A"
        iso_timestamp = None
    
    # Calculer la différence de prix
    try:
        price_diff = triggered_price - target_price
        price_diff_percent = ((triggered_price - target_price) / target_price) * 100 if target_price > 0 else 0
        diff_sign = "+" if price_diff >= 0 else ""
        diff_text = f"{diff_sign}${price_diff:,.2f} ({diff_sign}{price_diff_percent:.2f}%)"
    except:
        diff_text = "N/A"
    
    embed = {
        "title": f"🔔 Alerte Prix Crypto - {crypto_symbol}",
        "description": f"{emoji} L'alerte **{type_label}** a été déclenchée !",
        "color": color,
        "fields": [
            {
                "name": "💰 Crypto",
                "value": f"**{crypto_symbol}**",
                "inline": True
            },
            {
                "name": f"{emoji} Type d'alerte",
                "value": f"**{type_label}**",
                "inline": True
            },
            {
                "name": "🎯 Prix cible",
                "value": f"**${target_price:,.2f}**",
                "inline": True
            },
            {
                "name": "💵 Prix actuel",
                "value": f"**${triggered_price:,.2f}**",
                "inline": True
            },
            {
                "name": "📊 Différence",
                "value": f"**{diff_text}**",
                "inline": True
            },
            {
                "name": "⏰ Déclenchée le",
                "value": f"**{timestamp_str}**",
                "inline": True
            }
        ],
        "footer": {
            "text": "🚀 Crypto Monitoring Platform"
        }
    }
    
    # Ajouter le timestamp ISO si disponible
    if iso_timestamp:
        embed["timestamp"] = iso_timestamp
    
    return embed


def send_alert_discord(alert_data: Dict, webhook_url: Optional[str] = None) -> Dict:
    """
    Envoie une notification Discord via webhook avec un embed formaté.
    
    Args:
        alert_data: Données de l'alerte à envoyer
        webhook_url: URL du webhook Discord (optionnel, utilise le défaut si non fourni)
    
    Returns:
        Dictionnaire avec le résultat de l'envoi
    """
    result = {"success": False, "error": None}
    
    # Utiliser le webhook fourni ou le webhook par défaut
    url = webhook_url if webhook_url else DEFAULT_DISCORD_WEBHOOK_URL
    
    if not url:
        result["error"] = "Aucun webhook Discord configuré"
        print("[DISCORD] ⚠️ Aucun webhook Discord configuré")
        return result
    
    if not validate_discord_webhook_url(url):
        result["error"] = "URL de webhook Discord invalide"
        print(f"[DISCORD] ⚠️ URL de webhook invalide: {url[:50]}...")
        return result
    
    # Créer l'embed
    embed = create_alert_embed(alert_data)
    
    # Payload Discord avec embed
    payload = {
        "embeds": [embed]
    }
    
    crypto_symbol = alert_data.get("crypto_symbol", "N/A")
    
    try:
        print(f"[DISCORD] 📤 Envoi notification pour {crypto_symbol}...")
        
        resp = requests.post(
            url,
            json=payload,
            timeout=10,
        )
        
        if 200 <= resp.status_code < 300:
            result["success"] = True
            print(f"[DISCORD] ✅ Notification envoyée avec succès pour {crypto_symbol}")
            return result
        
        result["error"] = f"HTTP {resp.status_code}: {resp.text}"
        print(f"[DISCORD] ❌ Erreur HTTP: {resp.status_code}")
        return result
    
    except requests.exceptions.Timeout:
        result["error"] = "Timeout lors de l'envoi"
        print("[DISCORD] ❌ Timeout lors de l'envoi")
        return result
    
    except requests.exceptions.RequestException as e:
        result["error"] = f"Erreur réseau: {str(e)}"
        print(f"[DISCORD] ❌ Erreur réseau: {e}")
        return result
    
    except Exception as e:
        result["error"] = str(e)
        print(f"[DISCORD] ❌ Erreur inattendue: {e}")
        return result


def test_discord_webhook(webhook_url: str) -> Dict:
    """
    Teste un webhook Discord en envoyant un message de test.
    
    Args:
        webhook_url: URL du webhook à tester
    
    Returns:
        Dictionnaire avec le résultat du test
    """
    result = {"success": False, "error": None}
    
    if not validate_discord_webhook_url(webhook_url):
        result["error"] = "URL de webhook Discord invalide"
        return result
    
    test_embed = {
        "title": "✅ Test de connexion réussi !",
        "description": "Votre webhook Discord est correctement configuré pour recevoir les alertes crypto.",
        "color": COLOR_BLUE,
        "fields": [
            {
                "name": "🔔 Notifications",
                "value": "Vous recevrez désormais les alertes de prix ici.",
                "inline": False
            }
        ],
        "footer": {
            "text": "🚀 Crypto Monitoring Platform"
        },
        "timestamp": datetime.utcnow().isoformat()
    }
    
    payload = {
        "embeds": [test_embed]
    }
    
    try:
        resp = requests.post(
            webhook_url,
            json=payload,
            timeout=10,
        )
        
        if 200 <= resp.status_code < 300:
            result["success"] = True
            return result
        
        result["error"] = f"HTTP {resp.status_code}: {resp.text}"
        return result
    
    except Exception as e:
        result["error"] = str(e)
        return result
