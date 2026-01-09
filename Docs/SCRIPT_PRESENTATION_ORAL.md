# 🎤 SCRIPT DE PRÉSENTATION ORALE - CryptoTracker

> Ce que tu dois dire à ton prof, mot par mot, avec des exemples simples.

---

## 📌 ORDRE DE PRÉSENTATION

1. Introduction + Sprints (Trello/Scrum)
2. Diagramme d'Architecture
3. Docker
4. MongoDB (les tables)
5. Interface Utilisateur (avec exemples)
6. Interface Admin (avec exemples)
7. Discord Alertes
8. Grafana + Prometheus
9. Tests
10. CI/CD

---

# 1️⃣ INTRODUCTION + SPRINTS (Trello/Scrum)

## Ce que tu dis :

> "J'ai développé **CryptoTracker**, une plateforme pour surveiller 50 cryptomonnaies en temps réel."

> "J'ai utilisé la **méthodologie Scrum** avec **Trello** pour organiser mon travail."

> "Scrum, c'est quoi ? On divise le travail en **sprints**. Un sprint = une période courte (1-2 semaines) avec des tâches précises à finir."

## Les sprints que tu as fait :

| Sprint | Ce que j'ai fait | Combien de temps |
|--------|------------------|------------------|
| 1-2 | Collecte des prix + API + Interface React | 2 semaines |
| 3-4 | Tests + Authentification (login/register) | 1.5 semaines |
| 5-7 | Alertes email + Portfolio virtuel | 2 semaines |
| 8-10 | Prévisions + Indicateurs + Graphiques | 3 semaines |
| 11 | Documentation + Diagrammes | 1 semaine |
| 12 | Panel Admin | 1 semaine |
| 13 | Kubernetes + Monitoring | 1.5 semaines |
| 14 | CI/CD + Tests sécurité | 1 semaine |

## Ce que tu dis :

> "Au total, j'ai fait **14 sprints** sur environ **13 semaines**."

> "Chaque sprint avait un objectif clair. Par exemple, sprint 5-7 c'était les alertes et le portfolio."

> "Sur Trello, j'avais des colonnes : **À faire**, **En cours**, **Terminé**. Je déplaçais les tâches au fur et à mesure."

---

# 2️⃣ DIAGRAMME D'ARCHITECTURE

## Quel diagramme montrer : `Diagramme d'Architecture.png`

## Ce que tu dis :

> "Voici le **diagramme d'architecture** qui montre comment tout fonctionne ensemble."

> "En haut, on a le **Frontend React** - c'est ce que l'utilisateur voit dans son navigateur."

> "Le Frontend parle avec le **Backend FastAPI** - c'est le serveur qui traite les demandes."

> "Le Backend stocke les données dans **MongoDB** - c'est la base de données."

> "On a aussi **Redis** qui sert de cache, et **Celery** qui exécute les tâches en arrière-plan."

> "**Celery** collecte les prix des 50 cryptos toutes les minutes automatiquement."

## Schéma simple à dessiner si besoin :

```
┌──────────────┐
│   REACT      │  ← L'utilisateur voit ça
│  (Frontend)  │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   FASTAPI    │  ← Traite les demandes
│  (Backend)   │
└──────┬───────┘
       │
   ┌───┴───┐
   ▼       ▼
┌──────┐ ┌──────┐
│MONGO │ │REDIS │
│(Data)│ │(Cache)│
└──────┘ └──────┘
           │
           ▼
       ┌──────┐
       │CELERY│ ← Collecte les prix
       └──────┘
```

---

# 3️⃣ DOCKER

## Ce que tu dis :

> "J'ai utilisé **Docker** pour conteneuriser toute l'application."

> "Docker, c'est quoi ? Ça permet de mettre l'application dans une 'boîte' avec tout ce qu'il faut pour qu'elle marche. Comme ça, elle fonctionne pareil sur n'importe quel ordinateur."

> "J'ai **15 services Docker** qui tournent ensemble."

## Les services Docker :

