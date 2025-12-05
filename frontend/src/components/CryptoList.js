// CryptoList.js - Liste moderne avec statistiques

import React, { useState, useEffect } from 'react';
import cryptoService from '../api/cryptoService';
import './CryptoList.css';

const CryptoList = () => {
  const [cryptos, setCryptos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('');

  useEffect(() => {
    fetchCryptos();
  }, []);

  const fetchCryptos = async () => {
    try {
      setLoading(true);
      const data = await cryptoService.getAllCryptos();
      setCryptos(data);
      setError(null);
    } catch (err) {
      setError('Impossible de charger les cryptos');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const filteredCryptos = cryptos.filter((crypto) =>
    crypto.name?.toLowerCase().includes(filter.toLowerCase()) ||
    crypto.symbol?.toLowerCase().includes(filter.toLowerCase())
  );

  // Calculer les statistiques
  const stats = {
    total: cryptos.length,
    avgPrice: cryptos.length > 0 
      ? (cryptos.reduce((sum, c) => sum + (c.price_usd || 0), 0) / cryptos.length).toFixed(2)
      : 0,
    maxPrice: cryptos.length > 0 
      ? Math.max(...cryptos.map(c => c.price_usd || 0)).toFixed(2)
      : 0,
    minPrice: cryptos.length > 0 
      ? Math.min(...cryptos.map(c => c.price_usd || 0)).toFixed(6)
      : 0
  };

  if (loading) {
    return (
      <div className="crypto-list-container">
        <div className="loading">
          <div className="loading-spinner"></div>
          <p>⏳ Chargement des cryptos...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="crypto-list-container">
        <div className="error">❌ {error}</div>
      </div>
    );
  }

  return (
    <div className="crypto-list-container">
      <h1>💰 Liste des Cryptomonnaies</h1>
      <p className="page-subtitle">
        Suivez les prix en temps réel des principales cryptomonnaies
      </p>

      {/* Statistiques rapides */}
      <div className="quick-stats">
        <div className="quick-stat-card">
          <div className="quick-stat-label">Total Cryptos</div>
          <div className="quick-stat-value">{stats.total}</div>
        </div>
        <div className="quick-stat-card">
          <div className="quick-stat-label">Prix Moyen</div>
          <div className="quick-stat-value">${stats.avgPrice}</div>
        </div>
        <div className="quick-stat-card">
          <div className="quick-stat-label">Prix Max</div>
          <div className="quick-stat-value">${stats.maxPrice}</div>
        </div>
        <div className="quick-stat-card">
          <div className="quick-stat-label">Prix Min</div>
          <div className="quick-stat-value">${stats.minPrice}</div>
        </div>
      </div>

      {/* Barre de recherche */}
      <div className="search-bar">
        <input
          type="text"
          placeholder="🔍 Rechercher une crypto (nom ou symbole)..."
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
        />
        <button onClick={fetchCryptos} className="btn-refresh">
          🔄 Actualiser
        </button>
      </div>

      {/* Tableau */}
      <div className="table-wrapper">
        <table className="crypto-table">
          <thead>
            <tr>
              <th>Crypto</th>
              <th>Symbole</th>
              <th>Prix USD</th>
              <th>Coin ID</th>
              <th>Date</th>
            </tr>
          </thead>
          <tbody>
            {filteredCryptos.length > 0 ? (
              filteredCryptos.map((crypto, idx) => (
                <tr key={idx} className="crypto-row">
                  <td className="name">
                    <div className="icon">
                      {crypto.symbol ? crypto.symbol.charAt(0).toUpperCase() : '?'}
                    </div>
                    <span>{crypto.name || 'N/A'}</span>
                  </td>
                  <td className="symbol">{crypto.symbol || 'N/A'}</td>
                  <td className="price">${(crypto.price_usd || 0).toFixed(6)}</td>
                  <td className="volume">{crypto.coin_id || 'N/A'}</td>
                  <td className="volume">{crypto.timestamp || 'N/A'}</td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="5" className="no-results">
                  🔍 Aucune crypto trouvée pour "{filter}"
                </td>
              </tr>
            )}
          </tbody>
        </table>

        <div className="crypto-count">
          Affichage de {filteredCryptos.length} sur {cryptos.length} cryptos
        </div>
      </div>
    </div>
  );
};

export default CryptoList;