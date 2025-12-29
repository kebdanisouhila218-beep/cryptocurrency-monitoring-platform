// frontend/src/services/predictionService.js
import axios from 'axios';
import authService from './authService';

const API_URL = 'http://localhost:8000/predictions';

const predictionService = {
  getPredictions: async (cryptoSymbol, days = 90) => {
    try {
      const response = await axios.get(`${API_URL}/${cryptoSymbol}`, {
        params: { days },
        headers: authService.getAuthHeader(),
      });
      return { success: true, data: response.data };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Erreur lors de la récupération des prévisions',
      };
    }
  },

  getTechnicalIndicators: async (cryptoSymbol, days = 90) => {
    try {
      const response = await axios.get(`${API_URL}/indicators/${cryptoSymbol}`, {
        params: { days },
        headers: authService.getAuthHeader(),
      });
      return response.data;
    } catch (error) {
      console.error('Erreur indicateurs techniques:', error);
      return {
        error: error.response?.data?.detail || 'Erreur lors du chargement des indicateurs',
        crypto_symbol: cryptoSymbol
      };
    }
  },
};

export default predictionService;
