#!/usr/bin/env python3
"""
Vérifier si l'utilisateur admin existe dans la base de données
"""

import pymongo
from pymongo import MongoClient

def check_admin_user():
    """Vérifie l'utilisateur admin dans MongoDB"""
    
    try:
        # Connexion à MongoDB
        client = MongoClient("mongodb://127.0.0.1:27017/", serverSelectionTimeoutMS=5000)
        db = client["crypto_db"]
        users_collection = db["users"]
        
        print("="*60)
        print("🔍 VÉRIFICATION UTILISATEUR ADMIN")
        print("="*60)
        
        # Chercher l'utilisateur admin
        admin_user = users_collection.find_one({"username": "admin"})
        
        if admin_user:
            print("✅ Utilisateur admin trouvé:")
            print(f"   Username: {admin_user.get('username')}")
            print(f"   Email: {admin_user.get('email')}")
            print(f"   Created: {admin_user.get('created_at')}")
            print(f"   Active: {admin_user.get('is_active')}")
            print(f"   Role: {admin_user.get('role')}")
            
            # Vérifier le mot de passe
            hashed_password = admin_user.get('hashed_password')
            print(f"   Hashed password: {hashed_password[:50]}..." if hashed_password else "   No password")
        else:
            print("❌ Utilisateur admin NON trouvé dans la base de données")
            
            # Lister tous les utilisateurs
            print("\n📋 Liste de tous les utilisateurs:")
            users = list(users_collection.find({}, {"_id": 0, "hashed_password": 0}))
            for user in users:
                print(f"   - {user.get('username')} ({user.get('email')})")
        
        print("\n" + "="*60)
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    finally:
        if 'client' in locals():
            client.close()

if __name__ == "__main__":
    check_admin_user()
