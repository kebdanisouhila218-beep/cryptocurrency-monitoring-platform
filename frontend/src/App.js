// frontend/src/App.js

import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import CryptoList from './components/CryptoList';
import Dashboard from './components/Dashboard';
import Navigation from './components/Navigation';
import './App.css';

function App() {
  return (
    <Router>
      <Navigation />
      <div className="app-container">
        <Routes>
          <Route path="/" element={<CryptoList />} />
          <Route path="/dashboard" element={<Dashboard />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;