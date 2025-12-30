// frontend/src/components/Admin/AdminNotifications.js

import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getNotificationLogs, sendBroadcast } from '../../services/adminService';
import './Admin.css';

const AdminNotifications = () => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showBroadcastForm, setShowBroadcastForm] = useState(false);
  const [sending, setSending] = useState(false);
  
  const [broadcastData, setBroadcastData] = useState({
    subject: '',
    message: '',
    sendEmail: true,
    sendDiscord: true
  });

  useEffect(() => {
    loadLogs();
  }, []);

  const loadLogs = async () => {
    setLoading(true);
    try {
      const data = await getNotificationLogs();
      setLogs(data.logs || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSendBroadcast = async (e) => {
    e.preventDefault();
    if (!broadcastData.subject || !broadcastData.message) {
      alert('Veuillez remplir tous les champs');
      return;
    }
    
    if (!window.confirm('Envoyer cette notification à tous les utilisateurs ?')) return;
    
    setSending(true);
    try {
      const result = await sendBroadcast(
        broadcastData.subject,
        broadcastData.message,
        broadcastData.sendEmail,
        broadcastData.sendDiscord
      );
      alert(`✅ Notification envoyée à ${result.recipients} utilisateurs (${result.sent} réussis)`);
      setBroadcastData({ subject: '', message: '', sendEmail: true, sendDiscord: true });
      setShowBroadcastForm(false);
      await loadLogs();
    } catch (err) {
      alert(`Erreur: ${err.message}`);
    } finally {
      setSending(false);
    }
  };

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

  if (loading) {
    return (
      <div className="admin-container">
        <div className="admin-loading">
          <div className="spinner"></div>
          <p>Chargement des notifications...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="admin-container">
      <div className="admin-header">
        <h1>📧 Notifications</h1>
        <div className="header-actions">
          <button 
            onClick={() => setShowBroadcastForm(!showBroadcastForm)} 
            className="btn-primary"
          >
            📢 {showBroadcastForm ? 'Annuler' : 'Nouvelle notification'}
          </button>
          <button onClick={loadLogs} className="btn-refresh">
            🔄 Actualiser
          </button>
        </div>
      </div>

      {/* Navigation Admin */}
      <div className="admin-nav">
        <Link to="/admin" className="admin-nav-item">📊 Dashboard</Link>
        <Link to="/admin/users" className="admin-nav-item">👥 Utilisateurs</Link>
        <Link to="/admin/alerts" className="admin-nav-item">🔔 Alertes</Link>
        <Link to="/admin/notifications" className="admin-nav-item active">📧 Notifications</Link>
      </div>

      {/* Formulaire de broadcast */}
      {showBroadcastForm && (
        <div className="broadcast-form-container">
          <h2>📢 Envoyer une notification à tous</h2>
          <form onSubmit={handleSendBroadcast} className="broadcast-form">
            <div className="form-group">
              <label>Sujet</label>
              <input
                type="text"
                value={broadcastData.subject}
                onChange={(e) => setBroadcastData({...broadcastData, subject: e.target.value})}
                placeholder="Ex: Maintenance prévue"
                required
              />
            </div>
            <div className="form-group">
              <label>Message</label>
              <textarea
                value={broadcastData.message}
                onChange={(e) => setBroadcastData({...broadcastData, message: e.target.value})}
                placeholder="Votre message..."
                rows={5}
                required
              />
            </div>
            <div className="form-group checkbox-group">
              <label>
                <input
                  type="checkbox"
                  checked={broadcastData.sendEmail}
                  onChange={(e) => setBroadcastData({...broadcastData, sendEmail: e.target.checked})}
                />
                📧 Envoyer par email
              </label>
              <label>
                <input
                  type="checkbox"
                  checked={broadcastData.sendDiscord}
                  onChange={(e) => setBroadcastData({...broadcastData, sendDiscord: e.target.checked})}
                />
                💬 Envoyer sur Discord
              </label>
            </div>
            <div className="form-actions">
              <button type="submit" className="btn-primary" disabled={sending}>
                {sending ? '⏳ Envoi...' : '📤 Envoyer'}
              </button>
              <button 
                type="button" 
                className="btn-secondary"
                onClick={() => setShowBroadcastForm(false)}
              >
                Annuler
              </button>
            </div>
          </form>
        </div>
      )}

      {error && (
        <div className="admin-error">
          <p>❌ {error}</p>
        </div>
      )}

      {/* Historique des notifications */}
      <div className="admin-section">
        <h2>📜 Historique des notifications</h2>
        
        {logs.length === 0 ? (
          <div className="no-data">
            <p>Aucune notification envoyée</p>
          </div>
        ) : (
          <div className="notification-logs">
            {logs.map((log, index) => (
              <div key={index} className="notification-log-item">
                <div className="log-header">
                  <span className="log-type">
                    {log.type === 'broadcast' ? '📢 Broadcast' : '📧 Notification'}
                  </span>
                  <span className="log-date">{formatDate(log.timestamp)}</span>
                </div>
                <div className="log-content">
                  <h4>{log.subject}</h4>
                  <p>{log.message}</p>
                </div>
                <div className="log-meta">
                  <span>👤 Envoyé par: {log.sent_by}</span>
                  <span>📨 Destinataires: {log.recipients_count}</span>
                  <span>✅ Envoyés: {log.sent_count}</span>
                  {log.errors && log.errors.length > 0 && (
                    <span className="log-errors">❌ Erreurs: {log.errors.length}</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminNotifications;
