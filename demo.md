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

**Discours pour le prof :**
> "J'ai implémenté la partie collecte de données avec une architecture microservices. Le collector récupère les données de CoinPaprika, les stocke dans MongoDB, et l'API FastAPI les expose. J'ai mis en place des tests unitaires et d'intégration, plus un pipeline CI/CD avec GitHub Actions qui valide automatiquement les 3 workflows de tests."

