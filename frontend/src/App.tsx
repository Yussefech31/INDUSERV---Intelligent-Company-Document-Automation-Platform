import React, { useState, useEffect } from 'react';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { DashboardPage } from './pages/DashboardPage';
import { WorkspacePage } from './pages/WorkspacePage';
import { DocumentsPage } from './pages/DocumentsPage';
import { GenerationPage } from './pages/GenerationPage';
import { TemplatesPage } from './pages/TemplatesPage';
import { CalculationsPage } from './pages/CalculationsPage';
import { HistoryPage } from './pages/HistoryPage';
import { AISettingsPage } from './pages/AISettingsPage';
import { AppSettingsPage } from './pages/AppSettingsPage';
import { api } from './services/api';
import { AIProviderSetting, UserSetting } from './types';

export const App: React.FC = () => {
  const [currentTab, setCurrentTab] = useState<string>('dashboard');
  const [activeProvider, setActiveProvider] = useState<AIProviderSetting | null>(null);
  const [userSettings, setUserSettings] = useState<UserSetting | null>(null);

  // Content forwarded from Workspace to Generation
  const [generationDraft, setGenerationDraft] = useState<{ content: string; title?: string } | null>(null);

  useEffect(() => {
    loadAppMeta();
  }, [currentTab]);

  const loadAppMeta = async () => {
    try {
      const [providers, settings] = await Promise.all([
        api.getProviders().catch(() => [] as AIProviderSetting[]),
        api.getUserSettings().catch(() => null),
      ]);
      const active = providers.find((p) => p.is_active) || providers[0] || null;
      setActiveProvider(active);
      if (settings) setUserSettings(settings);
    } catch (err) {
      console.error('Failed to load initial metadata', err);
    }
  };

  const handleNavigateToGenerate = (content: string, title?: string) => {
    setGenerationDraft({ content, title });
    setCurrentTab('generation');
  };

  const getPageTitle = () => {
    switch (currentTab) {
      case 'dashboard':
        return { title: 'Tableau de bord', subtitle: "Aperçu général de l'activité documentaire et métriques clés" };
      case 'workspace':
        return { title: 'Espace IA Workspace', subtitle: 'Assistant conversationnel ancré sur vos documents d’entreprise' };
      case 'documents':
        return { title: 'Mes Documents', subtitle: 'Gestionnaire de fichiers sources (PDF, DOCX, XLSX, CSV, TXT)' };
      case 'generation':
        return { title: 'Génération de Documents', subtitle: 'Production de documents professionnels Word, PDF et Excel' };
      case 'templates':
        return { title: 'Catalogue & Modèles', subtitle: 'Modèles administratifs, marchés publics, finance, RH et commerce' };
      case 'calculations':
        return { title: 'Calculs & Analyse Financière', subtitle: 'Calculateur déterministe certifié Python (TVA, Marges, Écarts)' };
      case 'history':
        return { title: 'Historique des Tâches', subtitle: 'Journal complet des requêtes exécutées et documents téléchargés' };
      case 'ai-settings':
        return { title: 'Paramètres IA & Modèles', subtitle: 'Gestion des clés API, modèles et serveur local Ollama' };
      case 'settings':
        return { title: 'Paramètres Généraux', subtitle: 'Configuration de l’entreprise, identifiants légaux et langue' };
      default:
        return { title: 'INDUSERV', subtitle: '' };
    }
  };

  const pageMeta = getPageTitle();

  return (
    <div className="flex h-screen bg-slate-50 overflow-hidden font-sans">
      <Sidebar
        currentTab={currentTab}
        setCurrentTab={setCurrentTab}
        activeProviderName={activeProvider?.name}
        activeModelName={activeProvider?.model_name}
      />

      <div className="flex-1 flex flex-col h-screen overflow-hidden">
        <Header
          title={pageMeta.title}
          subtitle={pageMeta.subtitle}
          companyName={userSettings?.company_name}
        />

        <main className="flex-1 overflow-y-auto">
          {currentTab === 'dashboard' && <DashboardPage onNavigate={setCurrentTab} />}
          {currentTab === 'workspace' && (
            <WorkspacePage onNavigateToGenerate={handleNavigateToGenerate} />
          )}
          {currentTab === 'documents' && <DocumentsPage onNavigateToWorkspace={() => setCurrentTab('workspace')} />}
          {currentTab === 'generation' && (
            <GenerationPage initialDraft={generationDraft} onClearDraft={() => setGenerationDraft(null)} />
          )}
          {currentTab === 'templates' && (
            <TemplatesPage onSelectTemplate={(tpl) => {
              setGenerationDraft({ content: tpl.default_prompt, title: tpl.name });
              setCurrentTab('generation');
            }} />
          )}
          {currentTab === 'calculations' && <CalculationsPage />}
          {currentTab === 'history' && <HistoryPage />}
          {currentTab === 'ai-settings' && <AISettingsPage />}
          {currentTab === 'settings' && <AppSettingsPage />}
        </main>
      </div>
    </div>
  );
};

export default App;
