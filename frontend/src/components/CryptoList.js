// frontend/src/components/CryptoList.js

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

  if (loading) return <div className="loading">⏳ Chargement des cryptos...</div>;
  if (error) return <div className="error">❌ {error}</div>;

  return (
    <div className="crypto-list-container">
      <h1>💰 Liste des Cryptomonnaies</h1>

      <div className="search-bar">
        <input
          type="text"
          placeholder="Rechercher une crypto..."
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
        />
        <button onClick={fetchCryptos} className="btn-refresh">🔄 Actualiser</button>
      </div>

      <table className="crypto-table">
        <thead>
          <tr>
            <th>Nom</th>
            <th>Symbole</th>
            <th>Prix USD</th>
            <th>Coin ID</th>
            <th>Timestamp</th>
          </tr>
        </thead>
        <tbody>
          {filteredCryptos.length > 0 ? (
            filteredCryptos.map((crypto, idx) => (
              <tr key={idx} className="crypto-row">
                <td className="name">{crypto.name || 'N/A'}</td>
                <td className="symbol">{crypto.symbol || 'N/A'}</td>
                <td className="price">${(crypto.price_usd || 0).toFixed(6)}</td>
                <td>{crypto.coin_id || 'N/A'}</td>
                <td>{crypto.timestamp || 'N/A'}</td>
              </tr>
            ))
          ) : (
            <tr>
              <td colSpan="5" className="no-results">
                Aucune crypto trouvée 🔍
              </td>
            </tr>
          )}
        </tbody>
      </table>

      <div className="crypto-count">
        Affichage de {filteredCryptos.length} sur {cryptos.length} cryptos
      </div>
    </div>
  );
};

export default CryptoList;