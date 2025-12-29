import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import virtualPortfolioService from '../services/virtualPortfolioService';
import './VirtualPortfolio.css';

const VirtualPortfolioList = () => {
  const navigate = useNavigate();

  const [portfolios, setPortfolios] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newPortfolioName, setNewPortfolioName] = useState('');
  const [creating, setCreating] = useState(false);

  const fetchPortfolios = async () => {
    setError(null);
    try {
      const res = await virtualPortfolioService.getAllPortfolios();
      if (res.success) {
        setPortfolios(res.data?.portfolios || []);
      } else {
        setError(res.error || 'Erreur lors du chargement');
      }
    } catch (e) {
      setError("Erreur lors du chargement");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPortfolios();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleCreatePortfolio = async (e) => {
    e.preventDefault();

    if (!newPortfolioName.trim()) {
      alert('Veuillez saisir un nom de portfolio');
      return;
    }

    setCreating(true);
    try {
      const res = await virtualPortfolioService.createPortfolio(newPortfolioName);
      if (res.success) {
        alert('Portfolio créé avec succès ! 🎉');
        setShowCreateModal(false);
        setNewPortfolioName('');
        setLoading(true);
        await fetchPortfolios();
      } else {
        alert(res.error || 'Erreur lors de la création');
      }
    } catch (err) {
      alert("Erreur lors de la création");
    } finally {
      setCreating(false);
    }
  };

  const handleDeletePortfolio = async (portfolioId, portfolioName) => {
    const ok = window.confirm(`Supprimer le portfolio "${portfolioName}" ?`);
    if (!ok) return;

    const res = await virtualPortfolioService.deletePortfolio(portfolioId);
    if (res.success) {
      alert('Portfolio supprimé');
      setLoading(true);
      fetchPortfolios();
    } else {
      alert(res.error || 'Erreur lors de la suppression');
    }
  };

  const formatCurrency = (value) => {
    const v = Number(value);
    const safe = Number.isFinite(v) ? v : 0;
    return new Intl.NumberFormat('fr-FR', {
      style: 'currency',
      currency: 'USD'
    }).format(safe);
  };

  const formatPercent = (value) => {
    const v = Number(value);
    const safe = Number.isFinite(v) ? v : 0;
    const sign = safe >= 0 ? '+' : '';
    return `${sign}${safe.toFixed(2)}%`;
  };

  return (
    <div className="virtual-portfolio-container">
      <header className="portfolio-header">
        <div className="portfolio-title">
          <span className="emoji">💼</span>
          <h1>Mes Portfolios Virtuels</h1>
        </div>
        <button className="btn-create-portfolio" onClick={() => setShowCreateModal(true)}>
          ➕ Créer un Portfolio
        </button>
      </header>

      {loading && <div className="loading">⏳ Chargement...</div>}

      {error && <div className="error-message">❌ {error}</div>}

      {!loading && !error && portfolios.length === 0 && (
        <div className="empty-state">
          <div className="empty-icon">📊</div>
          <h3>Aucun portfolio</h3>
          <p>Créez votre premier portfolio virtuel pour commencer à simuler vos investissements crypto !</p>
        </div>
      )}

      {!loading && !error && portfolios.length > 0 && (
        <div className="portfolios-grid">
          {portfolios.map((portfolio) => (
            <div key={portfolio.portfolio_id} className="portfolio-card">
              <div className="portfolio-card-header">
                <h3>{portfolio.name}</h3>
                <div className="portfolio-actions">
                  <button
                    className="btn-view"
                    onClick={() => navigate(`/virtual-portfolio/${portfolio.portfolio_id}`)}
                    title="Voir les détails"
                  >
                    👁️
                  </button>
                  <button
                    className="btn-delete"
                    onClick={() => handleDeletePortfolio(portfolio.portfolio_id, portfolio.name)}
                    title="Supprimer"
                  >
                    🗑️
                  </button>
                </div>
              </div>

              <div className="portfolio-card-body">
                <div className="portfolio-stat">
                  <span className="stat-label">Valeur actuelle</span>
                  <span className="stat-value">{formatCurrency(portfolio.total_value_usd)}</span>
                </div>
                <div className="portfolio-stat">
                  <span className="stat-label">Investi</span>
                  <span className="stat-value">{formatCurrency(portfolio.total_invested_usd)}</span>
                </div>
                <div className="portfolio-stat">
                  <span className="stat-label">Profit/Loss</span>
                  <span className={`stat-value ${Number(portfolio.profit_loss_usd) >= 0 ? 'positive' : 'negative'}`}>
                    {formatCurrency(portfolio.profit_loss_usd)}
                    <span className="percent">({formatPercent(portfolio.profit_loss_percent)})</span>
                  </span>
                </div>
                <div className="portfolio-stat">
                  <span className="stat-label">Cryptos détenues</span>
                  <span className="stat-value">{Object.keys(portfolio.holdings || {}).length}</span>
                </div>
              </div>

              <div className="portfolio-card-footer">
                <span className="portfolio-date">
                  Créé le {portfolio.created_at ? new Date(portfolio.created_at).toLocaleDateString('fr-FR') : '-'}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {showCreateModal && (
        <div className="modal-overlay" onClick={() => setShowCreateModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h3>➕ Créer un nouveau portfolio</h3>
            <form onSubmit={handleCreatePortfolio}>
              <div className="form-group">
                <label>Nom du portfolio *</label>
                <input
                  type="text"
                  value={newPortfolioName}
                  onChange={(e) => setNewPortfolioName(e.target.value)}
                  placeholder="Ex: Mon Portfolio BTC/ETH"
                  required
                  autoFocus
                  disabled={creating}
                />
              </div>
              <div className="modal-actions">
                <button
                  type="button"
                  className="btn-cancel"
                  onClick={() => setShowCreateModal(false)}
                  disabled={creating}
                >
                  Annuler
                </button>
                <button type="submit" className="btn-confirm" disabled={creating || !newPortfolioName.trim()}>
                  {creating ? '⏳ Création...' : '✅ Créer'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default VirtualPortfolioList;
