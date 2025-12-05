// frontend/src/components/Navigation.js

import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import './Navigation.css';

const Navigation = () => {
  const [isDarkMode, setIsDarkMode] = useState(true);

  useEffect(() => {
    // Charger le thème depuis localStorage
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'light') {
      setIsDarkMode(false);
      document.body.classList.add('light-mode');
    }
  }, []);

  const toggleTheme = () => {
    setIsDarkMode(!isDarkMode);
    
    if (isDarkMode) {
      document.body.classList.add('light-mode');
      localStorage.setItem('theme', 'light');
    } else {
      document.body.classList.remove('light-mode');
      localStorage.setItem('theme', 'dark');
    }
  };

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-brand">
          🚀 CryptoTracker
        </Link>
        
        <div className="navbar-right">
          <ul className="nav-menu">
            <li className="nav-item">
              <Link to="/" className="nav-link">
                📋 Cryptos
              </Link>
            </li>
            <li className="nav-item">
              <Link to="/dashboard" className="nav-link">
                📊 Dashboard
              </Link>
            </li>
          </ul>

          <button 
            className="theme-toggle" 
            onClick={toggleTheme}
            aria-label="Toggle theme"
          >
            {isDarkMode ? '☀️' : '🌙'}
          </button>
        </div>
      </div>
    </nav>
  );
};

export default Navigation;