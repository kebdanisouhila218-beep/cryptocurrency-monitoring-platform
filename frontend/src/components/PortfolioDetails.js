import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import portfolioService from '../services/portfolioService';
import { toast } from './Toast';
import './PortfolioDetails.css';

const PortfolioDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [portfolio, setPortfolio] = useState(null);
  const [positions, setPositions] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [stats, setStats] = useState(null);
  const [allocation, setAllocation] = useState(null);
  const [performance, setPerformance] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [showTradeModal, setShowTradeModal] = useState(false);
  const [tradeData, setTradeData] = useState({
    crypto_symbol: '',
    side: 'buy',
    quantity: '',
    price: ''
  });

  const fetchPortfolioData = useCallback(async () => {
    setLoading(true);
    try {
      // Fetch portfolio details
      const portfolioResult = await portfolioService.getPortfolio(id);
      if (portfolioResult.success) {
        setPortfolio(portfolioResult.data);
      } else {
        toast.error(portfolioResult.error);
        navigate('/portfolio');
        return;
      }

      // Fetch positions, transactions, stats, allocation, and performance in parallel
      const [positionsResult, transactionsResult, statsResult, allocationResult, performanceResult] = await Promise.all([
        portfolioService.getPositions(id),
        portfolioService.getTransactions(id),
        portfolioService.getPortfolioStats(id),
        portfolioService.getPortfolioAllocation(id),
        portfolioService.getPortfolioPerformance(id, 30)
      ]);

      if (positionsResult.success) {
        setPositions(Array.isArray(positionsResult.data) ? positionsResult.data : (positionsResult.data.positions || []));
      }
      if (transactionsResult.success) {
        setTransactions(Array.isArray(transactionsResult.data) ? transactionsResult.data : (transactionsResult.data.transactions || []));
      }
      if (statsResult.success) setStats(statsResult.data);
      if (allocationResult.success) setAllocation(allocationResult.data);
      if (performanceResult.success) setPerformance(performanceResult.data);

    } catch (error) {
      toast.error('Erreur lors de la récupération des données du portefeuille');
    } finally {
      setLoading(false);
    }
  }, [id, navigate]);

  useEffect(() => {
    fetchPortfolioData();
  }, [fetchPortfolioData]);

  const handleTrade = async (e) => {
    e.preventDefault();
    try {
      const result = await portfolioService.executeTrade(id, tradeData);
      if (result.success) {
        toast.success(`Transaction ${tradeData.side === 'buy' ? 'd\'achat' : 'de vente'} effectuée avec succès`);
        setShowTradeModal(false);
        setTradeData({ crypto_symbol: '', side: 'buy', quantity: '', price: '' });
        fetchPortfolioData(); // Refresh all data
      } else {
        toast.error(result.error);
      }
    } catch (error) {
      toast.error('Erreur lors de la transaction');
    }
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(price);
  };

  const formatPercent = (value) => {
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
  };

  const formatDate = (timestamp) => {
    return new Date(timestamp * 1000).toLocaleString();
  };

  if (loading) {
    return (
      <div className="portfolio-details-container">
        <div className="loading">Chargement des détails du portefeuille...</div>
      </div>
    );
  }

  if (!portfolio) {
    return (
      <div className="portfolio-details-container">
        <div className="error">Portefeuille non trouvé</div>
      </div>
    );
  }

  return (
    <div className="portfolio-details-container">
      <div className="portfolio-details-header">
        <button className="back-btn" onClick={() => navigate('/portfolio')}>
          ← Retour aux portefeuilles
        </button>
        <div className="header-content">
          <h1>{portfolio.name}</h1>
          <p>{portfolio.description}</p>
          <button 
            className="btn btn-primary"
            onClick={() => setShowTradeModal(true)}
          >
            + Trader
          </button>
        </div>
      </div>

      {/* Stats Overview */}
      {stats && (
        <div className="stats-overview">
          <div className="stat-card">
            <h3>Valeur Totale</h3>
            <p className="stat-value">{formatPrice(stats.total_value)}</p>
          </div>
          <div className="stat-card">
            <h3>Liquidités</h3>
            <p className="stat-value">{formatPrice(stats.cash_balance)}</p>
          </div>
          <div className="stat-card">
            <h3>Investissement</h3>
            <p className="stat-value">{formatPrice(stats.total_invested)}</p>
          </div>
          <div className="stat-card">
            <h3>P&L Total</h3>
            <p className={`stat-value ${stats.total_pnl >= 0 ? 'positive' : 'negative'}`}>
              {formatPrice(stats.total_pnl)} ({formatPercent(stats.total_pnl_percent)})
            </p>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="tabs">
        <button 
          className={`tab ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          Aperçu
        </button>
        <button 
          className={`tab ${activeTab === 'positions' ? 'active' : ''}`}
          onClick={() => setActiveTab('positions')}
        >
          Positions ({positions.length})
        </button>
        <button 
          className={`tab ${activeTab === 'transactions' ? 'active' : ''}`}
          onClick={() => setActiveTab('transactions')}
        >
          Transactions ({transactions.length})
        </button>
        <button 
          className={`tab ${activeTab === 'allocation' ? 'active' : ''}`}
          onClick={() => setActiveTab('allocation')}
        >
          Allocation
        </button>
        <button 
          className={`tab ${activeTab === 'performance' ? 'active' : ''}`}
          onClick={() => setActiveTab('performance')}
        >
          Performance
        </button>
      </div>

      {/* Tab Content */}
      <div className="tab-content">
        {activeTab === 'overview' && (
          <div className="overview-tab">
            {allocation && (
              <div className="allocation-chart">
                <h3>Allocation du portefeuille</h3>
                <div className="allocation-items">
                  {allocation.allocation.map((item, index) => (
                    <div key={index} className="allocation-item">
                      <div className="allocation-bar" style={{ width: `${item.percentage}%` }}></div>
                      <span>{item.crypto_symbol}: {item.percentage.toFixed(1)}%</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            {performance && performance.performance.length > 0 && (
              <div className="performance-chart">
                <h3>Performance (30 jours)</h3>
                <div className="performance-points">
                  {performance.performance.map((point, index) => (
                    <div key={index} className="performance-point">
                      <span>{formatDate(point.date)}</span>
                      <span className={point.portfolio_value >= stats.total_invested ? 'positive' : 'negative'}>
                        {formatPrice(point.portfolio_value)}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'positions' && (
          <div className="positions-tab">
            {positions.length === 0 ? (
              <div className="empty-state">
                <p>Aucune position dans ce portefeuille</p>
              </div>
            ) : (
              <div className="positions-table">
                <table>
                  <thead>
                    <tr>
                      <th>Crypto</th>
                      <th>Quantité</th>
                      <th>Prix Moyen</th>
                      <th>Prix Actuel</th>
                      <th>Valeur</th>
                      <th>P&L</th>
                    </tr>
                  </thead>
                  <tbody>
                    {positions.map((position, index) => (
                      <tr key={index}>
                        <td>{position.crypto_symbol}</td>
                        <td>{position.quantity}</td>
                        <td>{formatPrice(position.average_price)}</td>
                        <td>{formatPrice(position.current_price)}</td>
                        <td>{formatPrice(position.quantity * position.current_price)}</td>
                        <td className={position.unrealized_pnl >= 0 ? 'positive' : 'negative'}>
                          {formatPrice(position.unrealized_pnl)} ({formatPercent(position.unrealized_pnl_percent)})
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {activeTab === 'transactions' && (
          <div className="transactions-tab">
            {transactions.length === 0 ? (
              <div className="empty-state">
                <p>Aucune transaction dans ce portefeuille</p>
              </div>
            ) : (
              <div className="transactions-table">
                <table>
                  <thead>
                    <tr>
                      <th>Date</th>
                      <th>Type</th>
                      <th>Crypto</th>
                      <th>Quantité</th>
                      <th>Prix</th>
                      <th>Total</th>
                    </tr>
                  </thead>
                  <tbody>
                    {transactions.map((transaction, index) => (
                      <tr key={index}>
                        <td>{formatDate(transaction.timestamp)}</td>
                        <td className={transaction.side === 'buy' ? 'buy' : 'sell'}>
                          {transaction.side === 'buy' ? 'Achat' : 'Vente'}
                        </td>
                        <td>{transaction.crypto_symbol}</td>
                        <td>{transaction.quantity}</td>
                        <td>{formatPrice(transaction.price)}</td>
                        <td>{formatPrice(transaction.total)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {activeTab === 'allocation' && allocation && (
          <div className="allocation-tab">
            <h3>Détail de l'allocation</h3>
            <div className="allocation-details">
              {allocation.allocation.map((item, index) => (
                <div key={index} className="allocation-detail-item">
                  <div className="allocation-header">
                    <span className="crypto-symbol">{item.crypto_symbol}</span>
                    <span className="allocation-percentage">{item.percentage.toFixed(1)}%</span>
                  </div>
                  <div className="allocation-values">
                    <span>Valeur: {formatPrice(item.value)}</span>
                    <span>Quantité: {item.quantity}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'performance' && performance && (
          <div className="performance-tab">
            <h3>Performance historique</h3>
            {performance.performance.length === 0 ? (
              <div className="empty-state">
                <p>Aucune donnée de performance disponible</p>
              </div>
            ) : (
              <div className="performance-table">
                <table>
                  <thead>
                    <tr>
                      <th>Date</th>
                      <th>Valeur Portefeuille</th>
                      <th>Investissement</th>
                      <th>P&L</th>
                    </tr>
                  </thead>
                  <tbody>
                    {performance.performance.map((point, index) => (
                      <tr key={index}>
                        <td>{formatDate(point.date)}</td>
                        <td>{formatPrice(point.portfolio_value)}</td>
                        <td>{formatPrice(point.total_invested)}</td>
                        <td className={point.portfolio_value >= point.total_invested ? 'positive' : 'negative'}>
                          {formatPrice(point.portfolio_value - point.total_invested)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Trade Modal */}
      {showTradeModal && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="modal-header">
              <h2>Trader - {portfolio.name}</h2>
              <button className="close-btn" onClick={() => setShowTradeModal(false)}>×</button>
            </div>
            <form onSubmit={handleTrade}>
              <div className="form-group">
                <label>Type de transaction*</label>
                <select
                  value={tradeData.side}
                  onChange={(e) => setTradeData({...tradeData, side: e.target.value})}
                >
                  <option value="buy">Achat</option>
                  <option value="sell">Vente</option>
                </select>
              </div>
              <div className="form-group">
                <label>Symbole de la crypto*</label>
                <input
                  type="text"
                  value={tradeData.crypto_symbol}
                  onChange={(e) => setTradeData({...tradeData, crypto_symbol: e.target.value.toUpperCase()})}
                  placeholder="BTC, ETH, etc."
                  required
                />
              </div>
              <div className="form-group">
                <label>Quantité*</label>
                <input
                  type="number"
                  value={tradeData.quantity}
                  onChange={(e) => setTradeData({...tradeData, quantity: e.target.value})}
                  min="0"
                  step="0.00000001"
                  required
                />
              </div>
              <div className="form-group">
                <label>Prix par unité (USD)*</label>
                <input
                  type="number"
                  value={tradeData.price}
                  onChange={(e) => setTradeData({...tradeData, price: e.target.value})}
                  min="0"
                  step="0.01"
                  required
                />
              </div>
              <div className="trade-summary">
                <p>Total: {formatPrice((parseFloat(tradeData.quantity) || 0) * (parseFloat(tradeData.price) || 0))}</p>
              </div>
              <div className="modal-actions">
                <button type="button" className="btn btn-secondary" onClick={() => setShowTradeModal(false)}>
                  Annuler
                </button>
                <button type="submit" className="btn btn-primary">
                  {tradeData.side === 'buy' ? 'Acheter' : 'Vendre'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default PortfolioDetails;
