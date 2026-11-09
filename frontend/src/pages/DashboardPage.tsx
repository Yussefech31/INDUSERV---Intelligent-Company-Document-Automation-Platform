import React, { useEffect, useState } from 'react';
import {
  Files,
  FileCheck2,
  ListTodo,
  Calculator,
  ArrowUpRight,
  Sparkles,
  BotMessageSquare,
  Upload,
  Cpu,
  Clock,
  CheckCircle2,
  FileSpreadsheet,
} from 'lucide-react';
import { api } from '../services/api';
import { DashboardStats } from '../types';

interface DashboardPageProps {
  onNavigate: (tab: string) => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({ onNavigate }) => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      setLoading(true);
      const data = await api.getDashboardStats();
      setStats(data);
    } catch (err) {
      console.error('Failed to load dashboard stats', err);
    } finally {
      setLoading(false);
    }
  };

  const categories = [
    { key: 'administrative', label: 'Administratif', color: 'bg-blue-500' },
    { key: 'procurement', label: "Appels d'Offres & Marchés", color: 'bg-indigo-500' },
    { key: 'financial', label: 'Financier & Comptable', color: 'bg-emerald-500' },
    { key: 'commercial', label: 'Commercial & Devis', color: 'bg-amber-500' },
    { key: 'hr', label: 'Ressources Humaines', color: 'bg-purple-500' },
    { key: 'operations', label: 'Opérations & Projets', color: 'bg-rose-500' },
  ];

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      {/* Top Banner / Hero */}
      <div className="bg-gradient-to-r from-slate-900 via-blue-950 to-slate-900 text-white rounded-2xl p-6 shadow-lg border border-slate-800 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-500/20 text-blue-300 border border-blue-400/30">
              Système Documentaire Intelligent
            </span>
            <span className="text-xs text-slate-400">Entreprise INDUSERV</span>
          </div>
          <h2 className="text-2xl font-bold tracking-tight">Plateforme d'Automatisation de Documents</h2>
          <p className="text-slate-300 text-sm mt-1 max-w-2xl">
            Analysez vos documents d'entreprise, exécutez des calculs certifiés sans erreur arithmétique,
            et générez instantanément des rapports administratifs, financiers, et réponses d'appels d'offres en Word, PDF et Excel.
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => onNavigate('workspace')}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-500 text-white px-4 py-2.5 rounded-lg text-sm font-semibold shadow-md transition-all cursor-pointer"
          >
            <BotMessageSquare className="w-4 h-4" />
            Ouvrir l'Espace IA
          </button>
          <button
            onClick={() => onNavigate('documents')}
            className="flex items-center gap-2 bg-slate-800 hover:bg-slate-700 text-slate-200 px-4 py-2.5 rounded-lg text-sm font-medium border border-slate-700 transition-all cursor-pointer"
          >
            <Upload className="w-4 h-4" />
            Importer des fichiers
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Documents Sources</p>
            <h3 className="text-2xl font-bold text-slate-900 mt-1">{stats?.total_documents ?? 0}</h3>
            <span className="text-[11px] text-slate-400">PDF, DOCX, XLSX analysés</span>
          </div>
          <div className="w-12 h-12 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center">
            <Files className="w-6 h-6" />
          </div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Documents Générés</p>
            <h3 className="text-2xl font-bold text-slate-900 mt-1">{stats?.total_generated ?? 0}</h3>
            <span className="text-[11px] text-emerald-600 font-medium">Word, PDF & Excel prêts</span>
          </div>
          <div className="w-12 h-12 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center">
            <FileCheck2 className="w-6 h-6" />
          </div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Tâches Exécutées</p>
            <h3 className="text-2xl font-bold text-slate-900 mt-1">{stats?.total_tasks ?? 0}</h3>
            <span className="text-[11px] text-slate-400">Analyses & synthèses</span>
          </div>
          <div className="w-12 h-12 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center">
            <ListTodo className="w-6 h-6" />
          </div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Calculs Certifiés</p>
            <h3 className="text-2xl font-bold text-slate-900 mt-1">{stats?.total_calculations ?? 0}</h3>
            <span className="text-[11px] text-blue-600 font-medium">Déterminisme Python 100%</span>
          </div>
          <div className="w-12 h-12 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center">
            <Calculator className="w-6 h-6" />
          </div>
        </div>
      </div>

      {/* Quick Actions & AI Provider Card */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Quick Actions Panel */}
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-xs lg:col-span-2">
          <h3 className="font-bold text-slate-900 text-base mb-4 flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-blue-600" />
            Actions Rapides & Workflows Recommandés
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <button
              onClick={() => onNavigate('workspace')}
              className="p-4 rounded-xl border border-slate-200 hover:border-blue-400 hover:bg-blue-50/40 text-left transition-all group cursor-pointer"
            >
              <div className="flex items-center justify-between mb-1">
                <span className="font-semibold text-sm text-slate-900 group-hover:text-blue-600">
                  Nouvelle Requête Documentaire
                </span>
                <ArrowUpRight className="w-4 h-4 text-slate-400 group-hover:text-blue-600" />
              </div>
              <p className="text-xs text-slate-500">
                Interrogez l'IA en sélectionnant des documents d'entreprise comme base de vérité.
              </p>
            </button>

            <button
              onClick={() => onNavigate('templates')}
              className="p-4 rounded-xl border border-slate-200 hover:border-indigo-400 hover:bg-indigo-50/40 text-left transition-all group cursor-pointer"
            >
              <div className="flex items-center justify-between mb-1">
                <span className="font-semibold text-sm text-slate-900 group-hover:text-indigo-600">
                  Analyser un Appel d'Offres (AO)
                </span>
                <ArrowUpRight className="w-4 h-4 text-slate-400 group-hover:text-indigo-600" />
              </div>
              <p className="text-xs text-slate-500">
                Extrayez les critères du RC/CCTP et dressez la matrice de conformité administrative.
              </p>
            </button>

            <button
              onClick={() => onNavigate('calculations')}
              className="p-4 rounded-xl border border-slate-200 hover:border-emerald-400 hover:bg-emerald-50/40 text-left transition-all group cursor-pointer"
            >
              <div className="flex items-center justify-between mb-1">
                <span className="font-semibold text-sm text-slate-900 group-hover:text-emerald-600">
                  Calculateur Financier & TVA
                </span>
                <ArrowUpRight className="w-4 h-4 text-slate-400 group-hover:text-emerald-600" />
              </div>
              <p className="text-xs text-slate-500">
                Simulez des montants HT/TTC, remises et marges avec traçabilité intégrale.
              </p>
            </button>

            <button
              onClick={() => onNavigate('generation')}
              className="p-4 rounded-xl border border-slate-200 hover:border-amber-400 hover:bg-amber-50/40 text-left transition-all group cursor-pointer"
            >
              <div className="flex items-center justify-between mb-1">
                <span className="font-semibold text-sm text-slate-900 group-hover:text-amber-600">
                  Générer Facture ou Lettre
                </span>
                <ArrowUpRight className="w-4 h-4 text-slate-400 group-hover:text-amber-600" />
              </div>
              <p className="text-xs text-slate-500">
                Créez directement un document Word (.docx) ou PDF prêt à l'impression.
              </p>
            </button>
          </div>
        </div>

        {/* AI Engine Status Card */}
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Statut Moteur IA</span>
              <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-100 text-emerald-800">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                Opérationnel
              </span>
            </div>

            <div className="p-4 rounded-lg bg-slate-50 border border-slate-200 space-y-3">
              <div className="flex items-start gap-3">
                <Cpu className="w-5 h-5 text-blue-600 shrink-0 mt-0.5" />
                <div className="overflow-hidden">
                  <div className="text-xs text-slate-500 font-medium">Fournisseur Actif</div>
                  <div className="text-sm font-bold text-slate-900 truncate">
                    {stats?.active_provider || 'Free API Provider'}
                  </div>
                </div>
              </div>

              <div>
                <div className="text-xs text-slate-500 font-medium">Modèle Sélectionné</div>
                <div className="text-xs font-mono font-semibold text-slate-700 bg-white px-2 py-1 rounded border border-slate-200 truncate mt-1">
                  {stats?.active_model || 'meta-llama/llama-3.3-70b'}
                </div>
              </div>
            </div>

            <p className="text-xs text-slate-500 mt-4 leading-relaxed">
              Compatible <strong>Ollama Local</strong> pour exécution 100% hors-ligne et confidentielle sans quitter votre infrastructure.
            </p>
          </div>

          <button
            onClick={() => onNavigate('ai-settings')}
            className="w-full mt-4 bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium py-2 rounded-lg text-xs transition-colors cursor-pointer"
          >
            Configurer les Modèles & Clés API
          </button>
        </div>
      </div>

      {/* Document Categories Breakdown & Recent Tasks */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Categories Distribution */}
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-xs">
          <h3 className="font-bold text-slate-900 text-base mb-4 flex items-center gap-2">
            <FileSpreadsheet className="w-4 h-4 text-indigo-600" />
            Couverture Documentaire par Pôle
          </h3>
          <div className="space-y-3">
            {categories.map((cat) => {
              const count = stats?.category_distribution?.[cat.key] ?? 0;
              return (
                <div key={cat.key} className="flex items-center justify-between text-xs">
                  <div className="flex items-center gap-2">
                    <span className={`w-2.5 h-2.5 rounded-full ${cat.color}`}></span>
                    <span className="font-medium text-slate-700">{cat.label}</span>
                  </div>
                  <span className="font-semibold text-slate-900 bg-slate-100 px-2 py-0.5 rounded">
                    {count} doc(s)
                  </span>
                </div>
              );
            })}
          </div>
          <button
            onClick={() => onNavigate('templates')}
            className="w-full mt-6 text-center text-xs font-semibold text-blue-600 hover:text-blue-700 hover:underline cursor-pointer"
          >
            Consulter le catalogue des 50+ modèles →
          </button>
        </div>

        {/* Recent Tasks History */}
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-xs lg:col-span-2">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-bold text-slate-900 text-base flex items-center gap-2">
              <Clock className="w-4 h-4 text-purple-600" />
              Activités & Tâches Récentes
            </h3>
            <button
              onClick={() => onNavigate('history')}
              className="text-xs font-medium text-blue-600 hover:underline cursor-pointer"
            >
              Voir tout l'historique
            </button>
          </div>

          {!stats?.recent_tasks || stats.recent_tasks.length === 0 ? (
            <div className="text-center py-8 border border-dashed border-slate-200 rounded-lg">
              <CheckCircle2 className="w-8 h-8 text-slate-300 mx-auto mb-2" />
              <p className="text-xs text-slate-500">Aucune tâche récente enregistrée.</p>
              <button
                onClick={() => onNavigate('workspace')}
                className="mt-2 text-xs font-semibold text-blue-600 hover:underline cursor-pointer"
              >
                Démarrer une première analyse
              </button>
            </div>
          ) : (
            <div className="divide-y divide-slate-100">
              {stats.recent_tasks.map((task) => (
                <div key={task.id} className="py-3 flex items-start justify-between gap-4">
                  <div className="space-y-0.5 overflow-hidden">
                    <div className="text-sm font-medium text-slate-900 truncate">{task.title}</div>
                    <div className="text-xs text-slate-500 truncate max-w-lg">{task.user_instructions}</div>
                  </div>
                  <div className="text-right shrink-0">
                    <span className="inline-block px-2 py-0.5 rounded text-[10px] font-semibold bg-blue-50 text-blue-700">
                      {task.execution_time_ms} ms
                    </span>
                    <div className="text-[10px] text-slate-400 mt-1">
                      {new Date(task.created_at).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

