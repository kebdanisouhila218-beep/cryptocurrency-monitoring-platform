# api/main.py
from fastapi import FastAPI, Depends
from datetime import datetime
from database import get_collection

app = FastAPI()

@app.get("/prices")
async def get_prices(collection = Depends(get_collection)):
    prices = list(collection.find({}, {"_id": 0}).sort("timestamp", -1).limit(50))
    for p in prices:
        p["timestamp"] = datetime.fromtimestamp(p["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
    return {"prices": prices}

@app.get("/")
async def root():
    return {"message": "🚀 API Crypto fonctionnelle !"}