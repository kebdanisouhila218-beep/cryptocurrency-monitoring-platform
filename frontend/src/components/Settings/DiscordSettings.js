// frontend/src/components/Settings/DiscordSettings.js - Configuration du webhook Discord

import React, { useState, useEffect } from 'react';
import profileService from '../../services/profileService';
import './DiscordSettings.css';

const DiscordSettings = () => {
  const [webhookUrl, setWebhookUrl] = useState('');
  const [isConfigured, setIsConfigured] = useState(false);
  const [maskedUrl, setMaskedUrl] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });
  const [showInput, setShowInput] = useState(false);

  useEffect(() => {
    loadDiscordConfig();
  }, []);

  const loadDiscordConfig = async () => {
    setLoading(true);
    const result = await profileService.getDiscordConfig();
    if (result.success) {
      setIsConfigured(result.data.is_configured);
      setMaskedUrl(result.data.discord_webhook_url || '');
    }
    setLoading(false);
  };

  const handleSave = async () => {
    // Validation côté client
    if (webhookUrl && !profileService.validateWebhookUrl(webhookUrl)) {
      setMessage({
        type: 'error',
        text: 'URL invalide. Format attendu: https://discord.com/api/webhooks/...'
      });
      return;
    }

    setSaving(true);
    setMessage({ type: '', text: '' });

    const result = await profileService.updateDiscordWebhook(webhookUrl);
    
    if (result.success) {
      setIsConfigured(result.data.is_configured);
      setMaskedUrl(result.data.discord_webhook_url || '');
      setWebhookUrl('');
      setShowInput(false);
      setMessage({
        type: 'success',
        text: webhookUrl 
          ? '✅ Webhook Discord configuré avec succès !' 
          : '✅ Webhook Discord supprimé.'
      });
    } else {
      setMessage({
        type: 'error',
        text: `❌ ${result.error}`
      });
    }

    setSaving(false);
  };

  const handleDelete = async () => {
    if (!window.confirm('Êtes-vous sûr de vouloir supprimer le webhook Discord ?')) {
      return;
    }

    setSaving(true);
    const result = await profileService.deleteDiscordWebhook();
    
    if (result.success) {
      setIsConfigured(false);
      setMaskedUrl('');
      setWebhookUrl('');
      setMessage({
        type: 'success',
        text: '✅ Webhook Discord supprimé.'
      });
    } else {
      setMessage({
        type: 'error',
        text: `❌ ${result.error}`
      });
    }

    setSaving(false);
  };

  const handleTest = async () => {
    setTesting(true);
    setMessage({ type: '', text: '' });

    const result = await profileService.testDiscordWebhook();
    
    if (result.success && result.data.success) {
      setMessage({
        type: 'success',
        text: '✅ Message de test envoyé ! Vérifiez votre canal Discord.'
      });
    } else {
      setMessage({
        type: 'error',
        text: `❌ ${result.data?.message || result.error}`
      });
    }

    setTesting(false);
  };

  if (loading) {
    return (
      <div className="discord-settings">
        <div className="loading">⏳ Chargement...</div>
      </div>
    );
  }

  return (
    <div className="discord-settings">
      <div className="discord-header">
        <div className="discord-icon">🎮</div>
        <div className="discord-title">
          <h3>Notifications Discord</h3>
          <p>Recevez les alertes de prix directement sur Discord</p>
        </div>
      </div>

      {message.text && (
        <div className={`message ${message.type}`}>
          {message.text}
        </div>
      )}

      <div className="discord-status">
        <span className={`status-badge ${isConfigured ? 'configured' : 'not-configured'}`}>
          {isConfigured ? '✅ Configuré' : '⚪ Non configuré'}
        </span>
        {isConfigured && maskedUrl && (
          <span className="masked-url">{maskedUrl}</span>
        )}
      </div>

      {!showInput && !isConfigured && (
        <button 
          className="btn-configure"
          onClick={() => setShowInput(true)}
        >
          🔧 Configurer Discord
        </button>
      )}

      {(showInput || isConfigured) && (
        <div className="webhook-form">
          {showInput && (
            <>
              <label htmlFor="webhook-url">URL du Webhook Discord</label>
              <input
                id="webhook-url"
                type="url"
                value={webhookUrl}
                onChange={(e) => setWebhookUrl(e.target.value)}
                placeholder="https://discord.com/api/webhooks/..."
                disabled={saving}
              />
              <p className="help-text">
                💡 Pour créer un webhook : Paramètres du serveur → Intégrations → Webhooks → Nouveau webhook
              </p>
            </>
          )}

          <div className="button-group">
            {showInput && (
              <>
                <button 
                  className="btn-save"
                  onClick={handleSave}
                  disabled={saving}
                >
                  {saving ? '⏳ Enregistrement...' : '💾 Enregistrer'}
                </button>
                <button 
                  className="btn-cancel"
                  onClick={() => {
                    setShowInput(false);
                    setWebhookUrl('');
                    setMessage({ type: '', text: '' });
                  }}
                  disabled={saving}
                >
                  Annuler
                </button>
              </>
            )}

            {isConfigured && !showInput && (
              <>
                <button 
                  className="btn-test"
                  onClick={handleTest}
                  disabled={testing}
                >
                  {testing ? '⏳ Test...' : '🧪 Tester'}
                </button>
                <button 
                  className="btn-modify"
                  onClick={() => setShowInput(true)}
                >
                  ✏️ Modifier
                </button>
                <button 
                  className="btn-delete"
                  onClick={handleDelete}
                  disabled={saving}
                >
                  🗑️ Supprimer
                </button>
              </>
            )}
          </div>
        </div>
      )}

      <div className="discord-info">
        <h4>📋 Comment ça marche ?</h4>
        <ol>
          <li>Créez un webhook dans les paramètres de votre serveur Discord</li>
          <li>Copiez l'URL du webhook et collez-la ci-dessus</li>
          <li>Testez la connexion avec le bouton "Tester"</li>
          <li>Quand une alerte se déclenche, vous recevrez une notification Discord !</li>
        </ol>
      </div>
    </div>
  );
};

export default DiscordSettings;
