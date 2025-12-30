#!/usr/bin/env python3
"""
Script pour créer un utilisateur administrateur
Usage:
    python create_admin.py <username> <email> <password>
    python create_admin.py admin admin@example.com admin123
"""

import os
import sys
from datetime import datetime
from pymongo import MongoClient
from passlib.context import CryptContext

# Configuration
MONGO_HOST = os.getenv("MONGO_HOST", "127.0.0.1")
MONGO_PORT = os.getenv("MONGO_PORT", "27017")
MONGO_URI = f"mongodb://{MONGO_HOST}:{MONGO_PORT}/"
DB_NAME = "crypto_db"

# Password hashing
pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """Hash le mot de passe."""
    return pwd_context.hash(password)


def create_admin(username: str, email: str, password: str) -> bool:
    """
    Crée un utilisateur administrateur
    
    Args:
        username: Nom d'utilisateur
        email: Email
        password: Mot de passe
    
    Returns:
        True si succès
    """
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        client.server_info()  # Test connexion
        db = client[DB_NAME]
        users_collection = db["users"]
        
        print(f"✅ Connexion MongoDB réussie")
        
        # Vérifier si l'utilisateur existe
        if users_collection.find_one({"username": username}):
            print(f"❌ L'utilisateur '{username}' existe déjà")
            
            # Proposer de le promouvoir en admin
            response = input("Voulez-vous le promouvoir en admin ? (o/n): ")
            if response.lower() == 'o':
                users_collection.update_one(
                    {"username": username},
                    {"$set": {"role": "admin"}}
                )
                print(f"✅ Utilisateur '{username}' promu en admin")
                return True
            return False
        
        if users_collection.find_one({"email": email}):
            print(f"❌ L'email '{email}' est déjà utilisé")
            return False
        
        # Créer l'utilisateur admin
        admin_user = {
            "username": username,
            "email": email,
            "hashed_password": get_password_hash(password),
            "created_at": datetime.utcnow(),
            "is_active": True,
            "role": "admin"
        }
        
        result = users_collection.insert_one(admin_user)
        
        print(f"\n✅ Administrateur créé avec succès!")
        print(f"   Username: {username}")
        print(f"   Email: {email}")
        print(f"   Role: admin")
        print(f"   ID: {result.inserted_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def list_admins():
    """Liste tous les administrateurs"""
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        db = client[DB_NAME]
        users_collection = db["users"]
        
        admins = list(users_collection.find(
            {"role": "admin"},
            {"_id": 0, "hashed_password": 0}
        ))
        
        print(f"\n👥 Administrateurs ({len(admins)}):\n")
        for admin in admins:
            print(f"  👤 {admin['username']}")
            print(f"     Email: {admin['email']}")
            print(f"     Actif: {'✅' if admin.get('is_active', True) else '❌'}")
            print(f"     Créé: {admin.get('created_at', 'N/A')}")
            print()
        
        if not admins:
            print("  Aucun administrateur trouvé")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python create_admin.py <username> <email> <password>")
        print("  python create_admin.py --list")
        print("\nExemple:")
        print("  python create_admin.py admin admin@crypto.com MonMotDePasse123")
        sys.exit(1)
    
    if sys.argv[1] == "--list":
        list_admins()
        sys.exit(0)
    
    if len(sys.argv) < 4:
        print("❌ Arguments manquants")
        print("Usage: python create_admin.py <username> <email> <password>")
        sys.exit(1)
    
    username = sys.argv[1]
    email = sys.argv[2]
    password = sys.argv[3]
    
    # Validation basique
    if len(password) < 6:
        print("❌ Le mot de passe doit contenir au moins 6 caractères")
        sys.exit(1)
    
    if "@" not in email:
        print("❌ Email invalide")
        sys.exit(1)
    
    success = create_admin(username, email, password)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
