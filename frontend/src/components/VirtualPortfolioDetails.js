import React, { useCallback, useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import virtualPortfolioService from '../services/virtualPortfolioService';
import { toast } from './Toast';
import './VirtualPortfolio.css';

const VirtualPortfolioDetails = () => {
  const { portfolioId } = useParams();
  const navigate = useNavigate();

  const [portfolio, setPortfolio] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showTransactionModal, setShowTransactionModal] = useState(false);
  const [transactionForm, setTransactionForm] = useState({
    transaction_type: 'BUY',
    crypto_symbol: '',
    quantity: '',
    price_usd: '',
    notes: ''
  });
  const [availableCryptos, setAvailableCryptos] = useState([]);
  const [loadingPrice, setLoadingPrice] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [filterType, setFilterType] = useState('ALL');

  const resetTransactionForm = () => {
    setTransactionForm({
      transaction_type: 'BUY',
      crypto_symbol: '',
      quantity: '',
      price_usd: '',
      notes: ''
    });
  };

  const fetchPortfolioData = async () => {
    setLoading(true);
    setError(null);

    try {
      const [portfolioRes, txRes] = await Promise.all([
        virtualPortfolioService.getPortfolio(portfolioId),
        virtualPortfolioService.getTransactions(portfolioId)
      ]);

      if (!portfolioRes.success) {
        const msg = portfolioRes.error || 'Erreur lors du chargement du portfolio';
        if (
          msg.toLowerCase().includes('accès refusé') ||
          msg.toLowerCase().includes('ressource non trouvée') ||
          msg.toLowerCase().includes('portfolio non trouvé')
        ) {
          alert(msg);
          navigate('/virtual-portfolio');
          return;
        }
        setError(msg);
        return;
      }

      if (!txRes.success) {
        const msg = txRes.error || 'Erreur lors du chargement des transactions';
        if (
          msg.toLowerCase().includes('accès refusé') ||
          msg.toLowerCase().includes('ressource non trouvée')
        ) {
          alert(msg);
          navigate('/virtual-portfolio');
          return;
        }
        setError(msg);
        return;
      }

      setPortfolio(portfolioRes.data);
      setTransactions(txRes.data?.transactions || []);
    } catch (e) {
      setError("Erreur lors du chargement");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPortfolioData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [portfolioId]);

  const loadAvailableCryptos = useCallback(async () => {
    const result = await virtualPortfolioService.getAvailableCryptos();
    if (result.success) {
      setAvailableCryptos(result.data?.cryptos || []);
      return;
    }
    setAvailableCryptos([]);
  }, []);

  useEffect(() => {
    loadAvailableCryptos();
  }, [loadAvailableCryptos]);

  const handleCryptoSelect = async (symbol) => {
    const normalized = String(symbol || '').toUpperCase().trim();
    if (!normalized) {
      setTransactionForm((prev) => ({ ...prev, crypto_symbol: '', price_usd: '' }));
      return;
    }

    setTransactionForm((prev) => ({ ...prev, crypto_symbol: normalized }));
    setLoadingPrice(true);

    const result = await virtualPortfolioService.getCryptoPrice(normalized);
    if (result.success) {
      const raw = result.data?.price_usd;
      const numeric = Number(raw);
      if (Number.isFinite(numeric)) {
        setTransactionForm((prev) => ({ ...prev, price_usd: numeric.toFixed(2) }));
        toast.success(`Prix actuel de ${normalized}: $${numeric.toFixed(2)}`);
      } else {
        setTransactionForm((prev) => ({ ...prev, price_usd: '' }));
        toast.error(`Prix invalide pour ${normalized}`);
      }
    } else {
      setTransactionForm((prev) => ({ ...prev, price_usd: '' }));
      toast.error(result.error || `Impossible de récupérer le prix de ${normalized}`);
    }

    setLoadingPrice(false);
  };

  const handleRefreshPerformance = async () => {
    const res = await virtualPortfolioService.getPerformance(portfolioId);
    if (res.success) {
      setPortfolio(res.data);
      alert('Performance actualisée ! 📊');
    } else {
      alert(res.error || 'Erreur lors de la mise à jour');
    }
  };

  const handleTransactionSubmit = async (e) => {
    e.preventDefault();

    if (!transactionForm.crypto_symbol || !transactionForm.quantity || !transactionForm.price_usd) {
      alert('Veuillez remplir tous les champs obligatoires');
      return;
    }

    const qty = parseFloat(transactionForm.quantity);
    const price = parseFloat(transactionForm.price_usd);

    if (!Number.isFinite(qty) || qty <= 0) {
      alert('Quantité invalide');
      return;
    }

    if (!Number.isFinite(price) || price <= 0) {
      alert('Prix invalide');
      return;
    }

    setSubmitting(true);
    try {
      const payload = {
        transaction_type: transactionForm.transaction_type,
        crypto_symbol: transactionForm.crypto_symbol.toUpperCase(),
        quantity: qty,
        price_usd: price,
        notes: transactionForm.notes
      };

      const res = await virtualPortfolioService.createTransaction(portfolioId, payload);
      if (res.success) {
        alert(`Transaction ${transactionForm.transaction_type} effectuée ! 🎉`);
        setShowTransactionModal(false);
        resetTransactionForm();
        await fetchPortfolioData();
      } else {
        alert(res.error || 'Erreur lors de la transaction');
      }
    } catch (err) {
      alert('Erreur lors de la transaction');
    } finally {
      setSubmitting(false);
    }
  };

  const handleFilterChange = async (type) => {
    setFilterType(type);

    const filter = type === 'ALL' ? null : type;
    const res = await virtualPortfolioService.getTransactions(portfolioId, filter);

    if (res.success) {
      setTransactions(res.data?.transactions || []);
    } else {
      alert(res.error || 'Erreur lors du filtrage');
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

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('fr-FR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const totalPreview = (() => {
    const qty = parseFloat(transactionForm.quantity);
    const price = parseFloat(transactionForm.price_usd);
    if (!Number.isFinite(qty) || !Number.isFinite(price)) return null;
    return qty * price;
  })();

  return (
    <div className="virtual-portfolio-details">
      <button className="btn-back" onClick={() => navigate('/virtual-portfolio')}>
        ← Retour à mes portfolios
      </button>

      {loading && <div className="loading">⏳ Chargement...</div>}

      {error && <div className="error-message">❌ {error}</div>}

      {!loading && portfolio && (
        <>
          <div className="portfolio-details-header">
            <div className="portfolio-info">
              <h1>{portfolio.name}</h1>
              <p className="portfolio-id">ID: {String(portfolio.portfolio_id || '').substring(0, 8)}...</p>
            </div>
            <div className="portfolio-actions-header">
              <button className="btn-refresh" onClick={handleRefreshPerformance}>
                🔄 Actualiser les performances
              </button>
              <button className="btn-transaction" onClick={() => setShowTransactionModal(true)}>
                ➕ Nouvelle Transaction
              </button>
            </div>
          </div>

          <div className="portfolio-stats-cards">
            <div className="stat-card-details">
              <div className="stat-label">Valeur actuelle</div>
              <div className="stat-value-large">{formatCurrency(portfolio.total_value_usd)}</div>
            </div>
            <div className="stat-card-details">
              <div className="stat-label">Investi</div>
              <div className="stat-value-large">{formatCurrency(portfolio.total_invested_usd)}</div>
            </div>
            <div className="stat-card-details">
              <div className="stat-label">Profit/Loss</div>
              <div className={`stat-value-large ${Number(portfolio.profit_loss_usd) >= 0 ? 'positive' : 'negative'}`}>
                {formatCurrency(portfolio.profit_loss_usd)}
                <div className="stat-percent">{formatPercent(portfolio.profit_loss_percent)}</div>
              </div>
            </div>
          </div>

          <div className="holdings-section">
            <h2>💼 Cryptos détenues</h2>
            {Object.keys(portfolio.holdings || {}).length === 0 ? (
              <p className="empty-holdings">Aucune crypto dans ce portfolio. Faites votre premier achat !</p>
            ) : (
              <div className="holdings-grid">
                {Object.entries(portfolio.holdings || {}).map(([symbol, quantity]) => (
                  <div key={symbol} className="holding-card">
                    <div className="holding-symbol">{symbol}</div>
                    <div className="holding-quantity">{Number(quantity).toFixed(8)}</div>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="transactions-section">
            <div className="transactions-header">
              <h2>📜 Historique des transactions</h2>
              <div className="transactions-filters">
                <button
                  className={`filter-btn ${filterType === 'ALL' ? 'active' : ''}`}
                  onClick={() => handleFilterChange('ALL')}
                >
                  Toutes
                </button>
                <button
                  className={`filter-btn ${filterType === 'BUY' ? 'active' : ''}`}
                  onClick={() => handleFilterChange('BUY')}
                >
                  📈 Achats
                </button>
                <button
                  className={`filter-btn ${filterType === 'SELL' ? 'active' : ''}`}
                  onClick={() => handleFilterChange('SELL')}
                >
                  📉 Ventes
                </button>
              </div>
            </div>

            {transactions.length === 0 ? (
              <p className="empty-transactions">Aucune transaction pour le moment.</p>
            ) : (
              <div className="transactions-list">
                {transactions.map((tx) => (
                  <div
                    key={tx.transaction_id}
                    className={`transaction-item ${String(tx.transaction_type || '').toLowerCase()}`}
                  >
                    <div className="transaction-icon">{tx.transaction_type === 'BUY' ? '📈' : '📉'}</div>
                    <div className="transaction-info">
                      <div className="transaction-main">
                        <span className="transaction-type">{tx.transaction_type}</span>
                        <span className="transaction-crypto">{tx.crypto_symbol}</span>
                        <span className="transaction-quantity">{tx.quantity}</span>
                        <span className="transaction-price">@ {formatCurrency(tx.price_usd)}</span>
                      </div>
                      <div className="transaction-details">
                        <span className="transaction-total">Total: {formatCurrency(tx.total_usd)}</span>
                        <span className="transaction-date">{formatDate(tx.timestamp)}</span>
                      </div>
                      {tx.notes && <div className="transaction-notes">📝 {tx.notes}</div>}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </>
      )}

      {showTransactionModal && (
        <div className="modal-overlay" onClick={() => setShowTransactionModal(false)} onKeyDown={(e) => e.key === 'Escape' && setShowTransactionModal(false)} tabIndex={-1}>
          <div className="modal-content modal-large" onClick={(e) => e.stopPropagation()} onKeyDown={(e) => e.stopPropagation()} aria-modal="true">
            <h3>➕ Nouvelle Transaction</h3>
            <form onSubmit={handleTransactionSubmit}>
              <div className="form-group">
                <label>Type de transaction *</label>
                <select
                  value={transactionForm.transaction_type}
                  onChange={(e) =>
                    setTransactionForm({
                      ...transactionForm,
                      transaction_type: e.target.value
                    })
                  }
                  disabled={submitting}
                >
                  <option value="BUY">📈 Achat (BUY)</option>
                  <option value="SELL">📉 Vente (SELL)</option>
                </select>
              </div>

              <div className="form-group">
                <label>Crypto (symbole) *</label>
                <select
                  name="crypto_symbol"
                  value={transactionForm.crypto_symbol}
                  onChange={(e) => handleCryptoSelect(e.target.value)}
                  required
                  disabled={submitting || loadingPrice}
                >
                  <option value="">-- Sélectionnez une crypto --</option>
                  {availableCryptos.map((crypto) => (
                    <option key={crypto.symbol} value={crypto.symbol}>
                      {crypto.symbol} - {crypto.name} (${Number(crypto.price_usd || 0).toFixed(2)})
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>Quantité *</label>
                  <input
                    type="number"
                    step="0.00000001"
                    value={transactionForm.quantity}
                    onChange={(e) => setTransactionForm({ ...transactionForm, quantity: e.target.value })}
                    placeholder="0.00"
                    required
                    min="0.00000001"
                    disabled={submitting}
                  />
                </div>

                <div className="form-group">
                  <label>Prix unitaire (USD) *</label>
                  <input
                    type="number"
                    step="0.01"
                    value={transactionForm.price_usd}
                    placeholder={loadingPrice ? '⏳ Chargement du prix...' : 'Prix automatique'}
                    required
                    min="0.01"
                    readOnly
                    disabled={submitting || loadingPrice}
                    style={{
                      backgroundColor: 'var(--bg-secondary)',
                      cursor: 'not-allowed',
                      opacity: loadingPrice ? 0.6 : 1
                    }}
                  />
                  {loadingPrice && (
                    <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                      ⏳ Récupération du prix en cours...
                    </span>
                  )}
                </div>
              </div>

              <div className="form-group">
                <label>Notes (optionnel)</label>
                <textarea
                  value={transactionForm.notes}
                  onChange={(e) => setTransactionForm({ ...transactionForm, notes: e.target.value })}
                  placeholder="Ajouter une note sur cette transaction..."
                  rows="3"
                  maxLength="500"
                  disabled={submitting}
                />
              </div>

              {transactionForm.quantity && transactionForm.price_usd && totalPreview !== null && (
                <div className="transaction-total-preview">Total: {formatCurrency(totalPreview)}</div>
              )}

              <div className="modal-actions">
                <button
                  type="button"
                  className="btn-cancel"
                  onClick={() => {
                    setShowTransactionModal(false);
                    resetTransactionForm();
                  }}
                  disabled={submitting}
                >
                  Annuler
                </button>
                <button
                  type="submit"
                  className="btn-confirm"
                  disabled={
                    submitting ||
                    !transactionForm.crypto_symbol ||
                    !transactionForm.quantity ||
                    !transactionForm.price_usd
                  }
                >
                  {submitting ? '⏳ Traitement...' : '✅ Valider'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default VirtualPortfolioDetails;
