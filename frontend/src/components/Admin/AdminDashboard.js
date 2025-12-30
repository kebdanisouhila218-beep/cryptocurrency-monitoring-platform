// frontend/src/components/Admin/AdminDashboard.js

import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getStats, getSystemHealth, getActivity } from '../../services/adminService';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';
import './Admin.css';

const AdminDashboard = () => {
  const [stats, setStats] = useState(null);
  const [health, setHealth] = useState(null);
  const [activity, setActivity] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [statsData, healthData, activityData] = await Promise.all([
        getStats(),
        getSystemHealth(),
        getActivity(7)
      ]);
      setStats(statsData);
      setHealth(healthData);
      setActivity(activityData);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const formatActivityData = () => {
    if (!activity) return [];
    
    const days = [];
    const today = new Date();
    
    for (let i = 6; i >= 0; i--) {
      const date = new Date(today);
      date.setDate(date.getDate() - i);
      const dateStr = date.toISOString().split('T')[0];
      
      days.push({
        date: dateStr.slice(5), // MM-DD
        registrations: activity.registrations[dateStr] || 0,
        alerts: activity.alerts_triggered[dateStr] || 0,
        transactions: activity.transactions[dateStr] || 0
      });
    }
    
    return days;
  };

  if (loading) {
    return (
      <div className="admin-container">
        <div className="admin-loading">
          <div className="spinner"></div>
          <p>Chargement du dashboard admin...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="admin-container">
        <div className="admin-error">
          <h2>❌ Erreur</h2>
          <p>{error}</p>
          <button onClick={loadData} className="btn-primary">Réessayer</button>
        </div>
      </div>
    );
  }

  return (
    <div className="admin-container">
      <div className="admin-header">
        <h1>🛡️ Dashboard Administrateur</h1>
        <button onClick={loadData} className="btn-refresh">🔄 Actualiser</button>
      </div>

      {/* Navigation Admin */}
      <div className="admin-nav">
        <Link to="/admin" className="admin-nav-item active">📊 Dashboard</Link>
        <Link to="/admin/users" className="admin-nav-item">👥 Utilisateurs</Link>
        <Link to="/admin/alerts" className="admin-nav-item">🔔 Alertes</Link>
        <Link to="/admin/notifications" className="admin-nav-item">📧 Notifications</Link>
      </div>

      {/* État des Services */}
      <div className="admin-section">
        <h2>🏥 État des Services</h2>
        <div className="health-grid">
          <div className={`health-card ${health?.api?.status}`}>
            <div className="health-icon">🖥️</div>
            <div className="health-info">
              <h3>API</h3>
              <span className={`status-badge ${health?.api?.status}`}>
                {health?.api?.status === 'healthy' ? '✅ En ligne' : '❌ Hors ligne'}
              </span>
            </div>
          </div>
          <div className={`health-card ${health?.mongodb?.status}`}>
            <div className="health-icon">🗄️</div>
            <div className="health-info">
              <h3>MongoDB</h3>
              <span className={`status-badge ${health?.mongodb?.status}`}>
                {health?.mongodb?.status === 'healthy' ? '✅ Connecté' : '❌ Déconnecté'}
              </span>
            </div>
          </div>
          <div className={`health-card ${health?.redis?.status}`}>
            <div className="health-icon">⚡</div>
            <div className="health-info">
              <h3>Redis</h3>
              <span className={`status-badge ${health?.redis?.status}`}>
                {health?.redis?.status === 'healthy' ? '✅ Connecté' : '⚠️ Non disponible'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Statistiques Globales */}
      <div className="admin-section">
        <h2>📊 Statistiques Globales</h2>
        <div className="stats-grid">
          <div className="stat-card users">
            <div className="stat-icon">👥</div>
            <div className="stat-info">
              <h3>Utilisateurs</h3>
              <div className="stat-value">{stats?.users?.total || 0}</div>
              <div className="stat-details">
                <span>✅ {stats?.users?.active || 0} actifs</span>
                <span>🛡️ {stats?.users?.admins || 0} admins</span>
              </div>
            </div>
          </div>
          <div className="stat-card alerts">
            <div className="stat-icon">🔔</div>
            <div className="stat-info">
              <h3>Alertes</h3>
              <div className="stat-value">{stats?.alerts?.total || 0}</div>
              <div className="stat-details">
                <span>🟢 {stats?.alerts?.active || 0} actives</span>
                <span>⚡ {stats?.alerts?.triggered || 0} déclenchées</span>
              </div>
            </div>
          </div>
          <div className="stat-card portfolios">
            <div className="stat-icon">💼</div>
            <div className="stat-info">
              <h3>Portfolios</h3>
              <div className="stat-value">{stats?.portfolios?.total || 0}</div>
              <div className="stat-details">
                <span>📈 {stats?.portfolios?.transactions || 0} transactions</span>
              </div>
            </div>
          </div>
          <div className="stat-card data">
            <div className="stat-icon">📈</div>
            <div className="stat-info">
              <h3>Données Prix</h3>
              <div className="stat-value">{stats?.data?.price_records?.toLocaleString() || 0}</div>
              <div className="stat-details">
                <span>enregistrements</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Graphique d'Activité */}
      <div className="admin-section">
        <h2>📈 Activité des 7 derniers jours</h2>
        <div className="activity-chart">
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={formatActivityData()}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="registrations" fill="#4CAF50" name="Inscriptions" />
              <Bar dataKey="alerts" fill="#FF9800" name="Alertes déclenchées" />
              <Bar dataKey="transactions" fill="#2196F3" name="Transactions" />
            </BarChart>
          </ResponsiveContainer>
        </div>
        {activity && (
          <div className="activity-totals">
            <div className="activity-total">
              <span className="label">Nouvelles inscriptions:</span>
              <span className="value">{activity.totals?.new_users || 0}</span>
            </div>
            <div className="activity-total">
              <span className="label">Alertes déclenchées:</span>
              <span className="value">{activity.totals?.alerts_triggered || 0}</span>
            </div>
            <div className="activity-total">
              <span className="label">Transactions:</span>
              <span className="value">{activity.totals?.transactions || 0}</span>
            </div>
          </div>
        )}
      </div>

      {/* Actions Rapides */}
      <div className="admin-section">
        <h2>⚡ Actions Rapides</h2>
        <div className="quick-actions">
          <Link to="/admin/users" className="action-btn">
            <span className="action-icon">👥</span>
            <span>Gérer les utilisateurs</span>
          </Link>
          <Link to="/admin/alerts" className="action-btn">
            <span className="action-icon">🔔</span>
            <span>Gérer les alertes</span>
          </Link>
          <Link to="/admin/notifications" className="action-btn">
            <span className="action-icon">📢</span>
            <span>Envoyer une notification</span>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;
