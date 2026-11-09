import React, { useState, useEffect } from 'react';
import {
  Cpu,
  Bot,
  Key,
  Server,
  Plus,
  Trash2,
  CheckCircle2,
  AlertCircle,
  Clock,
  Sparkles,
  ExternalLink,
  Shield,
  RefreshCw,
} from 'lucide-react';
import { api } from '../services/api';
import { AIProviderSetting, SystemPrompt } from '../types';

export const AISettingsPage: React.FC = () => {
  const [providers, setProviders] = useState<AIProviderSetting[]>([]);
  const [prompts, setPrompts] = useState<SystemPrompt[]>([]);
  const [loading, setLoading] = useState(true);

  // Active testing state
  const [testingId, setTestingId] = useState<number | null>(null);
  const [testResult, setTestResult] = useState<{ id: number; success: boolean; message: string; latency_ms?: number } | null>(null);

  // Form states for provider edit
  const [activeTab, setActiveTab] = useState<'providers' | 'prompts'>('providers');
  const [editingProvider, setEditingProvider] = useState<AIProviderSetting | null>(null);
  const [apiKeyInput, setApiKeyInput] = useState('');

  // Form states for prompt creation / editing
  const [showPromptModal, setShowPromptModal] = useState(false);
  const [promptForm, setPromptForm] = useState({
    id: 0,
    name: '',
    description: '',
    category: 'general',
    content: '',
    is_default: false,
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [provs, prmpts] = await Promise.all([api.getProviders(), api.getPrompts()]);
      setProviders(provs);
      setPrompts(prmpts);
      if (provs.length > 0 && !editingProvider) {
        setEditingProvider(provs[0]);
      }
    } catch (err) {
      console.error('Failed to load settings data', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectProvider = (p: AIProviderSetting) => {
    setEditingProvider(p);
    setApiKeyInput('');
    setTestResult(null);
  };

  const handleSaveProvider = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingProvider) return;

    try {
      const updateData: any = {
        name: editingProvider.name,
        base_url: editingProvider.base_url,
        model_name: editingProvider.model_name,
        temperature: editingProvider.temperature,
        max_tokens: editingProvider.max_tokens,
      };
      if (apiKeyInput.trim()) {
        updateData.api_key = apiKeyInput.trim();
      }

      const updated = await api.updateProvider(editingProvider.id, updateData);
      setProviders((prev) => prev.map((p) => (p.id === updated.id ? updated : p)));
      setEditingProvider(updated);
      setApiKeyInput('');
      alert('Paramètres du fournisseur IA sauvegardés avec succès !');
    } catch (err: any) {
      alert(`Erreur de sauvegarde: ${err.message}`);
    }
  };

  const handleActivateProvider = async (id: number) => {
    try {
      const activated = await api.activateProvider(id);
      setProviders((prev) =>
        prev.map((p) => ({ ...p, is_active: p.id === activated.id }))
      );
      if (editingProvider?.id === id) {
        setEditingProvider(activated);
      }
    } catch (err: any) {
      alert(`Erreur d'activation: ${err.message}`);
    }
  };

  const handleTestConnection = async (p: AIProviderSetting) => {
    setTestingId(p.id);
    setTestResult(null);
    try {
      const res = await api.testProvider({
        provider_type: p.provider_type,
        base_url: p.base_url,
        api_key: apiKeyInput.trim() || undefined,
        model_name: p.model_name,
      });
      setTestResult({
        id: p.id,
        success: res.success,
        message: res.message,
        latency_ms: res.latency_ms,
      });
    } catch (err: any) {
      setTestResult({
        id: p.id,
        success: false,
        message: `Erreur: ${err.message}`,
      });
    } finally {
      setTestingId(null);
    }
  };

  const handleOpenPromptModal = (prompt?: SystemPrompt) => {
    if (prompt) {
      setPromptForm({
        id: prompt.id,
        name: prompt.name,
        description: prompt.description || '',
        category: prompt.category,
        content: prompt.content,
        is_default: prompt.is_default,
      });
    } else {
      setPromptForm({
        id: 0,
        name: '',
        description: '',
        category: 'general',
        content: '',
        is_default: false,
      });
    }
    setShowPromptModal(true);
  };

  const handleSavePrompt = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (promptForm.id) {
        const updated = await api.updatePrompt(promptForm.id, promptForm);
        setPrompts((prev) => prev.map((p) => (p.id === updated.id ? updated : p)));
      } else {
        const created = await api.createPrompt(promptForm);
        setPrompts((prev) => [...prev, created]);
      }
      setShowPromptModal(false);
    } catch (err: any) {
      alert(`Erreur prompt: ${err.message}`);
    }
  };

  const handleDeletePrompt = async (id: number) => {
    if (!confirm('Êtes-vous sûr de vouloir supprimer ce profil de prompt ?')) return;
    try {
      await api.deletePrompt(id);
      setPrompts((prev) => prev.filter((p) => p.id !== id));
    } catch (err: any) {
      alert(err.message);
    }
  };

  const handleSetDefaultPrompt = async (id: number) => {
    try {
      const updated = await api.setDefaultPrompt(id);
      setPrompts((prev) =>
        prev.map((p) => ({ ...p, is_default: p.id === updated.id }))
      );
    } catch (err: any) {
      alert(err.message);
    }
  };

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      {/* Top Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-slate-900 tracking-tight">Paramètres IA & Moteurs LLM</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Gérez vos clés API, basculez entre les API Cloud gratuites et le modèle local Ollama 100% confidentiel.
          </p>
        </div>

        {/* Tab Toggle */}
        <div className="flex p-1 rounded-xl bg-slate-100 border border-slate-200">
          <button
            onClick={() => setActiveTab('providers')}
            className={`flex items-center gap-2 px-4 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
              activeTab === 'providers' ? 'bg-white text-blue-600 shadow-xs' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <Cpu className="w-4 h-4" />
            Fournisseurs IA
          </button>
          <button
            onClick={() => setActiveTab('prompts')}
            className={`flex items-center gap-2 px-4 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
              activeTab === 'prompts' ? 'bg-white text-blue-600 shadow-xs' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <Bot className="w-4 h-4" />
            Prompts Système ({prompts.length})
          </button>
        </div>
      </div>

      {activeTab === 'providers' ? (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column: Providers List */}
          <div className="space-y-3">
            <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider">Fournisseurs Configurés</h3>
            {providers.map((p) => {
              const isSelected = editingProvider?.id === p.id;
              return (
                <div
                  key={p.id}
                  onClick={() => handleSelectProvider(p)}
                  className={`p-4 rounded-xl border transition-all cursor-pointer ${
                    isSelected
                      ? 'bg-blue-50/50 border-blue-500 ring-1 ring-blue-500/20'
                      : 'bg-white border-slate-200 hover:border-slate-300'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-semibold text-sm text-slate-900">{p.name}</span>
                        {p.is_active && (
                          <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-200">
                            Actif
                          </span>
                        )}
                      </div>
                      <p className="text-xs text-slate-500 mt-1 font-mono truncate max-w-[200px]">
                        {p.model_name}
                      </p>
                    </div>

                    <span className="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded bg-slate-100 text-slate-600">
                      {p.provider_type}
                    </span>
                  </div>

                  <div className="mt-3 pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
                    <span className="text-slate-400 text-[11px]">
                      {p.provider_type === 'ollama' ? 'Hors-Ligne' : p.has_api_key ? 'Clé configurée' : 'Pas de clé'}
                    </span>
                    {!p.is_active && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleActivateProvider(p.id);
                        }}
                        className="text-xs font-semibold text-blue-600 hover:text-blue-800 cursor-pointer"
                      >
                        Activer
                      </button>
                    )}
                  </div>
                </div>
              );
            })}

            {/* Offline Ollama Callout */}
            <div className="p-4 rounded-xl bg-slate-900 text-slate-200 text-xs space-y-2 border border-slate-800">
              <div className="flex items-center gap-2 font-bold text-white">
                <Shield className="w-4 h-4 text-emerald-400" />
                Confidentialité 100% Locale
              </div>
              <p className="text-slate-400 text-[11px] leading-relaxed">
                Activez <strong>Ollama Local</strong> pour analyser vos documents sans transmettre le moindre octet à des serveurs tiers.
                Idéal pour les pièces financières et réponses d'appels d'offres confidentielles.
              </p>
            </div>
          </div>

          {/* Right Column: Configuration & Test */}
          <div className="lg:col-span-2 bg-white rounded-xl border border-slate-200 p-6 shadow-xs">
            {editingProvider ? (
              <form onSubmit={handleSaveProvider} className="space-y-6">
                <div className="flex items-center justify-between border-b border-slate-200 pb-4">
                  <div>
                    <h3 className="font-bold text-slate-900 text-base">{editingProvider.name}</h3>
                    <p className="text-xs text-slate-500">Type : {editingProvider.provider_type}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    {!editingProvider.is_active && (
                      <button
                        type="button"
                        onClick={() => handleActivateProvider(editingProvider.id)}
                        className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200 hover:bg-emerald-100 cursor-pointer"
                      >
                        Définir comme Actif
                      </button>
                    )}
                    <button
                      type="button"
                      disabled={testingId === editingProvider.id}
                      onClick={() => handleTestConnection(editingProvider)}
                      className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-100 text-slate-700 hover:bg-slate-200 cursor-pointer"
                    >
                      <RefreshCw className={`w-3.5 h-3.5 ${testingId === editingProvider.id ? 'animate-spin' : ''}`} />
                      Tester la Connexion
                    </button>
                  </div>
                </div>

                {/* Test Result Message Box */}
                {testResult && testResult.id === editingProvider.id && (
                  <div
                    className={`p-3 rounded-lg text-xs flex items-start gap-2.5 border ${
                      testResult.success
                        ? 'bg-emerald-50 text-emerald-900 border-emerald-200'
                        : 'bg-amber-50 text-amber-900 border-amber-200'
                    }`}
                  >
                    {testResult.success ? (
                      <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                    ) : (
                      <AlertCircle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
                    )}
                    <div>
                      <div className="font-semibold">{testResult.message}</div>
                      {testResult.latency_ms && (
                        <div className="text-[11px] opacity-80 mt-0.5">Latence mesurée : {testResult.latency_ms} ms</div>
                      )}
                    </div>
                  </div>
                )}

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1">Nom d'affichage</label>
                    <input
                      type="text"
                      value={editingProvider.name}
                      onChange={(e) => setEditingProvider({ ...editingProvider, name: e.target.value })}
                      className="w-full text-xs bg-slate-50 border border-slate-300 rounded-lg p-2.5 text-slate-900 focus:bg-white focus:ring-2 focus:ring-blue-500"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1">Base URL de l'API</label>
                    <input
                      type="text"
                      value={editingProvider.base_url}
                      onChange={(e) => setEditingProvider({ ...editingProvider, base_url: e.target.value })}
                      className="w-full text-xs font-mono bg-slate-50 border border-slate-300 rounded-lg p-2.5 text-slate-900 focus:bg-white focus:ring-2 focus:ring-blue-500"
                      required
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Identifiant du Modèle (Model ID)</label>
                  <input
                    type="text"
                    value={editingProvider.model_name}
                    onChange={(e) => setEditingProvider({ ...editingProvider, model_name: e.target.value })}
                    className="w-full text-xs font-mono bg-slate-50 border border-slate-300 rounded-lg p-2.5 text-slate-900 focus:bg-white focus:ring-2 focus:ring-blue-500"
                    placeholder="ex: meta-llama/llama-3.3-70b-instruct:free ou llama3.2"
                    required
                  />
                  <p className="text-[11px] text-slate-400 mt-1">
                    Pour Ollama, utilisez le nom téléchargé (ex: `llama3.2`, `mistral`, `qwen2.5`).
                  </p>
                </div>

                {editingProvider.provider_type !== 'ollama' && (
                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1">
                      Clé API Secrète
                    </label>
                    <div className="relative">
                      <input
                        type="password"
                        value={apiKeyInput}
                        onChange={(e) => setApiKeyInput(e.target.value)}
                        placeholder={
                          editingProvider.has_api_key
                            ? `Clé active (${editingProvider.masked_key}). Entrez une nouvelle clé pour modifier.`
                            : 'Entrez votre clé API (ex: sk-...)'
                        }
                        className="w-full text-xs font-mono bg-slate-50 border border-slate-300 rounded-lg p-2.5 pr-10 text-slate-900 focus:bg-white focus:ring-2 focus:ring-blue-500"
                      />
                      <Key className="w-4 h-4 text-slate-400 absolute right-3 top-3 pointer-events-none" />
                    </div>
                    <p className="text-[11px] text-slate-400 mt-1">
                      Les clés API sont stockées localement de manière sécurisée et ne sont jamais exposées en clair.
                    </p>
                  </div>
                )}

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1">
                      Température : {editingProvider.temperature}
                    </label>
                    <input
                      type="range"
                      min="0.0"
                      max="1.0"
                      step="0.05"
                      value={editingProvider.temperature}
                      onChange={(e) =>
                        setEditingProvider({ ...editingProvider, temperature: parseFloat(e.target.value) })
                      }
                      className="w-full"
                    />
                    <div className="flex justify-between text-[10px] text-slate-400 mt-0.5">
                      <span>0.0 (Factuel & Précis)</span>
                      <span>1.0 (Créatif)</span>
                    </div>
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1">Tokens Maximum</label>
                    <input
                      type="number"
                      value={editingProvider.max_tokens}
                      onChange={(e) =>
                        setEditingProvider({ ...editingProvider, max_tokens: parseInt(e.target.value) || 2048 })
                      }
                      className="w-full text-xs bg-slate-50 border border-slate-300 rounded-lg p-2 text-slate-900"
                    />
                  </div>
                </div>

                <div className="pt-4 border-t border-slate-200 flex justify-end">
                  <button
                    type="submit"
                    className="bg-blue-600 hover:bg-blue-700 text-white px-5 py-2.5 rounded-lg text-xs font-semibold shadow-xs cursor-pointer"
                  >
                    Enregistrer les Modifications
                  </button>
                </div>
              </form>
            ) : (
              <div className="text-center py-12 text-slate-400 text-xs">Sélectionnez un fournisseur à gauche.</div>
            )}
          </div>
        </div>
      ) : (
        /* Prompts Management Tab */
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-bold text-slate-900 text-base">Profils de Prompts Système</h3>
              <p className="text-xs text-slate-500">
                Personnalisez les directives de comportement de l'assistant selon la nature des documents à traiter.
              </p>
            </div>
            <button
              onClick={() => handleOpenPromptModal()}
              className="flex items-center gap-1.5 bg-blue-600 hover:bg-blue-700 text-white px-3.5 py-2 rounded-lg text-xs font-semibold shadow-xs cursor-pointer"
            >
              <Plus className="w-4 h-4" />
              Nouveau Profil de Prompt
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {prompts.map((p) => (
              <div
                key={p.id}
                className={`bg-white rounded-xl border p-5 flex flex-col justify-between shadow-xs ${
                  p.is_default ? 'border-blue-500 ring-1 ring-blue-500/20' : 'border-slate-200'
                }`}
              >
                <div>
                  <div className="flex items-start justify-between gap-2 mb-2">
                    <h4 className="font-bold text-sm text-slate-900">{p.name}</h4>
                    {p.is_default && (
                      <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-blue-100 text-blue-800">
                        Par Défaut
                      </span>
                    )}
                  </div>
                  <span className="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded bg-slate-100 text-slate-600">
                    {p.category}
                  </span>
                  <p className="text-xs text-slate-500 mt-2 line-clamp-2">
                    {p.description || 'Aucune description fournie.'}
                  </p>
                  <div className="mt-3 bg-slate-50 p-2.5 rounded-lg border border-slate-100 text-[11px] text-slate-700 font-mono line-clamp-3 whitespace-pre-wrap">
                    {p.content}
                  </div>
                </div>

                <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => handleOpenPromptModal(p)}
                      className="font-medium text-blue-600 hover:underline cursor-pointer"
                    >
                      Modifier
                    </button>
                    {!p.is_default && (
                      <button
                        onClick={() => handleDeletePrompt(p.id)}
                        className="text-rose-600 hover:text-rose-800 cursor-pointer"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    )}
                  </div>
                  {!p.is_default && (
                    <button
                      onClick={() => handleSetDefaultPrompt(p.id)}
                      className="text-slate-600 hover:text-slate-900 font-medium cursor-pointer"
                    >
                      Définir par défaut
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Prompt Create / Edit Modal */}
      {showPromptModal && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl max-w-xl w-full p-6 shadow-xl border border-slate-200 space-y-4">
            <h3 className="font-bold text-slate-900 text-base">
              {promptForm.id ? 'Modifier le Prompt Système' : 'Créer un Profil de Prompt Système'}
            </h3>

            <form onSubmit={handleSavePrompt} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Titre du Profil</label>
                <input
                  type="text"
                  value={promptForm.name}
                  onChange={(e) => setPromptForm({ ...promptForm, name: e.target.value })}
                  className="w-full text-xs bg-slate-50 border border-slate-300 rounded-lg p-2.5 text-slate-900"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Catégorie</label>
                  <select
                    value={promptForm.category}
                    onChange={(e) => setPromptForm({ ...promptForm, category: e.target.value })}
                    className="w-full text-xs bg-slate-50 border border-slate-300 rounded-lg p-2.5 text-slate-900"
                  >
                    <option value="general">Général</option>
                    <option value="procurement">Appels d'Offres & Marchés</option>
                    <option value="financial">Financier & Comptable</option>
                    <option value="administrative">Administratif</option>
                    <option value="legal">Juridique & Contrats</option>
                    <option value="hr">Ressources Humaines</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Description courte</label>
                  <input
                    type="text"
                    value={promptForm.description}
                    onChange={(e) => setPromptForm({ ...promptForm, description: e.target.value })}
                    className="w-full text-xs bg-slate-50 border border-slate-300 rounded-lg p-2.5 text-slate-900"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Contenu du Prompt Système</label>
                <textarea
                  rows={8}
                  value={promptForm.content}
                  onChange={(e) => setPromptForm({ ...promptForm, content: e.target.value })}
                  className="w-full text-xs font-mono bg-slate-50 border border-slate-300 rounded-lg p-3 text-slate-900 focus:bg-white"
                  placeholder="Directives strictes pour l'IA..."
                  required
                />
              </div>

              <div className="flex items-center justify-between pt-3 border-t border-slate-200">
                <button
                  type="button"
                  onClick={() => setShowPromptModal(false)}
                  className="text-xs font-semibold text-slate-600 hover:text-slate-900 cursor-pointer"
                >
                  Annuler
                </button>
                <button
                  type="submit"
                  className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-xs font-semibold cursor-pointer"
                >
                  Sauvegarder le Prompt
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

