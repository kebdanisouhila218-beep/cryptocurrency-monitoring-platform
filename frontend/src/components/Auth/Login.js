// frontend/src/components/Auth/Login.js
import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import authService from '../../services/authService';
import './Login.css';

const Login = () => {
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    setError(''); // Effacer l'erreur quand l'utilisateur tape
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    // Validation basique
    if (!formData.username || !formData.password) {
      setError('Tous les champs sont requis');
      setLoading(false);
      return;
    }

    try {
      const result = await authService.login(formData.username, formData.password);
      
      if (result.success) {
        // Connexion réussie
        console.log('✅ Connexion réussie');
        navigate('/dashboard'); // Rediriger vers le dashboard
      } else {
        setError(result.error);
      }
    } catch (err) {
      setError('Une erreur est survenue');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          <h1>🔐 Connexion</h1>
          <p>Accédez à votre compte CryptoTracker</p>
        </div>

        {error && (
          <div className="error-message">
            ❌ {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label htmlFor="username">Nom d'utilisateur</label>
            <input
              type="text"
              id="username"
              name="username"
              value={formData.username}
              onChange={handleChange}
              placeholder="Entrez votre nom d'utilisateur"
              disabled={loading}
              autoComplete="username"
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Mot de passe</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="Entrez votre mot de passe"
              disabled={loading}
              autoComplete="current-password"
            />
          </div>

          <button 
            type="submit" 
            className="btn-login"
            disabled={loading}
          >
            {loading ? '⏳ Connexion...' : '🚀 Se connecter'}
          </button>
        </form>

        <div className="login-footer">
          <p>
            Pas encore de compte ?{' '}
            <Link to="/register" className="link-register">
              Créer un compte
            </Link>
          </p>
        </div>

        {/* Compte de test pour faciliter les démos */}
        <div className="test-account">
          <p>💡 Compte de test : <strong>bob</strong> / <strong>password123</strong></p>
        </div>
      </div>
    </div>
  );
};

export default Login;