// Alerts.js - Gestion des alertes de prix

import React, { useState, useEffect, useCallback } from 'react';
import alertService from '../services/alertService';
import analyticsService from '../services/analyticsService';
import './Alerts.css';

const Alerts = () => {
  // State
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('all'); // 'all', 'active', 'triggered'
  const [toast, setToast] = useState(null);
  const [deleteModal, setDeleteModal] = useState({ show: false, alertId: null });
  const [formLoading, setFormLoading] = useState(false);
  const [cryptoOptions, setCryptoOptions] = useState([]);
  const [loadingCryptos, setLoadingCryptos] = useState(true);

  // Form state
  const [formData, setFormData] = useState({
    crypto_symbol: 'BTC',
    target_price: '',
    alert_type: 'above'
  });

  // Stats
  const [stats, setStats] = useState({
    total: 0,
    active: 0,
    triggered: 0
  });

  // Show toast notification
  const showToast = (message, type = 'success') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 4000);
  };

  // Fetch alerts
  const fetchAlerts = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const result = await alertService.getAllAlerts();

      if (result.success) {
        const alertsData = result.data.alerts || [];
        setAlerts(alertsData);

        // Calculate stats
        const activeCount = alertsData.filter(a => a.is_active).length;
        const triggeredCount = alertsData.filter(a => !a.is_active && a.triggered_at).length;
        setStats({
          total: alertsData.length,
          active: activeCount,
          triggered: triggeredCount
        });
      } else {
        setError(result.error);
      }
    } catch (err) {
      setError('Erreur de connexion au serveur');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAlerts();
  }, [fetchAlerts]);

  // Charger les cryptos disponibles depuis la DB
  useEffect(() => {
    const loadCryptos = async () => {
      setLoadingCryptos(true);
      const result = await analyticsService.getAvailableCryptos();
      if (result.success && result.data.cryptos) {
        const options = result.data.cryptos.map(crypto => ({
          value: crypto.symbol,
          label: `${crypto.name} (${crypto.symbol})`
        }));
        setCryptoOptions(options);
      }
      setLoadingCryptos(false);
    };
    loadCryptos();
  }, []);

  // Handle form input change
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  // Create alert
  const handleCreateAlert = async (e) => {
    e.preventDefault();

    // Validation
    const price = parseFloat(formData.target_price);
    if (!price || price <= 0) {
      showToast('Le prix cible doit être supérieur à 0', 'error');
      return;
    }

    setFormLoading(true);

    try {
      const result = await alertService.createAlert({
        crypto_symbol: formData.crypto_symbol,
        target_price: price,
        alert_type: formData.alert_type
      });

      if (result.success) {
        showToast(`Alerte ${formData.crypto_symbol} créée avec succès! 🔔`, 'success');
        setFormData({ crypto_symbol: 'BTC', target_price: '', alert_type: 'above' });
        fetchAlerts();
      } else {
        showToast(result.error, 'error');
      }
    } catch (err) {
      showToast('Erreur lors de la création', 'error');
    } finally {
      setFormLoading(false);
    }
  };

  // Delete alert
  const handleDeleteAlert = async () => {
    if (!deleteModal.alertId) return;

    try {
      const result = await alertService.deleteAlert(deleteModal.alertId);

      if (result.success) {
        showToast('Alerte supprimée avec succès', 'success');
        fetchAlerts();
      } else {
        showToast(result.error, 'error');
      }
    } catch (err) {
      showToast('Erreur lors de la suppression', 'error');
    } finally {
      setDeleteModal({ show: false, alertId: null });
    }
  };

  // Toggle alert active status
  const handleToggleAlert = async (alertId, currentStatus) => {
    try {
      const result = await alertService.updateAlert(alertId, {
        is_active: !currentStatus
      });

      if (result.success) {
        showToast(
          currentStatus ? 'Alerte désactivée' : 'Alerte réactivée',
          'success'
        );
        fetchAlerts();
      } else {
        showToast(result.error, 'error');
      }
    } catch (err) {
      showToast('Erreur lors de la mise à jour', 'error');
    }
  };

  // Filter alerts
  const filteredAlerts = alerts.filter(alert => {
    if (filter === 'active') return alert.is_active;
    if (filter === 'triggered') return !alert.is_active && alert.triggered_at;
    return true;
  });

  // Sort by created_at (most recent first)
  const sortedAlerts = [...filteredAlerts].sort((a, b) => 
    new Date(b.created_at) - new Date(a.created_at)
  );

  // Format date
  const formatDate = (dateString) => {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('fr-FR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // Format price
  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(price);
  };

  return (
    <div className="alerts-container">
      {/* Toast Notification */}
      {toast && (
        <div className={`toast toast-${toast.type}`} style={{
          position: 'fixed',
          top: '100px',
          right: '20px',
          padding: '16px 24px',
          borderRadius: '12px',
          background: toast.type === 'success' ? '#22c55e' : '#ef4444',
          color: 'white',
          fontWeight: '600',
          zIndex: 1001,
          animation: 'fadeInUp 0.3s ease-out',
          boxShadow: '0 4px 20px rgba(0,0,0,0.2)'
        }}>
          {toast.message}
        </div>
      )}

      {/* Header */}
      <header className="alerts-header">
        <div className="alerts-title">
          <span className="emoji">🔔</span>
          <h1>Mes Alertes</h1>
        </div>
        <p className="subtitle">Gérez vos alertes de prix personnalisées</p>
      </header>

      {/* Stats */}
      <div className="alerts-stats">
        <div className="stat-card total">
          <div className="stat-icon">📊</div>
          <div className="stat-value">{stats.total}</div>
          <div className="stat-label">Total</div>
        </div>
        <div className="stat-card active">
          <div className="stat-icon">🔔</div>
          <div className="stat-value">{stats.active}</div>
          <div className="stat-label">Actives</div>
        </div>
        <div className="stat-card triggered">
          <div className="stat-icon">✅</div>
          <div className="stat-value">{stats.triggered}</div>
          <div className="stat-label">Déclenchées</div>
        </div>
      </div>

      {/* Create Alert Form */}
      <section className="create-alert-section">
        <h2>➕ Créer une nouvelle alerte</h2>
        <form className="alert-form" onSubmit={handleCreateAlert}>
          <div className="form-group">
            <label>Cryptomonnaie</label>
            <select
              name="crypto_symbol"
              value={formData.crypto_symbol}
              onChange={handleInputChange}
              disabled={loadingCryptos}
            >
              {loadingCryptos ? (
                <option>Chargement...</option>
              ) : cryptoOptions.length === 0 ? (
                <option>Aucune crypto disponible</option>
              ) : (
                cryptoOptions.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))
              )}
            </select>
          </div>

          <div className="form-group">
            <label>Prix cible (USD)</label>
            <input
              type="number"
              name="target_price"
              value={formData.target_price}
              onChange={handleInputChange}
              placeholder="Ex: 50000"
              min="0"
              step="0.01"
              required
            />
          </div>

          <div className="form-group">
            <label>Type d'alerte</label>
            <select
              name="alert_type"
              value={formData.alert_type}
              onChange={handleInputChange}
            >
              <option value="above">📈 Au-dessus de</option>
              <option value="below">📉 En-dessous de</option>
            </select>
          </div>

          <button type="submit" className="btn-create" disabled={formLoading}>
            {formLoading ? '⏳ Création...' : '🔔 Créer l\'alerte'}
          </button>
        </form>
      </section>

      {/* Filters */}
      <div className="filters-section">
        <button
          className={`filter-btn ${filter === 'all' ? 'active' : ''}`}
          onClick={() => setFilter('all')}
        >
          📋 Toutes <span className="count">{stats.total}</span>
        </button>
        <button
          className={`filter-btn ${filter === 'active' ? 'active' : ''}`}
          onClick={() => setFilter('active')}
        >
          🔔 Actives <span className="count">{stats.active}</span>
        </button>
        <button
          className={`filter-btn ${filter === 'triggered' ? 'active' : ''}`}
          onClick={() => setFilter('triggered')}
        >
          ✅ Déclenchées <span className="count">{stats.triggered}</span>
        </button>
      </div>

      {/* Error Message */}
      {error && (
        <div className="error-message">
          ❌ {error}
        </div>
      )}

      {/* Loading */}
      {loading && (
        <div className="loading-container">
          <div className="spinner"></div>
          <p className="loading-text">Chargement des alertes...</p>
        </div>
      )}

      {/* Alerts List */}
      {!loading && !error && (
        <>
          {sortedAlerts.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">🔕</div>
              <h3>Aucune alerte</h3>
              <p>
                {filter === 'all'
                  ? 'Créez votre première alerte de prix ci-dessus'
                  : filter === 'active'
                  ? 'Aucune alerte active pour le moment'
                  : 'Aucune alerte déclenchée'}
              </p>
            </div>
          ) : (
            <div className="alerts-list">
              {sortedAlerts.map(alert => (
                <div
                  key={alert.id}
                  className={`alert-card ${alert.is_active ? 'active' : 'triggered'}`}
                >
                  <div className="alert-card-header">
                    <div className="alert-crypto">
                      <div className="crypto-icon">
                        {alert.crypto_symbol.substring(0, 2)}
                      </div>
                      <div className="crypto-info">
                        <h3>{alert.crypto_symbol}</h3>
                        <span className={`alert-type ${alert.alert_type}`}>
                          {alert.alert_type === 'above' ? '📈 Au-dessus de' : '📉 En-dessous de'}
                        </span>
                      </div>
                    </div>
                    <div className={`alert-status ${alert.is_active ? 'active' : 'triggered'}`}>
                      {alert.is_active ? '🔔 Active' : '✅ Déclenchée'}
                    </div>
                  </div>

                  <div className="alert-card-body">
                    <div className="alert-detail">
                      <span className="label">Prix cible</span>
                      <span className="value price">{formatPrice(alert.target_price)}</span>
                    </div>
                    {alert.triggered_at && (
                      <div className="alert-detail">
                        <span className="label">Déclenchée le</span>
                        <span className="value">{formatDate(alert.triggered_at)}</span>
                      </div>
                    )}
                    <div className="alert-detail">
                      <span className="label">Créée le</span>
                      <span className="value">{formatDate(alert.created_at)}</span>
                    </div>
                  </div>

                  <div className="alert-card-footer">
                    <span className="alert-date">
                      🆔 {alert.id.substring(0, 8)}...
                    </span>
                    <div className="alert-actions">
                      {alert.is_active && (
                        <button
                          className="btn-action toggle"
                          onClick={() => handleToggleAlert(alert.id, alert.is_active)}
                          title="Désactiver"
                        >
                          ⏸️ Pause
                        </button>
                      )}
                      {!alert.is_active && !alert.triggered_at && (
                        <button
                          className="btn-action toggle"
                          onClick={() => handleToggleAlert(alert.id, alert.is_active)}
                          title="Réactiver"
                        >
                          ▶️ Activer
                        </button>
                      )}
                      <button
                        className="btn-action delete"
                        onClick={() => setDeleteModal({ show: true, alertId: alert.id })}
                        title="Supprimer"
                      >
                        🗑️ Supprimer
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}

      {/* Delete Confirmation Modal */}
      {deleteModal.show && (
        <div className="modal-overlay" onClick={() => setDeleteModal({ show: false, alertId: null })} onKeyDown={(e) => e.key === 'Escape' && setDeleteModal({ show: false, alertId: null })} tabIndex={-1}>
          <div className="modal-content" onClick={e => e.stopPropagation()} onKeyDown={e => e.stopPropagation()} aria-modal="true">
            <h3>🗑️ Supprimer l'alerte ?</h3>
            <p>Cette action est irréversible. Voulez-vous vraiment supprimer cette alerte ?</p>
            <div className="modal-actions">
              <button
                className="btn-cancel"
                onClick={() => setDeleteModal({ show: false, alertId: null })}
              >
                Annuler
              </button>
              <button className="btn-confirm" onClick={handleDeleteAlert}>
                Supprimer
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Alerts;
