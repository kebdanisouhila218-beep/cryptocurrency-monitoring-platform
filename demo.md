Python 3.11
FastAPI
MongoDB
Redis + Celery
React
Docker

**Architecture en 3 couches :**
1. **Collecte** : Le collector récupère les données toutes les minutes
2. **Stockage** : MongoDB garde l'historique des prix
3. **Présentation** : API REST + Interface React avec graphiques


# 1. Montrer l'architecture
docker-compose ps

# 2. Lancer les services
docker-compose up -d

# 3. Vérifier les logs du collector
docker logs collector-test

# 4. Vérifier MongoDB
docker exec -it mongo mongosh
> use crypto_db
> db.prices.find().limit(5)

# 5. Tester l'API
curl http://localhost:8000/
curl http://localhost:8000/prices

# 6. Montrer les tests qui passent
# Tests unitaires collector
docker-compose up --build collector-test

# Tests unitaires API
docker-compose run --rm test-unit-api

# Tests d'intégration
docker-compose run --rm test-integration 

# Lancer SERVEUR 
cd api
>> uvicorn main:app --reload


http://127.0.0.1:8000/


PS C:\Users\etudiant\Documents\GitHub\cryptocurrency-monitoring-platform\api> uvicorn main:app --reload   ( terminal)

(.venv) PS C:\Users\etudiant\Documents\GitHub\cryptocurrency-monitoring-platform\frontend> npm start (vs)

http://localhost:3000/

