// frontend/src/components/AdvancedCharts/HeatmapChart.js

import React, { useState, useEffect, useCallback } from 'react';
import analyticsService from '../../services/analyticsService';
import './HeatmapChart.css';

const HeatmapChart = () => {
  const [period, setPeriod] = useState('24h');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);

    const result = await analyticsService.getHeatmapData(period);

    if (result.success) {
      setData(result.data.data);
    } else {
      setError(result.error);
    }

    setLoading(false);
  }, [period]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const getColorForPercentage = (percent) => {
    if (percent >= 10) return '#16a34a';
    if (percent >= 5) return '#22c55e';
    if (percent >= 2) return '#86efac';
    if (percent >= 0) return '#bbf7d0';
    if (percent >= -2) return '#fecaca';
    if (percent >= -5) return '#fca5a5';
    if (percent >= -10) return '#ef4444';
    return '#dc2626';
  };

  const getTextColor = (percent) => {
    return Math.abs(percent) > 5 ? 'white' : 'var(--text-primary)';
  };

  const formatPrice = (price) => {
    if (price >= 1000) {
      return `$${(price / 1000).toFixed(1)}K`;
    }
    if (price >= 1) {
      return `$${price.toFixed(2)}`;
    }
    return `$${price.toFixed(4)}`;
  };

  const formatVolume = (volume) => {
    if (volume >= 1e9) return `$${(volume / 1e9).toFixed(1)}B`;
    if (volume >= 1e6) return `$${(volume / 1e6).toFixed(1)}M`;
    if (volume >= 1e3) return `$${(volume / 1e3).toFixed(1)}K`;
    return `$${volume.toFixed(0)}`;
  };

  if (loading && !data) {
    return (
      <div className="heatmap-container">
        <div className="loading">
          <div className="spinner"></div>
          <p>Chargement de la heatmap...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="heatmap-container">
      <header className="chart-header">
        <div className="chart-title">
          <span className="emoji">🔥</span>
          <h1>Heatmap de Performance</h1>
        </div>
        <p className="subtitle">Variation de prix de toutes les cryptomonnaies</p>
      </header>

      {/* Contrôles */}
      <div className="heatmap-controls">
        <div className="period-buttons">
          {[
            { value: '1h', label: '1H' },
            { value: '24h', label: '24H' },
            { value: '7d', label: '7J' },
            { value: '30d', label: '30J' }
          ].map(p => (
            <button
              key={p.value}
              className={`period-btn ${period === p.value ? 'active' : ''}`}
              onClick={() => setPeriod(p.value)}
            >
              {p.label}
            </button>
          ))}
        </div>

        <button onClick={fetchData} className="btn-refresh" disabled={loading}>
          {loading ? '⏳ Chargement...' : '🔄 Actualiser'}
        </button>
      </div>

      {error && (
        <div className="error-message">❌ {error}</div>
      )}

      {data && (
        <>
          {/* Statistiques globales */}
          <div className="market-stats">
            <div className="stat-card">
              <span className="stat-icon">📊</span>
              <div className="stat-info">
                <span className="stat-label">Total Cryptos</span>
                <span className="stat-value">{data.length}</span>
              </div>
            </div>
            <div className="stat-card">
              <span className="stat-icon">🟢</span>
              <div className="stat-info">
                <span className="stat-label">En hausse</span>
                <span className="stat-value green">{data.filter(c => c.price_change_percent > 0).length}</span>
              </div>
            </div>
            <div className="stat-card">
              <span className="stat-icon">🔴</span>
              <div className="stat-info">
                <span className="stat-label">En baisse</span>
                <span className="stat-value red">{data.filter(c => c.price_change_percent < 0).length}</span>
              </div>
            </div>
            <div className="stat-card">
              <span className="stat-icon">⚖️</span>
              <div className="stat-info">
                <span className="stat-label">Stable</span>
                <span className="stat-value">{data.filter(c => c.price_change_percent === 0).length}</span>
              </div>
            </div>
          </div>

          {/* Grille Heatmap */}
          <div className="heatmap-grid">
            {data.map((crypto, index) => (
              <div
                key={crypto.symbol}
                className="heatmap-cell"
                style={{
                  backgroundColor: getColorForPercentage(crypto.price_change_percent),
                  color: getTextColor(crypto.price_change_percent),
                  animationDelay: `${index * 0.03}s`
                }}
                title={`${crypto.name}\nPrix: ${formatPrice(crypto.current_price)}\nVariation: ${crypto.price_change_percent.toFixed(2)}%\nVolume 24h: ${formatVolume(crypto.volume_24h)}`}
              >
                <div className="cell-symbol">{crypto.symbol}</div>
                <div className="cell-percent">
                  {crypto.price_change_percent >= 0 ? '+' : ''}
                  {crypto.price_change_percent.toFixed(2)}%
                </div>
                <div className="cell-price">{formatPrice(crypto.current_price)}</div>
              </div>
            ))}
          </div>

          {/* Légende */}
          <div className="heatmap-legend">
            <h4>Légende des couleurs</h4>
            <div className="legend-gradient">
              <div className="gradient-bar"></div>
              <div className="gradient-labels">
                <span>-10%</span>
                <span>-5%</span>
                <span>0%</span>
                <span>+5%</span>
                <span>+10%</span>
              </div>
            </div>
          </div>

          {/* Top Gainers & Losers */}
          <div className="top-movers">
            <div className="movers-section gainers">
              <h3>🚀 Top Gainers</h3>
              <div className="movers-list">
                {data.filter(c => c.price_change_percent > 0).slice(0, 5).map(crypto => (
                  <div key={crypto.symbol} className="mover-item gainer">
                    <div className="mover-info">
                      <span className="mover-symbol">{crypto.symbol}</span>
                      <span className="mover-name">{crypto.name}</span>
                    </div>
                    <div className="mover-stats">
                      <span className="mover-price">{formatPrice(crypto.current_price)}</span>
                      <span className="mover-percent">
                        +{crypto.price_change_percent.toFixed(2)}%
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="movers-section losers">
              <h3>📉 Top Losers</h3>
              <div className="movers-list">
                {data.filter(c => c.price_change_percent < 0).slice(-5).reverse().map(crypto => (
                  <div key={crypto.symbol} className="mover-item loser">
                    <div className="mover-info">
                      <span className="mover-symbol">{crypto.symbol}</span>
                      <span className="mover-name">{crypto.name}</span>
                    </div>
                    <div className="mover-stats">
                      <span className="mover-price">{formatPrice(crypto.current_price)}</span>
                      <span className="mover-percent">
                        {crypto.price_change_percent.toFixed(2)}%
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default HeatmapChart;