| Service | C'est quoi |
|---------|------------|
| **mongo** | Base de données MongoDB |
| **redis** | Cache mémoire |
| **api** | Le backend FastAPI |
| **scheduler** | Celery Beat - planifie les tâches |
| **worker** | Celery Worker - exécute les tâches |
| **prometheus** | Collecte les métriques |
| **grafana** | Affiche les graphiques de monitoring |
| **mongodb-exporter** | Envoie les stats de Mongo à Prometheus |
| **redis-exporter** | Envoie les stats de Redis à Prometheus |
| **node-exporter** | Métriques du système (CPU, RAM) |
| **sonarqube** | Analyse la qualité du code |

## Ce que tu dis :

> "Pour tout lancer, une seule commande : `docker-compose up`"

> "En 2 minutes, toute l'application est prête."

---

# 4️⃣ MONGODB (Les tables)

## Ce que tu dis :

> "J'ai choisi **MongoDB** comme base de données."

> "Pourquoi MongoDB ? Parce que c'est une base **NoSQL**. Les données sont stockées comme du JSON, c'est flexible."

> "Pour les cryptos, les données changent souvent. MongoDB est parfait pour ça."

## Les 6 collections (tables) :

| Collection | Ce qu'elle stocke | Exemple |
|------------|-------------------|---------|
| **cryptos** | Les 50 cryptos avec leur prix actuel | `{symbol: "BTC", price: 45000}` |
| **price_history** | L'historique des prix pour les graphiques | `{symbol: "BTC", price: 44500, date: "2025-01-08"}` |
| **users** | Les utilisateurs | `{username: "souhila", email: "...", password: "hashé"}` |
| **alerts** | Les alertes configurées | `{crypto: "BTC", target: 50000, type: "above"}` |
| **portfolio** | Les portfolios virtuels | `{name: "Mon Portfolio", positions: [...]}` |
| **transactions** | Historique achats/ventes | `{type: "buy", crypto: "ETH", amount: 0.5}` |

## Ce que tu dis :

> "Par exemple, dans la collection **cryptos**, chaque document ressemble à ça :"

```json
{
  "symbol": "BTC",
  "name": "Bitcoin",
  "price_usd": 45000,
  "volume_24h": 25000000000,
  "last_updated": "2025-01-09"
}
```

---

# 5️⃣ INTERFACE UTILISATEUR (avec exemples)

## Ce que tu dis :

> "Maintenant je vais montrer ce que l'**utilisateur normal** peut faire."

---

### 📊 PAGE DASHBOARD

**Ce que tu montres :** La liste des 50 cryptos

**Ce que tu dis :**
> "Ici on voit les **50 cryptomonnaies** avec leur prix en temps réel."

> "Les prix sont mis à jour automatiquement toutes les minutes grâce à **Celery**."

> "Celery, c'est un système de tâches en arrière-plan. Il va chercher les prix sur l'API CoinPaprika et les stocke dans MongoDB."

**Exemple à montrer :**
> "Regardez, Bitcoin est à 45 000$, Ethereum à 2 500$..."

---

### 🔮 PAGE PRÉVISIONS

**Ce que tu montres :** Sélectionner BTC, 30 jours, cliquer sur Générer

**Ce que tu dis :**
> "Ici je peux **prédire le prix** d'une crypto."

> "Je choisis Bitcoin, 30 jours, et je clique sur Générer."

> "Le système utilise 3 algorithmes :"
> - "**SMA** : Moyenne simple des derniers prix"
> - "**EMA** : Moyenne qui donne plus de poids aux prix récents"
> - "**Régression linéaire** : Une droite de tendance"

> "La **prévision optimale** combine les 3 pour être plus fiable."

---

### 🔔 PAGE ALERTES

**Ce que tu montres :** Créer une alerte "BTC > 50000"

**Ce que tu dis :**
> "Ici je peux créer une **alerte de prix**."

> "Par exemple, je veux être notifié quand Bitcoin dépasse 50 000$."

**Exemple à faire en live :**
1. Cliquer sur "Créer une alerte"
2. Choisir BTC
3. Mettre 50000
4. Choisir "Au-dessus"
5. Cliquer sur Créer

> "Quand le prix dépasse 50 000$, je reçois un **email** ou un message **Discord**."

---

### 💬 DISCORD WEBHOOK

