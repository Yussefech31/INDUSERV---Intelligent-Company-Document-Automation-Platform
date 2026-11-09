import React, { useState, useEffect } from 'react';
import { Building2, Save, Globe, Shield, FileCheck } from 'lucide-react';
import { api } from '../services/api';
import { UserSetting } from '../types';

export const AppSettingsPage: React.FC = () => {
  const [settings, setSettings] = useState<UserSetting | null>(null);
  const [loading, setLoading] = useState(true);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      setLoading(true);
      const data = await api.getUserSettings();
      setSettings(data);
    } catch (err) {
      console.error('Failed to load settings', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!settings) return;

    try {
      const updated = await api.updateUserSettings({
        company_name: settings.company_name,
        company_details: settings.company_details,
        default_language: settings.default_language,
      });
      setSettings(updated);
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (err: any) {
      alert(`Erreur: ${err.message}`);
    }
  };

  return (
    <div className="p-8 space-y-8 max-w-4xl mx-auto">
      <div>
        <h2 className="text-xl font-bold text-slate-900 tracking-tight">Paramètres Généraux de l'Entreprise</h2>
        <p className="text-xs text-slate-500 mt-0.5">
          Ces coordonnées figurent automatiquement sur les en-têtes et pieds de page des documents Word, PDF et Excel générés.
        </p>
      </div>

      {saved && (
        <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-xl text-xs flex items-center gap-2">
          <FileCheck className="w-4 h-4 text-emerald-600" />
          Paramètres sauvegardés avec succès.
        </div>
      )}

      {settings && (
        <form onSubmit={handleSave} className="bg-white rounded-xl border border-slate-200 p-6 shadow-xs space-y-6">
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Raison Sociale / Nom de l'Entreprise</label>
            <input
              type="text"
              value={settings.company_name}
              onChange={(e) => setSettings({ ...settings, company_name: e.target.value })}
              className="w-full text-xs font-medium bg-slate-50 border border-slate-300 rounded-lg p-2.5 text-slate-900 focus:bg-white focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Coordonnées Légales & Mentions Obligatoires
            </label>
            <textarea
              rows={4}
              value={settings.company_details}
              onChange={(e) => setSettings({ ...settings, company_details: e.target.value })}
              className="w-full text-xs bg-slate-50 border border-slate-300 rounded-lg p-3 text-slate-900 focus:bg-white focus:ring-2 focus:ring-blue-500"
              placeholder="Adresse, SIRET, N° TVA intracommunautaire, Téléphone, Email..."
              required
            />
            <p className="text-[11px] text-slate-400 mt-1">
              Ce bloc textuel est intégré dans les cartouches légaux de vos devis, factures et courriers administratifs.
            </p>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Langue par Défaut de Rédaction</label>
            <select
              value={settings.default_language}
              onChange={(e) => setSettings({ ...settings, default_language: e.target.value })}
              className="w-full text-xs bg-slate-50 border border-slate-300 rounded-lg p-2.5 text-slate-900 focus:bg-white"
            >
              <option value="fr">Français (Prioritaire / Recommandé)</option>
              <option value="en">English</option>
              <option value="ar">العربية (Arabe)</option>
            </select>
          </div>

          <div className="pt-4 border-t border-slate-200 flex justify-end">
            <button
              type="submit"
              className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-5 py-2.5 rounded-lg text-xs font-semibold shadow-xs cursor-pointer"
            >
              <Save className="w-4 h-4" />
              Enregistrer les Paramètres
            </button>
          </div>
        </form>
      )}
    </div>
  );
};

