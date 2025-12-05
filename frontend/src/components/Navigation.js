// Navigation.js - Navigation moderne avec toggle theme

import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import './Navigation.css';

const Navigation = () => {
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [isRotating, setIsRotating] = useState(false);
  const location = useLocation();

  useEffect(() => {
    // Charger le thème depuis localStorage
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
      setIsDarkMode(true);
      document.body.classList.add('dark-mode');
    } else {
      // Par défaut mode jour (beige/marron)
      document.body.classList.remove('dark-mode');
    }
  }, []);

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

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-brand">
          <span>🚀</span>
          <span>CryptoTracker</span>
        </Link>
        
        <div className="navbar-right">
          <ul className="nav-menu">
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
          </ul>

          <button 
            className={`theme-toggle ${isRotating ? 'rotating' : ''}`}
            onClick={toggleTheme}
            aria-label="Toggle theme"
            title={isDarkMode ? 'Mode Jour' : 'Mode Nuit'}
          >
            {isDarkMode ? '☀️' : '🌙'}
          </button>
        </div>
      </div>
    </nav>
  );
};

export default Navigation;