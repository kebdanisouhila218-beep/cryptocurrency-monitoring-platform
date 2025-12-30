#!/usr/bin/env python3
"""
Test différents formats de login pour trouver le bon
"""

import requests
import json

def test_login_formats():
    """Test différents formats de login"""
    
    base_url = "http://localhost:8000"
    
    print("="*60)
    print("🔍 TEST DIFFÉRENTS FORMATS DE LOGIN")
    print("="*60)
    
    formats = [
        {
            "name": "Form-data (dict)",
            "method": requests.post,
            "kwargs": {
                "url": f"{base_url}/auth/login",
                "data": {
                    "username": "admin",
                    "password": "MotDePasse123"
                }
            }
        },
        {
            "name": "Form-data (string)",
            "method": requests.post,
            "kwargs": {
                "url": f"{base_url}/auth/login",
                "data": "username=admin&MotDePasse123",
                "headers": {"Content-Type": "application/x-www-form-urlencoded"}
            }
        },
        {
            "name": "JSON",
            "method": requests.post,
            "kwargs": {
                "url": f"{base_url}/auth/login",
                "json": {
                    "username": "admin",
                    "password": "MotDePasse123"
                }
            }
        },
        {
            "name": "Form-data avec content-type explicite",
            "method": requests.post,
            "kwargs": {
                "url": f"{base_url}/auth/login",
                "data": {
                    "username": "admin",
                    "password": "MotDePasse123"
                },
                "headers": {"Content-Type": "application/x-www-form-urlencoded"}
            }
        }
    ]
    
    for i, format_test in enumerate(formats, 1):
        print(f"\n{i}. Test: {format_test['name']}")
        print("-" * 40)
        
        try:
            response = format_test["method"](**format_test["kwargs"])
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                token = response.json().get("access_token")
                print(f"   ✅ SUCCESS - Token: {token[:50]}...")
                
                # Test endpoint protégé
                headers = {"Authorization": f"Bearer {token}"}
                test_response = requests.get(f"{base_url}/prices", headers=headers)
                print(f"   Test endpoint: {test_response.status_code}")
                
            else:
                print(f"   ❌ FAILED - Response: {response.text[:200]}")
                print(f"   Headers sent: {format_test['kwargs'].get('headers', {})}")
                
        except Exception as e:
            print(f"   ❌ EXCEPTION: {e}")
    
    print("\n" + "="*60)
    print("🏁 TEST TERMINÉ")
    print("="*60)

if __name__ == "__main__":
    test_login_formats()
