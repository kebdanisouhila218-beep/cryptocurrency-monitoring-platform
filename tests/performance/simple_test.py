#!/usr/bin/env python3
"""
Test simple pour vérifier l'authentification
"""

import requests
import json

def test_auth():
    """Test l'authentification avec différents formats"""
    
    base_url = "http://localhost:8000"
    
    print("="*60)
    print("🔍 TEST D'AUTHENTIFICATION")
    print("="*60)
    
    # Test 1: Login admin avec form-data
    print("\n1. Test login admin (form-data)...")
    try:
        response = requests.post(
            f"{base_url}/auth/login",
            data={
                "username": "admin",
                "password": "admin123"
            }
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
        if response.status_code == 200:
            token = response.json().get("access_token")
            print(f"   ✅ Token: {token[:50]}...")
        else:
            print(f"   ❌ Erreur: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Test 2: Login admin avec JSON
    print("\n2. Test login admin (JSON)...")
    try:
        response = requests.post(
            f"{base_url}/auth/login",
            json={
                "username": "admin",
                "password": "admin123"
            }
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
        if response.status_code == 200:
            token = response.json().get("access_token")
            print(f"   ✅ Token: {token[:50]}...")
        else:
            print(f"   ❌ Erreur: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Test 3: Créer un utilisateur
    print("\n3. Test création utilisateur...")
    try:
        username = f"test_user_{int(time.time())}"
        response = requests.post(
            f"{base_url}/auth/register",
            json={
                "username": username,
                "email": f"{username}@test.com",
                "password": "TestPassword123!"
            }
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
        
        if response.status_code == 200:
            # Test login avec le nouvel utilisateur
            print(f"\n4. Test login nouvel utilisateur ({username})...")
            login_response = requests.post(
                f"{base_url}/auth/login",
                data={
                    "username": username,
                    "password": "TestPassword123!"
                }
            )
            print(f"   Status: {login_response.status_code}")
            print(f"   Response: {login_response.text[:200]}")
            if login_response.status_code == 200:
                token = login_response.json().get("access_token")
                print(f"   ✅ Token: {token[:50]}...")
                
                # Test endpoint protégé
                print(f"\n5. Test endpoint protégé...")
                headers = {"Authorization": f"Bearer {token}"}
                prices_response = requests.get(f"{base_url}/prices", headers=headers)
                print(f"   Status: {prices_response.status_code}")
                if prices_response.status_code == 200:
                    print(f"   ✅ Prix récupérés: {len(prices_response.json().get('prices', []))}")
                else:
                    print(f"   ❌ Erreur: {prices_response.text[:200]}")
            else:
                print(f"   ❌ Login échoué")
        else:
            print(f"   ❌ Création échouée")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    print("\n" + "="*60)
    print("🏁 TEST TERMINÉ")
    print("="*60)

if __name__ == "__main__":
    import time
    test_auth()
