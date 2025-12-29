// frontend/src/components/Predictions.js
import React, { useState, useEffect, useCallback } from 'react';
import predictionService from '../services/predictionService';
import cryptoService from '../api/cryptoService';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import './Predictions.css';

const Predictions = () => {
  // ===== 1. TOUS LES ÉTATS =====
  const [cryptos, setCryptos] = useState([]);
  const [selectedCrypto, setSelectedCrypto] = useState('BTC');
  const [predictions, setPredictions] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [period, setPeriod] = useState(90);

  // ===== 2. TOUTES LES FONCTIONS (AVANT useEffect) =====
  
  // Fonction pour charger la liste des cryptos
  const loadCryptos = async () => {
    try {
      const data = await cryptoService.getAllCryptos();
      setCryptos(data);
    } catch (err) {
      console.error('Erreur chargement cryptos:', err);
    }
  };

  // Fonction pour charger les prévisions (avec useCallback)
  const loadPredictions = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const result = await predictionService.getPredictions(selectedCrypto, period);
      
      if (result.success) {
        setPredictions(result.data);
      } else {
        setError(result.error);
      }
    } catch (err) {
      setError('Erreur lors du chargement des prévisions');
    } finally {
      setLoading(false);
    }
  }, [selectedCrypto, period]);

  // ===== 3. TOUS LES useEffect (APRÈS LES FONCTIONS) =====
  
  // Charger la liste des cryptos au démarrage
  useEffect(() => {
    loadCryptos();
  }, []);

  // Charger les prévisions quand la crypto ou la période change
  useEffect(() => {
    if (selectedCrypto) {
      loadPredictions();
    }
  }, [selectedCrypto, period, loadPredictions]);

  // ===== 4. FONCTIONS UTILITAIRES =====
  
  const getTrendIcon = (trend) => {
    switch (trend) {
      case 'bullish':
        return '📈';
      case 'bearish':
        return '📉';
      default:
        return '➡️';
    }
  };

  const getTrendLabel = (trend) => {
    switch (trend) {
      case 'bullish':
        return 'Haussière';
      case 'bearish':
        return 'Baissière';
      default:
        return 'Neutre';
    }
  };

  const getTrendClass = (trend) => {
    switch (trend) {
      case 'bullish':
        return 'bullish';
      case 'bearish':
        return 'bearish';
      default:
        return 'neutral';
    }
  };

  const getChangeClass = (value) => {
    if (value === null || value === undefined) return '';
    return value > 0 ? 'positive' : 'negative';
  };

  const formatPercent = (value) => {
    if (value === null || value === undefined) return 'N/A';
    const num = Number(value);
    if (!Number.isFinite(num)) return 'N/A';
    const sign = num > 0 ? '+' : '';
    return `${sign}${num.toFixed(2)}%`;
  };

  const getConfidenceLabel = (confidence) => {
    switch (confidence) {
      case 'high':
        return '🟢 Élevée';
      case 'medium':
        return '🟡 Moyenne';
      case 'low':
        return '🔴 Faible';
      default:
        return 'N/A';
    }
  };

  // ===== 5. DONNÉES POUR GRAPHIQUES =====
  
  const chartData =
    predictions
      ? [
          {
            name: 'Prix Actuel',
            value: predictions.current_price,
            type: 'current',
          },
          {
            name: 'SMA 7j',
            value: predictions.moving_averages?.sma_7,
            type: 'sma',
          },
          {
            name: 'SMA 30j',
            value: predictions.moving_averages?.sma_30,
            type: 'sma',
          },
          {
            name: 'SMA 90j',
            value: predictions.moving_averages?.sma_90,
            type: 'sma',
          },
          {
            name: 'Prévision 7j',
            value: predictions.trend_analysis?.prediction_7d,
            type: 'prediction',
          },
          {
            name: 'Prévision 30j',
            value: predictions.trend_analysis?.prediction_30d,
            type: 'prediction',
          },
        ].filter((item) => item.value !== null && item.value !== undefined)
      : [];

  // ===== 6. RENDER (JSX) =====
  
  return (
    <div className="predictions-container">
      <div className="predictions-header">
        <div className="title-container">
          <span className="emoji">🔮</span>
          <h1>Prévisions & Analyse</h1>
        </div>
        <p className="subtitle">Moyennes mobiles et prévisions basées sur l'historique des prix</p>
      </div>

      {/* Contrôles */}
      <div className="predictions-controls">
        <div className="control-group">
          <label>Cryptomonnaie</label>
          <select
            value={selectedCrypto}
            onChange={(e) => setSelectedCrypto(e.target.value)}
            className="crypto-select"
          >
            {cryptos.map((crypto) => (
              <option key={crypto.symbol} value={crypto.symbol}>
                {crypto.name} ({crypto.symbol})
              </option>
            ))}
          </select>
        </div>

        <div className="control-group">
          <label>Période d'analyse</label>
          <select
            value={period}
            onChange={(e) => setPeriod(Number(e.target.value))}
            className="period-select"
          >
            <option value={30}>30 jours</option>
            <option value={60}>60 jours</option>
            <option value={90}>90 jours</option>
          </select>
        </div>

        <button onClick={loadPredictions} className="btn-refresh" disabled={loading}>
          {loading ? '⏳ Chargement...' : '🔄 Actualiser'}
        </button>
      </div>

      {/* Message d'erreur */}
      {error && <div className="error-message">❌ {error}</div>}

      {/* Loading */}
      {loading && (
        <div className="loading-container">
          <div className="spinner"></div>
          <p className="loading-text">Calcul des prévisions...</p>
        </div>
      )}

      {/* Résultats */}
      {!loading && predictions && (
        <>
          {/* Prix Actuel & Tendance */}
          <div className="current-info">
            <div className="info-card price-card">
              <div className="card-icon">💰</div>
              <div className="card-content">
                <div className="card-label">Prix Actuel</div>
                <div className="card-value">${Number(predictions.current_price).toLocaleString()}</div>
              </div>
            </div>

            <div className={`info-card trend-card ${getTrendClass(predictions.trend_analysis?.trend)}`}>
              <div className="card-icon">{getTrendIcon(predictions.trend_analysis?.trend)}</div>
              <div className="card-content">
                <div className="card-label">Tendance</div>
                <div className="card-value">{getTrendLabel(predictions.trend_analysis?.trend)}</div>
                <div className="card-sublabel">
                  Confiance: {getConfidenceLabel(predictions.trend_analysis?.confidence)}
                </div>
              </div>
            </div>
          </div>

          {/* Moyennes Mobiles SMA */}
          <div className="section">
            <h2>📊 Moyennes Mobiles Simples (SMA)</h2>
            <div className="sma-grid">
              <div className="sma-card">
                <div className="sma-label">SMA 7 jours</div>
                <div className="sma-value">
                  {predictions.moving_averages?.sma_7
                    ? `$${Number(predictions.moving_averages.sma_7).toLocaleString()}`
                    : 'Données insuffisantes'}
                </div>
              </div>

              <div className="sma-card">
                <div className="sma-label">SMA 30 jours</div>
                <div className="sma-value">
                  {predictions.moving_averages?.sma_30
                    ? `$${Number(predictions.moving_averages.sma_30).toLocaleString()}`
                    : 'Données insuffisantes'}
                </div>
              </div>

              <div className="sma-card">
                <div className="sma-label">SMA 90 jours</div>
                <div className="sma-value">
                  {predictions.moving_averages?.sma_90
                    ? `$${Number(predictions.moving_averages.sma_90).toLocaleString()}`
                    : 'Données insuffisantes'}
                </div>
              </div>
            </div>
          </div>

          {/* Moyennes Mobiles EMA */}
          <div className="section">
            <h2>📈 Moyennes Mobiles Exponentielles (EMA)</h2>
            <div className="sma-grid">
              <div className="sma-card ema">
                <div className="sma-label">EMA 7 périodes</div>
                <div className="sma-value">
                  {predictions.exponential_averages?.ema_7
                    ? `$${Number(predictions.exponential_averages.ema_7).toLocaleString()}`
                    : 'Données insuffisantes'}
                </div>
              </div>

              <div className="sma-card ema">
                <div className="sma-label">EMA 20 périodes</div>
                <div className="sma-value">
                  {predictions.exponential_averages?.ema_20
                    ? `$${Number(predictions.exponential_averages.ema_20).toLocaleString()}`
                    : 'Données insuffisantes'}
                </div>
              </div>

              <div className="sma-card ema">
                <div className="sma-label">EMA 50 périodes</div>
                <div className="sma-value">
                  {predictions.exponential_averages?.ema_50
                    ? `$${Number(predictions.exponential_averages.ema_50).toLocaleString()}`
                    : 'Données insuffisantes'}
                </div>
              </div>
            </div>
          </div>

          {/* Prévisions */}
          <div className="section">
            <h2>🔮 Prévisions de Prix</h2>
            <div className="predictions-grid">
              <div className="prediction-card">
                <div className="prediction-period">7 jours</div>
                <div className="prediction-value">
                  ${Number(predictions.trend_analysis?.prediction_7d).toLocaleString()}
                </div>
                <div className="prediction-info">Régression linéaire</div>
              </div>

              <div className="prediction-card">
                <div className="prediction-period">30 jours</div>
                <div className="prediction-value">
                  ${Number(predictions.trend_analysis?.prediction_30d).toLocaleString()}
                </div>
                <div className="prediction-info">Régression linéaire</div>
              </div>

              <div className="prediction-card weighted">
                <div className="prediction-period">🎯 Prédiction Optimale</div>
                <div className="prediction-value">
                  ${predictions.weighted_prediction?.value
                    ? Number(predictions.weighted_prediction.value).toLocaleString()
                    : 'N/A'}
                </div>
                <div className="prediction-info">
                  Moyenne pondérée (SMA 20%, EMA 40%, LR 40%)
                </div>
                <div className="prediction-confidence">
                  Confiance: {getConfidenceLabel(predictions.weighted_prediction?.confidence)}
                </div>
              </div>
            </div>

            {/* Volatilité */}
            {predictions.volatility && (
              <div className="volatility-info">
                <span className="volatility-label">📊 Volatilité (30j):</span>
                <span className={`volatility-value ${predictions.volatility > 5 ? 'high' : predictions.volatility > 2 ? 'medium' : 'low'}`}>
                  {predictions.volatility.toFixed(2)}%
                </span>
                <span className="volatility-desc">
                  {predictions.volatility > 5 ? '(Élevée)' : predictions.volatility > 2 ? '(Moyenne)' : '(Faible)'}
                </span>
              </div>
            )}
          </div>

          {/* Évolution Récente */}
          <div className="section">
            <h2>📈 Évolution Récente</h2>
            <div className="changes-grid">
              <div className="change-card">
                <div className="change-period">7 jours</div>
                <div className={`change-value ${getChangeClass(predictions.price_changes?.['7_days'])}`}>
                  {formatPercent(predictions.price_changes?.['7_days'])}
                </div>
              </div>

              <div className="change-card">
                <div className="change-period">30 jours</div>
                <div className={`change-value ${getChangeClass(predictions.price_changes?.['30_days'])}`}>
                  {formatPercent(predictions.price_changes?.['30_days'])}
                </div>
              </div>

              <div className="change-card">
                <div className="change-period">90 jours</div>
                <div className={`change-value ${getChangeClass(predictions.price_changes?.['90_days'])}`}>
                  {formatPercent(predictions.price_changes?.['90_days'])}
                </div>
              </div>
            </div>
          </div>

          {/* Graphique */}
          <div className="section">
            <h2>📊 Comparaison Visuelle</h2>
            <div className="chart-container">
              <ResponsiveContainer width="100%" height={350}>
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="value"
                    stroke="#8884d8"
                    strokeWidth={2}
                    name="Prix (USD)"
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Disclaimer */}
          <div className="disclaimer">
            ⚠️ <strong>Avertissement :</strong> Ces prévisions sont basées sur des modèles statistiques simples
            et ne constituent PAS des conseils financiers. Les marchés de cryptomonnaies sont hautement volatils.
          </div>
        </>
      )}
    </div>
  );
};

export default Predictions;