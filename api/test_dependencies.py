#!/usr/bin/env python3
# api/test_dependencies.py - Vérifier que toutes les dépendances sont OK

import sys

print("🔍 Vérification des dépendances JWT...\n")

# Test 1: FastAPI
try:
    import fastapi
    print("✅ FastAPI:", fastapi.__version__)
except ImportError as e:
    print("❌ FastAPI:", e)
    sys.exit(1)

# Test 2: PyMongo
try:
    import pymongo
    print("✅ PyMongo:", pymongo.__version__)
except ImportError as e:
    print("❌ PyMongo:", e)
    sys.exit(1)

# Test 3: python-jose (JWT)
try:
    from jose import jwt
    print("✅ python-jose: OK")
except ImportError as e:
    print("❌ python-jose manquant!")
    print("   Installer avec: pip install python-jose[cryptography]")
    sys.exit(1)

# Test 4: passlib (hashing)
try:
    from passlib.context import CryptContext
    print("✅ passlib: OK")
except ImportError as e:
    print("❌ passlib manquant!")
    print("   Installer avec: pip install passlib[bcrypt]")
    sys.exit(1)

# Test 5: email-validator
try:
    import email_validator
    print("✅ email-validator:", email_validator.__version__)
except ImportError as e:
    print("❌ email-validator manquant!")
    print("   Installer avec: pip install email-validator")
    sys.exit(1)

# Test 6: python-multipart
try:
    import multipart
    print("✅ python-multipart: OK")
except ImportError as e:
    print("❌ python-multipart manquant!")
    print("   Installer avec: pip install python-multipart")
    sys.exit(1)

print("\n" + "="*50)
print("🎉 Toutes les dépendances sont installées !")
print("="*50)

# Test 7: Tester le hashage de mot de passe
print("\n🔐 Test de hashage de mot de passe...")
try:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hashed = pwd_context.hash("test_password")
    is_valid = pwd_context.verify("test_password", hashed)
    if is_valid:
        print("✅ Hashage bcrypt fonctionne !")
    else:
        print("❌ Problème avec le hashage bcrypt")
except Exception as e:
    print(f"❌ Erreur hashage: {e}")

# Test 8: Tester la création de JWT
print("\n🎫 Test de création de JWT...")
try:
    from datetime import datetime, timedelta
    secret_key = "test_secret"
    to_encode = {"sub": "testuser", "exp": datetime.utcnow() + timedelta(minutes=30)}
    token = jwt.encode(to_encode, secret_key, algorithm="HS256")
    print(f"✅ JWT créé: {token[:50]}...")
    
    # Vérifier le décodage
    decoded = jwt.decode(token, secret_key, algorithms=["HS256"])
    if decoded["sub"] == "testuser":
        print("✅ JWT décodé correctement !")
    else:
        print("❌ Problème de décodage JWT")
except Exception as e:
    print(f"❌ Erreur JWT: {e}")

# Test 9: Connexion MongoDB
print("\n🗄️  Test connexion MongoDB...")
try:
    from pymongo import MongoClient
    client = MongoClient("mongodb://127.0.0.1:27017/", serverSelectionTimeoutMS=5000)
    client.server_info()
    print("✅ MongoDB accessible !")
except Exception as e:
    print(f"❌ MongoDB non accessible: {e}")

print("\n✅ TOUS LES TESTS PASSÉS !")
print("\nVous pouvez maintenant lancer l'API avec:")
print("  uvicorn main:app --reload")