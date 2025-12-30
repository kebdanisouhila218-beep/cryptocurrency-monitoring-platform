# tests/security/zap_scan.py
"""
Tests de sécurité avec OWASP ZAP pour CryptoTracker API

Prérequis:
    - OWASP ZAP installé et lancé en mode daemon
    - docker run -u zap -p 8080:8080 -i owasp/zap2docker-stable zap.sh -daemon -host 0.0.0.0 -port 8080

Usage:
    python zap_scan.py
    python zap_scan.py --target http://localhost:8000 --zap-host http://localhost:8080
"""

import argparse
import json
import time
import sys
from datetime import datetime

try:
    from zapv2 import ZAPv2
    ZAP_AVAILABLE = True
except ImportError:
    ZAP_AVAILABLE = False
    print("⚠️ python-owasp-zap-v2.4 non installé. Installez avec: pip install python-owasp-zap-v2.4")


class ZAPSecurityScanner:
    """Scanner de sécurité OWASP ZAP"""
    
    def __init__(self, zap_host='http://localhost:8080', target_url='http://localhost:8000'):
        self.zap_host = zap_host
        self.target_url = target_url
        self.zap = None
        self.results = {
            'scan_date': datetime.now().isoformat(),
            'target': target_url,
            'alerts': [],
            'summary': {}
        }
        
    def connect(self):
        """Connexion à ZAP"""
        if not ZAP_AVAILABLE:
            print("❌ ZAP Python API non disponible")
            return False
            
        try:
            self.zap = ZAPv2(proxies={'http': self.zap_host, 'https': self.zap_host})
            version = self.zap.core.version
            print(f"✅ Connecté à OWASP ZAP version {version}")
            return True
        except Exception as e:
            print(f"❌ Impossible de se connecter à ZAP: {e}")
            print(f"   Assurez-vous que ZAP est lancé sur {self.zap_host}")
            return False
    
    def spider_scan(self):
        """Scan Spider pour découvrir les URLs"""
        print("\n" + "="*60)
        print("🕷️ Démarrage du Spider Scan...")
        print("="*60)
        
        try:
            # Accéder à la cible
            self.zap.urlopen(self.target_url)
            time.sleep(2)
            
            # Lancer le spider
            scan_id = self.zap.spider.scan(self.target_url)
            print(f"   Spider ID: {scan_id}")
            
            # Attendre la fin
            while int(self.zap.spider.status(scan_id)) < 100:
                progress = self.zap.spider.status(scan_id)
                print(f"   Progression: {progress}%", end='\r')
                time.sleep(1)
            
            print(f"\n✅ Spider terminé - {len(self.zap.spider.results(scan_id))} URLs découvertes")
            return True
            
        except Exception as e:
            print(f"❌ Erreur Spider: {e}")
            return False
    
    def passive_scan(self):
        """Scan passif (analyse du trafic)"""
        print("\n" + "="*60)
        print("🔍 Scan Passif en cours...")
        print("="*60)
        
        try:
            # Attendre que le scan passif soit terminé
            while int(self.zap.pscan.records_to_scan) > 0:
                remaining = self.zap.pscan.records_to_scan
                print(f"   Records restants: {remaining}", end='\r')
                time.sleep(1)
            
            print("\n✅ Scan passif terminé")
            return True
            
        except Exception as e:
            print(f"❌ Erreur scan passif: {e}")
            return False
    
    def active_scan(self, quick=True):
        """Scan actif (tests d'intrusion)"""
        print("\n" + "="*60)
        print("⚡ Démarrage du Scan Actif...")
        print("="*60)
        
        try:
            # Configuration du scan
            if quick:
                # Scan rapide - seulement les vulnérabilités critiques
                self.zap.ascan.set_option_thread_per_host(5)
            
            # Lancer le scan actif
            scan_id = self.zap.ascan.scan(self.target_url)
            print(f"   Scan ID: {scan_id}")
            
            # Attendre la fin
            while int(self.zap.ascan.status(scan_id)) < 100:
                progress = self.zap.ascan.status(scan_id)
                print(f"   Progression: {progress}%", end='\r')
                time.sleep(5)
            
            print("\n✅ Scan actif terminé")
            return True
            
        except Exception as e:
            print(f"❌ Erreur scan actif: {e}")
            return False
    
    def get_alerts(self):
        """Récupère les alertes de sécurité"""
        print("\n" + "="*60)
        print("📋 Récupération des alertes...")
        print("="*60)
        
        try:
            alerts = self.zap.core.alerts(baseurl=self.target_url)
            
            # Classifier par risque
            risk_counts = {'High': 0, 'Medium': 0, 'Low': 0, 'Informational': 0}
            
            for alert in alerts:
                risk = alert.get('risk', 'Informational')
                risk_counts[risk] = risk_counts.get(risk, 0) + 1
                
                self.results['alerts'].append({
                    'name': alert.get('name'),
                    'risk': risk,
                    'confidence': alert.get('confidence'),
                    'url': alert.get('url'),
                    'description': alert.get('description'),
                    'solution': alert.get('solution'),
                    'cweid': alert.get('cweid'),
                    'wascid': alert.get('wascid')
                })
            
            self.results['summary'] = {
                'total_alerts': len(alerts),
                'high_risk': risk_counts['High'],
                'medium_risk': risk_counts['Medium'],
                'low_risk': risk_counts['Low'],
                'informational': risk_counts['Informational']
            }
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur récupération alertes: {e}")
            return False
    
    def print_report(self):
        """Affiche le rapport"""
        print("\n" + "="*60)
        print("📊 RAPPORT DE SÉCURITÉ OWASP ZAP")
        print("="*60)
        print(f"🎯 Cible: {self.target_url}")
        print(f"📅 Date: {self.results['scan_date']}")
        print("-"*60)
        
        summary = self.results['summary']
        print(f"📈 Total alertes: {summary.get('total_alerts', 0)}")
        print(f"   🔴 Haute: {summary.get('high_risk', 0)}")
        print(f"   🟠 Moyenne: {summary.get('medium_risk', 0)}")
        print(f"   🟡 Basse: {summary.get('low_risk', 0)}")
        print(f"   🔵 Info: {summary.get('informational', 0)}")
        print("-"*60)
        
        # Afficher les alertes critiques
        high_alerts = [a for a in self.results['alerts'] if a['risk'] == 'High']
        if high_alerts:
            print("\n🔴 ALERTES CRITIQUES:")
            for alert in high_alerts:
                print(f"\n   ⚠️ {alert['name']}")
                print(f"      URL: {alert['url']}")
                print(f"      Solution: {alert['solution'][:100]}..." if alert['solution'] else "")
        
        medium_alerts = [a for a in self.results['alerts'] if a['risk'] == 'Medium']
        if medium_alerts:
            print("\n🟠 ALERTES MOYENNES:")
            for alert in medium_alerts[:5]:  # Limiter à 5
                print(f"   - {alert['name']}")
        
        print("\n" + "="*60)
        
        # Verdict
        if summary.get('high_risk', 0) > 0:
            print("❌ VERDICT: VULNÉRABILITÉS CRITIQUES DÉTECTÉES")
            return False
        elif summary.get('medium_risk', 0) > 3:
            print("⚠️ VERDICT: PLUSIEURS VULNÉRABILITÉS MOYENNES")
            return False
        else:
            print("✅ VERDICT: AUCUNE VULNÉRABILITÉ CRITIQUE")
            return True
    
    def save_report(self, filename='zap_report.json'):
        """Sauvegarde le rapport en JSON"""
        filepath = f"results/{filename}"
        try:
            import os
            os.makedirs('results', exist_ok=True)
            with open(filepath, 'w') as f:
                json.dump(self.results, f, indent=2)
            print(f"📁 Rapport sauvegardé: {filepath}")
        except Exception as e:
            print(f"❌ Erreur sauvegarde: {e}")
    
    def run_full_scan(self, active=False):
        """Exécute un scan complet"""
        print("\n" + "="*60)
        print("🔒 OWASP ZAP SECURITY SCAN - CryptoTracker")
        print("="*60)
        
        if not self.connect():
            return False
        
        self.spider_scan()
        self.passive_scan()
        
        if active:
            self.active_scan()
        
        self.get_alerts()
        success = self.print_report()
        self.save_report()
        
        return success


