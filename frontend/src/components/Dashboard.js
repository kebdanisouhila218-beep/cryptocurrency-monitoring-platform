// Dashboard.js - Dashboard moderne avec animations

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
    avgPrice: cryptos.length > 0 
      ? cryptos.reduce((sum, c) => sum + (c.price_usd || 0), 0) / cryptos.length 
      : 0,
    maxPrice: cryptos.length > 0 
      ? Math.max(...cryptos.map(c => c.price_usd || 0)) 
      : 0,
    minPrice: cryptos.length > 0 
      ? Math.min(...cryptos.map(c => c.price_usd || 0)) 
      : 0,
  };

  // Données pour graphiques
  const chartData = sortedCryptos.slice(0, 10).map(c => ({
    name: c.symbol,
    price: c.price_usd || 0,
    volume: (c.volume_24h || 0) / 1e9,
  }));

  // Tooltip personnalisé
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div style={{
          background: 'var(--bg-card)',
          border: '1px solid var(--border-color)',
          padding: '12px 16px',
          borderRadius: '12px',
          boxShadow: '0 4px 20px var(--shadow)'
        }}>
          <p style={{ 
            color: 'var(--text-primary)', 
            fontWeight: 'bold',
            marginBottom: '8px'
          }}>
            {label}
          </p>
          {payload.map((entry, index) => (
            <p key={index} style={{ 
              color: entry.color,
              fontSize: '0.9rem'
            }}>
              {entry.name}: {entry.value.toFixed(2)}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  if (loading && cryptos.length === 0) {
    return (
      <div className="dashboard-container">
        <div className="loading">
          <div className="loading-spinner"></div>
          <p>Chargement des données...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
  <div className="dashboard-header">
    <div className="dashboard-title">
      <span className="emoji">📊</span>
      <h1>Dashboard</h1>
    </div>

    <p className="subtitle">
      Analyse approfondie des marchés de cryptomonnaies
    </p>
  </div>


      {/* Cartes de stats avec icônes */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">📈</div>
          <div className="stat-label">Total Cryptos</div>
          <div className="stat-value">{stats.totalCryptos}</div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">💰</div>
          <div className="stat-label">Prix Moyen</div>
          <div className="stat-value">${stats.avgPrice.toFixed(2)}</div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">🚀</div>
          <div className="stat-label">Prix Maximum</div>
          <div className="stat-value">${stats.maxPrice.toFixed(2)}</div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">📉</div>
          <div className="stat-label">Prix Minimum</div>
          <div className="stat-value">${stats.minPrice.toFixed(6)}</div>
        </div>
      </div>

      {/* Filtres */}
      <div className="filters-section">
        <div className="search-box">
          <input
            type="text"
            placeholder="Rechercher par nom ou symbole..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
          {searchTerm && (
            <button 
              onClick={() => setSearchTerm('')}
              className="clear-btn"
              title="Effacer"
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
            <option value="price">📊 Trier par Prix</option>
            <option value="volume">📈 Trier par Volume</option>
            <option value="name">🔤 Trier par Nom (A-Z)</option>
          </select>
        </div>

        <button 
          onClick={fetchCryptos} 
          className={`refresh-btn ${loading ? 'loading' : ''}`}
          disabled={loading}
        >
          {loading ? 'Actualisation...' : ' Actualiser'}
        </button>
      </div>

      {/* Graphiques */}
      <div className="charts-section">
        <div className="chart-card">
          <h2>💵 Prix USD par Crypto</h2>
          {chartData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip content={<CustomTooltip />} />
                <Bar 
                  dataKey="price" 
                  fill="url(#colorGradient)" 
                  radius={[8, 8, 0, 0]}
                />
                <defs>
                  <linearGradient id="colorGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="var(--gradient-1)" stopOpacity={0.8}/>
                    <stop offset="100%" stopColor="var(--gradient-2)" stopOpacity={0.8}/>
                  </linearGradient>
                </defs>
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <p className="no-data">Aucune donnée disponible</p>
          )}
        </div>

        
      </div>

      {/* Tableau */}
      <div className="table-section">
        <h2>📋 Liste Complète des Cryptomonnaies</h2>
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
                  <td colSpan="5" className="no-results">
                    🔍 Aucun résultat trouvé pour "{searchTerm}"
                  </td>
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