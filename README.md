#  Cryptocurrency Monitoring Platform

##  Objectif du projet
Créer une plateforme complète de **surveillance, d’analyse et de prévision** du marché des cryptomonnaies.  
Le projet comprend :
- Un **collecteur** de données (application Python) qui récupère les prix, volumes et capitalisations depuis une API publique (ex : CoinCap).  
- Un **backend API** (FastAPI) pour exposer les données à d’autres services.  
- Un **frontend web** (React ou Streamlit) pour visualiser les courbes, graphiques et tendances.

---

##  Architecture prévue
collector (Python)
->
MongoDB (base de données)
->
backend API (FastAPI)
->
frontend (React / Streamlit)


Chaque composant sera **conteneurisé avec Docker** et connecté via `docker-compose`.

---

##  Technologies utilisées
| Composant | Technologie |
|------------|--------------|
| Langage principal | Python 3 |
| Base de données | MongoDB |
| API Backend | FastAPI |
| Frontend | React (Vite) |
| Conteneurisation | Docker |
| CI/CD | GitHub Actions |
| Gestion de projet | GitHub Projects |

---

##  Démarrage rapide
```bash
# Cloner le projet
git clone https://github.com/kebdanisouhila218-beep/cryptocurrency-monitoring-platform.git

# Lancer les services Docker
docker compose up

#Auteurs

Souhila Aicha Kebdani
Projet académique – Master 2 ILSEN (2025)
