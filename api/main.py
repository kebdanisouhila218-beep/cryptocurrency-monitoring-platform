# api/main.py

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from datetime import datetime
from database import get_collection

app = FastAPI()

# ✅ CORS - Autoriser React et le HTML local
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ PAGE HTML
@app.get("/", response_class=HTMLResponse)
async def serve_html():
    return """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>💰 Crypto Tracker</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        header {
            text-align: center;
            color: white;
            margin-bottom: 40px;
        }
        header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
        }
        .controls {
            display: flex;
            gap: 10px;
            margin-bottom: 30px;
        }
        .controls input {
            flex: 1;
            padding: 12px 15px;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
        }
        .controls button {
            padding: 12px 30px;
            background-color: #fff;
            color: #667eea;
            border: none;
            border-radius: 8px;
            font-weight: bold;
            cursor: pointer;
            transition: 0.3s;
        }
        .controls button:hover {
            background-color: #f0f0f0;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .stat-card h3 {
            color: #666;
            margin-bottom: 10px;
            font-size: 0.9rem;
        }
        .stat-value {
            font-size: 1.8rem;
            font-weight: bold;
            color: #667eea;
        }
        .table-wrapper {
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        thead {
            background-color: #f8f9fa;
            border-bottom: 2px solid #ddd;
        }
        th {
            padding: 15px;
            text-align: left;
            font-weight: bold;
            color: #333;
        }
        td {
            padding: 15px;
            border-bottom: 1px solid #eee;
        }
        tbody tr:hover {
            background-color: #f5f5f5;
        }
        .loading {
            text-align: center;
            padding: 40px;
            color: white;
            font-size: 1.2rem;
        }
        .error {
            background-color: #f8d7da;
            color: #721c24;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>💰 Crypto Tracker</h1>
            <p>Affichage des cryptomonnaies en temps réel</p>
        </header>

        <div class="controls">
            <input type="text" id="search" placeholder="Chercher une crypto...">
            <button onclick="loadData()">🔄 Actualiser</button>
        </div>

        <div id="stats" class="stats"></div>
        <div id="error" class="error" style="display: none;"></div>
        <div id="loading" class="loading" style="display: none;">⏳ Chargement...</div>

        <div id="tableContainer" class="table-wrapper" style="display: none;">
            <table>
                <thead>
                    <tr>
                        <th>Nom</th>
                        <th>Symbole</th>
                        <th>Prix USD</th>
                        <th>Coin ID</th>
                        <th>Timestamp</th>
                    </tr>
                </thead>
                <tbody id="tbody"></tbody>
            </table>
        </div>
    </div>

    <script>
        let allData = [];

        document.addEventListener('DOMContentLoaded', loadData);
        document.getElementById('search').addEventListener('keyup', filterData);

        async function loadData() {
            const loading = document.getElementById('loading');
            const error = document.getElementById('error');
            const tableContainer = document.getElementById('tableContainer');

            loading.style.display = 'block';
            error.style.display = 'none';
            tableContainer.style.display = 'none';

            try {
                const response = await fetch('http://127.0.0.1:8000/prices');
                const data = await response.json();

                if (!data.prices || data.prices.length === 0) {
                    error.textContent = '❌ Aucune donnée disponible';
                    error.style.display = 'block';
                    loading.style.display = 'none';
                    return;
                }

                allData = data.prices;
                displayTable(allData);
                displayStats(allData);
                loading.style.display = 'none';
                tableContainer.style.display = 'block';

            } catch (err) {
                error.textContent = '❌ Erreur: ' + err.message;
                error.style.display = 'block';
                loading.style.display = 'none';
            }
        }

        function displayTable(data) {
            const tbody = document.getElementById('tbody');
            tbody.innerHTML = '';

            data.forEach(crypto => {
                const row = tbody.insertRow();
                row.innerHTML = `
                    <td>${crypto.name || 'N/A'}</td>
                    <td><strong>${crypto.symbol || 'N/A'}</strong></td>
                    <td>$${(crypto.price_usd || 0).toFixed(6)}</td>
                    <td>${crypto.coin_id || 'N/A'}</td>
                    <td>${crypto.timestamp || 'N/A'}</td>
                `;
            });
        }

        function displayStats(data) {
            const statsContainer = document.getElementById('stats');
            const prices = data.map(c => c.price_usd || 0);
            
            statsContainer.innerHTML = `
                <div class="stat-card">
                    <h3>📊 Total Cryptos</h3>
                    <div class="stat-value">${data.length}</div>
                </div>
                <div class="stat-card">
                    <h3>💰 Prix Min</h3>
                    <div class="stat-value">$${Math.min(...prices).toFixed(6)}</div>
                </div>
                <div class="stat-card">
                    <h3>📈 Prix Max</h3>
                    <div class="stat-value">$${Math.max(...prices).toFixed(6)}</div>
                </div>
            `;
        }

        function filterData() {
            const search = document.getElementById('search').value.toLowerCase();
            const filtered = allData.filter(c =>
                (c.name && c.name.toLowerCase().includes(search)) ||
                (c.symbol && c.symbol.toLowerCase().includes(search))
            );
            displayTable(filtered);
        }
    </script>
</body>
</html>"""

# ✅ API
@app.get("/prices")
async def get_prices(collection = Depends(get_collection)):
    """Retourne tous les prix enregistrés dans MongoDB"""
    try:
        prices = list(collection.find({}, {"_id": 0}).sort("timestamp", -1).limit(50))
        for p in prices:
            if "timestamp" in p:
                p["timestamp"] = datetime.fromtimestamp(p["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
        return {"prices": prices}
    except Exception as e:
        return {"error": str(e), "prices": []}

@app.get("/health")
async def health_check():
    return {"status": "✅ API is healthy"}