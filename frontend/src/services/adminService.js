// frontend/src/services/adminService.js - Service pour les fonctionnalités admin

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const getAuthHeaders = () => {
  const token = localStorage.getItem('token');
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  };
};

// ===== STATISTIQUES =====

export const getStats = async () => {
  const response = await fetch(`${API_URL}/admin/stats`, {
    headers: getAuthHeaders()
  });
  if (!response.ok) throw new Error('Failed to fetch stats');
  return response.json();
};

export const getSystemHealth = async () => {
  const response = await fetch(`${API_URL}/admin/system/health`, {
    headers: getAuthHeaders()
  });
  if (!response.ok) throw new Error('Failed to fetch system health');
  return response.json();
};

export const getActivity = async (days = 7) => {
  const response = await fetch(`${API_URL}/admin/system/activity?days=${days}`, {
    headers: getAuthHeaders()
  });
  if (!response.ok) throw new Error('Failed to fetch activity');
  return response.json();
};

// ===== UTILISATEURS =====

export const getUsers = async (skip = 0, limit = 100) => {
  const response = await fetch(`${API_URL}/admin/users?skip=${skip}&limit=${limit}`, {
    headers: getAuthHeaders()
  });
  if (!response.ok) throw new Error('Failed to fetch users');
  return response.json();
};

export const getUser = async (username) => {
  const response = await fetch(`${API_URL}/admin/users/${username}`, {
    headers: getAuthHeaders()
  });
  if (!response.ok) throw new Error('Failed to fetch user');
  return response.json();
};

export const updateUser = async (username, data) => {
  const response = await fetch(`${API_URL}/admin/users/${username}`, {
    method: 'PUT',
    headers: getAuthHeaders(),
    body: JSON.stringify(data)
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to update user');
  }
  return response.json();
};

export const deleteUser = async (username) => {
  const response = await fetch(`${API_URL}/admin/users/${username}`, {
    method: 'DELETE',
    headers: getAuthHeaders()
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to delete user');
  }
  return response.json();
};

export const promoteUser = async (username) => {
  const response = await fetch(`${API_URL}/admin/users/${username}/promote`, {
    method: 'POST',
    headers: getAuthHeaders()
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to promote user');
  }
  return response.json();
};

export const demoteUser = async (username) => {
  const response = await fetch(`${API_URL}/admin/users/${username}/demote`, {
    method: 'POST',
    headers: getAuthHeaders()
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to demote user');
  }
  return response.json();
};

// ===== ALERTES =====

export const getAllAlerts = async (skip = 0, limit = 100, activeOnly = false) => {
  const response = await fetch(
    `${API_URL}/admin/alerts?skip=${skip}&limit=${limit}&active_only=${activeOnly}`,
    { headers: getAuthHeaders() }
  );
  if (!response.ok) throw new Error('Failed to fetch alerts');
  return response.json();
};

export const disableAllAlerts = async () => {
  const response = await fetch(`${API_URL}/admin/alerts/disable-all`, {
    method: 'POST',
    headers: getAuthHeaders()
  });
  if (!response.ok) throw new Error('Failed to disable alerts');
  return response.json();
};

export const deleteAlert = async (alertId) => {
  const response = await fetch(`${API_URL}/admin/alerts/${alertId}`, {
    method: 'DELETE',
    headers: getAuthHeaders()
  });
  if (!response.ok) throw new Error('Failed to delete alert');
  return response.json();
};

// ===== NOTIFICATIONS =====

export const getNotificationLogs = async (skip = 0, limit = 50) => {
  const response = await fetch(
    `${API_URL}/admin/notifications/logs?skip=${skip}&limit=${limit}`,
    { headers: getAuthHeaders() }
  );
  if (!response.ok) throw new Error('Failed to fetch notification logs');
  return response.json();
};

export const sendBroadcast = async (subject, message, sendEmail = true, sendDiscord = true) => {
  const response = await fetch(`${API_URL}/admin/notifications/broadcast`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({
      subject,
      message,
      send_email: sendEmail,
      send_discord: sendDiscord
    })
  });
  if (!response.ok) throw new Error('Failed to send broadcast');
  return response.json();
};

// ===== DONNÉES =====

export const getCollectionsInfo = async () => {
  const response = await fetch(`${API_URL}/admin/data/collections`, {
    headers: getAuthHeaders()
  });
  if (!response.ok) throw new Error('Failed to fetch collections info');
  return response.json();
};

export const deleteOldPrices = async (days = 30) => {
  const response = await fetch(`${API_URL}/admin/data/prices/old?days=${days}`, {
    method: 'DELETE',
    headers: getAuthHeaders()
  });
  if (!response.ok) throw new Error('Failed to delete old prices');
  return response.json();
};

export default {
  getStats,
  getSystemHealth,
  getActivity,
  getUsers,
  getUser,
  updateUser,
  deleteUser,
  promoteUser,
  demoteUser,
  getAllAlerts,
  disableAllAlerts,
  deleteAlert,
  getNotificationLogs,
  sendBroadcast,
  getCollectionsInfo,
  deleteOldPrices
};
