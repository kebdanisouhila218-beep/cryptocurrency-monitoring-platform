// Portfolio service - API calls for portfolio management
import axios from 'axios';
import authService from './authService';

const API_URL = 'http://localhost:8000';

const portfolioService = {
  // Get all portfolios for the current user
  getPortfolios: async () => {
    try {
      const response = await axios.get(`${API_URL}/portfolio`, {
        headers: authService.getAuthHeader()
      });
      return { success: true, data: response.data };
    } catch (error) {
      console.error('Error fetching portfolios:', error);
      if (error.response?.status === 401) {
        authService.logout();
        window.location.href = '/login';
      }
      return {
        success: false,
        error: error.response?.data?.detail || 'Erreur lors de la récupération des portefeuilles'
      };
    }
  },

  // Get a specific portfolio by ID
  getPortfolio: async (portfolioId) => {
    try {
      const response = await axios.get(`${API_URL}/portfolio/${portfolioId}`, {
        headers: authService.getAuthHeader()
      });
      return { success: true, data: response.data };
    } catch (error) {
      console.error('Error fetching portfolio:', error);
      if (error.response?.status === 401) {
        authService.logout();
        window.location.href = '/login';
      }
      return {
        success: false,
        error: error.response?.data?.detail || 'Erreur lors de la récupération du portefeuille'
      };
    }
  },

  // Create a new portfolio
  createPortfolio: async (portfolioData) => {
    try {
      const response = await axios.post(`${API_URL}/portfolio`, portfolioData, {
        headers: {
          ...authService.getAuthHeader(),
          'Content-Type': 'application/json'
        }
      });
      return { success: true, data: response.data };
    } catch (error) {
      console.error('Error creating portfolio:', error);
      return {
        success: false,
        error: error.response?.data?.detail || 'Erreur lors de la création du portefeuille'
      };
    }
  },

  // Update a portfolio
  updatePortfolio: async (portfolioId, portfolioData) => {
    try {
      const response = await axios.put(`${API_URL}/portfolio/${portfolioId}`, portfolioData, {
        headers: {
          ...authService.getAuthHeader(),
          'Content-Type': 'application/json'
        }
      });
      return { success: true, data: response.data };
    } catch (error) {
      console.error('Error updating portfolio:', error);
      return {
        success: false,
        error: error.response?.data?.detail || 'Erreur lors de la mise à jour du portefeuille'
      };
    }
  },

  // Delete a portfolio
  deletePortfolio: async (portfolioId) => {
    try {
      await axios.delete(`${API_URL}/portfolio/${portfolioId}`, {
        headers: authService.getAuthHeader()
      });
      return { success: true };
    } catch (error) {
      console.error('Error deleting portfolio:', error);
      return {
        success: false,
        error: error.response?.data?.detail || 'Erreur lors de la suppression du portefeuille'
      };
    }
  },

  // Get positions in a portfolio
  getPositions: async (portfolioId) => {
    try {
      const response = await axios.get(`${API_URL}/portfolio/${portfolioId}/positions`, {
        headers: authService.getAuthHeader()
      });
      return { success: true, data: response.data };
    } catch (error) {
      console.error('Error fetching positions:', error);
      if (error.response?.status === 401) {
        authService.logout();
        window.location.href = '/login';
      }
      return {
        success: false,
        error: error.response?.data?.detail || 'Erreur lors de la récupération des positions'
      };
    }
  },

  // Get transactions for a portfolio
  getTransactions: async (portfolioId) => {
    try {
      const response = await axios.get(`${API_URL}/portfolio/${portfolioId}/transactions`, {
        headers: authService.getAuthHeader()
      });
      return { success: true, data: response.data };
    } catch (error) {
      console.error('Error fetching transactions:', error);
      if (error.response?.status === 401) {
        authService.logout();
        window.location.href = '/login';
      }
      return {
        success: false,
        error: error.response?.data?.detail || 'Erreur lors de la récupération des transactions'
      };
    }
  },

  // Execute a trade (buy or sell)
  executeTrade: async (portfolioId, tradeData) => {
    try {
      const response = await axios.post(`${API_URL}/portfolio/${portfolioId}/trade`, tradeData, {
        headers: {
          ...authService.getAuthHeader(),
          'Content-Type': 'application/json'
        }
      });
      return { success: true, data: response.data };
    } catch (error) {
      console.error('Error executing trade:', error);
      return {
        success: false,
        error: error.response?.data?.detail || 'Erreur lors de l\'exécution de la transaction'
      };
    }
  },

  // Get portfolio statistics
  getPortfolioStats: async (portfolioId) => {
    try {
      const response = await axios.get(`${API_URL}/portfolio/${portfolioId}/stats`, {
        headers: authService.getAuthHeader()
      });
      return { success: true, data: response.data };
    } catch (error) {
      console.error('Error fetching portfolio stats:', error);
      if (error.response?.status === 401) {
        authService.logout();
        window.location.href = '/login';
      }
      return {
        success: false,
        error: error.response?.data?.detail || 'Erreur lors de la récupération des statistiques'
      };
    }
  },

  // Get portfolio allocation
  getPortfolioAllocation: async (portfolioId) => {
    try {
      const response = await axios.get(`${API_URL}/portfolio/${portfolioId}/allocation`, {
        headers: authService.getAuthHeader()
      });
      return { success: true, data: response.data };
    } catch (error) {
      console.error('Error fetching portfolio allocation:', error);
      if (error.response?.status === 401) {
        authService.logout();
        window.location.href = '/login';
      }
      return {
        success: false,
        error: error.response?.data?.detail || 'Erreur lors de la récupération de l\'allocation'
      };
    }
  },

  // Get portfolio performance
  getPortfolioPerformance: async (portfolioId, days = 30) => {
    try {
      const response = await axios.get(`${API_URL}/portfolio/${portfolioId}/performance?days=${days}`, {
        headers: authService.getAuthHeader()
      });
      return { success: true, data: response.data };
    } catch (error) {
      console.error('Error fetching portfolio performance:', error);
      if (error.response?.status === 401) {
        authService.logout();
        window.location.href = '/login';
      }
      return {
        success: false,
        error: error.response?.data?.detail || 'Erreur lors de la récupération de la performance'
      };
    }
  }
};

export default portfolioService;
