import React, { useState, useEffect } from 'react';
import {
  FileCheck2,
  FileText,
  FileSpreadsheet,
  Download,
  Sparkles,
  Layers,
  CheckCircle2,
  Clock,
  Printer,
  ChevronRight,
  ExternalLink,
} from 'lucide-react';
import { api } from '../services/api';
import { GeneratedDocumentItem, TemplateItem } from '../types';

interface GenerationPageProps {
  initialDraft?: { content: string; title?: string } | null;
  onClearDraft?: () => void;
}

export const GenerationPage: React.FC<GenerationPageProps> = ({ initialDraft, onClearDraft }) => {
  const [selectedFormat, setSelectedFormat] = useState<'docx' | 'pdf' | 'xlsx'>('docx');
  const [selectedCategory, setSelectedCategory] = useState<string>('administrative');
  const [title, setTitle] = useState<string>('Lettre de Transmission & Attestation Officielle');
  const [content, setContent] = useState<string>(
    "## 1. Objet et Contexte\nLa présente atteste de la parfaite conformité des prestations réalisées au titre du contrat cadre.\n\n## 2. Constatations et Livrables\nL'ensemble des documents techniques et administratifs a été remis conformément au calendrier.\n\n- Rapport d'analyse technique validé\n- PV de recette sans réserves\n- Bordereau financier certifié"
  );

  const [includeCalculations, setIncludeCalculations] = useState(true);
  const [loading, setLoading] = useState(false);
  const [latestGenerated, setLatestGenerated] = useState<GeneratedDocumentItem | null>(null);
  const [historyList, setHistoryList] = useState<GeneratedDocumentItem[]>([]);

  useEffect(() => {
    loadHistory();
  }, []);

  useEffect(() => {
    if (initialDraft) {
      if (initialDraft.title) setTitle(initialDraft.title);
      if (initialDraft.content) setContent(initialDraft.content);
    }
  }, [initialDraft]);

  const loadHistory = async () => {
    try {
      const docs = await api.getGeneratedDocuments();
      setHistoryList(docs);
    } catch (err) {
      console.error('Failed to load generated history', err);
    }
  };

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;

    try {
      setLoading(true);
      const calcData = includeCalculations
        ? {
            currency: 'EUR',
            inputs: { ht_amount: 4500.0 },
            result: 5130.0,
            details: {
              gross_ht: 4500.0,
              discount_amount: 225.0,
              net_ht: 4275.0,
              tva_amount: 855.0,
              total_ttc: 5130.0,
            },
          }
        : undefined;

      const generated = await api.generateDocument({
        title: title.trim(),
        category: selectedCategory,
        format: selectedFormat,
        content: content.trim(),
        calculation_data: calcData,
      });

      setLatestGenerated(generated);
      setHistoryList((prev) => [generated, ...prev]);
      if (onClearDraft) onClearDraft();
    } catch (err: any) {
      alert(`Erreur de génération : ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      {/* Top Banner */}
      <div>
        <h2 className="text-xl font-bold text-slate-900 tracking-tight">Studio de Génération de Documents</h2>
        <p className="text-xs text-slate-500 mt-0.5">
          Exportez vos rapports d'appels d'offres, factures, devis et lettres administratives aux formats professionnels Word (.docx), PDF et Excel (.xlsx).
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Generator Form */}
        <div className="lg:col-span-7 bg-white rounded-xl border border-slate-200 p-6 shadow-xs">
          <form onSubmit={handleGenerate} className="space-y-5">
            {/* Format Selection Cards */}
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-2">
                1. Choisissez le Format de Sortie
              </label>
              <div className="grid grid-cols-3 gap-3">
                <button
                  type="button"
                  onClick={() => setSelectedFormat('docx')}
                  className={`p-3.5 rounded-xl border text-left transition-all cursor-pointer ${
                    selectedFormat === 'docx'
                      ? 'border-blue-600 bg-blue-50/50 ring-2 ring-blue-500/20'
                      : 'border-slate-200 hover:border-slate-300 bg-white'
                  }`}
                >
                  <FileText className={`w-5 h-5 mb-1.5 ${selectedFormat === 'docx' ? 'text-blue-600' : 'text-slate-500'}`} />
                  <div className="font-bold text-xs text-slate-900">Word (.docx)</div>
                  <div className="text-[10px] text-slate-500 mt-0.5">En-têtes, tables & modifiable</div>
                </button>

                <button
                  type="button"
                  onClick={() => setSelectedFormat('pdf')}
                  className={`p-3.5 rounded-xl border text-left transition-all cursor-pointer ${
                    selectedFormat === 'pdf'
                      ? 'border-red-600 bg-red-50/50 ring-2 ring-red-500/20'
                      : 'border-slate-200 hover:border-slate-300 bg-white'
                  }`}
                >
                  <FileText className={`w-5 h-5 mb-1.5 ${selectedFormat === 'pdf' ? 'text-red-600' : 'text-slate-500'}`} />
                  <div className="font-bold text-xs text-slate-900">PDF (.pdf)</div>
                  <div className="text-[10px] text-slate-500 mt-0.5">Mise en page certifiée & accents</div>
                </button>

                <button
                  type="button"
                  onClick={() => setSelectedFormat('xlsx')}
                  className={`p-3.5 rounded-xl border text-left transition-all cursor-pointer ${
                    selectedFormat === 'xlsx'
                      ? 'border-emerald-600 bg-emerald-50/50 ring-2 ring-emerald-500/20'
                      : 'border-slate-200 hover:border-slate-300 bg-white'
                  }`}
                >
                  <FileSpreadsheet className={`w-5 h-5 mb-1.5 ${selectedFormat === 'xlsx' ? 'text-emerald-600' : 'text-slate-500'}`} />
                  <div className="font-bold text-xs text-slate-900">Excel (.xlsx)</div>
                  <div className="text-[10px] text-slate-500 mt-0.5">Formules actives & multi-onglets</div>
                </button>
              </div>
            </div>

            {/* Title & Category */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Catégorie Métier</label>
                <select
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                  className="w-full text-xs bg-slate-50 border border-slate-300 rounded-lg p-2.5 text-slate-900 focus:bg-white"
                >
                  <option value="administrative">Documents Administratifs</option>
                  <option value="procurement">Appels d'Offres & Marchés Publics</option>
                  <option value="financial">Finance & Comptabilité</option>
                  <option value="commercial">Commercial & Ventes</option>
                  <option value="hr">Ressources Humaines</option>
                  <option value="operations">Opérations & Projets</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Titre Officiel du Document</label>
                <input
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="w-full text-xs bg-slate-50 border border-slate-300 rounded-lg p-2.5 text-slate-900 focus:bg-white focus:ring-2 focus:ring-blue-500 font-medium"
                  required
                />
              </div>
            </div>

            {/* Content text */}
            <div>
              <div className="flex items-center justify-between mb-1">
                <label className="text-xs font-semibold text-slate-700">
                  Contenu Structuré (Titres, Paragraphes, Puces)
                </label>
                <span className="text-[10px] text-slate-400 font-mono">Format Markdown supporté (#, ##, -, &gt;)</span>
              </div>
              <textarea
                rows={8}
                value={content}
                onChange={(e) => setContent(e.target.value)}
                className="w-full text-xs font-mono bg-slate-50 border border-slate-300 rounded-lg p-3 text-slate-900 focus:bg-white focus:ring-2 focus:ring-blue-500"
                placeholder="Rédigez ou collez le texte du document..."
                required
              />
            </div>

            {/* Calculations Checkbox */}
            <div className="flex items-center gap-2 p-3 bg-slate-50 rounded-xl border border-slate-200">
              <input
                type="checkbox"
                id="inc_calc"
                checked={includeCalculations}
                onChange={(e) => setIncludeCalculations(e.target.checked)}
                className="rounded text-blue-600 focus:ring-blue-500"
              />
              <label htmlFor="inc_calc" className="text-xs text-slate-700 font-medium cursor-pointer">
                Inclure automatiquement le tableau récapitulatif financier certifié (HT / TVA / TTC)
              </label>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white font-semibold py-3 rounded-xl text-xs flex items-center justify-center gap-2 shadow-xs cursor-pointer transition-colors"
            >
              <FileCheck2 className="w-4 h-4" />
              <span>{loading ? 'Génération du fichier en cours...' : `Générer le Document ${selectedFormat.toUpperCase()}`}</span>
            </button>
          </form>
        </div>

        {/* Right Side: Generated File Download & Recent Files */}
        <div className="lg:col-span-5 space-y-6">
          {/* Latest Generated Card */}
          {latestGenerated ? (
            <div className="bg-gradient-to-br from-emerald-500 to-teal-700 text-white rounded-2xl p-6 shadow-md space-y-4">
              <div className="flex items-center justify-between">
                <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-white/20 border border-white/30 uppercase tracking-wide">
                  Génération Réussie
                </span>
                <span className="text-[10px] uppercase font-mono bg-black/20 px-2 py-0.5 rounded">
                  {latestGenerated.format}
                </span>
              </div>

              <div>
                <h4 className="font-bold text-base">{latestGenerated.title}</h4>
                <p className="text-xs text-emerald-100 font-mono mt-1 truncate">{latestGenerated.filename}</p>
                <div className="text-[11px] text-emerald-100/80 mt-1">
                  Taille : {(latestGenerated.file_size / 1024).toFixed(1)} KB
                </div>
              </div>

              <a
                href={latestGenerated.download_url}
                download
                className="inline-flex items-center justify-center gap-2 w-full bg-white text-emerald-900 hover:bg-emerald-50 font-bold py-2.5 rounded-xl text-xs shadow-md transition-all cursor-pointer"
              >
                <Download className="w-4 h-4 text-emerald-600" />
                Télécharger le Document
              </a>
            </div>
          ) : (
            <div className="bg-white rounded-xl border border-dashed border-slate-300 p-8 text-center text-slate-400 space-y-2">
              <FileCheck2 className="w-8 h-8 mx-auto text-slate-300" />
              <div className="text-xs font-semibold text-slate-600">Aucun document généré dans cette session</div>
              <p className="text-[11px] text-slate-400 max-w-xs mx-auto">
                Remplissez les informations à gauche et cliquez sur Générer pour produire un livrable téléchargeable.
              </p>
            </div>
          )}

          {/* Historical Generated Documents */}
          <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-xs space-y-4">
            <h4 className="font-bold text-sm text-slate-900 flex items-center gap-2">
              <Clock className="w-4 h-4 text-slate-500" />
              Derniers Documents Produits
            </h4>

            {historyList.length === 0 ? (
              <p className="text-xs text-slate-400 py-3 text-center">Aucun document dans l'historique.</p>
            ) : (
              <div className="divide-y divide-slate-100">
                {historyList.slice(0, 5).map((doc) => (
                  <div key={doc.id} className="py-3 flex items-center justify-between gap-3 text-xs">
                    <div className="overflow-hidden">
                      <div className="font-semibold text-slate-900 truncate" title={doc.title}>
                        {doc.title}
                      </div>
                      <div className="text-[10px] text-slate-400 font-mono">
                        {doc.format.toUpperCase()} • {(doc.file_size / 1024).toFixed(1)} KB
                      </div>
                    </div>

                    <a
                      href={doc.download_url}
                      download
                      className="p-1.5 rounded-lg bg-slate-100 hover:bg-blue-50 text-slate-600 hover:text-blue-600 transition-colors cursor-pointer shrink-0"
                      title="Télécharger"
                    >
                      <Download className="w-3.5 h-3.5" />
                    </a>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

