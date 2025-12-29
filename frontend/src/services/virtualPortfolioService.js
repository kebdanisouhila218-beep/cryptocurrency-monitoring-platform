import axios from 'axios';
import authService from './authService';

const API_URL = 'http://localhost:8000/virtual-portfolio';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

api.interceptors.request.use(
  (config) => {
    const token = authService.getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

const mapError = (error) => {
  const status = error?.response?.status;
  const detail = error?.response?.data?.detail;

  if (status === 401) {
    return 'Session expirée, veuillez vous reconnecter';
  }
  if (status === 403) {
    return 'Accès refusé à cette ressource';
  }
  if (status === 404) {
    return 'Ressource non trouvée';
  }
  if (status === 400) {
    return detail || 'Requête invalide';
  }
  if (status >= 500) {
    return 'Erreur serveur, veuillez réessayer';
  }

  return detail || "Une erreur s'est produite";
};

const createPortfolio = async (name) => {
  try {
    console.log('[VIRTUAL-PORTFOLIO] Création portfolio:', name);
    const response = await api.post('', { name });
    return { success: true, data: response.data };
  } catch (error) {
    return { success: false, error: mapError(error) };
  }
};

const getAllPortfolios = async () => {
  try {
    const response = await api.get('');
    return { success: true, data: response.data };
  } catch (error) {
    return { success: false, error: mapError(error) };
  }
};

const getPortfolio = async (portfolioId) => {
  try {
    const response = await api.get(`/${portfolioId}`);
    return { success: true, data: response.data };
  } catch (error) {
    return { success: false, error: mapError(error) };
  }
};

const updatePortfolio = async (portfolioId, name) => {
  try {
    const response = await api.put(`/${portfolioId}`, { name });
    return { success: true, data: response.data };
  } catch (error) {
    return { success: false, error: mapError(error) };
  }
};

const deletePortfolio = async (portfolioId) => {
  try {
    const response = await api.delete(`/${portfolioId}`);
    return { success: true, data: response.data };
  } catch (error) {
    return { success: false, error: mapError(error) };
  }
};

const createTransaction = async (portfolioId, transactionData) => {
  try {
    const transactionType = transactionData?.transaction_type;
    const cryptoSymbol = transactionData?.crypto_symbol;
    console.log('[VIRTUAL-PORTFOLIO] Transaction:', transactionType, cryptoSymbol);

    const response = await api.post(`/${portfolioId}/transaction`, transactionData);
    return { success: true, data: response.data };
  } catch (error) {
    return { success: false, error: mapError(error) };
  }
};

const getTransactions = async (portfolioId, transactionType = null) => {
  try {
    const params = new URLSearchParams();
    if (transactionType) {
      params.set('transaction_type', transactionType);
    }

    const query = params.toString();
    const url = query
      ? `/${portfolioId}/transactions?${query}`
      : `/${portfolioId}/transactions`;

    const response = await api.get(url);
    return { success: true, data: response.data };
  } catch (error) {
    return { success: false, error: mapError(error) };
  }
};

const getPerformance = async (portfolioId) => {
  try {
    const response = await api.get(`/${portfolioId}/performance`);
    return { success: true, data: response.data };
  } catch (error) {
    return { success: false, error: mapError(error) };
  }
};

const getAvailableCryptos = async () => {
  try {
    const response = await api.get('/available-cryptos');
    return { success: true, data: response.data };
  } catch (error) {
    return { success: false, error: mapError(error) };
  }
};

const getCryptoPrice = async (symbol) => {
  try {
    const safeSymbol = encodeURIComponent(String(symbol || '').trim());
    const response = await api.get(`/crypto-price/${safeSymbol}`);
    return { success: true, data: response.data };
  } catch (error) {
    return { success: false, error: mapError(error) };
  }
};

const getGlobalStats = async () => {
  try {
    const response = await api.get('/stats/global');
    return { success: true, data: response.data };
  } catch (error) {
    return { success: false, error: mapError(error) };
  }
};

const getPerformanceHistory = async (days = 30) => {
  try {
    const response = await api.get('/performance/history', { params: { days } });
    return { success: true, data: response.data };
  } catch (error) {
    return { success: false, error: mapError(error) };
  }
};

const getPerformanceByCrypto = async () => {
  try {
    const response = await api.get('/performance/by-crypto');
    return { success: true, data: response.data };
  } catch (error) {
    return { success: false, error: mapError(error) };
  }
};

const virtualPortfolioService = {
  createPortfolio,
  getAllPortfolios,
  getPortfolio,
  updatePortfolio,
  deletePortfolio,
  createTransaction,
  getTransactions,
  getPerformance,
  getAvailableCryptos,
  getCryptoPrice,
  getGlobalStats,
  getPerformanceHistory,
  getPerformanceByCrypto
};

export default virtualPortfolioService;