**Ce que tu dis :**
> "L'utilisateur peut ajouter son **webhook Discord** dans son profil."

> "Un webhook, c'est une URL spéciale de Discord. Quand une alerte se déclenche, le système envoie un message sur le serveur Discord de l'utilisateur."

**Exemple :**
> "Si j'ai configuré mon Discord et que BTC dépasse 50 000$, je reçois ce message sur Discord :"

```
🔔 ALERTE CRYPTO
Bitcoin (BTC) a dépassé 50,000 $
Prix actuel: 50,150 $
```

---

### 💼 PAGE PORTFOLIO VIRTUEL

**Ce que tu montres :** Acheter 0.1 BTC

**Ce que tu dis :**
> "Le portfolio virtuel permet de **simuler des achats** sans risque."

> "C'est comme un jeu. Je peux acheter et vendre des cryptos avec de l'argent fictif."

**Exemple à faire en live :**
1. Cliquer sur "Acheter"
2. Choisir BTC
3. Quantité : 0.1
4. Confirmer

> "Le système calcule automatiquement mon **profit ou perte** (P&L)."

> "Si j'ai acheté 0.1 BTC à 45 000$ et qu'il monte à 50 000$, je vois que j'ai gagné 500$ virtuellement."

---

### 📈 PAGE INDICATEURS

**Ce que tu montres :** Les indicateurs RSI, MACD, Bollinger

**Ce que tu dis :**
> "Les indicateurs techniques aident à savoir **quand acheter ou vendre**."

> "**RSI** : Si c'est au-dessus de 70, le prix est trop haut, il faut peut-être vendre."

> "**MACD** : Si la ligne bleue croise la rouge vers le haut, c'est un signal d'achat."

> "Le système combine les indicateurs et donne un **signal** : ACHETER, VENDRE ou NEUTRE."

---

# 6️⃣ INTERFACE ADMIN

## Ce que tu dis :

> "Maintenant je me connecte en tant qu'**Administrateur** pour montrer la différence."

---

### 👤 DIFFÉRENCE USER vs ADMIN

| Fonctionnalité | Utilisateur | Admin |
|----------------|-------------|-------|
| Voir les cryptos | ✅ | ✅ |
| Créer des alertes | ✅ | ✅ |
| Portfolio virtuel | ✅ | ✅ |
| Voir les prévisions | ✅ | ✅ |
| **Voir tous les utilisateurs** | ❌ | ✅ |
| **Supprimer un utilisateur** | ❌ | ✅ |
| **Voir les statistiques système** | ❌ | ✅ |
| **Promouvoir en admin** | ❌ | ✅ |

**Ce que tu dis :**
> "L'utilisateur normal peut seulement gérer **son propre compte**."

> "L'admin peut voir **tous les utilisateurs** et les gérer."

---

### 🛡️ PANEL ADMIN

**Ce que tu montres :** Le panel admin avec la liste des users

**Ce que tu dis :**
> "Ici je vois **tous les utilisateurs** de la plateforme."

> "Je peux voir leur email, leur date d'inscription, leur rôle."

> "Je peux **supprimer** un compte si besoin."

> "Je peux **promouvoir** un utilisateur en admin."

**Exemple :**
> "Si je veux que 'user1' devienne admin, je clique sur 'Promouvoir'."

---

# 7️⃣ GRAFANA + PROMETHEUS

## Ce que tu dis :

> "Pour surveiller que l'application fonctionne bien, j'utilise **Prometheus** et **Grafana**."

> "**Prometheus** collecte les métriques toutes les 15 secondes."

> "**Grafana** affiche ces métriques sous forme de graphiques."

---

### Accès :

| Outil | URL | Login |
|-------|-----|-------|
| Grafana | `http://localhost:3001` | admin / admin123 |
| Prometheus | `http://localhost:9090` | - |

---

### Ce que tu montres sur Grafana :

**Dashboard 1 : Crypto Dashboard**
> "Ce graphique montre les prix des cryptos en temps réel."

**Dashboard 2 : System Metrics**
> "Ici je vois le **CPU**, la **RAM**, les **requêtes par seconde**."

> "Si l'API reçoit trop de requêtes, je le vois ici."

