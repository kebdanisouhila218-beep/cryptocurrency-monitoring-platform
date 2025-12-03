Voici une présentation de 3 minutes simple et efficace :

---

## 🎤 PRÉSENTATION (3 minutes)

### 1. Introduction (30 secondes)
"Bonjour, je vais vous présenter ma **plateforme de surveillance des cryptomonnaies**. C'est un système qui collecte automatiquement les prix des cryptos depuis l'API CoinPaprika, les stocke dans une base de données, et les affiche via une interface web moderne."

### 2. Architecture & Choix Techniques (1 minute)

**"Pourquoi ces technologies ?"**

- **Python 3.11** → Langage simple, beaucoup de bibliothèques pour les APIs et les données
- **FastAPI** → Framework moderne, rapide, documentation auto-générée (Swagger)
- **MongoDB** → Base NoSQL parfaite pour stocker du JSON (données des cryptos)
- **Redis + Celery** → Pour planifier la collecte automatique toutes les minutes
- **React** → Interface moderne, composants réutilisables, graphiques avec Recharts
- **Docker** → Tout l'environnement dans des containers, facile à déployer

**Architecture en 3 couches :**
1. **Collecte** : Le collector récupère les données toutes les minutes
2. **Stockage** : MongoDB garde l'historique des prix
3. **Présentation** : API REST + Interface React avec graphiques

### 3. Fonctionnalités Réalisées (45 secondes)

✅ **Sprint 1 TERMINÉ :**
- Collecte automatique depuis CoinPaprika (Bitcoin, Ethereum)
- Stockage dans MongoDB avec timestamp
- API REST avec 3 endpoints : `/`, `/prices`, `/health`
- Interface React avec tableau filtrable et graphiques
- Tests unitaires + tests d'intégration
- Pipeline CI/CD avec 3 workflows GitHub Actions

### 4. Démonstration Rapide (30 secondes)

"Je vais vous montrer rapidement que tout fonctionne :"

```bash
# 1. Services actifs
docker-compose ps

# 2. API accessible
curl http://localhost:8000/prices

# 3. Interface web
# Ouvrir http://localhost:3000
```

**Montrer :**
- Le tableau avec les cryptos
- Les graphiques (prix et volumes)
- La recherche en temps réel

### 5. Tests & Qualité (15 secondes)

"J'ai mis en place 3 types de tests automatisés :"
- Tests unitaires du collector
- Tests unitaires de l'API
- Tests d'intégration avec MongoDB réel

**Tous les tests passent automatiquement sur GitHub Actions à chaque commit.**

### 6. Roadmap Future (15 secondes)

"Pour les prochains sprints, je prévois :"
- Authentification utilisateurs (JWT)
- Système d'alertes de prix
- Portfolio virtuel pour simuler des achats
- Déploiement sur Kubernetes

---

## 🎯 POINTS CLÉS À MENTIONNER

1. **Architecture microservices** → Services séparés et scalables
2. **Tests automatisés** → Qualité du code garantie
3. **CI/CD** → Déploiement automatisé et fiable
4. **Conteneurisation** → Environnement reproductible partout
5. **Interface moderne** → UX fluide avec React et graphiques

---

## 💡 SI ON TE POSE DES QUESTIONS

**"Pourquoi MongoDB et pas PostgreSQL ?"**
→ Les données de cryptos sont en JSON, MongoDB est natif JSON, plus simple pour ce cas

**"Pourquoi Celery ?"**
→ Pour planifier des tâches récurrentes (collecte toutes les minutes) de façon robuste avec retry automatique

**"Comment tu gères les erreurs ?"**
→ Celery retry automatiquement (3 fois), les tests vérifient les cas d'erreur, logs détaillés

**"C'est scalable ?"**
→ Oui : Docker Swarm ou Kubernetes, worker Celery multi-instances, MongoDB peut être répliqué

---

**Ton pitch final :**
"En résumé, j'ai créé une architecture solide, testée et automatisée qui collecte, stocke et affiche les données cryptos en temps réel. Tout est conteneurisé et prêt pour la production."