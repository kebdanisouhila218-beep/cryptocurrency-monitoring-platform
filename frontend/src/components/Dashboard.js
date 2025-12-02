// frontend/src/components/Dashboard.js

import React, { useState, useEffect } from 'react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import cryptoService from '../api/cryptoService';
import './Dashboard.css';

const Dashboard = () => {
  const [cryptos, setCryptos] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState('price');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchCryptos();
  }, []);

  const fetchCryptos = async () => {
    try {
      setLoading(true);
      const data = await cryptoService.getAllCryptos();
      setCryptos(data);
    } catch (error) {
      console.error('Erreur:', error);
    } finally {
      setLoading(false);
    }
  };

  // Filtrer par nom ou symbole
  const filteredCryptos = cryptos.filter(c =>
    c.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    c.symbol?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Trier les cryptos filtrées
  const sortedCryptos = [...filteredCryptos].sort((a, b) => {
    switch(sortBy) {
      case 'price':
        return (b.price_usd || 0) - (a.price_usd || 0);
      case 'volume':
        return (b.volume_24h || 0) - (a.volume_24h || 0);
      case 'name':
        return (a.name || '').localeCompare(b.name || '');
      default:
        return 0;
    }
  });

  // Statistiques
  const stats = {
    totalCryptos: cryptos.length,
    avgPrice: cryptos.length > 0 ? cryptos.reduce((sum, c) => sum + (c.price_usd || 0), 0) / cryptos.length : 0,
    maxPrice: cryptos.length > 0 ? Math.max(...cryptos.map(c => c.price_usd || 0)) : 0,
    minPrice: cryptos.length > 0 ? Math.min(...cryptos.map(c => c.price_usd || 0)) : 0,
  };

  // Données pour graphiques
  const chartData = sortedCryptos.slice(0, 10).map(c => ({
    name: c.symbol,
    price: c.price_usd || 0,
    volume: (c.volume_24h || 0) / 1e9,
  }));

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h1>Dashboard</h1>
        <p className="subtitle">Analyse des cryptomonnaies</p>
      </div>

      {/* Cartes de stats */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">Total Cryptos</div>
          <div className="stat-value">{stats.totalCryptos}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Prix Moyen</div>
          <div className="stat-value">${stats.avgPrice.toFixed(2)}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Prix Max</div>
          <div className="stat-value">${stats.maxPrice.toFixed(2)}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Prix Min</div>
          <div className="stat-value">${stats.minPrice.toFixed(6)}</div>
        </div>
      </div>

      {/* Filtres */}
      <div className="filters-section">
        <div className="search-box">
          <input
            type="text"
            placeholder="Chercher par nom ou symbole..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
          {searchTerm && (
            <button 
              onClick={() => setSearchTerm('')}
              className="clear-btn"
            >
              ✕
            </button>
          )}
        </div>

        <div className="sort-box">
          <select 
            value={sortBy} 
            onChange={(e) => setSortBy(e.target.value)}
            className="sort-select"
          >
            <option value="price">Trier par Prix</option>
            <option value="volume">Trier par Volume</option>
            <option value="name">Trier par Nom (A-Z)</option>
          </select>
        </div>

        <button onClick={fetchCryptos} className="refresh-btn">
          Actualiser
        </button>
      </div>

      {/* Graphiques */}
      <div className="charts-section">
        <div className="chart-card">
          <h2>Prix USD</h2>
          {chartData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={chartData} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
                <XAxis dataKey="name" stroke="#999" />
                <YAxis stroke="#999" />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#fff', 
                    border: '1px solid #ddd',
                    borderRadius: '6px'
                  }}
                  formatter={(value) => `$${value.toFixed(2)}`}
                />
                <Bar dataKey="price" fill="#8b7d9f" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <p className="no-data">Aucune donnée</p>
          )}
        </div>

        <div className="chart-card">
          <h2>Volume 24h</h2>
          {chartData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={chartData} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
                <XAxis dataKey="name" stroke="#999" />
                <YAxis stroke="#999" />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#fff', 
                    border: '1px solid #ddd',
                    borderRadius: '6px'
                  }}
                  formatter={(value) => `$${value.toFixed(2)}B`}
                />
                <Line 
                  type="monotone" 
                  dataKey="volume" 
                  stroke="#a39fb3"
                  strokeWidth={2}
                  dot={{ fill: '#a39fb3', r: 4 }}
                  activeDot={{ r: 6 }}
                />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <p className="no-data">Aucune donnée</p>
          )}
        </div>
      </div>

      {/* Tableau */}
      <div className="table-section">
        <h2>Liste des Cryptomonnaies</h2>
        <div className="table-wrapper">
          <table className="crypto-table">
            <thead>
              <tr>
                <th>Nom</th>
                <th>Symbole</th>
                <th>Prix USD</th>
                <th>Volume 24h</th>
                <th>Coin ID</th>
              </tr>
            </thead>
            <tbody>
              {sortedCryptos.length > 0 ? (
                sortedCryptos.map((crypto, idx) => (
                  <tr key={idx} className="table-row">
                    <td>{crypto.name || 'N/A'}</td>
                    <td className="symbol">{crypto.symbol || 'N/A'}</td>
                    <td className="price">${(crypto.price_usd || 0).toFixed(6)}</td>
                    <td>${((crypto.volume_24h || 0) / 1e9).toFixed(2)}B</td>
                    <td className="coin-id">{crypto.coin_id || 'N/A'}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="5" className="no-results">Aucun résultat trouvé</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
        <div className="table-info">
          Affichage de {sortedCryptos.length} sur {cryptos.length} cryptos
        </div>
      </div>
    </div>
  );
};

export default Dashboard;