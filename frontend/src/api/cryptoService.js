// frontend/src/api/cryptoService.js

import axios from 'axios';

const API_BASE = 'http://localhost:8000';

const cryptoService = {
  // Récupérer toutes les cryptos (depuis /prices)
  getAllCryptos: async () => {
    try {
      const response = await axios.get(`${API_BASE}/prices`);
      // Transformer les données du format /prices
      return response.data.prices || [];
    } catch (error) {
      console.error('Erreur lors de la récupération des cryptos:', error);
      throw error;
    }
  },

  // Récupérer une crypto spécifique (filtrée depuis /prices)
  getCryptoByName: async (name) => {
    try {
      const response = await axios.get(`${API_BASE}/prices`);
      const prices = response.data.prices || [];
      
      // Filtrer pour trouver la crypto
      const crypto = prices.find(p => 
        p.name?.toLowerCase().includes(name.toLowerCase()) || 
        p.symbol?.toLowerCase().includes(name.toLowerCase())
      );
      
      if (!crypto) {
        throw new Error(`Crypto '${name}' not found`);
      }
      
      return crypto;
    } catch (error) {
      console.error(`Erreur lors de la récupération de ${name}:`, error);
      throw error;
    }
  },

  // Récupérer l'historique des prix
  getCryptoHistory: async (name, days = 7) => {
    try {
      const response = await axios.get(`${API_BASE}/prices`);
      const prices = response.data.prices || [];
      
      // Filtrer et limiter aux N derniers jours
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
      console.error(`Erreur lors de la récupération de l'historique:`, error);
      throw error;
    }
  }
};

export default cryptoService;