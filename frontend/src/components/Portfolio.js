import React, { useState, useEffect } from 'react';
import portfolioService from '../services/portfolioService';
import { toast } from './Toast';
import './Portfolio.css';

const Portfolio = () => {
  const [portfolios, setPortfolios] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showTradeModal, setShowTradeModal] = useState(false);
  const [selectedPortfolio, setSelectedPortfolio] = useState(null);
  const [portfolioStats, setPortfolioStats] = useState({});
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    initial_cash: 10000
  });
  const [tradeData, setTradeData] = useState({
    crypto_symbol: '',
    side: 'buy',
    quantity: '',
    price: ''
  });

  useEffect(() => {
    fetchPortfolios();
  }, []);

  const fetchPortfolios = async () => {
    setLoading(true);
    try {
      const result = await portfolioService.getPortfolios();
      if (result.success) {
        const portfoliosList = Array.isArray(result.data)
          ? result.data
          : (result.data.portfolios || []);

        setPortfolios(portfoliosList);
        // Fetch stats for each portfolio
        portfoliosList.forEach(async (portfolio) => {
          const statsResult = await portfolioService.getPortfolioStats(portfolio.id);
          if (statsResult.success) {
            setPortfolioStats(prev => ({
              ...prev,
              [portfolio.id]: statsResult.data
            }));
          }
        });
      } else {
        toast.error(result.error);
      }
    } catch (error) {
      toast.error('Erreur lors de la récupération des portefeuilles');
    } finally {
      setLoading(false);
    }
  };

  const handleCreatePortfolio = async (e) => {
    e.preventDefault();
    try {
      const result = await portfolioService.createPortfolio(formData);
      if (result.success) {
        toast.success('Portefeuille créé avec succès');
        setShowCreateModal(false);
        setFormData({ name: '', description: '', initial_cash: 10000 });
        fetchPortfolios();
      } else {
        toast.error(result.error);
      }
    } catch (error) {
      toast.error('Erreur lors de la création du portefeuille');
    }
  };

  const handleDeletePortfolio = async (portfolioId) => {
    if (!window.confirm('Êtes-vous sûr de vouloir supprimer ce portefeuille ?')) {
      return;
    }
    try {
      const result = await portfolioService.deletePortfolio(portfolioId);
      if (result.success) {
        toast.success('Portefeuille supprimé avec succès');
        fetchPortfolios();
      } else {
        toast.error(result.error);
      }
    } catch (error) {
      toast.error('Erreur lors de la suppression du portefeuille');
    }
  };

  const handleTrade = async (e) => {
    e.preventDefault();
    try {
      const result = await portfolioService.executeTrade(selectedPortfolio.id, tradeData);
      if (result.success) {
        toast.success(`Transaction ${tradeData.side === 'buy' ? 'd\'achat' : 'de vente'} effectuée avec succès`);
        setShowTradeModal(false);
        setTradeData({ crypto_symbol: '', side: 'buy', quantity: '', price: '' });
        fetchPortfolios();
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
    const num = Number(value);
    if (!Number.isFinite(num)) {
      return "0.00%";
    }
    return `${num >= 0 ? '+' : ''}${num.toFixed(2)}%`;
  };

  if (loading) {
    return (
      <div className="portfolio-container">
        <div className="loading">Chargement des portefeuilles...</div>
      </div>
    );
  }

  return (
    <div className="portfolio-container">
      <div className="portfolio-header">
        <h1>Mes Portefeuilles</h1>
        <button 
          className="btn btn-primary"
          onClick={() => setShowCreateModal(true)}
        >
          + Nouveau Portefeuille
        </button>
      </div>

      {portfolios.length === 0 ? (
        <div className="empty-state">
          <h3>Aucun portefeuille</h3>
          <p>Créez votre premier portefeuille pour commencer à investir</p>
          <button 
            className="btn btn-primary"
            onClick={() => setShowCreateModal(true)}
          >
            Créer un portefeuille
          </button>
        </div>
      ) : (
        <div className="portfolio-grid">
          {portfolios.map((portfolio) => {
            const stats = portfolioStats[portfolio.id];
            return (
              <div key={portfolio.id} className="portfolio-card">
                <div className="portfolio-card-header">
                  <h3>{portfolio.name}</h3>
                  <div className="portfolio-actions">
                    <button 
                      className="btn btn-sm btn-info"
                      onClick={() => {
                        setSelectedPortfolio(portfolio);
                        setShowTradeModal(true);
                      }}
                    >
                      Trader
                    </button>
                    <button 
                      className="btn btn-sm btn-primary"
                      onClick={() => window.location.href = `/portfolio/${portfolio.id}`}
                    >
                      Détails
                    </button>
                    <button 
                      className="btn btn-sm btn-danger"
                      onClick={() => handleDeletePortfolio(portfolio.id)}
                    >
                      Supprimer
                    </button>
                  </div>
                </div>
                
                <p className="portfolio-description">{portfolio.description}</p>
                
                {stats && (
                  <div className="portfolio-stats">
                    <div className="stat">
                      <span className="label">Valeur totale:</span>
                      <span className="value">{formatPrice(stats.total_value)}</span>
                    </div>
                    <div className="stat">
                      <span className="label">Liquidités:</span>
                      <span className="value">{formatPrice(stats.cash_balance)}</span>
                    </div>
                    <div className="stat">
                      <span className="label">Investissement:</span>
                      <span className="value">{formatPrice(stats.total_invested)}</span>
                    </div>
                    <div className="stat">
                      <span className="label">P&L:</span>
                      <span className={`value ${stats.total_pnl >= 0 ? 'positive' : 'negative'}`}>
                        {formatPrice(stats.total_pnl)} ({formatPercent(stats.total_pnl_percent)})
                      </span>
                    </div>
                    <div className="stat">
                      <span className="label">Positions:</span>
                      <span className="value">{stats.position_count}</span>
                    </div>
                  </div>
                )}
                
                <div className="portfolio-footer">
                  <small>Créé le {new Date(portfolio.created_at).toLocaleDateString()}</small>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Create Portfolio Modal */}
      {showCreateModal && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="modal-header">
              <h2>Nouveau Portefeuille</h2>
              <button className="close-btn" onClick={() => setShowCreateModal(false)}>×</button>
            </div>
            <form onSubmit={handleCreatePortfolio}>
              <div className="form-group">
                <label>Nom du portefeuille*</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                  placeholder="Ex: Portefeuille Long Terme"
                  required
                />
              </div>
              <div className="form-group">
                <label>Description</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({...formData, description: e.target.value})}
                  placeholder="Ex: Investissements BTC/ETH sur 2025, stratégie DCA"
                  rows="3"
                />
              </div>
              <div className="form-group">
                <label>Fonds initiaux (USD)*</label>
                <input
                  type="number"
                  value={formData.initial_cash}
                  onChange={(e) => setFormData({...formData, initial_cash: parseFloat(e.target.value)})}
                  placeholder="Ex: 10000"
                  min="0"
                  step="0.01"
                  required
                />
              </div>
              <div className="modal-actions">
                <button type="button" className="btn btn-secondary" onClick={() => setShowCreateModal(false)}>
                  Annuler
                </button>
                <button type="submit" className="btn btn-primary">
                  Créer
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Trade Modal */}
      {showTradeModal && selectedPortfolio && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="modal-header">
              <h2>Trader - {selectedPortfolio.name}</h2>
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

export default Portfolio;