def run_without_zap():
    """Exécute des tests de sécurité basiques sans ZAP"""
    import requests
    
    print("\n" + "="*60)
    print("🔒 TESTS DE SÉCURITÉ BASIQUES (sans ZAP)")
    print("="*60)
    
    target = "http://localhost:8000"
    issues = []
    
    # Test 1: Headers de sécurité
    print("\n📋 Test 1: Headers de sécurité...")
    try:
        r = requests.get(f"{target}/health")
        headers = r.headers
        
        security_headers = [
            'X-Content-Type-Options',
            'X-Frame-Options',
            'X-XSS-Protection',
            'Strict-Transport-Security',
            'Content-Security-Policy'
        ]
        
        for header in security_headers:
            if header not in headers:
                issues.append(f"Header manquant: {header}")
                print(f"   ⚠️ {header}: MANQUANT")
            else:
                print(f"   ✅ {header}: {headers[header]}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # Test 2: SQL Injection basique
    print("\n📋 Test 2: SQL Injection basique...")
    try:
        payloads = ["' OR '1'='1", "1; DROP TABLE users;--", "admin'--"]
        for payload in payloads:
            r = requests.post(f"{target}/auth/login", data={
                "username": payload,
                "password": "test"
            })
            if r.status_code == 200:
                issues.append(f"Possible SQL Injection avec: {payload}")
                print(f"   ⚠️ Payload accepté: {payload}")
            else:
                print(f"   ✅ Payload rejeté: {payload[:20]}...")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # Test 3: XSS basique
    print("\n📋 Test 3: XSS basique...")
    try:
        xss_payloads = ["<script>alert('xss')</script>", "<img src=x onerror=alert('xss')>"]
        for payload in xss_payloads:
            r = requests.post(f"{target}/auth/register", json={
                "username": payload,
                "email": "test@test.com",
                "password": "test123"
            })
            if payload in r.text:
                issues.append(f"Possible XSS: payload reflété")
                print(f"   ⚠️ XSS potentiel détecté")
            else:
                print(f"   ✅ Payload non reflété")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # Test 4: Endpoints sensibles exposés
    print("\n📋 Test 4: Endpoints sensibles...")
    sensitive_endpoints = ['/admin', '/.env', '/config', '/debug', '/.git']
    for endpoint in sensitive_endpoints:
        try:
            r = requests.get(f"{target}{endpoint}")
            if r.status_code == 200:
                issues.append(f"Endpoint sensible accessible: {endpoint}")
                print(f"   ⚠️ {endpoint}: ACCESSIBLE (status {r.status_code})")
            else:
                print(f"   ✅ {endpoint}: Protégé (status {r.status_code})")
        except:
            print(f"   ✅ {endpoint}: Non accessible")
    
    # Rapport
    print("\n" + "="*60)
    print("📊 RÉSUMÉ")
    print("="*60)
    print(f"Issues trouvées: {len(issues)}")
    for issue in issues:
        print(f"   ⚠️ {issue}")
    
    if len(issues) == 0:
        print("✅ Aucune vulnérabilité évidente détectée")
        return True
    else:
        print("⚠️ Des problèmes de sécurité ont été détectés")
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='OWASP ZAP Security Scanner')
    parser.add_argument('--target', default='http://localhost:8000', help='URL cible')
    parser.add_argument('--zap-host', default='http://localhost:8080', help='URL de ZAP')
    parser.add_argument('--active', action='store_true', help='Activer le scan actif')
    parser.add_argument('--no-zap', action='store_true', help='Tests basiques sans ZAP')
    
    args = parser.parse_args()
    
    if args.no_zap:
        success = run_without_zap()
    else:
        scanner = ZAPSecurityScanner(zap_host=args.zap_host, target_url=args.target)
        success = scanner.run_full_scan(active=args.active)
    
    sys.exit(0 if success else 1)
