import React, { useState, useEffect } from 'react';
import {
  FileSpreadsheet,
  FileText,
  FileCheck2,
  Search,
  Plus,
  ArrowRight,
  Sparkles,
  Building2,
  Briefcase,
  Receipt,
  Users,
  Settings2,
  Shield,
  Layers,
} from 'lucide-react';
import { api } from '../services/api';
import { TemplateItem } from '../types';

interface TemplatesPageProps {
  onSelectTemplate?: (tpl: TemplateItem) => void;
}

export const TemplatesPage: React.FC<TemplatesPageProps> = ({ onSelectTemplate }) => {
  const [templates, setTemplates] = useState<TemplateItem[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [loading, setLoading] = useState(true);

  // New Template Modal
  const [showModal, setShowModal] = useState(false);
  const [newTpl, setNewTpl] = useState({
    name: '',
    category: 'administrative',
    code: '',
    description: '',
    default_prompt: '',
    supported_formats: 'docx,pdf',
  });

  useEffect(() => {
    loadTemplates();
  }, [selectedCategory]);

  const loadTemplates = async () => {
    try {
      setLoading(true);
      const data = await api.getTemplates(selectedCategory === 'all' ? undefined : selectedCategory);
      setTemplates(data);
    } catch (err) {
      console.error('Failed to load templates', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTemplate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await fetch('/api/v1/templates/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: newTpl.name,
          category: newTpl.category,
          code: newTpl.code.trim().toLowerCase().replace(/\s+/g, '_'),
          description: newTpl.description,
          default_prompt: newTpl.default_prompt,
          supported_formats: newTpl.supported_formats,
        }),
      });
      if (!res.ok) throw new Error(await res.text());
      setShowModal(false);
      loadTemplates();
    } catch (err: any) {
      alert(`Erreur: ${err.message}`);
    }
  };

  const categories = [
    { id: 'all', label: 'Tous les Modèles', icon: Layers },
    { id: 'administrative', label: 'Administratif', icon: Building2 },
    { id: 'procurement', label: "Appels d'Offres", icon: Briefcase },
    { id: 'financial', label: 'Finance & Factures', icon: Receipt },
    { id: 'commercial', label: 'Commercial & Devis', icon: Sparkles },
    { id: 'hr', label: 'Ressources Humaines', icon: Users },
    { id: 'operations', label: 'Opérations & Projets', icon: Settings2 },
  ];

  const filteredTemplates = templates.filter(
    (t) =>
      t.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      t.description.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900 tracking-tight">Catalogue de Modèles & Workflows</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Bibliothèque d'actes d'entreprise normés : courriers administratifs, réponses d'appels d'offres, factures et contrats.
          </p>
        </div>

        <button
          onClick={() => setShowModal(true)}
          className="flex items-center gap-1.5 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2.5 rounded-xl text-xs font-semibold shadow-xs cursor-pointer"
        >
          <Plus className="w-4 h-4" />
          Ajouter un Modèle Personnalisé
        </button>
      </div>

      {/* Category Pills & Search */}
      <div className="space-y-4">
        <div className="flex flex-wrap gap-2">
          {categories.map((c) => {
            const Icon = c.icon;
            const isSelected = selectedCategory === c.id;
            return (
              <button
                key={c.id}
                onClick={() => setSelectedCategory(c.id)}
                className={`flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-semibold transition-all cursor-pointer ${
                  isSelected
                    ? 'bg-blue-600 text-white shadow-xs'
                    : 'bg-white text-slate-700 border border-slate-200 hover:bg-slate-50'
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                {c.label}
              </button>
            );
          })}
        </div>

        <div className="relative max-w-md">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Rechercher un modèle de document..."
            className="w-full text-xs bg-white border border-slate-200 rounded-lg pl-9 pr-3 py-2 text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>

      {/* Templates Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {filteredTemplates.map((tpl) => (
          <div
            key={tpl.id}
            className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs flex flex-col justify-between hover:border-blue-400 transition-all group"
          >
            <div>
              <div className="flex items-start justify-between gap-2 mb-2">
                <span className="text-[10px] uppercase font-mono font-bold px-2 py-0.5 rounded bg-blue-50 text-blue-700">
                  {tpl.category}
                </span>
                <div className="flex items-center gap-1 text-[10px] font-mono text-slate-500 uppercase">
                  {tpl.supported_formats.split(',').map((f) => (
                    <span key={f} className="bg-slate-100 px-1.5 py-0.5 rounded">
                      {f.trim()}
                    </span>
                  ))}
                </div>
              </div>

              <h4 className="font-bold text-sm text-slate-900 group-hover:text-blue-600 transition-colors">
                {tpl.name}
              </h4>
              <p className="text-xs text-slate-500 mt-2 leading-relaxed">
                {tpl.description}
              </p>
            </div>

            <div className="mt-6 pt-3 border-t border-slate-100 flex items-center justify-between">
              <span className="text-[11px] text-slate-400 font-mono truncate max-w-[140px]">
                {tpl.code}
              </span>
              <button
                onClick={() => onSelectTemplate && onSelectTemplate(tpl)}
                className="flex items-center gap-1 text-xs font-semibold text-blue-600 hover:text-blue-800 cursor-pointer"
              >
                <span>Utiliser ce Modèle</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* New Template Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-xl border border-slate-200 space-y-4">
            <h3 className="font-bold text-base text-slate-900">Ajouter un Nouveau Modèle au Catalogue</h3>

            <form onSubmit={handleCreateTemplate} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Nom du Document</label>
                <input
                  type="text"
                  value={newTpl.name}
                  onChange={(e) => setNewTpl({ ...newTpl, name: e.target.value })}
                  className="w-full text-xs bg-slate-50 border border-slate-300 rounded-lg p-2.5 text-slate-900"
                  placeholder="ex: Contrat de Sous-Traitance Industrielle"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Catégorie</label>
                  <select
                    value={newTpl.category}
                    onChange={(e) => setNewTpl({ ...newTpl, category: e.target.value })}
                    className="w-full text-xs bg-slate-50 border border-slate-300 rounded-lg p-2.5 text-slate-900"
                  >
                    <option value="administrative">Administratif</option>
                    <option value="procurement">Appels d'Offres</option>
                    <option value="financial">Finance & Comptabilité</option>
                    <option value="commercial">Commercial & Ventes</option>
                    <option value="hr">Ressources Humaines</option>
                    <option value="operations">Opérations & Projets</option>
                    <option value="legal">Juridique & Contrats</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Code Unique</label>
                  <input
                    type="text"
                    value={newTpl.code}
                    onChange={(e) => setNewTpl({ ...newTpl, code: e.target.value })}
                    className="w-full text-xs font-mono bg-slate-50 border border-slate-300 rounded-lg p-2.5 text-slate-900"
                    placeholder="subcontract_agreement"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Description</label>
                <input
                  type="text"
                  value={newTpl.description}
                  onChange={(e) => setNewTpl({ ...newTpl, description: e.target.value })}
                  className="w-full text-xs bg-slate-50 border border-slate-300 rounded-lg p-2.5 text-slate-900"
                  placeholder="Objectif et cas d'usage de ce document..."
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Instruction / Prompt de Rédaction</label>
                <textarea
                  rows={4}
                  value={newTpl.default_prompt}
                  onChange={(e) => setNewTpl({ ...newTpl, default_prompt: e.target.value })}
                  className="w-full text-xs font-mono bg-slate-50 border border-slate-300 rounded-lg p-2.5 text-slate-900"
                  placeholder="Rédigez un contrat en définissant les parties..."
                  required
                />
              </div>

              <div className="flex items-center justify-between pt-3 border-t border-slate-200">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="text-xs font-semibold text-slate-600 hover:text-slate-900 cursor-pointer"
                >
                  Annuler
                </button>
                <button
                  type="submit"
                  className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-xs font-semibold cursor-pointer"
                >
                  Enregistrer le Modèle
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

