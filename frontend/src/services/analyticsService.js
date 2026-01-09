// frontend/src/services/analyticsService.js

import axios from 'axios';
import authService from './authService';

const API_URL = 'http://localhost:8000/analytics';

const analyticsService = {
  // Récupérer les cryptos disponibles depuis la DB
  getAvailableCryptos: async () => {
    try {
      const response = await axios.get(`${API_URL}/available-cryptos`, {
        headers: authService.getAuthHeader()
      });
      return { success: true, data: response.data };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Erreur lors de la récupération des cryptos disponibles'
      };
    }
  },

  // Données candlestick (OHLC)
  getCandlestickData: async (cryptoSymbol, interval = '1h', days = 7) => {
    try {
      const response = await axios.get(`${API_URL}/candlestick/${cryptoSymbol}`, {
        params: { interval, days },
        headers: authService.getAuthHeader()
      });
      return { success: true, data: response.data };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Erreur lors de la récupération des données candlestick'
      };
    }
  },

  // Données heatmap
  getHeatmapData: async (period = '24h') => {
    try {
      const response = await axios.get(`${API_URL}/heatmap`, {
        params: { period },
        headers: authService.getAuthHeader()
      });
      return { success: true, data: response.data };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Erreur lors de la récupération de la heatmap'
      };
    }
  },

  // Comparaison multi-cryptos
  compareCryptos: async (symbols, days = 7) => {
    try {
      const response = await axios.post(
        `${API_URL}/compare`,
        symbols,
        {
          params: { days },
          headers: authService.getAuthHeader()
        }
      );
      return { success: true, data: response.data };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Erreur lors de la comparaison'
      };
    }
  },

  // Vue d'ensemble du marché
  getMarketOverview: async () => {
    try {
      const response = await axios.get(`${API_URL}/market-overview`, {
        headers: authService.getAuthHeader()
      });
      return { success: true, data: response.data };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Erreur lors de la récupération de l\'overview'
      };
    }
  }
};

export default analyticsService;
