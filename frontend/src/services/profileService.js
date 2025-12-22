// frontend/src/services/profileService.js - Service pour la gestion du profil utilisateur

import axios from 'axios';
import authService from './authService';

const API_URL = 'http://localhost:8000/profile';

const profileService = {
  // Récupérer le profil complet
  getProfile: async () => {
    try {
      const response = await axios.get(API_URL, {
        headers: authService.getAuthHeader()
      });
      return { success: true, data: response.data };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Erreur lors de la récupération du profil'
      };
    }
  },

  // Récupérer la configuration Discord
  getDiscordConfig: async () => {
    try {
      const response = await axios.get(`${API_URL}/discord`, {
        headers: authService.getAuthHeader()
      });
      return { success: true, data: response.data };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Erreur lors de la récupération de la config Discord'
      };
    }
  },

  // Mettre à jour le webhook Discord
  updateDiscordWebhook: async (webhookUrl) => {
    try {
      const response = await axios.put(
        `${API_URL}/discord`,
        { discord_webhook_url: webhookUrl || null },
        { headers: authService.getAuthHeader() }
      );
      return { success: true, data: response.data };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Erreur lors de la mise à jour du webhook'
      };
    }
  },

  // Supprimer le webhook Discord
  deleteDiscordWebhook: async () => {
    try {
      const response = await axios.delete(`${API_URL}/discord`, {
        headers: authService.getAuthHeader()
      });
      return { success: true, data: response.data };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Erreur lors de la suppression du webhook'
      };
    }
  },

  // Tester le webhook Discord
  testDiscordWebhook: async () => {
    try {
      const response = await axios.post(
        `${API_URL}/discord/test`,
        {},
        { headers: authService.getAuthHeader() }
      );
      return { success: true, data: response.data };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Erreur lors du test du webhook'
      };
    }
  },

  // Valider le format d'un webhook Discord (côté client)
  validateWebhookUrl: (url) => {
    if (!url) return true; // Vide est valide (pour supprimer)
    
    const validPrefixes = [
      'https://discord.com/api/webhooks/',
      'https://discordapp.com/api/webhooks/',
      'https://canary.discord.com/api/webhooks/',
      'https://ptb.discord.com/api/webhooks/'
    ];
    
    return validPrefixes.some(prefix => url.startsWith(prefix));
  }
};

export default profileService;
