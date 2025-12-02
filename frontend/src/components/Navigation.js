// frontend/src/components/Navigation.js

import React from 'react';
import { Link } from 'react-router-dom';
import './Navigation.css';

const Navigation = () => {
  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-brand">
          🚀 CryptoTracker
        </Link>
        
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
      </div>
    </nav>
  );
};

export default Navigation;