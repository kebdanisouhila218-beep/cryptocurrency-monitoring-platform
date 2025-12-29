// frontend/src/components/PerformanceTracker.js
import React, { useEffect, useState } from 'react';
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
import virtualPortfolioService from '../services/virtualPortfolioService';
import { toast } from './Toast';
import './PerformanceTracker.css';

const COLORS = ['#22c55e', '#ef4444', '#3b82f6', '#f59e0b', '#8b5cf6', '#ec4899'];

const PerformanceTracker = () => {
  const [globalStats, setGlobalStats] = useState(null);
  const [history, setHistory] = useState([]);
  const [cryptosPerformance, setCryptosPerformance] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedPeriod, setSelectedPeriod] = useState(30);

  useEffect(() => {
    loadAllData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedPeriod]);

  const loadAllData = async () => {
    setLoading(true);

    const [statsResult, historyResult, cryptosResult] = await Promise.all([
      virtualPortfolioService.getGlobalStats(),
      virtualPortfolioService.getPerformanceHistory(selectedPeriod),
      virtualPortfolioService.getPerformanceByCrypto(),
    ]);

    if (statsResult.success) {
      setGlobalStats(statsResult.data?.stats || null);
    } else {
      toast.error(statsResult.error);
      setGlobalStats(null);
    }

    if (historyResult.success) {
      setHistory(historyResult.data?.history || []);
    } else {
      toast.error(historyResult.error);
      setHistory([]);
    }

    if (cryptosResult.success) {
      setCryptosPerformance(cryptosResult.data?.cryptos || []);
    } else {
      toast.error(cryptosResult.error);
      setCryptosPerformance([]);
    }

    setLoading(false);
  };

  const formatCurrency = (value) => {
    const v = Number(value);
    const safe = Number.isFinite(v) ? v : 0;
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(safe);
  };

  const formatPercent = (value) => {
    const v = Number(value);
    const safe = Number.isFinite(v) ? v : 0;
    const sign = safe >= 0 ? '+' : '';
    return `${sign}${safe.toFixed(2)}%`;
  };

  if (loading) {
    return (
      <div className="performance-tracker">
        <div className="loading-container">
          <div className="spinner"></div>
          <p>Chargement des performances...</p>
        </div>
      </div>
    );
  }

  if (!globalStats || (globalStats.total_portfolios || 0) === 0) {
    return (
      <div className="performance-tracker">
        <div className="empty-state">
          <div className="empty-icon">📊</div>
          <h3>Aucun portfolio</h3>
          <p>Créez votre premier portfolio virtuel pour suivre vos performances.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="performance-tracker">
      <header className="performance-header">
        <div className="title-container">
          <span className="emoji">📊</span>
          <h1>Suivi des Performances</h1>
        </div>
        <p className="subtitle">Vue d'ensemble de tous vos portfolios virtuels</p>
      </header>

      <div className="global-stats-grid">
        <div className="stat-card-large total">
          <div className="stat-header">
            <div className="stat-icon">💰</div>
            <div className="stat-label">Valeur Totale</div>
          </div>
          <div className="stat-value-large">{formatCurrency(globalStats.total_current_value)}</div>
          <div className="stat-subtext">Investi: {formatCurrency(globalStats.total_invested)}</div>
        </div>

        <div className="stat-card-large profit">
          <div className="stat-header">
            <div className="stat-icon">{(globalStats.total_profit_loss || 0) >= 0 ? '📈' : '📉'}</div>
            <div className="stat-label">Profit/Loss</div>
          </div>
          <div
            className={`stat-value-large ${(globalStats.total_profit_loss || 0) >= 0 ? 'positive' : 'negative'}`}
          >
            {formatCurrency(globalStats.total_profit_loss)}
          </div>
          <div
            className={`stat-subtext ${(globalStats.total_profit_loss || 0) >= 0 ? 'positive' : 'negative'}`}
          >
            {formatPercent(globalStats.total_profit_loss_percent)}
          </div>
        </div>

        <div className="stat-card-large portfolios">
          <div className="stat-header">
            <div className="stat-icon">💼</div>
            <div className="stat-label">Portfolios</div>
          </div>
          <div className="stat-value-large">{globalStats.total_portfolios}</div>
          <div className="stat-subtext">{globalStats.total_transactions} transactions</div>
        </div>
      </div>

      {globalStats.best_portfolio && (
        <div className="best-worst-section">
          <div className="portfolio-highlight best">
            <div className="highlight-icon">🏆</div>
            <div className="highlight-content">
              <div className="highlight-label">Meilleur Portfolio</div>
              <div className="highlight-name">{globalStats.best_portfolio.name}</div>
              <div className="highlight-value positive">
                {formatPercent(globalStats.best_portfolio.profit_loss_percent)}
              </div>
            </div>
          </div>

          {globalStats.worst_portfolio && globalStats.worst_portfolio.profit_loss_percent < 0 && (
            <div className="portfolio-highlight worst">
              <div className="highlight-icon">⚠️</div>
              <div className="highlight-content">
                <div className="highlight-label">Portfolio à surveiller</div>
                <div className="highlight-name">{globalStats.worst_portfolio.name}</div>
                <div className="highlight-value negative">
                  {formatPercent(globalStats.worst_portfolio.profit_loss_percent)}
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      <div className="period-selector">
        <button className={selectedPeriod === 7 ? 'active' : ''} onClick={() => setSelectedPeriod(7)}>
          7 jours
        </button>
        <button className={selectedPeriod === 30 ? 'active' : ''} onClick={() => setSelectedPeriod(30)}>
          30 jours
        </button>
        <button className={selectedPeriod === 90 ? 'active' : ''} onClick={() => setSelectedPeriod(90)}>
          90 jours
        </button>
      </div>

      {history.length > 0 && (
        <div className="chart-section">
          <h2>📈 Évolution de la Valeur</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={history}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip formatter={(value) => formatCurrency(value)} />
              <Legend />
              <Line type="monotone" dataKey="value" stroke="#22c55e" strokeWidth={2} name="Valeur Actuelle" />
              <Line
                type="monotone"
                dataKey="invested"
                stroke="#94a3b8"
                strokeWidth={2}
                strokeDasharray="5 5"
                name="Investi"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {cryptosPerformance.length > 0 && (
        <div className="chart-section">
          <h2>💎 Performance par Cryptomonnaie</h2>
          <div className="cryptos-performance-list">
            {cryptosPerformance.map((crypto, index) => (
              <div key={crypto.symbol} className="crypto-performance-card">
                <div className="crypto-header">
                  <div
                    className="crypto-icon"
                    style={{
                      background: `linear-gradient(135deg, ${COLORS[index % COLORS.length]}, ${
                        COLORS[(index + 1) % COLORS.length]
                      })`,
                    }}
                  >
                    {String(crypto.symbol || '').substring(0, 2)}
                  </div>
                  <div className="crypto-info">
                    <h3>{crypto.symbol}</h3>
                    <p>{crypto.name}</p>
                  </div>
                  <div className={`crypto-profit ${(crypto.profit_loss || 0) >= 0 ? 'positive' : 'negative'}`}>
                    {formatPercent(crypto.profit_loss_percent)}
                  </div>
                </div>

                <div className="crypto-details-grid">
                  <div className="crypto-detail">
                    <span className="label">Quantité</span>
                    <span className="value">{crypto.quantity}</span>
                  </div>
                  <div className="crypto-detail">
                    <span className="label">Prix Moyen d'Achat</span>
                    <span className="value">{formatCurrency(crypto.avg_buy_price)}</span>
                  </div>
                  <div className="crypto-detail">
                    <span className="label">Prix Actuel</span>
                    <span className="value">{formatCurrency(crypto.current_price)}</span>
                  </div>
                  <div className="crypto-detail">
                    <span className="label">Valeur Actuelle</span>
                    <span className="value">{formatCurrency(crypto.current_value)}</span>
                  </div>
                  <div className="crypto-detail">
                    <span className="label">Coût Total</span>
                    <span className="value">{formatCurrency(crypto.total_cost)}</span>
                  </div>
                  <div className="crypto-detail">
                    <span className="label">Profit/Loss</span>
                    <span className={`value ${(crypto.profit_loss || 0) >= 0 ? 'positive' : 'negative'}`}>
                      {formatCurrency(crypto.profit_loss)}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default PerformanceTracker;
