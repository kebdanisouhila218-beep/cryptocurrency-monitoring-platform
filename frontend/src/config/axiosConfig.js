// frontend/src/config/axiosConfig.js
import axios from 'axios';
import authService from '../services/authService';

// Créer une instance axios personnalisée
const apiClient = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Intercepteur de requête - Ajouter automatiquement le token
apiClient.interceptors.request.use(
  (config) => {
    const token = authService.getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Intercepteur de réponse - Gérer les erreurs automatiquement
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Si erreur 401 (Unauthorized), déconnecter automatiquement
    if (error.response?.status === 401) {
      console.log('❌ Token expiré ou invalide - Déconnexion automatique');
      authService.logout();
      window.location.href = '/login';
    }
    
    // Si erreur 403 (Forbidden)
    if (error.response?.status === 403) {
      console.log('❌ Accès refusé - Permissions insuffisantes');
      // Afficher un message d'erreur ou rediriger
    }

    // Si erreur réseau
    if (!error.response) {
      console.log('❌ Erreur réseau - Vérifier la connexion');
    }

    return Promise.reject(error);
  }
);

export default apiClient;