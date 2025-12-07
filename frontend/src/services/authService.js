// frontend/src/services/authService.js
import axios from 'axios';

const API_URL = 'http://127.0.0.1:8000/auth';

// Créer une instance axios avec config par défaut
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

const authService = {
  // Inscription
  register: async (username, email, password) => {
    try {
      const response = await api.post('/register', {
        username,
        email,
        password
      });
      return { success: true, data: response.data };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Erreur lors de l\'inscription'
      };
    }
  },

  // Connexion
  login: async (username, password) => {
    try {
      const formData = new URLSearchParams();
      formData.append('username', username);
      formData.append('password', password);

      const response = await axios.post(`${API_URL}/login`, formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      });

      if (response.data.access_token) {
        // Stocker le token et les infos utilisateur
        localStorage.setItem('token', response.data.access_token);
        localStorage.setItem('username', username);
        return { success: true, data: response.data };
      }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Identifiants incorrects'
      };
    }
  },

  // Déconnexion
  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    localStorage.removeItem('userInfo');
  },

  // Récupérer le token
  getToken: () => {
    return localStorage.getItem('token');
  },

  // Récupérer le nom d'utilisateur
  getUsername: () => {
    return localStorage.getItem('username');
  },

  // Vérifier si l'utilisateur est connecté
  isAuthenticated: () => {
    const token = localStorage.getItem('token');
    if (!token) return false;

    // Vérifier si le token n'est pas expiré
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      const expiry = payload.exp * 1000; // Convertir en millisecondes
      return Date.now() < expiry;
    } catch (error) {
      return false;
    }
  },

  // Récupérer les infos de l'utilisateur connecté
  getCurrentUser: async () => {
    const token = authService.getToken();
    if (!token) return null;

    try {
      const response = await axios.get(`${API_URL}/me`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      localStorage.setItem('userInfo', JSON.stringify(response.data));
      return response.data;
    } catch (error) {
      console.error('Erreur récupération utilisateur:', error);
      return null;
    }
  },

  // Créer un header avec le token pour les requêtes authentifiées
  getAuthHeader: () => {
    const token = authService.getToken();
    return token ? { Authorization: `Bearer ${token}` } : {};
  }
};

export default authService;