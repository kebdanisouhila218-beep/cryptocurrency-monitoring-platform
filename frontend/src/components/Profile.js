// frontend/src/components/Profile.js
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import authService from '../services/authService';
import './Profile.css';

const Profile = () => {
  const [userInfo, setUserInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    fetchUserInfo();
  }, []);

  const fetchUserInfo = async () => {
    try {
      setLoading(true);
      const data = await authService.getCurrentUser();
      
      if (data) {
        setUserInfo(data);
      } else {
        setError('Impossible de récupérer les informations');
      }
    } catch (err) {
      setError('Erreur lors du chargement du profil');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    authService.logout();
    navigate('/login');
  };

  if (loading) {
    return (
      <div className="profile-container">
        <div className="profile-card">
          <div className="loading-spinner"></div>
          <p>Chargement du profil...</p>
        </div>
      </div>
    );
  }

  if (error || !userInfo) {
    return (
      <div className="profile-container">
        <div className="profile-card">
          <div className="error-message">{error}</div>
          <button onClick={fetchUserInfo} className="btn-retry">
            🔄 Réessayer
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="profile-container">
      <div className="profile-card">
        <div className="profile-header">
          <div className="profile-avatar">
            {userInfo.username.charAt(0).toUpperCase()}
          </div>
          <h1>Mon Profil</h1>
        </div>

        <div className="profile-info">
          <div className="info-group">
            <label>👤 Nom d'utilisateur</label>
            <div className="info-value">{userInfo.username}</div>
          </div>

          <div className="info-group">
            <label>📧 Email</label>
            <div className="info-value">{userInfo.email}</div>
          </div>

          <div className="info-group">
            <label>🎭 Rôle</label>
            <div className={`info-value badge badge-${userInfo.role}`}>
              {userInfo.role === 'admin' ? '👑 Administrateur' : '👤 Utilisateur'}
            </div>
          </div>

          <div className="info-group">
            <label>📅 Membre depuis</label>
            <div className="info-value">
              {new Date(userInfo.created_at).toLocaleDateString('fr-FR', {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
              })}
            </div>
          </div>

          <div className="info-group">
            <label>✅ Statut</label>
            <div className={`info-value badge ${userInfo.is_active ? 'badge-active' : 'badge-inactive'}`}>
              {userInfo.is_active ? '🟢 Actif' : '🔴 Inactif'}
            </div>
          </div>
        </div>

        <div className="profile-actions">
          <button className="btn-logout" onClick={handleLogout}>
            🚪 Se déconnecter
          </button>
          <button className="btn-back" onClick={() => navigate('/dashboard')}>
            ← Retour au Dashboard
          </button>
        </div>

        {/* Statistiques utilisateur */}
        <div className="profile-stats">
          <h3>📊 Statistiques</h3>
          <div className="stats-grid">
            <div className="stat-item">
              <div className="stat-icon">🔐</div>
              <div className="stat-label">Sessions actives</div>
              <div className="stat-value">1</div>
            </div>
            <div className="stat-item">
              <div className="stat-icon">⏱️</div>
              <div className="stat-label">Dernière connexion</div>
              <div className="stat-value">Aujourd'hui</div>
            </div>
            <div className="stat-item">
              <div className="stat-icon">🛡️</div>
              <div className="stat-label">Sécurité</div>
              <div className="stat-value">Élevée</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile;