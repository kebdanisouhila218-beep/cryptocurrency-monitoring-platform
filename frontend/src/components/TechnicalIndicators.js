// frontend/src/components/TechnicalIndicators.js
import React, { useState, useEffect, useCallback } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar, Cell } from 'recharts';
import predictionService from '../services/predictionService';
import './TechnicalIndicators.css';

const CRYPTO_OPTIONS = [
  { value: 'BTC', label: 'Bitcoin (BTC)' },
  { value: 'ETH', label: 'Ethereum (ETH)' },
  { value: 'BNB', label: 'BNB (BNB)' },
  { value: 'SOL', label: 'Solana (SOL)' },
  { value: 'XRP', label: 'Ripple (XRP)' },
  { value: 'ADA', label: 'Cardano (ADA)' },
  { value: 'DOGE', label: 'Dogecoin (DOGE)' },
  { value: 'DOT', label: 'Polkadot (DOT)' },
  { value: 'MATIC', label: 'Polygon (MATIC)' },
  { value: 'LTC', label: 'Litecoin (LTC)' },
  { value: 'AVAX', label: 'Avalanche (AVAX)' },
  { value: 'LINK', label: 'Chainlink (LINK)' },
  { value: 'ATOM', label: 'Cosmos (ATOM)' },
  { value: 'UNI', label: 'Uniswap (UNI)' },
  { value: 'XLM', label: 'Stellar (XLM)' }
];

