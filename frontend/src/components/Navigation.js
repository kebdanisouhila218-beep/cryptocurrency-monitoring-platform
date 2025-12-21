// Navigation.js - Navigation moderne avec toggle theme

import React, { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import authService from '../services/authService';
import './Navigation.css';

const Navigation = () => {
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [isRotating, setIsRotating] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [username, setUsername] = useState('');
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    // Charger le thème depuis localStorage
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
      setIsDarkMode(true);
      document.body.classList.add('dark-mode');
    } else {
      document.body.classList.remove('dark-mode');
    }

    // Vérifier l'authentification
    checkAuth();
  }, [location]); // Re-vérifier à chaque changement de route

  const checkAuth = () => {
    const authenticated = authService.isAuthenticated();
    setIsAuthenticated(authenticated);
    if (authenticated) {
      setUsername(authService.getUsername() || 'Utilisateur');
    }
  };

  const toggleTheme = () => {
    // Animation de rotation
    setIsRotating(true);
    setTimeout(() => setIsRotating(false), 500);

    setIsDarkMode(!isDarkMode);
    
    if (isDarkMode) {
      // Passer au mode jour (beige/marron)
      document.body.classList.remove('dark-mode');
      localStorage.setItem('theme', 'light');
    } else {
      // Passer au mode nuit (noir/blanc)
      document.body.classList.add('dark-mode');
      localStorage.setItem('theme', 'dark');
    }
  };

  const handleLogout = () => {
    authService.logout();
    setIsAuthenticated(false);
    setUsername('');
    navigate('/login');
  };

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-brand">
          <span>🚀</span>
          <span>CryptoTracker</span>
        </Link>
        
        <div className="navbar-right">
          <ul className="nav-menu">
            {isAuthenticated ? (
              <>
                <li className="nav-item">
                  <Link 
                    to="/" 
                    className={`nav-link ${location.pathname === '/' ? 'active' : ''}`}
                  >
                    <span>📋</span>
                    <span>Cryptos</span>
                  </Link>
                </li>
                <li className="nav-item">
                  <Link 
                    to="/dashboard" 
                    className={`nav-link ${location.pathname === '/dashboard' ? 'active' : ''}`}
                  >
                    <span>📊</span>
                    <span>Dashboard</span>
                  </Link>
                </li>
                <li className="nav-item">
                  <Link 
                    to="/alerts" 
                    className={`nav-link ${location.pathname === '/alerts' ? 'active' : ''}`}
                  >
                    <span>🔔</span>
                    <span>Alertes</span>
                  </Link>
                </li>
                <li className="nav-item">
                  <Link 
                    to="/profile" 
                    className={`nav-link ${location.pathname === '/profile' ? 'active' : ''}`}
                  >
                    <span>👤</span>
                    <span>{username}</span>
                  </Link>
                </li>
                <li className="nav-item">
                  <button onClick={handleLogout} className="btn-logout" title="Déconnexion">
                    Déconnexion
                  </button>
                </li>
              </>
            ) : (
              <>
                <li className="nav-item">
                  <Link 
                    to="/login" 
                    className={`nav-link ${location.pathname === '/login' ? 'active' : ''}`}
                  >
                    <span>🔐</span>
                    <span>Connexion</span>
                  </Link>
                </li>
                <li className="nav-item">
                  <Link 
                    to="/register" 
                    className={`nav-link ${location.pathname === '/register' ? 'active' : ''}`}
                  >
                    <span>📝</span>
                    <span>Inscription</span>
                  </Link>
                </li>
              </>
            )}
          </ul>

          <button 
            className={`theme-toggle ${isRotating ? 'rotating' : ''}`}
            onClick={toggleTheme}
            aria-label="Toggle theme"
            title={isDarkMode ? 'Mode Jour' : 'Mode Nuit'}
          >
            {isDarkMode ? '🌙' : '☀️'}
          </button>
        </div>
      </div>
    </nav>
  );
};

export default Navigation;