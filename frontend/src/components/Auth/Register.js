// frontend/src/components/Auth/Register.js
import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import authService from '../../services/authService';
import './Register.css';

const Register = () => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    // Effacer l'erreur du champ modifié
    if (errors[e.target.name]) {
      setErrors({
        ...errors,
        [e.target.name]: ''
      });
    }
  };

  const validateForm = () => {
    const newErrors = {};

    // Validation username
    if (!formData.username) {
      newErrors.username = 'Le nom d\'utilisateur est requis';
    } else if (formData.username.length < 3) {
      newErrors.username = 'Minimum 3 caractères';
    }

    // Validation email
    if (!formData.email) {
      newErrors.email = 'L\'email est requis';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Email invalide';
    }

    // Validation password
    if (!formData.password) {
      newErrors.password = 'Le mot de passe est requis';
    } else if (formData.password.length < 6) {
      newErrors.password = 'Minimum 6 caractères';
    }

    // Validation confirmation
    if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Les mots de passe ne correspondent pas';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    console.log('[REGISTER] handleSubmit appelé');
    
    if (!validateForm()) {
      console.log('[REGISTER] Validation échouée');
      return;
    }

    console.log('[REGISTER] Validation OK, appel API...');
    setLoading(true);

    try {
      const result = await authService.register(
        formData.username,
        formData.email,
        formData.password
      );
      console.log('[REGISTER] Résultat reçu:', result);

      if (result && result.success) {
        console.log('[REGISTER] Inscription réussie');
        setSuccess(true);
        // Rediriger vers la page de connexion après 2 secondes
        setTimeout(() => {
          navigate('/login');
        }, 2000);
      } else {
        console.log('[REGISTER] Échec inscription:', result?.error);
        setErrors({ general: result?.error || 'Erreur inscription' });
      }
    } catch (err) {
      console.error('[REGISTER] Exception:', err);
      setErrors({ general: 'Une erreur est survenue' });
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className="register-container">
        <div className="register-card">
          <div className="success-message">
            <div className="success-icon">✅</div>
            <h2>Inscription réussie !</h2>
            <p>Redirection vers la page de connexion...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="register-container">
      <div className="register-card">
        <div className="register-header">
          <h1>Inscription</h1>
          <p>Créez votre compte CryptoTracker</p>
        </div>

        {errors.general && (
          <div className="error-message">
            ❌ {errors.general}
          </div>
        )}

        <form onSubmit={handleSubmit} className="register-form">
          <div className="form-group">
            <label htmlFor="username">Nom d'utilisateur *</label>
            <input
              type="text"
              id="username"
              name="username"
              value={formData.username}
              onChange={handleChange}
              placeholder="Choisissez un nom d'utilisateur"
              disabled={loading}
              className={errors.username ? 'input-error' : ''}
            />
            {errors.username && (
              <span className="field-error">{errors.username}</span>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="email">Email *</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="votre@email.com"
              disabled={loading}
              className={errors.email ? 'input-error' : ''}
            />
            {errors.email && (
              <span className="field-error">{errors.email}</span>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="password">Mot de passe *</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="Minimum 6 caractères"
              disabled={loading}
              className={errors.password ? 'input-error' : ''}
            />
            {errors.password && (
              <span className="field-error">{errors.password}</span>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="confirmPassword">Confirmer le mot de passe *</label>
            <input
              type="password"
              id="confirmPassword"
              name="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleChange}
              placeholder="Répétez le mot de passe"
              disabled={loading}
              className={errors.confirmPassword ? 'input-error' : ''}
            />
            {errors.confirmPassword && (
              <span className="field-error">{errors.confirmPassword}</span>
            )}
          </div>

          <button 
            type="submit" 
            className="btn-register"
            disabled={loading}
          >
            {loading ? '⏳ Inscription...' : '🚀 Créer mon compte'}
          </button>
        </form>

        <div className="register-footer">
          <p>
            Vous avez déjà un compte ?{' '}
            <Link to="/login" className="link-login">
              Se connecter
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Register;