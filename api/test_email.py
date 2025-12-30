from services.email_service import send_email

# Test d'envoi d'email
result = send_email(
    to_email="kebdanisouhila218@gmail.com",
    subject="Test de notification CryptoTracker",
    body="Ceci est un test d'envoi de notification depuis l'admin."
)

print(f"Résultat: {result}")
