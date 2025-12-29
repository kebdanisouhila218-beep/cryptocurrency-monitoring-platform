// Navigation.js - Navigation moderne avec toggle theme

import React, { useState, useEffect, useRef } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import authService from '../services/authService';
import './Navigation.css';

const Navigation = () => {
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [isRotating, setIsRotating] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [username, setUsername] = useState('');

  const [dataDropdownOpen, setDataDropdownOpen] = useState(false);
  const [analysisDropdownOpen, setAnalysisDropdownOpen] = useState(false);
  const [userDropdownOpen, setUserDropdownOpen] = useState(false);

  const location = useLocation();
  const navigate = useNavigate();

  const dataDropdownRef = useRef(null);
  const analysisDropdownRef = useRef(null);
  const userDropdownRef = useRef(null);

  useEffect(() => {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
      setIsDarkMode(true);
      document.body.classList.add('dark-mode');
    } else {
      document.body.classList.remove('dark-mode');
    }

    checkAuth();
  }, [location]);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dataDropdownRef.current && !dataDropdownRef.current.contains(event.target)) {
        setDataDropdownOpen(false);
      }
      if (analysisDropdownRef.current && !analysisDropdownRef.current.contains(event.target)) {
        setAnalysisDropdownOpen(false);
      }
      if (userDropdownRef.current && !userDropdownRef.current.contains(event.target)) {
        setUserDropdownOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const checkAuth = () => {
    const authenticated = authService.isAuthenticated();
    setIsAuthenticated(authenticated);
    if (authenticated) {
      setUsername(authService.getUsername() || 'Utilisateur');
    }
  };

  const toggleTheme = () => {
    setIsRotating(true);
    setTimeout(() => setIsRotating(false), 500);

    setIsDarkMode(!isDarkMode);

    if (isDarkMode) {
      document.body.classList.remove('dark-mode');
      localStorage.setItem('theme', 'light');
    } else {
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

  const closeAllDropdowns = () => {
    setDataDropdownOpen(false);
    setAnalysisDropdownOpen(false);
    setUserDropdownOpen(false);
  };

  const isRouteActive = (routes) => {
    return routes.some((route) => location.pathname === route);
  };

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-brand" onClick={closeAllDropdowns}>
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
                    onClick={closeAllDropdowns}
                  >
                    <span className="nav-icon">🏠</span>
                    <span className="nav-text">Accueil</span>
                  </Link>
                </li>

                <li className="nav-item dropdown" ref={dataDropdownRef}>
                  <button
                    type="button"
                    className={`nav-link dropdown-toggle ${isRouteActive(['/dashboard', '/performance']) ? 'active' : ''}`}
                    onClick={() => {
                      setDataDropdownOpen(!dataDropdownOpen);
                      setAnalysisDropdownOpen(false);
                      setUserDropdownOpen(false);
                    }}
                  >
                    <span className="nav-icon">📊</span>
                    <span className="nav-text">Données</span>
                    <span className={`arrow ${dataDropdownOpen ? 'open' : ''}`}>▼</span>
                  </button>

                  {dataDropdownOpen && (
                    <div className="dropdown-menu">
                      <Link to="/dashboard" className="dropdown-item" onClick={closeAllDropdowns}>
                        <span>📊</span>
                        <span>Dashboard</span>
                      </Link>

                      <Link to="/performance" className="dropdown-item" onClick={closeAllDropdowns}>
                        <span>📈</span>
                        <span>Performances</span>
                      </Link>
                    </div>
                  )}
                </li>

                <li className="nav-item dropdown" ref={analysisDropdownRef}>
                  <button
                    type="button"
                    className={`nav-link dropdown-toggle ${isRouteActive(['/predictions', '/technical-indicators', '/candlestick', '/heatmap']) ? 'active' : ''}`}
                    onClick={() => {
                      setAnalysisDropdownOpen(!analysisDropdownOpen);
                      setDataDropdownOpen(false);
                      setUserDropdownOpen(false);
                    }}
                  >
                    <span className="nav-icon">🔮</span>
                    <span className="nav-text">Analyses</span>
                    <span className={`arrow ${analysisDropdownOpen ? 'open' : ''}`}>▼</span>
                  </button>

                  {analysisDropdownOpen && (
                    <div className="dropdown-menu">
                      <Link to="/predictions" className="dropdown-item" onClick={closeAllDropdowns}>
                        <span>🔮</span>
                        <span>Prévisions</span>
                      </Link>
                      <Link to="/technical-indicators" className="dropdown-item" onClick={closeAllDropdowns}>
                        <span>🔬</span>
                        <span>Indicateurs</span>
                      </Link>
                      <Link to="/candlestick" className="dropdown-item" onClick={closeAllDropdowns}>
                        <span>📈</span>
                        <span>Chandeliers</span>
                      </Link>
                      <Link to="/heatmap" className="dropdown-item" onClick={closeAllDropdowns}>
                        <span>🔥</span>
                        <span>Heatmap</span>
                      </Link>
                    </div>
                  )}
                </li>

                <li className="nav-item">
                  <Link
                    to="/alerts"
                    className={`nav-link ${location.pathname === '/alerts' ? 'active' : ''}`}
                    onClick={closeAllDropdowns}
                  >
                    <span className="nav-icon">🔔</span>
                    <span className="nav-text">Alertes</span>
                  </Link>
                </li>

                <li className="nav-item">
                  <Link
                    to="/virtual-portfolio"
                    className={`nav-link ${location.pathname.startsWith('/virtual-portfolio') ? 'active' : ''}`}
                    onClick={closeAllDropdowns}
                  >
                    <span className="nav-icon">💼</span>
                    <span className="nav-text">Portfolio Virtuel</span>
                  </Link>
                </li>

                <li className="nav-item dropdown" ref={userDropdownRef}>
                  <button
                    type="button"
                    className={`nav-link dropdown-toggle ${isRouteActive(['/profile']) ? 'active' : ''}`}
                    onClick={() => {
                      setUserDropdownOpen(!userDropdownOpen);
                      setDataDropdownOpen(false);
                      setAnalysisDropdownOpen(false);
                    }}
                  >
                    <span className="nav-icon">👤</span>
                    <span className="nav-text">{username}</span>
                    <span className={`arrow ${userDropdownOpen ? 'open' : ''}`}>▼</span>
                  </button>

                  {userDropdownOpen && (
                    <div className="dropdown-menu dropdown-menu-right">
                      <Link to="/profile" className="dropdown-item" onClick={closeAllDropdowns}>
                        <span>👤</span>
                        <span>Mon Profil</span>
                      </Link>
                      <div className="dropdown-divider"></div>
                      <button
                        type="button"
                        onClick={() => {
                          handleLogout();
                          closeAllDropdowns();
                        }}
                        className="dropdown-item logout-item"
                      >
                        <span>🚪</span>
                        <span>Déconnexion</span>
                      </button>
                    </div>
                  )}
                </li>
              </>
            ) : (
              <>
                <li className="nav-item">
                  <Link to="/login" className={`nav-link ${location.pathname === '/login' ? 'active' : ''}`}>
                    <span className="nav-icon">🔐</span>
                    <span className="nav-text">Connexion</span>
                  </Link>
                </li>
                <li className="nav-item">
                  <Link to="/register" className={`nav-link ${location.pathname === '/register' ? 'active' : ''}`}>
                    <span className="nav-icon">📝</span>
                    <span className="nav-text">Inscription</span>
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