// frontend/src/components/Admin/AdminAlerts.js

import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getAllAlerts, disableAllAlerts, deleteAlert } from '../../services/adminService';
import './Admin.css';

const AdminAlerts = () => {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filterActive, setFilterActive] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [actionLoading, setActionLoading] = useState(false);

  useEffect(() => {
    loadAlerts();
  }, []);

  const loadAlerts = async () => {
    setLoading(true);
    try {
      const data = await getAllAlerts(0, 200);
      setAlerts(data.alerts || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDisableAll = async () => {
    if (!window.confirm('⚠️ Désactiver TOUTES les alertes actives ?')) return;
    setActionLoading(true);
    try {
      const result = await disableAllAlerts();
      alert(`✅ ${result.disabled_count} alertes désactivées`);
      await loadAlerts();
    } catch (err) {
      alert(`Erreur: ${err.message}`);
    } finally {
      setActionLoading(false);
    }
  };

  const handleDelete = async (alertId) => {
    if (!window.confirm('Supprimer cette alerte ?')) return;
    setActionLoading(true);
    try {
      await deleteAlert(alertId);
      await loadAlerts();
    } catch (err) {
      alert(`Erreur: ${err.message}`);
    } finally {
      setActionLoading(false);
    }
  };

  const filteredAlerts = alerts.filter(alert => {
    const matchesSearch = 
      alert.crypto_symbol?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      alert.user_id?.toLowerCase().includes(searchTerm.toLowerCase());
    
    let matchesFilter = true;
    if (filterActive === 'active') matchesFilter = alert.is_active;
    if (filterActive === 'inactive') matchesFilter = !alert.is_active;
    if (filterActive === 'triggered') matchesFilter = alert.triggered_at != null;
    
    return matchesSearch && matchesFilter;
  });

  const formatDate = (dateStr) => {
    if (!dateStr) return 'N/A';
    return new Date(dateStr).toLocaleDateString('fr-FR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatPrice = (price) => {
    if (!price) return 'N/A';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 6
    }).format(price);
  };

  if (loading) {
    return (
      <div className="admin-container">
        <div className="admin-loading">
          <div className="spinner"></div>
          <p>Chargement des alertes...</p>
        </div>
      </div>
    );
  }

  const activeCount = alerts.filter(a => a.is_active).length;
  const triggeredCount = alerts.filter(a => a.triggered_at).length;

  return (
    <div className="admin-container">
      <div className="admin-header">
        <h1>🔔 Gestion des Alertes</h1>
        <div className="header-actions">
          <button 
            onClick={handleDisableAll} 
            className="btn-danger"
            disabled={actionLoading || activeCount === 0}
          >
            🔕 Désactiver toutes ({activeCount})
          </button>
          <button onClick={loadAlerts} className="btn-refresh" disabled={actionLoading}>
            🔄 Actualiser
          </button>
        </div>
      </div>

      {/* Navigation Admin */}
      <div className="admin-nav">
        <Link to="/admin" className="admin-nav-item">📊 Dashboard</Link>
        <Link to="/admin/users" className="admin-nav-item">👥 Utilisateurs</Link>
        <Link to="/admin/alerts" className="admin-nav-item active">🔔 Alertes</Link>
        <Link to="/admin/notifications" className="admin-nav-item">📧 Notifications</Link>
      </div>

      {/* Stats rapides */}
      <div className="alert-stats">
        <div className="alert-stat">
          <span className="stat-label">Total</span>
          <span className="stat-value">{alerts.length}</span>
        </div>
        <div className="alert-stat active">
          <span className="stat-label">Actives</span>
          <span className="stat-value">{activeCount}</span>
        </div>
        <div className="alert-stat triggered">
          <span className="stat-label">Déclenchées</span>
          <span className="stat-value">{triggeredCount}</span>
        </div>
      </div>

      {/* Filtres */}
      <div className="admin-filters">
        <div className="filter-group">
          <input
            type="text"
            placeholder="🔍 Rechercher par crypto ou utilisateur..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
        </div>
        <div className="filter-group">
          <select
            value={filterActive}
            onChange={(e) => setFilterActive(e.target.value)}
            className="filter-select"
          >
            <option value="all">Toutes les alertes</option>
            <option value="active">🟢 Actives</option>
            <option value="inactive">🔴 Inactives</option>
            <option value="triggered">⚡ Déclenchées</option>
          </select>
        </div>
      </div>

      {error && (
        <div className="admin-error">
          <p>❌ {error}</p>
        </div>
      )}

      {/* Tableau des alertes */}
      <div className="admin-table-container">
        <table className="admin-table">
          <thead>
            <tr>
              <th>Utilisateur</th>
              <th>Crypto</th>
              <th>Type</th>
              <th>Prix cible</th>
              <th>Statut</th>
              <th>Créée le</th>
              <th>Déclenchée</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredAlerts.map(alert => (
              <tr key={alert.id} className={!alert.is_active ? 'inactive-row' : ''}>
                <td>
                  <span className="user-badge">👤 {alert.user_id}</span>
                </td>
                <td>
                  <span className="crypto-badge">{alert.crypto_symbol}</span>
                </td>
                <td>
                  <span className={`type-badge ${alert.alert_type}`}>
                    {alert.alert_type === 'above' ? '📈 Au-dessus' : '📉 En-dessous'}
                  </span>
                </td>
                <td className="price-cell">{formatPrice(alert.target_price)}</td>
                <td>
                  <span className={`status-badge ${alert.is_active ? 'active' : 'inactive'}`}>
                    {alert.is_active ? '🟢 Active' : '🔴 Inactive'}
                  </span>
                </td>
                <td>{formatDate(alert.created_at)}</td>
                <td>
                  {alert.triggered_at ? (
                    <span className="triggered-badge">⚡ {formatDate(alert.triggered_at)}</span>
                  ) : (
                    <span className="not-triggered">-</span>
                  )}
                </td>
                <td>
                  <button
                    onClick={() => handleDelete(alert.id)}
                    className="btn-action btn-danger"
                    disabled={actionLoading}
                    title="Supprimer"
                  >
                    🗑️
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {filteredAlerts.length === 0 && (
        <div className="no-data">
          <p>Aucune alerte trouvée</p>
        </div>
      )}
    </div>
  );
};

export default AdminAlerts;
