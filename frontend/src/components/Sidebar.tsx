import React from 'react';
import {
  LayoutDashboard,
  BotMessageSquare,
  Files,
  FileCheck2,
  FileSpreadsheet,
  Calculator,
  History,
  Cpu,
  Settings,
  Sparkles,
} from 'lucide-react';

interface SidebarProps {
  currentTab: string;
  setCurrentTab: (tab: string) => void;
  activeProviderName?: string;
  activeModelName?: string;
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentTab,
  setCurrentTab,
  activeProviderName = 'Free API Provider',
  activeModelName = 'meta-llama/llama-3.3-70b',
}) => {
  const navItems = [
    { id: 'dashboard', label: 'Tableau de bord', icon: LayoutDashboard },
    { id: 'workspace', label: 'Espace IA Workspace', icon: BotMessageSquare, highlight: true },
    { id: 'documents', label: 'Mes Documents', icon: Files },
    { id: 'generation', label: 'Génération de Documents', icon: FileCheck2 },
    { id: 'templates', label: 'Catalogue & Modèles', icon: FileSpreadsheet },
    { id: 'calculations', label: 'Calculs & Analyse', icon: Calculator },
    { id: 'history', label: 'Historique des Tâches', icon: History },
    { id: 'ai-settings', label: 'Paramètres IA', icon: Cpu },
    { id: 'settings', label: 'Paramètres Généraux', icon: Settings },
  ];

  return (
    <aside className="w-64 bg-slate-900 text-slate-200 flex flex-col h-screen border-r border-slate-800 shrink-0">
      {/* Brand Header */}
      <div className="h-16 flex items-center px-6 border-b border-slate-800 gap-3">
        <div className="w-9 h-9 rounded-lg bg-blue-600 flex items-center justify-center text-white font-bold shadow-md shadow-blue-500/20">
          <Sparkles className="w-5 h-5" />
        </div>
        <div>
          <div className="font-bold text-white text-base tracking-wide flex items-center gap-1.5">
            INDUSERV
            <span className="text-[10px] bg-blue-500/20 text-blue-400 font-semibold px-1.5 py-0.5 rounded border border-blue-400/30">
              v1.0
            </span>
          </div>
          <p className="text-[11px] text-slate-400">Document Automation AI</p>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setCurrentTab(item.id)}
              className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-sm font-medium transition-colors text-left ${
                isActive
                  ? 'bg-blue-600 text-white shadow-sm shadow-blue-600/30'
                  : 'text-slate-300 hover:bg-slate-800 hover:text-white'
              }`}
            >
              <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-slate-400'}`} />
              <span>{item.label}</span>
              {item.highlight && !isActive && (
                <span className="ml-auto w-2 h-2 rounded-full bg-blue-400 ring-2 ring-blue-400/20"></span>
              )}
            </button>
          );
        })}
      </nav>

      {/* Active AI Status Footer */}
      <div className="p-3 border-t border-slate-800 bg-slate-950/50 m-3 rounded-xl border">
        <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
          <span className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            Moteur IA Actif
          </span>
          <span className="text-[10px] uppercase font-mono text-slate-500">Prêt</span>
        </div>
        <div className="text-xs font-semibold text-slate-200 truncate" title={activeProviderName}>
          {activeProviderName}
        </div>
        <div className="text-[11px] text-slate-400 font-mono truncate" title={activeModelName}>
          {activeModelName}
        </div>
      </div>
    </aside>
  );
};