const TechnicalIndicators = () => {
  const [selectedCrypto, setSelectedCrypto] = useState('BTC');
  const [days, setDays] = useState(90);
  const [indicators, setIndicators] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchIndicators = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await predictionService.getTechnicalIndicators(selectedCrypto, days);
      
      if (data.error) {
        setError(data.message || data.error);
        setIndicators(null);
      } else {
        setIndicators(data);
      }
    } catch (err) {
      setError('Erreur lors du chargement des indicateurs');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [selectedCrypto, days]);

  useEffect(() => {
    fetchIndicators();
  }, [fetchIndicators]);

  if (loading) {
    return (
      <div className="indicators-container">
        <div className="loading">
          <div className="spinner"></div>
          <p>Calcul des indicateurs techniques...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="indicators-container">
        <div className="indicators-header">
          <div className="indicators-title">
            <span className="emoji">🔬</span>
            <h1>Indicateurs Techniques</h1>
          </div>
        </div>
        <div className="filters-section">
          <div className="filter-group">
            <label>Cryptomonnaie</label>
            <select value={selectedCrypto} onChange={(e) => setSelectedCrypto(e.target.value)}>
              {CRYPTO_OPTIONS.map(opt => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>
          </div>
          <button onClick={fetchIndicators} className="btn-refresh">
            🔄 Réessayer
          </button>
        </div>
        <div className="error-message">
          ❌ {error}
        </div>
      </div>
    );
  }

  if (!indicators) return null;

  // Préparer les données pour les graphiques RSI
  const rsiData = indicators.rsi.series.map((value, index) => ({
    index,
    RSI: parseFloat(value.toFixed(2))
  }));

  // Préparer les données pour les graphiques MACD
  const macdData = indicators.macd.macd_series.map((value, index) => ({
    index,
    MACD: parseFloat(value.toFixed(4)),
    Signal: parseFloat((indicators.macd.signal_series[index] || 0).toFixed(4)),
    Histogram: parseFloat((indicators.macd.histogram_series[index] || 0).toFixed(4))
  }));

  // Fonction pour obtenir la classe CSS du signal combiné
  const getSignalClass = (signal) => {
    const signalLower = signal.toLowerCase().replace(/\s/g, '-');
    return `signal-${signalLower}`;
  };

  return (
    <div className="indicators-container">
      {/* Header */}
      <div className="indicators-header">
        <div className="indicators-title">
          <span className="emoji">🔬</span>
          <h1>Indicateurs Techniques</h1>
        </div>
        <p className="subtitle">
          Analyse avancée avec RSI, MACD et Bollinger Bands
        </p>
      </div>

      {/* Filtres */}
      <div className="filters-section">
        <div className="filter-group">
          <label>Cryptomonnaie</label>
          <select value={selectedCrypto} onChange={(e) => setSelectedCrypto(e.target.value)}>
            {CRYPTO_OPTIONS.map(opt => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label>Période d'analyse</label>
          <select value={days} onChange={(e) => setDays(Number(e.target.value))}>
            <option value={30}>30 jours</option>
            <option value={60}>60 jours</option>
            <option value={90}>90 jours</option>
          </select>
        </div>

        <button onClick={fetchIndicators} className="btn-refresh">
          🔄 Actualiser
        </button>
      </div>

      {/* Info prix actuel */}
      <div className="current-price-info">
        <span className="crypto-name">{selectedCrypto}</span>
        <span className="price">${indicators.current_price?.toLocaleString()}</span>
        <span className="data-points">{indicators.num_points} points analysés</span>
      </div>

      {/* Signal Combiné - Carte principale */}
      <div className={`combined-signal-card ${getSignalClass(indicators.combined_signal.signal)}`}>
        <div className="signal-content">
          <div className="signal-emoji">{indicators.combined_signal.emoji}</div>
          <div className="signal-info">
            <h2>{indicators.combined_signal.signal}</h2>
            <p>{indicators.combined_signal.description}</p>
            <div className="signal-force">
              Force du signal : {indicators.combined_signal.force}%
            </div>
          </div>
        </div>
      </div>

      {/* Grille des indicateurs */}
      <div className="indicators-grid">
        {/* RSI Card */}
        <div className="indicator-card rsi-card">
          <div className="indicator-header">
            <h3>📊 RSI (Relative Strength Index)</h3>
            <span className={`signal-badge ${indicators.rsi.signal.toLowerCase()}`}>
              {indicators.rsi.signal}
            </span>
          </div>
          
          <div className="indicator-value-big">
            <span className="value">{indicators.rsi.value}</span>
            <span className="unit">/ 100</span>
          </div>

          <div className="rsi-gauge">
            <div className="gauge-bar">
              <div className="gauge-zone survente">0-30</div>
              <div className="gauge-zone neutre">30-70</div>
              <div className="gauge-zone surachat">70-100</div>
              <div 
                className="gauge-pointer" 
                style={{ left: `${indicators.rsi.value}%` }}
              />
            </div>
          </div>

          <p className="indicator-interpretation">
            {indicators.rsi.interpretation}
          </p>

          {rsiData.length > 0 && (
            <div className="chart-container">
              <ResponsiveContainer width="100%" height={150}>
                <LineChart data={rsiData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" />
                  <XAxis dataKey="index" hide />
                  <YAxis domain={[0, 100]} tick={{ fill: 'var(--text-muted)' }} />
                  <Tooltip 
                    contentStyle={{ 
                      background: 'var(--bg-card)', 
                      border: '1px solid var(--border-color)',
                      borderRadius: '8px'
                    }}
                  />
                  <Line type="monotone" dataKey="RSI" stroke="#8b5cf6" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>

        {/* MACD Card */}
        <div className="indicator-card macd-card">
          <div className="indicator-header">
            <h3>📈 MACD</h3>
            <span className={`signal-badge ${indicators.macd.trading_signal.toLowerCase()}`}>
              {indicators.macd.trading_signal}
            </span>
          </div>

          <div className="macd-values">
            <div className="macd-value-item">
              <span className="label">MACD</span>
              <span className="value">{indicators.macd.macd}</span>
            </div>
            <div className="macd-value-item">
              <span className="label">Signal</span>
              <span className="value">{indicators.macd.signal}</span>
            </div>
            <div className="macd-value-item">
              <span className="label">Histogram</span>
              <span className={`value ${indicators.macd.histogram > 0 ? 'positive' : 'negative'}`}>
                {indicators.macd.histogram}
              </span>
            </div>
          </div>

          <p className="indicator-interpretation">
            {indicators.macd.interpretation}
          </p>

          {macdData.length > 0 && (
            <div className="chart-container">
              <ResponsiveContainer width="100%" height={120}>
                <LineChart data={macdData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" />
                  <XAxis dataKey="index" hide />
                  <YAxis tick={{ fill: 'var(--text-muted)' }} />
                  <Tooltip 
                    contentStyle={{ 
                      background: 'var(--bg-card)', 
                      border: '1px solid var(--border-color)',
                      borderRadius: '8px'
                    }}
                  />
                  <Legend />
                  <Line type="monotone" dataKey="MACD" stroke="#3b82f6" strokeWidth={2} dot={false} />
                  <Line type="monotone" dataKey="Signal" stroke="#f59e0b" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>

              <ResponsiveContainer width="100%" height={80}>
                <BarChart data={macdData}>
                  <XAxis dataKey="index" hide />
                  <YAxis tick={{ fill: 'var(--text-muted)' }} />
                  <Tooltip 
                    contentStyle={{ 
                      background: 'var(--bg-card)', 
                      border: '1px solid var(--border-color)',
                      borderRadius: '8px'
                    }}
                  />
                  <Bar dataKey="Histogram">
                    {macdData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.Histogram > 0 ? '#22c55e' : '#ef4444'} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>

        {/* Bollinger Bands Card */}
        <div className="indicator-card bb-card">
          <div className="indicator-header">
            <h3>📊 Bollinger Bands</h3>
            <span className={`signal-badge ${indicators.bollinger_bands.trading_signal.toLowerCase()}`}>
              {indicators.bollinger_bands.trading_signal}
            </span>
          </div>

          <div className="bb-values">
            <div className="bb-value-item upper">
              <span className="label">Bande Sup</span>
              <span className="value">${indicators.bollinger_bands.upper?.toLocaleString()}</span>
            </div>
            <div className="bb-value-item middle">
              <span className="label">Moyenne</span>
              <span className="value">${indicators.bollinger_bands.middle?.toLocaleString()}</span>
            </div>
            <div className="bb-value-item lower">
              <span className="label">Bande Inf</span>
              <span className="value">${indicators.bollinger_bands.lower?.toLocaleString()}</span>
            </div>
          </div>

          <div className="bb-stats">
            <div className="stat">
              <span className="label">Largeur</span>
              <span className="value">{indicators.bollinger_bands.width_percent?.toFixed(2)}%</span>
            </div>
            <div className="stat">
              <span className="label">Position (%B)</span>
              <span className="value">{(indicators.bollinger_bands.percent_b * 100).toFixed(1)}%</span>
            </div>
          </div>

          <p className="indicator-interpretation">
            {indicators.bollinger_bands.interpretation}
          </p>

          {/* Visualisation de la position dans les bandes */}
          <div className="bb-position-visual">
            <div className="bb-bar">
              <div className="bb-zone lower-zone"></div>
              <div className="bb-zone middle-zone"></div>
              <div className="bb-zone upper-zone"></div>
              <div 
                className="bb-pointer" 
                style={{ left: `${Math.min(100, Math.max(0, indicators.bollinger_bands.percent_b * 100))}%` }}
              >
                <span className="pointer-label">Prix actuel</span>
              </div>
            </div>
            <div className="bb-labels">
              <span>Bande Inf</span>
              <span>Moyenne</span>
              <span>Bande Sup</span>
            </div>
          </div>
        </div>
      </div>

      {/* Résumé des signaux */}
      <div className="signals-summary">
        <h3>📋 Résumé des Signaux</h3>
        <div className="signals-table">
          <div className="signal-row">
            <span className="indicator-name">RSI (14)</span>
            <span className={`signal-value ${indicators.rsi.signal.toLowerCase()}`}>
              {indicators.rsi.signal}
            </span>
            <span className="indicator-detail">{indicators.rsi.value}/100</span>
          </div>
          <div className="signal-row">
            <span className="indicator-name">MACD (12/26/9)</span>
            <span className={`signal-value ${indicators.macd.trading_signal.toLowerCase()}`}>
              {indicators.macd.trading_signal}
            </span>
            <span className="indicator-detail">Hist: {indicators.macd.histogram}</span>
          </div>
          <div className="signal-row">
            <span className="indicator-name">Bollinger Bands (20)</span>
            <span className={`signal-value ${indicators.bollinger_bands.trading_signal.toLowerCase()}`}>
              {indicators.bollinger_bands.trading_signal}
            </span>
            <span className="indicator-detail">%B: {(indicators.bollinger_bands.percent_b * 100).toFixed(1)}%</span>
          </div>
        </div>
      </div>

      {/* Avertissement */}
      <div className="warning-box">
        ⚠️ <strong>Avertissement :</strong> Ces indicateurs sont des outils d'aide à la décision. 
        Ils ne constituent pas des conseils financiers. Toujours effectuer sa propre analyse avant d'investir.
        Les marchés de cryptomonnaies sont hautement volatils.
      </div>
    </div>
  );
};

export default TechnicalIndicators;
