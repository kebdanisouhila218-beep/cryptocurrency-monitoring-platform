// frontend/src/api/cryptoService.js

import axios from 'axios';

const API_BASE = 'http://127.0.0.1:8000';

const cryptoService = {
  // Récupérer toutes les cryptos
  getAllCryptos: async () => {
    try {
      const response = await axios.get(`${API_BASE}/prices`);
      return response.data.prices || [];
    } catch (error) {
      console.error('Erreur lors de la récupération des cryptos:', error);
      throw error;
    }
  },

  // Récupérer une crypto spécifique
  getCryptoByName: async (name) => {
    try {
      const response = await axios.get(`${API_BASE}/prices`);
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
      const response = await axios.get(`${API_BASE}/prices`);
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
  }
};

export default cryptoService;