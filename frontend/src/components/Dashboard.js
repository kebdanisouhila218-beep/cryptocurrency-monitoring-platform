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

  useEffect(() => {
    fetchCryptos();
  }, []);

  const fetchCryptos = async () => {
    try {
      const data = await cryptoService.getAllCryptos();
      setCryptos(data);
      if (data.length > 0) {
        setSelectedCrypto(data[0].name?.toLowerCase() || 'bitcoin');
      }
    } catch (error) {
      console.error('Erreur:', error);
    }
  };

  useEffect(() => {
    if (selectedCrypto) {
      fetchHistory();
    }
  }, [selectedCrypto]);

  const fetchHistory = async () => {
    try {
      setLoading(true);
      const data = await cryptoService.getCryptoHistory(selectedCrypto, 7);
      setHistory(data);
    } catch (error) {
      console.error('Erreur:', error);
      setHistory([]);
    } finally {
      setLoading(false);
    }
  };

  const stats = {
    totalCryptos: cryptos.length,
    avgPrice: cryptos.length > 0 ? cryptos.reduce((sum, c) => sum + (c.price_usd || 0), 0) / cryptos.length : 0,
    totalVolume: cryptos.reduce((sum, c) => sum + (c.volume_24h || 0), 0),
  };

  const volumeData = cryptos.slice(0, 10).map(c => ({
    name: c.symbol,
    volume: (c.volume_24h || 0) / 1e9,
  }));

  const priceData = history.map((h, idx) => ({
    date: `Jour ${idx + 1}`,
    price: h.price_usd || 0,
  }));

  return (
    <div className="dashboard-container">
      <h1>📊 Dashboard Crypto</h1>

      <div className="stats-grid">
        <div className="stat-card">
          <h3>📊 Total Cryptos</h3>
          <p className="stat-value">{stats.totalCryptos}</p>
        </div>
        <div className="stat-card">
          <h3>📈 Prix Moyen USD</h3>
          <p className="stat-value">${stats.avgPrice.toFixed(2)}</p>
        </div>
        <div className="stat-card">
          <h3>💰 Volume Total 24h</h3>
          <p className="stat-value">${(stats.totalVolume / 1e9).toFixed(2)}B</p>
        </div>
      </div>

      <div className="control-panel">
        <div className="control-group">
          <label htmlFor="crypto-select">Sélectionner une crypto:</label>
          <select 
            id="crypto-select"
            value={selectedCrypto} 
            onChange={(e) => setSelectedCrypto(e.target.value)}
          >
            {cryptos.map((crypto, idx) => (
              <option key={idx} value={crypto.name?.toLowerCase() || ''}>
                {crypto.name} ({crypto.symbol})
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="charts-grid">
        <div className="chart-container">
          <h3>📈 Prix ({selectedCrypto})</h3>
          {loading ? (
            <p className="loading">⏳ Chargement...</p>
          ) : priceData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={priceData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip formatter={(value) => `$${value.toFixed(6)}`} />
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