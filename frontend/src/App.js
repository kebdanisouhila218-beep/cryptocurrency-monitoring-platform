// App.js - Application principale avec authentification

import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import CryptoList from './components/CryptoList';
import Dashboard from './components/Dashboard';
import Navigation from './components/Navigation';
import Login from './components/Auth/Login';
import Register from './components/Auth/Register';
import Profile from './components/Profile';
import Alerts from './components/Alerts';
import Portfolio from './components/Portfolio';
import PortfolioDetails from './components/PortfolioDetails';
import VirtualPortfolioList from './components/VirtualPortfolioList';
import VirtualPortfolioDetails from './components/VirtualPortfolioDetails';
import PerformanceTracker from './components/PerformanceTracker';
import Predictions from './components/Predictions';
import TechnicalIndicators from './components/TechnicalIndicators';
import CandlestickChart from './components/AdvancedCharts/CandlestickChart';
import HeatmapChart from './components/AdvancedCharts/HeatmapChart';
import ProtectedRoute from './components/ProtectedRoute';
import Toast from './components/Toast';
import { AdminDashboard, AdminUsers, AdminAlerts, AdminNotifications } from './components/Admin';
import './App.css';

function App() {
  return (
    <Router>
      <div className="app-container">
        <Navigation />
        <Toast />
        <Routes>
          {/* Routes publiques */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          
          {/* Routes protégées */}
          <Route 
            path="/" 
            element={
              <ProtectedRoute>
                <CryptoList />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/dashboard" 
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/profile" 
            element={
              <ProtectedRoute>
                <Profile />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/alerts" 
            element={
              <ProtectedRoute>
                <Alerts />
              </ProtectedRoute>
            } 
          />

          <Route 
            path="/portfolio" 
            element={
              <ProtectedRoute>
                <Portfolio />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/portfolio/:id" 
            element={
              <ProtectedRoute>
                <PortfolioDetails />
              </ProtectedRoute>
            } 
          />

          {/* Routes Portfolio Virtuel */}
          <Route 
            path="/virtual-portfolio" 
            element={
              <ProtectedRoute>
                <VirtualPortfolioList />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/virtual-portfolio/:portfolioId" 
            element={
              <ProtectedRoute>
                <VirtualPortfolioDetails />
              </ProtectedRoute>
            } 
          />

          <Route 
            path="/performance" 
            element={
              <ProtectedRoute>
                <PerformanceTracker />
              </ProtectedRoute>
            } 
          />

          <Route 
            path="/predictions" 
            element={
              <ProtectedRoute>
                <Predictions />
              </ProtectedRoute>
            } 
          />

          <Route 
            path="/technical-indicators" 
            element={
              <ProtectedRoute>
                <TechnicalIndicators />
              </ProtectedRoute>
            } 
          />

          <Route 
            path="/candlestick" 
            element={
              <ProtectedRoute>
                <CandlestickChart />
              </ProtectedRoute>
            } 
          />

          <Route 
            path="/heatmap" 
            element={
              <ProtectedRoute>
                <HeatmapChart />
              </ProtectedRoute>
            } 
          />
          
          {/* Routes Admin */}
          <Route 
            path="/admin" 
            element={
              <ProtectedRoute>
                <AdminDashboard />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/admin/users" 
            element={
              <ProtectedRoute>
                <AdminUsers />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/admin/alerts" 
            element={
              <ProtectedRoute>
                <AdminAlerts />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/admin/notifications" 
            element={
              <ProtectedRoute>
                <AdminNotifications />
              </ProtectedRoute>
            } 
          />

          {/* Route par défaut */}
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;