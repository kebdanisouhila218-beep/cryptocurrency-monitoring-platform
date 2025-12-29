// frontend/src/components/AdvancedCharts/CandlestickChart.js

import React, { useState, useEffect, useCallback } from 'react';
import { ComposedChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import analyticsService from '../../services/analyticsService';
import './CandlestickChart.css';

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
  { value: 'LINK', label: 'Chainlink (LINK)' }
];

const CandlestickChart = () => {
  const [selectedCrypto, setSelectedCrypto] = useState('BTC');
  const [interval, setInterval] = useState('1h');
  const [days, setDays] = useState(7);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);

    const result = await analyticsService.getCandlestickData(selectedCrypto, interval, days);

    if (result.success) {
      // Formater les données pour le graphique
      const formatted = result.data.data.map(candle => {
        const isGreen = candle.close >= candle.open;
        return {
          timestamp: new Date(candle.timestamp).toLocaleString('fr-FR', {
            day: '2-digit',
            month: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
          }),
          open: candle.open,
          high: candle.high,
          low: candle.low,
          close: candle.close,
          volume: candle.volume,
          // Pour représenter le corps de la bougie
          bodyLow: Math.min(candle.open, candle.close),
          bodyHigh: Math.max(candle.open, candle.close),
          bodyHeight: Math.abs(candle.close - candle.open),
          wickTop: candle.high - Math.max(candle.open, candle.close),
          wickBottom: Math.min(candle.open, candle.close) - candle.low,
          isGreen: isGreen,
          fill: isGreen ? '#22c55e' : '#ef4444'
        };
      });

      setData(formatted);
    } else {
      setError(result.error);
    }

    setLoading(false);
  }, [selectedCrypto, interval, days]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const d = payload[0].payload;
      const isGreen = d.close >= d.open;

      return (
        <div className="candlestick-tooltip">
          <p className="tooltip-date">{d.timestamp}</p>
          <div className="tooltip-row">
            <span className="label">Open:</span>
            <span className={isGreen ? 'green' : 'red'}>${d.open.toLocaleString()}</span>
          </div>
          <div className="tooltip-row">
            <span className="label">High:</span>
            <span>${d.high.toLocaleString()}</span>
          </div>
          <div className="tooltip-row">
            <span className="label">Low:</span>
            <span>${d.low.toLocaleString()}</span>
          </div>
          <div className="tooltip-row">
            <span className="label">Close:</span>
            <span className={isGreen ? 'green' : 'red'}>${d.close.toLocaleString()}</span>
          </div>
          <div className="tooltip-row">
            <span className="label">Volume:</span>
            <span>${(d.volume / 1000000).toFixed(2)}M</span>
          </div>
        </div>
      );
    }
    return null;
  };

  if (loading && !data) {
    return (
      <div className="candlestick-container">
        <div className="loading">
          <div className="spinner"></div>
          <p>Chargement des données...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="candlestick-container">
      <header className="chart-header">
        <div className="chart-title">
          <span className="emoji">📈</span>
          <h1>Graphique en Chandeliers</h1>
        </div>
        <p className="subtitle">Visualisation OHLC (Open, High, Low, Close)</p>
      </header>

      {/* Contrôles */}
      <div className="chart-controls">
        <div className="form-group">
          <label>Cryptomonnaie</label>
          <select value={selectedCrypto} onChange={(e) => setSelectedCrypto(e.target.value)}>
            {CRYPTO_OPTIONS.map(option => (
              <option key={option.value} value={option.value}>{option.label}</option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label>Intervalle</label>
          <select value={interval} onChange={(e) => setInterval(e.target.value)}>
            <option value="5m">5 minutes</option>
            <option value="15m">15 minutes</option>
            <option value="30m">30 minutes</option>
            <option value="1h">1 heure</option>
            <option value="4h">4 heures</option>
            <option value="1d">1 jour</option>
          </select>
        </div>

        <div className="form-group">
          <label>Période</label>
          <select value={days} onChange={(e) => setDays(Number(e.target.value))}>
            <option value={1}>1 jour</option>
            <option value={3}>3 jours</option>
            <option value={7}>7 jours</option>
            <option value={14}>14 jours</option>
            <option value={30}>30 jours</option>
          </select>
        </div>

        <button onClick={fetchData} className="btn-refresh" disabled={loading}>
          {loading ? '⏳ Chargement...' : '🔄 Actualiser'}
        </button>
      </div>

      {error && (
        <div className="error-message">❌ {error}</div>
      )}

      {data && data.length > 0 && (
        <div className="chart-wrapper">
          <div className="chart-info">
            <span className="crypto-symbol">{selectedCrypto}</span>
            <span className="data-points">{data.length} bougies</span>
          </div>

          <ResponsiveContainer width="100%" height={500}>
            <ComposedChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" />
              <XAxis
                dataKey="timestamp"
                tick={{ fill: 'var(--text-muted)', fontSize: 11 }}
                angle={-45}
                textAnchor="end"
                height={80}
                interval="preserveStartEnd"
              />
              <YAxis
                domain={['auto', 'auto']}
                tick={{ fill: 'var(--text-muted)' }}
                tickFormatter={(value) => `$${value.toLocaleString()}`}
              />
              <Tooltip content={<CustomTooltip />} />
              
              {/* Corps des bougies */}
              <Bar dataKey="bodyHeight" stackId="candle" barSize={8}>
                {data.map((entry, index) => (
                  <Cell 
                    key={`body-${index}`} 
                    fill={entry.fill}
                    stroke={entry.fill}
                  />
                ))}
              </Bar>
            </ComposedChart>
          </ResponsiveContainer>

          {/* Statistiques */}
          <div className="chart-stats">
            <div className="stat-item">
              <span className="stat-label">Prix actuel</span>
              <span className="stat-value">${data[data.length - 1]?.close.toLocaleString()}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Plus haut</span>
              <span className="stat-value green">${Math.max(...data.map(d => d.high)).toLocaleString()}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Plus bas</span>
              <span className="stat-value red">${Math.min(...data.map(d => d.low)).toLocaleString()}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Variation</span>
              <span className={`stat-value ${data[data.length - 1]?.close >= data[0]?.open ? 'green' : 'red'}`}>
                {((data[data.length - 1]?.close - data[0]?.open) / data[0]?.open * 100).toFixed(2)}%
              </span>
            </div>
          </div>

          <div className="chart-legend">
            <div className="legend-item">
              <div className="legend-color" style={{ background: '#22c55e' }}></div>
              <span>Haussier (Close &gt; Open)</span>
            </div>
            <div className="legend-item">
              <div className="legend-color" style={{ background: '#ef4444' }}></div>
              <span>Baissier (Close &lt; Open)</span>
            </div>
          </div>
        </div>
      )}

      {data && data.length === 0 && (
        <div className="no-data">
          <p>Aucune donnée disponible pour cette période</p>
        </div>
      )}
    </div>
  );
};

export default CandlestickChart;