**Ce que tu dis :**
> "Grâce à ça, je sais si MongoDB est lent, si Redis est saturé, ou si l'API a des problèmes."

---

# 8️⃣ TESTS

## Ce que tu dis :

> "J'ai écrit des **tests** pour m'assurer que le code fonctionne bien."

---

### Types de tests :

| Type | Outil | Pourquoi |
|------|-------|----------|
| **Unitaires** | pytest | Teste chaque fonction seule |
| **Intégration** | pytest + Docker | Teste que MongoDB et l'API marchent ensemble |
| **Performance** | Locust, k6 | Teste si l'app supporte 100 utilisateurs |
| **Sécurité** | Trivy, Snyk, ZAP | Cherche les failles de sécurité |
| **E2E** | Playwright | Simule un vrai utilisateur qui clique |

---

### Ce que tu dis :

> "Les **tests unitaires** vérifient que chaque fonction fait ce qu'elle doit."

> "Exemple : je teste que la fonction `get_crypto_price("BTC")` retourne bien un prix."

> "Les **tests d'intégration** vérifient que les composants marchent ensemble."

> "Exemple : l'API peut bien se connecter à MongoDB."

> "Les **tests de performance** avec **Locust** simulent 100 utilisateurs en même temps."

> "Les **tests de sécurité** cherchent les failles. **Trivy** scanne les images Docker."

> "J'ai une **couverture de 75%** - ça veut dire que 75% du code est testé."

---

# 9️⃣ CI/CD

## Ce que tu dis :

> "**CI/CD** veut dire Intégration Continue et Déploiement Continu."

> "À chaque fois que je pousse du code sur GitHub, des tests automatiques se lancent."

---

### Les 12 workflows GitHub Actions :

| Workflow | Ce qu'il fait |
|----------|---------------|
| `ci-cd.yml` | Tests → Build → Deploy |
| `test-api.yml` | Lance les tests de l'API |
| `security-tests.yml` | Scan de sécurité |
| `performance-tests.yml` | Tests de charge |
| `build.yml` | Construit les images Docker |
| `deploy-production.yml` | Déploie en production |

---

### Pipeline simplifié :

```
Je pousse du code
       ↓
   Tests automatiques
       ↓
   Build de l'image Docker
       ↓
   Scan de sécurité
       ↓
   Déploiement (si tout est vert)
```

**Ce que tu dis :**
> "Si un test échoue, le déploiement s'arrête automatiquement."

> "Le code qui arrive en production est **toujours testé**."

---

## Diagramme à montrer : `Diagramme CI-CD Pipeline.png`

**Ce que tu dis :**
> "Ce diagramme montre le pipeline complet."

---

# 🎯 RÉSUMÉ FINAL

## Ce que tu dis à la fin :

> "Pour résumer, j'ai créé une plateforme complète avec :"

| Élément | Chiffre |
|---------|---------|
| Lignes de code | ~20 000 |
| Services Docker | 15 |
| Collections MongoDB | 6 |
| Endpoints API | 35+ |
| Workflows CI/CD | 12 |
| Sprints | 14 |
| Diagrammes UML | 10 |

> "J'ai appris à utiliser **Scrum**, **Docker**, **CI/CD**, le **monitoring**, et à créer une application **full-stack** complète."

---

# ❓ QUESTIONS POSSIBLES DU PROF

| Question | Réponse courte |
|----------|----------------|
| "Pourquoi MongoDB et pas MySQL ?" | "MongoDB est NoSQL, plus flexible pour les données qui changent souvent comme les prix crypto." |
| "Comment Celery collecte les données ?" | "Celery Beat lance une tâche toutes les minutes. La tâche appelle l'API CoinPaprika et stocke dans MongoDB." |
| "C'est quoi un webhook Discord ?" | "Une URL spéciale qui permet d'envoyer des messages sur un serveur Discord depuis mon application." |
| "Pourquoi React ?" | "React est rapide, moderne, et les composants se mettent à jour sans recharger la page." |
| "C'est quoi Prometheus ?" | "Un outil qui collecte des métriques (CPU, RAM, requêtes) pour surveiller l'application." |

---

**Bonne chance pour ta présentation ! 🚀**
