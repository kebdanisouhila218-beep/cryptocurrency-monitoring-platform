// frontend/src/components/Dashboard.js

import React, { useState, useEffect } from 'react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import cryptoService from '../api/cryptoService';
import './Dashboard.css';

const Dashboard = () => {
  const [cryptos, setCryptos] = useState([]);
  const [selectedCrypto, setSelectedCrypto] = useState('bitcoin');
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [days, setDays] = useState(7);

  // Charger les cryptos
  useEffect(() => {
    fetchCryptos();
  }, []);

  const fetchCryptos = async () => {
    try {
      const data = await cryptoService.getAllCryptos();
      setCryptos(data);
    } catch (error) {
      console.error('Erreur:', error);
    }
  };

  // Charger l'historique d'une crypto
  useEffect(() => {
    if (selectedCrypto) {
      fetchHistory();
    }
  }, [selectedCrypto, days]);

  const fetchHistory = async () => {
    try {
      setLoading(true);
      const data = await cryptoService.getCryptoHistory(selectedCrypto, days);
      setHistory(data);
    } catch (error) {
      console.error('Erreur:', error);
    } finally {
      setLoading(false);
    }
  };

  // Calculer les statistiques
  const stats = {
    totalMarketCap: cryptos.reduce((sum, c) => sum + (c.market_cap || 0), 0),
    avgPrice: cryptos.length > 0 ? cryptos.reduce((sum, c) => sum + c.price_usd, 0) / cryptos.length : 0,
    topGainer: cryptos.length > 0 ? cryptos.reduce((prev, curr) => (prev.change_24h > curr.change_24h ? prev : curr)) : null,
  };

  // Données pour le graphique des prix
  const priceData = history.length > 0 ? history.map(h => ({
    date: new Date(h.timestamp).toLocaleDateString('fr-FR'),
    price: h.price_usd,
  })) : [];

  // Données pour le graphique des volumes
  const volumeData = cryptos.slice(0, 10).map(c => ({
    name: c.symbol,
    volume: c.volume_24h / 1e9,
  }));

  return (
    <div className="dashboard-container">
      <h1>📊 Dashboard Crypto</h1>

      {/* Cartes de statistiques */}
      <div className="stats-grid">
        <div className="stat-card">
          <h3>💼 Capitalisation Totale</h3>
          <p className="stat-value">${(stats.totalMarketCap / 1e9).toFixed(2)}B</p>
        </div>
        <div className="stat-card">
          <h3>📈 Prix Moyen</h3>
          <p className="stat-value">${stats.avgPrice.toFixed(2)}</p>
        </div>
        <div className="stat-card">
          <h3>🚀 Top Gainer (24h)</h3>
          <p className="stat-value">
            {stats.topGainer ? `${stats.topGainer.symbol} +${stats.topGainer.change_24h.toFixed(2)}%` : 'N/A'}
          </p>
        </div>
      </div>

      {/* Sélection de la crypto */}
      <div className="control-panel">
        <div className="control-group">
          <label htmlFor="crypto-select">Sélectionner une crypto:</label>
          <select 
            id="crypto-select"
            value={selectedCrypto} 
            onChange={(e) => setSelectedCrypto(e.target.value)}
          >
            {cryptos.map(crypto => (
              <option key={crypto._id} value={crypto.name.toLowerCase()}>
                {crypto.name} ({crypto.symbol})
              </option>
            ))}
          </select>
        </div>

        <div className="control-group">
          <label htmlFor="days-select">Période:</label>
          <select 
            id="days-select"
            value={days} 
            onChange={(e) => setDays(parseInt(e.target.value))}
          >
            <option value={7}>7 jours</option>
            <option value={30}>30 jours</option>
            <option value={90}>90 jours</option>
          </select>
        </div>
      </div>

      {/* Graphiques */}
      <div className="charts-grid">
        {/* Graphique des prix */}
        <div className="chart-container">
          <h3>📈 Historique des Prix ({selectedCrypto})</h3>
          {loading ? (
            <p className="loading">⏳ Chargement...</p>
          ) : priceData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={priceData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip formatter={(value) => `$${value.toFixed(2)}`} />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="price" 
                  stroke="#007bff" 
                  strokeWidth={2}
                  dot={{ r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <p>Aucune donnée disponible</p>
          )}
        </div>

        {/* Graphique des volumes */}
        <div className="chart-container">
          <h3>📊 Top 10 Volumes 24h</h3>
          {volumeData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={volumeData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip formatter={(value) => `$${value.toFixed(2)}B`} />
                <Legend />
                <Bar dataKey="volume" fill="#28a745" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <p>Aucune donnée disponible</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;