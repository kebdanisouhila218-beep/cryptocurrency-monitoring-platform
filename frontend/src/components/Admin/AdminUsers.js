// frontend/src/components/Admin/AdminUsers.js

import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getUsers, updateUser, deleteUser, promoteUser, demoteUser } from '../../services/adminService';
import './Admin.css';

const AdminUsers = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterRole, setFilterRole] = useState('all');
  const [selectedUser, setSelectedUser] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    setLoading(true);
    try {
      const data = await getUsers();
      setUsers(data.users || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleActive = async (username, currentStatus) => {
    setActionLoading(true);
    try {
      await updateUser(username, { is_active: !currentStatus });
      await loadUsers();
    } catch (err) {
      alert(`Erreur: ${err.message}`);
    } finally {
      setActionLoading(false);
    }
  };

  const handlePromote = async (username) => {
    if (!window.confirm(`Promouvoir ${username} en administrateur ?`)) return;
    setActionLoading(true);
    try {
      await promoteUser(username);
      await loadUsers();
    } catch (err) {
      alert(`Erreur: ${err.message}`);
    } finally {
      setActionLoading(false);
    }
  };

  const handleDemote = async (username) => {
    if (!window.confirm(`Rétrograder ${username} en utilisateur standard ?`)) return;
    setActionLoading(true);
    try {
      await demoteUser(username);
      await loadUsers();
    } catch (err) {
      alert(`Erreur: ${err.message}`);
    } finally {
      setActionLoading(false);
    }
  };

  const handleDelete = async (username) => {
    if (!window.confirm(`⚠️ Supprimer définitivement ${username} et toutes ses données ?`)) return;
    setActionLoading(true);
    try {
      await deleteUser(username);
      await loadUsers();
    } catch (err) {
      alert(`Erreur: ${err.message}`);
    } finally {
      setActionLoading(false);
    }
  };

  const filteredUsers = users.filter(user => {
    const matchesSearch = user.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         user.email.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesRole = filterRole === 'all' || user.role === filterRole;
    return matchesSearch && matchesRole;
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

  if (loading) {
    return (
      <div className="admin-container">
        <div className="admin-loading">
          <div className="spinner"></div>
          <p>Chargement des utilisateurs...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="admin-container">
      <div className="admin-header">
        <h1>👥 Gestion des Utilisateurs</h1>
        <button onClick={loadUsers} className="btn-refresh" disabled={actionLoading}>
          🔄 Actualiser
        </button>
      </div>

      {/* Navigation Admin */}
      <div className="admin-nav">
        <Link to="/admin" className="admin-nav-item">📊 Dashboard</Link>
        <Link to="/admin/users" className="admin-nav-item active">👥 Utilisateurs</Link>
        <Link to="/admin/alerts" className="admin-nav-item">🔔 Alertes</Link>
        <Link to="/admin/notifications" className="admin-nav-item">📧 Notifications</Link>
      </div>

      {/* Filtres */}
      <div className="admin-filters">
        <div className="filter-group">
          <input
            type="text"
            placeholder="🔍 Rechercher par nom ou email..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
        </div>
        <div className="filter-group">
          <select
            value={filterRole}
            onChange={(e) => setFilterRole(e.target.value)}
            className="filter-select"
          >
            <option value="all">Tous les rôles</option>
            <option value="admin">🛡️ Admins</option>
            <option value="user">👤 Utilisateurs</option>
          </select>
        </div>
        <div className="filter-info">
          {filteredUsers.length} utilisateur(s) trouvé(s)
        </div>
      </div>

      {error && (
        <div className="admin-error">
          <p>❌ {error}</p>
        </div>
      )}

      {/* Tableau des utilisateurs */}
      <div className="admin-table-container">
        <table className="admin-table">
          <thead>
            <tr>
              <th>Utilisateur</th>
              <th>Email</th>
              <th>Rôle</th>
              <th>Statut</th>
              <th>Inscrit le</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredUsers.map(user => (
              <tr key={user.username} className={!user.is_active ? 'inactive-row' : ''}>
                <td>
                  <div className="user-cell">
                    <span className="user-avatar">
                      {user.role === 'admin' ? '🛡️' : '👤'}
                    </span>
                    <span className="user-name">{user.username}</span>
                  </div>
                </td>
                <td>{user.email}</td>
                <td>
                  <span className={`role-badge ${user.role}`}>
                    {user.role === 'admin' ? '🛡️ Admin' : '👤 User'}
                  </span>
                </td>
                <td>
                  <span className={`status-badge ${user.is_active ? 'active' : 'inactive'}`}>
                    {user.is_active ? '✅ Actif' : '❌ Inactif'}
                  </span>
                </td>
                <td>{formatDate(user.created_at)}</td>
                <td>
                  <div className="action-buttons">
                    <button
                      onClick={() => handleToggleActive(user.username, user.is_active)}
                      className={`btn-action ${user.is_active ? 'btn-warning' : 'btn-success'}`}
                      disabled={actionLoading}
                      title={user.is_active ? 'Désactiver' : 'Activer'}
                    >
                      {user.is_active ? '🔒' : '🔓'}
                    </button>
                    {user.role === 'user' ? (
                      <button
                        onClick={() => handlePromote(user.username)}
                        className="btn-action btn-promote"
                        disabled={actionLoading}
                        title="Promouvoir en admin"
                      >
                        ⬆️
                      </button>
                    ) : (
                      <button
                        onClick={() => handleDemote(user.username)}
                        className="btn-action btn-demote"
                        disabled={actionLoading}
                        title="Rétrograder en user"
                      >
                        ⬇️
                      </button>
                    )}
                    <button
                      onClick={() => handleDelete(user.username)}
                      className="btn-action btn-danger"
                      disabled={actionLoading}
                      title="Supprimer"
                    >
                      🗑️
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {filteredUsers.length === 0 && (
        <div className="no-data">
          <p>Aucun utilisateur trouvé</p>
        </div>
      )}
    </div>
  );
};

export default AdminUsers;
