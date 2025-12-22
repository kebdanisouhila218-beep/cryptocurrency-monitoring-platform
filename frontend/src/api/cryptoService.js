// frontend/src/api/cryptoService.js - Version avec authentification

import axios from 'axios';
import authService from '../services/authService';

const API_BASE = 'http://localhost:8000';

const cryptoService = {
  // Récupérer toutes les cryptos (route protégée)
  getAllCryptos: async () => {
    try {
      const response = await axios.get(`${API_BASE}/prices`, {
        headers: authService.getAuthHeader()
      });
      return response.data.prices || [];
    } catch (error) {
      console.error('Erreur lors de la récupération des cryptos:', error);
      
      // Si erreur 401, rediriger vers login
      if (error.response?.status === 401) {
        authService.logout();
        window.location.href = '/login';
      }
      
      throw error;
    }
  },

  // Récupérer une crypto spécifique
  getCryptoByName: async (name) => {
    try {
      const response = await axios.get(`${API_BASE}/prices`, {
        headers: authService.getAuthHeader()
      });
      const prices = response.data.prices || [];
      
      const crypto = prices.find(p => 
        p.name?.toLowerCase().includes(name.toLowerCase()) || 
        p.symbol?.toLowerCase().includes(name.toLowerCase())
      );
      
      if (!crypto) {
        throw new Error(`Crypto '${name}' not found`);
      }
      
      return crypto;
    } catch (error) {
      console.error(`Erreur: ${error.message}`);
      throw error;
    }
  },

  // Récupérer l'historique des prix
  getCryptoHistory: async (name, days = 7) => {
    try {
      const response = await axios.get(`${API_BASE}/prices`, {
        headers: authService.getAuthHeader()
      });
      const prices = response.data.prices || [];
      
      const history = prices
        .filter(p => 
          p.name?.toLowerCase().includes(name.toLowerCase()) || 
          p.symbol?.toLowerCase().includes(name.toLowerCase())
        )
        .slice(0, days);
      
      if (history.length === 0) {
        throw new Error(`No history found for '${name}'`);
      }
      
      return history;
    } catch (error) {
      console.error(`Erreur: ${error.message}`);
      throw error;
    }
  },

  // Récupérer les derniers prix (avec limite)
  getLatestPrices: async (limit = 10) => {
    try {
      const response = await axios.get(`${API_BASE}/prices/latest`, {
        params: { limit },
        headers: authService.getAuthHeader()
      });
      return response.data.prices || [];
    } catch (error) {
      console.error('Erreur lors de la récupération des derniers prix:', error);
      throw error;
    }
  }
};

export default cryptoService;