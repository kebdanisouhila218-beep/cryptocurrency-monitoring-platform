// frontend/src/services/alertService.js
import axios from 'axios';
import authService from './authService';

const API_URL = 'http://localhost:8000/alerts';

const alertService = {
  // Créer une nouvelle alerte
  createAlert: async (alertData) => {
    try {
      const response = await axios.post(API_URL, alertData, {
        headers: {
          ...authService.getAuthHeader(),
          'Content-Type': 'application/json'
        }
      });
      return { success: true, data: response.data };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Erreur lors de la création de l\'alerte'
      };
    }
  },

  // Récupérer toutes les alertes de l'utilisateur
  getAllAlerts: async (filters = {}) => {
    try {
      const params = new URLSearchParams();
      if (filters.is_active !== undefined && filters.is_active !== null) {
        params.append('is_active', filters.is_active);
      }
      if (filters.crypto_symbol) {
        params.append('crypto_symbol', filters.crypto_symbol);
      }

      const url = params.toString() ? `${API_URL}?${params.toString()}` : API_URL;
      
      const response = await axios.get(url, {
        headers: authService.getAuthHeader()
      });
      return { success: true, data: response.data };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Erreur lors de la récupération des alertes'
      };
    }
  },

  // Récupérer une alerte par ID
  getAlert: async (alertId) => {
    try {
      const response = await axios.get(`${API_URL}/${alertId}`, {
        headers: authService.getAuthHeader()
      });
      return { success: true, data: response.data };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Erreur lors de la récupération de l\'alerte'
      };
    }
  },

  // Mettre à jour une alerte
  updateAlert: async (alertId, data) => {
    try {
      const response = await axios.put(`${API_URL}/${alertId}`, data, {
        headers: {
          ...authService.getAuthHeader(),
          'Content-Type': 'application/json'
        }
      });
      return { success: true, data: response.data };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Erreur lors de la mise à jour de l\'alerte'
      };
    }
  },

  // Supprimer une alerte
  deleteAlert: async (alertId) => {
    try {
      const response = await axios.delete(`${API_URL}/${alertId}`, {
        headers: authService.getAuthHeader()
      });
      return { success: true, data: response.data };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Erreur lors de la suppression de l\'alerte'
      };
    }
  },

  // Forcer une vérification des alertes
  checkAlertsNow: async () => {
    try {
      const response = await axios.post(`${API_URL}/check-now`, {}, {
        headers: authService.getAuthHeader()
      });
      return { success: true, data: response.data };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Erreur lors de la vérification des alertes'
      };
    }
  },

  // Récupérer les statistiques globales
  getStats: async () => {
    try {
      const response = await axios.get(`${API_URL}/stats/global`, {
        headers: authService.getAuthHeader()
      });
      return { success: true, data: response.data };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Erreur lors de la récupération des statistiques'
      };
    }
  },

  // Debug endpoint
  getDebug: async () => {
    try {
      const response = await axios.get(`${API_URL}/debug`, {
        headers: authService.getAuthHeader()
      });
      return { success: true, data: response.data };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Erreur lors du debug'
      };
    }
  }
};

export default alertService;
