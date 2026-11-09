import React, { useState, useEffect } from 'react';
import {
  Send,
  Bot,
  User,
  Sparkles,
  Paperclip,
  Check,
  FileText,
  FileCheck2,
  FileSpreadsheet,
  Clock,
  ShieldCheck,
  AlertCircle,
  Copy,
  ChevronRight,
  Download,
} from 'lucide-react';
import { api } from '../services/api';
import { SystemPrompt, AIProviderSetting, DocumentItem, WorkspaceChatResponse } from '../types';

interface WorkspacePageProps {
  onNavigateToGenerate?: (content: string, title?: string) => void;
}

export const WorkspacePage: React.FC<WorkspacePageProps> = ({ onNavigateToGenerate }) => {
  const [prompts, setPrompts] = useState<SystemPrompt[]>([]);
  const [providers, setProviders] = useState<AIProviderSetting[]>([]);
  const [documents, setDocuments] = useState<DocumentItem[]>([]);

  const [selectedPromptId, setSelectedPromptId] = useState<number | undefined>();
  const [selectedProviderId, setSelectedProviderId] = useState<number | undefined>();
  const [selectedDocIds, setSelectedDocIds] = useState<number[]>([]);

  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [chatHistory, setChatHistory] = useState<
    Array<{
      id: string;
      role: 'user' | 'assistant';
      content: string;
      referencedChunks?: any[];
      executionTimeMs?: number;
      modelName?: string;
    }>
  >([]);

  const [copiedId, setCopiedId] = useState<string | null>(null);

  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      const [promptsData, providersData, docsData] = await Promise.all([
        api.getPrompts(),
        api.getProviders(),
        api.getDocuments().catch(() => [] as DocumentItem[]),
      ]);

      setPrompts(promptsData);
      setProviders(providersData);
      setDocuments(docsData);

      // Default prompt
      const defPrompt = promptsData.find((p) => p.is_default) || promptsData[0];
      if (defPrompt) setSelectedPromptId(defPrompt.id);

      // Default provider
      const defProv = providersData.find((p) => p.is_active) || providersData[0];
      if (defProv) setSelectedProviderId(defProv.id);
    } catch (err) {
      console.error('Failed to load workspace data', err);
    }
  };

  const handleToggleDoc = (docId: number) => {
    setSelectedDocIds((prev) =>
      prev.includes(docId) ? prev.filter((id) => id !== docId) : [...prev, docId]
    );
  };

  const handleSendMessage = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!inputMessage.trim() || loading) return;

    const userText = inputMessage.trim();
    const messageId = Date.now().toString();

    // Add user message to UI immediately
    setChatHistory((prev) => [
      ...prev,
      { id: messageId, role: 'user', content: userText },
    ]);
    setInputMessage('');
    setLoading(true);

    try {
      const resp: WorkspaceChatResponse = await api.chatWorkspace({
        message: userText,
        prompt_id: selectedPromptId,
        provider_id: selectedProviderId,
        document_ids: selectedDocIds,
        include_calculations: true,
      });

      setChatHistory((prev) => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: resp.response,
          referencedChunks: resp.referenced_chunks,
          executionTimeMs: resp.execution_time_ms,
          modelName: resp.model_name,
        },
      ]);
    } catch (err: any) {
      setChatHistory((prev) => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: `Erreur d'exécution : ${err.message || 'Impossible de joindre le service IA.'}`,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleCopyText = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const activePrompt = prompts.find((p) => p.id === selectedPromptId);

  return (
    <div className="flex h-[calc(100vh-4rem)] overflow-hidden">
      {/* Left Configuration & Grounding Sidebar */}
      <div className="w-80 bg-slate-50 border-r border-slate-200 p-5 flex flex-col justify-between overflow-y-auto shrink-0">
        <div className="space-y-6">
          <div>
            <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2 flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5 text-blue-600" />
              1. Modèle & Moteur IA
            </h3>
            <select
              value={selectedProviderId ?? ''}
              onChange={(e) => setSelectedProviderId(Number(e.target.value))}
              className="w-full text-xs font-medium bg-white border border-slate-300 rounded-lg p-2.5 text-slate-800 focus:ring-2 focus:ring-blue-500"
            >
              {providers.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name} {p.is_active ? '★ (Actif)' : ''}
                </option>
              ))}
            </select>
          </div>

          <div>
            <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2 flex items-center gap-1.5">
              <Bot className="w-3.5 h-3.5 text-blue-600" />
              2. Profil de Prompt Système
            </h3>
            <select
              value={selectedPromptId ?? ''}
              onChange={(e) => setSelectedPromptId(Number(e.target.value))}
              className="w-full text-xs font-medium bg-white border border-slate-300 rounded-lg p-2.5 text-slate-800 focus:ring-2 focus:ring-blue-500"
            >
              {prompts.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name} ({p.category})
                </option>
              ))}
            </select>
            {activePrompt && (
              <p className="text-[11px] text-slate-500 mt-1.5 line-clamp-2 italic">
                "{activePrompt.description || activePrompt.content.slice(0, 80)}..."
              </p>
            )}
          </div>

          <div>
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
                <Paperclip className="w-3.5 h-3.5 text-blue-600" />
                3. Documents de Référence ({selectedDocIds.length} actif)
              </h3>
            </div>

            {documents.length === 0 ? (
              <div className="p-3 text-center border border-dashed border-slate-300 rounded-lg bg-white">
                <FileText className="w-6 h-6 text-slate-400 mx-auto mb-1" />
                <p className="text-xs text-slate-600">Aucun document chargé.</p>
                <p className="text-[10px] text-slate-400 mt-0.5">
                  Importez des PDF ou Excel dans l'onglet "Mes Documents".
                </p>
              </div>
            ) : (
              <div className="max-h-56 overflow-y-auto space-y-1.5 bg-white border border-slate-200 rounded-lg p-2">
                {documents.map((doc) => {
                  const isChecked = selectedDocIds.includes(doc.id);
                  return (
                    <div
                      key={doc.id}
                      onClick={() => handleToggleDoc(doc.id)}
                      className={`flex items-center justify-between p-2 rounded text-xs cursor-pointer transition-colors ${
                        isChecked
                          ? 'bg-blue-50 text-blue-900 font-medium border border-blue-200'
                          : 'hover:bg-slate-50 text-slate-700'
                      }`}
                    >
                      <div className="flex items-center gap-2 overflow-hidden">
                        <input
                          type="checkbox"
                          checked={isChecked}
                          onChange={() => {}}
                          className="rounded text-blue-600 focus:ring-blue-500"
                        />
                        <span className="truncate" title={doc.original_filename}>
                          {doc.original_filename}
                        </span>
                      </div>
                      <span className="text-[10px] uppercase font-mono px-1 py-0.5 rounded bg-slate-100 text-slate-500 shrink-0">
                        {doc.file_type}
                      </span>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>

        {/* Security / Grounding Banner */}
        <div className="mt-4 p-3 bg-blue-50/60 border border-blue-200 rounded-xl text-blue-950 text-xs space-y-1">
          <div className="flex items-center gap-1.5 font-semibold text-blue-800">
            <ShieldCheck className="w-4 h-4 text-blue-600" />
            Ancrage Documentaire Strict
          </div>
          <p className="text-[11px] text-blue-800 leading-snug">
            L'IA est instruite pour s'appuyer uniquement sur les documents cochés. Toute donnée manquante est signalée au lieu d'être inventée.
          </p>
        </div>
      </div>

      {/* Main Chat Panel */}
      <div className="flex-1 flex flex-col bg-white">
        {/* Messages Stream */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {chatHistory.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center max-w-lg mx-auto text-slate-500 space-y-3">
              <div className="w-14 h-14 rounded-2xl bg-blue-50 text-blue-600 flex items-center justify-center shadow-xs">
                <Bot className="w-8 h-8" />
              </div>
              <h3 className="text-lg font-bold text-slate-900">Espace de Travail Documentaire</h3>
              <p className="text-xs text-slate-500 leading-relaxed">
                Posez vos questions d'analyse, demandez une synthèse d'appel d'offres, une extraction de clauses ou un projet de courrier.
                L'IA utilisera vos documents sélectionnés et le moteur de calcul Python déterministe.
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 w-full pt-4 text-left">
                <button
                  onClick={() => setInputMessage("Rédiger une lettre d'accompagnement officielle pour la remise de nos livrables du contrat.")}
                  className="p-3 text-xs rounded-lg border border-slate-200 hover:border-blue-400 hover:bg-blue-50/40 text-slate-700 transition-all cursor-pointer"
                >
                  ✉️ <strong>Lettre officielle</strong> d'accompagnement
                </button>
                <button
                  onClick={() => setInputMessage("Analyser l'appel d'offres : extraire l'autorité contractante, la date limite et les critères d'éligibilité.")}
                  className="p-3 text-xs rounded-lg border border-slate-200 hover:border-blue-400 hover:bg-blue-50/40 text-slate-700 transition-all cursor-pointer"
                >
                  📋 <strong>Analyse d'Appel d'Offres</strong> & critères
                </button>
                <button
                  onClick={() => setInputMessage("Calculer le montant TTC pour 3 prestations à 2 500 € HT avec TVA 20% et remise de 5%.")}
                  className="p-3 text-xs rounded-lg border border-slate-200 hover:border-blue-400 hover:bg-blue-50/40 text-slate-700 transition-all cursor-pointer"
                >
                  🧮 <strong>Chiffrage & TVA</strong> avec vérification
                </button>
                <button
                  onClick={() => setInputMessage("Établir la liste des pièces administratives obligatoires manquantes dans notre dossier.")}
                  className="p-3 text-xs rounded-lg border border-slate-200 hover:border-blue-400 hover:bg-blue-50/40 text-slate-700 transition-all cursor-pointer"
                >
                  🔍 <strong>Matrice de conformité</strong> des pièces
                </button>
              </div>
            </div>
          ) : (
            chatHistory.map((msg) => (
              <div
                key={msg.id}
                className={`flex gap-4 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                {msg.role === 'assistant' && (
                  <div className="w-8 h-8 rounded-lg bg-blue-600 text-white flex items-center justify-center shrink-0 shadow-xs">
                    <Bot className="w-5 h-5" />
                  </div>
                )}

                <div
                  className={`max-w-3xl rounded-xl p-4 text-sm leading-relaxed shadow-xs ${
                    msg.role === 'user'
                      ? 'bg-blue-600 text-white'
                      : 'bg-slate-50 border border-slate-200 text-slate-900'
                  }`}
                >
                  <div className="whitespace-pre-wrap">{msg.content}</div>

                  {/* Assistant Footnotes: Referenced chunks & Execution info */}
                  {msg.role === 'assistant' && (
                    <div className="mt-4 pt-3 border-t border-slate-200 flex flex-wrap items-center justify-between gap-2 text-[11px] text-slate-500">
                      <div className="flex items-center gap-3">
                        {msg.executionTimeMs !== undefined && (
                          <span className="flex items-center gap-1 font-mono">
                            <Clock className="w-3 h-3 text-slate-400" />
                            {msg.executionTimeMs} ms
                          </span>
                        )}
                        {msg.modelName && (
                          <span className="bg-slate-200 px-1.5 py-0.5 rounded text-[10px] font-mono">
                            {msg.modelName}
                          </span>
                        )}
                        {msg.referencedChunks && msg.referencedChunks.length > 0 && (
                          <span className="text-blue-600 font-medium">
                            {msg.referencedChunks.length} extrait(s) document(s) cité(s)
                          </span>
                        )}
                      </div>

                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => handleCopyText(msg.content, msg.id)}
                          className="flex items-center gap-1 hover:text-slate-900 cursor-pointer"
                        >
                          {copiedId === msg.id ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
                          {copiedId === msg.id ? 'Copié' : 'Copier'}
                        </button>

                        {onNavigateToGenerate && (
                          <button
                            onClick={() => onNavigateToGenerate(msg.content, 'Document généré depuis Workspace')}
                            className="flex items-center gap-1 text-blue-600 hover:text-blue-800 font-medium cursor-pointer"
                          >
                            <FileCheck2 className="w-3.5 h-3.5" />
                            Créer Document (Word/PDF)
                          </button>
                        )}
                      </div>
                    </div>
                  )}
                </div>

                {msg.role === 'user' && (
                  <div className="w-8 h-8 rounded-lg bg-slate-800 text-white flex items-center justify-center shrink-0">
                    <User className="w-5 h-5" />
                  </div>
                )}
              </div>
            ))
          )}

          {loading && (
            <div className="flex items-center gap-3 text-slate-500 text-xs italic">
              <div className="w-8 h-8 rounded-lg bg-blue-100 text-blue-600 flex items-center justify-center animate-pulse">
                <Bot className="w-5 h-5" />
              </div>
              <span>Analyse des documents sources et formulation de la réponse...</span>
            </div>
          )}
        </div>

        {/* Input Bar */}
        <div className="p-4 border-t border-slate-200 bg-white">
          <form onSubmit={handleSendMessage} className="flex gap-2 items-center">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder="Décrivez votre tâche ou posez une question sur les documents sélectionnés..."
              className="flex-1 bg-slate-50 border border-slate-300 rounded-xl px-4 py-3 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white transition-all"
              disabled={loading}
            />
            <button
              type="submit"
              disabled={loading || !inputMessage.trim()}
              className="bg-blue-600 hover:bg-blue-700 disabled:bg-slate-300 text-white px-5 py-3 rounded-xl font-medium text-sm flex items-center gap-2 shadow-xs transition-colors cursor-pointer"
            >
              <Send className="w-4 h-4" />
              <span>Envoyer</span>
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

