# api/services/email_service.py - Service d'envoi d'emails pour les alertes

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Optional
import os
from datetime import datetime


# Configuration SMTP (depuis variables d'environnement)
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", SMTP_USER)
SMTP_FROM_NAME = os.getenv("SMTP_FROM_NAME", "Crypto Monitoring")

# Mode debug (n'envoie pas vraiment l'email)
EMAIL_DEBUG_MODE = os.getenv("EMAIL_DEBUG_MODE", "true").lower() == "true"


def get_alert_email_template(alert_data: Dict) -> str:
    """
    Génère le template HTML pour l'email d'alerte.
    
    Args:
        alert_data: Dictionnaire contenant les données de l'alerte
    
    Returns:
        HTML formaté pour l'email
    """
    crypto_symbol = alert_data.get("crypto_symbol", "N/A")
    alert_type = alert_data.get("alert_type", "N/A")
    target_price = alert_data.get("target_price", 0)
    triggered_price = alert_data.get("triggered_price", 0)
    triggered_at = alert_data.get("triggered_at", datetime.utcnow())
    
    # Formater la date
    if isinstance(triggered_at, datetime):
        triggered_at_str = triggered_at.strftime("%d/%m/%Y à %H:%M:%S UTC")
    else:
        triggered_at_str = str(triggered_at)
    
    # Déterminer le message selon le type d'alerte
    if alert_type == "above":
        condition_text = f"a dépassé le seuil de"
        emoji = "📈"
        color = "#28a745"  # Vert
    else:
        condition_text = f"est passé sous le seuil de"
        emoji = "📉"
        color = "#dc3545"  # Rouge
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #f5f5f5;
                margin: 0;
                padding: 20px;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                background-color: #ffffff;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                overflow: hidden;
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }}
            .header h1 {{
                margin: 0;
                font-size: 24px;
            }}
            .content {{
                padding: 30px;
            }}
            .alert-box {{
                background-color: {color}15;
                border-left: 4px solid {color};
                padding: 20px;
                margin: 20px 0;
                border-radius: 0 8px 8px 0;
            }}
            .price-info {{
                display: flex;
                justify-content: space-between;
                margin: 15px 0;
                padding: 15px;
                background-color: #f8f9fa;
                border-radius: 8px;
            }}
            .price-item {{
                text-align: center;
            }}
            .price-label {{
                font-size: 12px;
                color: #6c757d;
                text-transform: uppercase;
            }}
            .price-value {{
                font-size: 24px;
                font-weight: bold;
                color: #333;
            }}
            .footer {{
                background-color: #f8f9fa;
                padding: 20px;
                text-align: center;
                font-size: 12px;
                color: #6c757d;
            }}
            .crypto-symbol {{
                font-size: 36px;
                font-weight: bold;
                color: {color};
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔔 Alerte Prix Crypto</h1>
            </div>
            <div class="content">
                <div class="alert-box">
                    <p style="margin: 0; font-size: 18px;">
                        {emoji} <span class="crypto-symbol">{crypto_symbol}</span> {condition_text} 
                        <strong>${target_price:,.2f}</strong>
                    </p>
                </div>
                
                <div class="price-info">
                    <div class="price-item">
                        <div class="price-label">Prix cible</div>
                        <div class="price-value">${target_price:,.2f}</div>
                    </div>
                    <div class="price-item">
                        <div class="price-label">Prix actuel</div>
                        <div class="price-value" style="color: {color};">${triggered_price:,.2f}</div>
                    </div>
                </div>
                
                <p style="color: #6c757d; font-size: 14px;">
                    ⏰ Alerte déclenchée le <strong>{triggered_at_str}</strong>
                </p>
                
                <p style="margin-top: 30px;">
                    Connectez-vous à votre tableau de bord pour voir plus de détails et gérer vos alertes.
                </p>
            </div>
            <div class="footer">
                <p>Cet email a été envoyé automatiquement par Crypto Monitoring Platform.</p>
                <p>© 2024 Crypto Monitoring - Tous droits réservés</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html


def get_alert_email_text(alert_data: Dict) -> str:
    """
    Génère la version texte de l'email d'alerte.
    
    Args:
        alert_data: Dictionnaire contenant les données de l'alerte
    
    Returns:
        Texte formaté pour l'email
    """
    crypto_symbol = alert_data.get("crypto_symbol", "N/A")
    alert_type = alert_data.get("alert_type", "N/A")
    target_price = alert_data.get("target_price", 0)
    triggered_price = alert_data.get("triggered_price", 0)
    triggered_at = alert_data.get("triggered_at", datetime.utcnow())
    
    if isinstance(triggered_at, datetime):
        triggered_at_str = triggered_at.strftime("%d/%m/%Y à %H:%M:%S UTC")
    else:
        triggered_at_str = str(triggered_at)
    
    if alert_type == "above":
        condition_text = "a dépassé le seuil"
    else:
        condition_text = "est passé sous le seuil"
    
    text = f"""
🔔 ALERTE PRIX CRYPTO

{crypto_symbol} {condition_text} de ${target_price:,.2f}

Prix cible: ${target_price:,.2f}
Prix actuel: ${triggered_price:,.2f}

⏰ Alerte déclenchée le {triggered_at_str}

---
Crypto Monitoring Platform
    """
    
    return text.strip()


def send_alert_email(user_email: str, alert_data: Dict) -> Dict:
    """
    Envoie un email d'alerte à l'utilisateur.
    
    Args:
        user_email: Adresse email de l'utilisateur
        alert_data: Dictionnaire contenant les données de l'alerte
            - crypto_symbol: Symbole de la crypto
            - alert_type: Type d'alerte (above/below)
            - target_price: Prix cible
            - triggered_price: Prix qui a déclenché l'alerte
            - triggered_at: Date de déclenchement
    
    Returns:
        Dictionnaire avec le statut de l'envoi
    """
    print(f"\n[EMAIL] 📧 Préparation de l'email pour: {user_email}")
    print(f"[EMAIL] Données alerte: {alert_data}")
    
    result = {
        "success": False,
        "recipient": user_email,
        "error": None
    }
    
    # Vérifier la configuration SMTP
    if not SMTP_USER or not SMTP_PASSWORD:
        if EMAIL_DEBUG_MODE:
            print(f"[EMAIL] ⚠️ Mode DEBUG activé - Email non envoyé")
            print(f"[EMAIL] Destinataire: {user_email}")
            print(f"[EMAIL] Sujet: 🔔 Alerte {alert_data.get('crypto_symbol', 'N/A')} - Prix atteint!")
            result["success"] = True
            result["debug_mode"] = True
            return result
        else:
            print(f"[EMAIL] ❌ Configuration SMTP manquante (SMTP_USER ou SMTP_PASSWORD)")
            result["error"] = "Configuration SMTP manquante"
            return result
    
    try:
        # Créer le message
        message = MIMEMultipart("alternative")
        crypto_symbol = alert_data.get("crypto_symbol", "CRYPTO")
        message["Subject"] = f"🔔 Alerte {crypto_symbol} - Prix atteint!"
        message["From"] = f"{SMTP_FROM_NAME} <{SMTP_FROM_EMAIL}>"
        message["To"] = user_email
        
        # Ajouter les versions texte et HTML
        text_content = get_alert_email_text(alert_data)
        html_content = get_alert_email_template(alert_data)
        
        part1 = MIMEText(text_content, "plain")
        part2 = MIMEText(html_content, "html")
        
        message.attach(part1)
        message.attach(part2)
        
        # Envoyer l'email
        print(f"[EMAIL] 📤 Connexion au serveur SMTP {SMTP_HOST}:{SMTP_PORT}...")
        
        context = ssl.create_default_context()
        
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls(context=context)
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_FROM_EMAIL, user_email, message.as_string())
        
        print(f"[EMAIL] ✅ Email envoyé avec succès à {user_email}")
        result["success"] = True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"[EMAIL] ❌ Erreur d'authentification SMTP: {e}")
        result["error"] = f"Erreur d'authentification: {str(e)}"
        
    except smtplib.SMTPException as e:
        print(f"[EMAIL] ❌ Erreur SMTP: {e}")
        result["error"] = f"Erreur SMTP: {str(e)}"
        
    except Exception as e:
        print(f"[EMAIL] ❌ Erreur inattendue: {e}")
        result["error"] = str(e)
    
    return result


def send_test_email(recipient_email: str) -> Dict:
    """
    Envoie un email de test pour vérifier la configuration SMTP.
    
    Args:
        recipient_email: Adresse email du destinataire
    
    Returns:
        Dictionnaire avec le statut de l'envoi
    """
    test_alert_data = {
        "crypto_symbol": "BTC",
        "alert_type": "above",
        "target_price": 50000.00,
        "triggered_price": 51234.56,
        "triggered_at": datetime.utcnow()
    }
    
    print(f"[EMAIL] 🧪 Envoi d'un email de test à {recipient_email}")
    return send_alert_email(recipient_email, test_alert_data)


if __name__ == "__main__":
    # Test manuel
    print("Test du service email...")
    result = send_test_email("test@example.com")
    print(f"\nRésultat: {result}")
