// frontend/src/components/Toast.js
import React, { useState, useEffect } from 'react';
import './Toast.css';

let toastInstance = null;

const Toast = () => {
  const [toasts, setToasts] = useState([]);

  useEffect(() => {
    toastInstance = {
      success: (message) => addToast(message, 'success'),
      error: (message) => addToast(message, 'error'),
      info: (message) => addToast(message, 'info'),
      warning: (message) => addToast(message, 'warning'),
    };
  }, []);

  const addToast = (message, type) => {
    const id = Date.now();
    const newToast = { id, message, type };
    
    setToasts((prev) => [...prev, newToast]);

    // Auto-dismiss après 4 secondes
    setTimeout(() => {
      removeToast(id);
    }, 4000);
  };

  const removeToast = (id) => {
    setToasts((prev) => prev.filter((toast) => toast.id !== id));
  };

  const getIcon = (type) => {
    switch (type) {
      case 'success':
        return '✅';
      case 'error':
        return '❌';
      case 'warning':
        return '⚠️';
      case 'info':
        return 'ℹ️';
      default:
        return '📢';
    }
  };

  return (
    <div className="toast-container">
      {toasts.map((toast) => (
        <div
          key={toast.id}
          className={`toast toast-${toast.type}`}
          onClick={() => removeToast(toast.id)}
        >
          <span className="toast-icon">{getIcon(toast.type)}</span>
          <span className="toast-message">{toast.message}</span>
          <button className="toast-close" onClick={() => removeToast(toast.id)}>
            ✕
          </button>
        </div>
      ))}
    </div>
  );
};

// Export des fonctions helper
export const toast = {
  success: (message) => toastInstance?.success(message),
  error: (message) => toastInstance?.error(message),
  info: (message) => toastInstance?.info(message),
  warning: (message) => toastInstance?.warning(message),
};

export default Toast;