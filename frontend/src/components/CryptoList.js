// frontend/src/components/CryptoList.js

import React, { useState, useEffect } from 'react';
import cryptoService from '../api/cryptoService';
import './CryptoList.css';

const CryptoList = () => {
  const [cryptos, setCryptos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedCrypto, setSelectedCrypto] = useState(null);
  const [filter, setFilter] = useState('');

  // Charger les cryptos au montage
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

  // Filtrer les cryptos
  const filteredCryptos = cryptos.filter((crypto) =>
    crypto.name.toLowerCase().includes(filter.toLowerCase()) ||
    crypto.symbol.toLowerCase().includes(filter.toLowerCase())
  );

  if (loading) return <div className="loading">⏳ Chargement des cryptos...</div>;
  if (error) return <div className="error">❌ {error}</div>;

  return (
    <div className="crypto-list-container">
      <h1>💰 Liste des Cryptomonnaies</h1>

      {/* Barre de recherche */}
      <div className="search-bar">
        <input
          type="text"
          placeholder="Rechercher une crypto (Bitcoin, BTC...)"
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
        />
        <button onClick={fetchCryptos} className="btn-refresh">🔄 Actualiser</button>
      </div>

      {/* Tableau */}
      <table className="crypto-table">
        <thead>
          <tr>
            <th>Nom</th>
            <th>Symbole</th>
            <th>Prix USD</th>
            <th>Prix EUR</th>
            <th>Volume 24h</th>
            <th>Variation 24h</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          {filteredCryptos.length > 0 ? (
            filteredCryptos.map((crypto) => (
              <tr key={crypto._id} className="crypto-row">
                <td className="name">
                  <span className="icon">{crypto.name.charAt(0)}</span>
                  {crypto.name}
                </td>
                <td className="symbol">{crypto.symbol}</td>
                <td className="price">${crypto.price_usd.toFixed(2)}</td>
                <td className="price">€{crypto.price_eur.toFixed(2)}</td>
                <td className="volume">${(crypto.volume_24h / 1e9).toFixed(2)}B</td>
                <td className={`change ${crypto.change_24h >= 0 ? 'positive' : 'negative'}`}>
                  {crypto.change_24h >= 0 ? '📈' : '📉'} {crypto.change_24h.toFixed(2)}%
                </td>
                <td>
                  <button 
                    className="btn-view"
                    onClick={() => setSelectedCrypto(crypto.name)}
                  >
                    📊 Voir
                  </button>
                </td>
              </tr>
            ))
          ) : (
            <tr>
              <td colSpan="7" className="no-results">
                Aucune crypto trouvée 🔍
              </td>
            </tr>
          )}
        </tbody>
      </table>

      {/* Afficher le nombre de résultats */}
      <div className="crypto-count">
        Affichage de {filteredCryptos.length} sur {cryptos.length} cryptos
      </div>
    </div>
  );
};

export default CryptoList;