import React, { useState, useEffect } from 'react';
import {
  History,
  Clock,
  Trash2,
  Copy,
  Check,
  Download,
  FileCheck2,
  Search,
  RefreshCw,
  FileText,
} from 'lucide-react';
import { api } from '../services/api';
import { TaskHistoryItem } from '../types';

export const HistoryPage: React.FC = () => {
  const [tasks, setTasks] = useState<TaskHistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTask, setSelectedTask] = useState<TaskHistoryItem | null>(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      setLoading(true);
      const data = await api.getTaskHistory();
      setTasks(data);
      if (data.length > 0 && !selectedTask) {
        setSelectedTask(data[0]);
      }
    } catch (err) {
      console.error('Failed to load history', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Voulez-vous supprimer cet enregistrement d’historique ?')) return;
    try {
      await fetch(`/api/v1/history/${id}`, { method: 'DELETE' });
      setTasks((prev) => prev.filter((t) => t.id !== id));
      if (selectedTask?.id === id) {
        setSelectedTask(null);
      }
    } catch (err: any) {
      alert(`Erreur: ${err.message}`);
    }
  };

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const filteredTasks = tasks.filter(
    (t) =>
      t.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      t.user_instructions.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="p-8 space-y-6 max-w-7xl mx-auto">
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900 tracking-tight">Historique des Tâches & Générations</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Journal complet de toutes les analyses documentaires, prompts exécutés et livrables créés.
          </p>
        </div>

        <button
          onClick={loadHistory}
          className="flex items-center gap-1.5 text-xs text-slate-600 hover:text-slate-900 px-3 py-2 rounded-lg border border-slate-200 bg-white hover:bg-slate-50 cursor-pointer"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          Actualiser
        </button>
      </div>

      {/* Main Split View: Left List, Right Detail */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left List */}
        <div className="lg:col-span-5 bg-white rounded-xl border border-slate-200 p-4 shadow-xs flex flex-col h-[700px]">
          <div className="relative mb-3">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Rechercher une tâche..."
              className="w-full text-xs bg-slate-50 border border-slate-200 rounded-lg pl-9 pr-3 py-2 text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div className="flex-1 overflow-y-auto space-y-2 pr-1">
            {filteredTasks.length === 0 ? (
              <p className="text-center py-12 text-slate-400 text-xs">Aucune tâche enregistrée.</p>
            ) : (
              filteredTasks.map((t) => {
                const isSelected = selectedTask?.id === t.id;
                return (
                  <div
                    key={t.id}
                    onClick={() => setSelectedTask(t)}
                    className={`p-3 rounded-xl border transition-all cursor-pointer ${
                      isSelected
                        ? 'bg-blue-50/60 border-blue-500 ring-1 ring-blue-500/20'
                        : 'bg-white border-slate-200 hover:border-slate-300'
                    }`}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="font-semibold text-xs text-slate-900 truncate" title={t.title}>
                        {t.title}
                      </div>
                      <span className="font-mono text-[10px] bg-slate-100 text-slate-600 px-1.5 py-0.5 rounded shrink-0">
                        {t.execution_time_ms} ms
                      </span>
                    </div>

                    <p className="text-[11px] text-slate-500 mt-1 line-clamp-2">
                      {t.user_instructions}
                    </p>

                    <div className="mt-2 pt-2 border-t border-slate-100 flex items-center justify-between text-[10px] text-slate-400">
                      <span>{new Date(t.created_at).toLocaleString('fr-FR')}</span>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDelete(t.id);
                        }}
                        className="text-rose-500 hover:text-rose-700 cursor-pointer"
                        title="Supprimer cette tâche"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Right Detail Pane */}
        <div className="lg:col-span-7 bg-white rounded-xl border border-slate-200 p-6 shadow-xs flex flex-col justify-between h-[700px] overflow-hidden">
          {selectedTask ? (
            <div className="flex flex-col h-full overflow-hidden">
              <div className="border-b border-slate-200 pb-3 mb-4 flex items-start justify-between">
                <div>
                  <h3 className="font-bold text-base text-slate-900">{selectedTask.title}</h3>
                  <div className="flex items-center gap-2 text-xs text-slate-500 mt-0.5">
                    <span>Date : {new Date(selectedTask.created_at).toLocaleString('fr-FR')}</span>
                    <span>•</span>
                    <span className="font-mono text-blue-600 font-semibold">{selectedTask.execution_time_ms} ms</span>
                  </div>
                </div>

                <button
                  onClick={() => handleCopy(selectedTask.response_text)}
                  className="flex items-center gap-1 text-xs text-slate-600 hover:text-slate-900 px-2.5 py-1.5 rounded-lg border border-slate-200 hover:bg-slate-50 cursor-pointer"
                >
                  {copied ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
                  <span>{copied ? 'Copié' : 'Copier'}</span>
                </button>
              </div>

              {/* Instructions */}
              <div className="mb-4">
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block mb-1">
                  Instruction de l'utilisateur
                </span>
                <div className="p-3 bg-slate-50 rounded-lg border border-slate-200 text-xs text-slate-800 font-medium">
                  {selectedTask.user_instructions}
                </div>
              </div>

              {/* Response Body */}
              <div className="flex-1 overflow-y-auto pr-2 mb-4 space-y-2">
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">
                  Réponse Fournie & Document Produit
                </span>
                <div className="p-4 bg-slate-50/50 rounded-xl border border-slate-200 text-xs text-slate-900 whitespace-pre-wrap font-sans leading-relaxed">
                  {selectedTask.response_text}
                </div>
              </div>

              {/* Linked Generated Documents (if any) */}
              {selectedTask.generated_documents && selectedTask.generated_documents.length > 0 && (
                <div className="pt-3 border-t border-slate-200">
                  <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block mb-2">
                    Livrables Fichiers Rattachés
                  </span>
                  <div className="flex flex-wrap gap-2">
                    {selectedTask.generated_documents.map((g) => (
                      <a
                        key={g.id}
                        href={g.download_url}
                        download
                        className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-blue-50 border border-blue-200 text-blue-800 text-xs font-semibold hover:bg-blue-100 cursor-pointer"
                      >
                        <Download className="w-3.5 h-3.5" />
                        <span>{g.title} ({g.format.toUpperCase()})</span>
                      </a>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="flex items-center justify-center h-full text-slate-400 text-xs">
              Sélectionnez une tâche dans la colonne de gauche.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

