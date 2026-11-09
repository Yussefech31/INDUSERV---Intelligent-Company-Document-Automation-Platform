import React, { useState, useEffect, useRef } from 'react';
import {
  Upload,
  Files,
  FileText,
  FileSpreadsheet,
  Trash2,
  Download,
  Eye,
  CheckCircle2,
  AlertTriangle,
  Clock,
  Search,
  RefreshCw,
  BotMessageSquare,
  ShieldAlert,
  Layers,
} from 'lucide-react';
import { api } from '../services/api';
import { DocumentItem, DocumentDetail } from '../types';

interface DocumentsPageProps {
  onNavigateToWorkspace?: () => void;
}

export const DocumentsPage: React.FC<DocumentsPageProps> = ({ onNavigateToWorkspace }) => {
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedDocDetail, setSelectedDocDetail] = useState<DocumentDetail | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);

  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    try {
      setLoading(true);
      const data = await api.getDocuments();
      setDocuments(data);
    } catch (err) {
      console.error('Failed to load documents', err);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (files: FileList | null) => {
    if (!files || files.length === 0) return;
    try {
      setUploading(true);
      const uploaded = await api.uploadDocuments(files);
      setDocuments((prev) => [...uploaded, ...prev]);
    } catch (err: any) {
      alert(`Erreur d'importation : ${err.message}`);
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const handleDelete = async (id: number, name: string) => {
    if (!confirm(`Confirmez-vous la suppression du document "${name}" ?`)) return;
    try {
      await api.deleteDocument(id);
      setDocuments((prev) => prev.filter((d) => d.id !== id));
      if (selectedDocDetail?.id === id) {
        setSelectedDocDetail(null);
      }
    } catch (err: any) {
      alert(err.message);
    }
  };

  const handleViewDetail = async (id: number) => {
    try {
      setDetailLoading(true);
      const detail = await api.getDocumentDetail(id);
      setSelectedDocDetail(detail);
    } catch (err: any) {
      alert(`Erreur lors de la lecture des détails: ${err.message}`);
    } finally {
      setDetailLoading(false);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  };

  const filteredDocs = documents.filter((d) =>
    d.original_filename.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="p-8 space-y-6 max-w-7xl mx-auto">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900 tracking-tight">Gestionnaire de Documents Sources</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Téléversez vos dossiers administratifs, appels d'offres (RC/CCTP), bilans et devis au format PDF, DOCX, XLSX.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <input
            type="file"
            ref={fileInputRef}
            onChange={(e) => handleFileUpload(e.target.files)}
            multiple
            accept=".pdf,.docx,.doc,.xlsx,.xls,.csv,.txt,.md"
            className="hidden"
          />
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={uploading}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white px-4 py-2.5 rounded-xl text-xs font-semibold shadow-xs cursor-pointer transition-colors"
          >
            <Upload className="w-4 h-4" />
            {uploading ? 'Extraction en cours...' : 'Importer des Documents'}
          </button>
        </div>
      </div>

      {/* Drag & Drop Upload Zone */}
      <div
        onClick={() => fileInputRef.current?.click()}
        onDragOver={(e) => e.preventDefault()}
        onDrop={(e) => {
          e.preventDefault();
          handleFileUpload(e.dataTransfer.files);
        }}
        className="border-2 border-dashed border-slate-300 hover:border-blue-500 bg-slate-50/60 hover:bg-blue-50/20 rounded-2xl p-8 text-center cursor-pointer transition-all"
      >
        <div className="w-12 h-12 rounded-xl bg-blue-100 text-blue-600 flex items-center justify-center mx-auto mb-3">
          <Upload className="w-6 h-6" />
        </div>
        <h4 className="font-bold text-sm text-slate-900">Glissez-déposez vos fichiers ici ou parcourez votre disque</h4>
        <p className="text-xs text-slate-500 mt-1 max-w-md mx-auto">
          Prise en charge de <strong>PDF</strong> (extraction page par page & détection de scan), <strong>DOCX</strong> (titres & tableaux), <strong>XLSX</strong> (multi-feuilles & chiffres), <strong>CSV</strong> et <strong>TXT</strong>.
        </p>
        <span className="inline-block mt-3 px-2.5 py-1 rounded-full text-[10px] font-mono bg-slate-200 text-slate-700">
          Taille max : 50 Mo par fichier
        </span>
      </div>

      {/* Search Bar */}
      <div className="flex items-center justify-between gap-4">
        <div className="relative flex-1 max-w-sm">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Rechercher par nom de fichier..."
            className="w-full text-xs bg-white border border-slate-200 rounded-lg pl-9 pr-3 py-2 text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <button
          onClick={loadDocuments}
          className="flex items-center gap-1.5 text-xs text-slate-600 hover:text-slate-900 px-3 py-2 rounded-lg border border-slate-200 bg-white hover:bg-slate-50 cursor-pointer"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          Actualiser
        </button>
      </div>

      {/* Documents Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
        {filteredDocs.length === 0 ? (
          <div className="text-center py-12 text-slate-400 text-xs">
            <Files className="w-8 h-8 text-slate-300 mx-auto mb-2" />
            Aucun document trouvé. Importez des fichiers pour commencer l'analyse.
          </div>
        ) : (
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200 text-slate-500 uppercase tracking-wider font-semibold text-[11px]">
                <th className="py-3 px-4">Document</th>
                <th className="py-3 px-4">Type</th>
                <th className="py-3 px-4">Taille</th>
                <th className="py-3 px-4">Pages / Feuilles</th>
                <th className="py-3 px-4">Extraits (Chunks)</th>
                <th className="py-3 px-4">Statut</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filteredDocs.map((doc) => (
                <tr key={doc.id} className="hover:bg-slate-50/60 transition-colors">
                  <td className="py-3 px-4">
                    <div className="flex items-center gap-2.5">
                      {doc.file_type === 'pdf' ? (
                        <FileText className="w-4 h-4 text-red-500 shrink-0" />
                      ) : doc.file_type === 'xlsx' ? (
                        <FileSpreadsheet className="w-4 h-4 text-emerald-600 shrink-0" />
                      ) : (
                        <FileText className="w-4 h-4 text-blue-600 shrink-0" />
                      )}
                      <div>
                        <div className="font-semibold text-slate-900 truncate max-w-xs" title={doc.original_filename}>
                          {doc.original_filename}
                        </div>
                        <div className="text-[10px] text-slate-400">
                          {new Date(doc.created_at).toLocaleDateString('fr-FR', {
                            day: 'numeric',
                            month: 'short',
                            year: 'numeric',
                          })}
                        </div>
                      </div>
                    </div>
                  </td>

                  <td className="py-3 px-4">
                    <span className="uppercase font-mono font-bold text-[10px] px-1.5 py-0.5 rounded bg-slate-100 text-slate-600">
                      {doc.file_type}
                    </span>
                  </td>

                  <td className="py-3 px-4 font-mono text-slate-600">{formatFileSize(doc.file_size)}</td>

                  <td className="py-3 px-4 text-slate-700">
                    {doc.page_count} {doc.file_type === 'xlsx' ? 'feuille(s)' : 'page(s)'}
                  </td>

                  <td className="py-3 px-4">
                    <span className="inline-flex items-center gap-1 font-mono text-slate-700 bg-slate-100 px-2 py-0.5 rounded">
                      <Layers className="w-3 h-3 text-slate-400" />
                      {doc.chunk_count}
                    </span>
                  </td>

                  <td className="py-3 px-4">
                    {doc.is_scanned_likely ? (
                      <span className="inline-flex items-center gap-1 text-[11px] font-medium text-amber-700 bg-amber-50 px-2 py-0.5 rounded border border-amber-200">
                        <ShieldAlert className="w-3 h-3 text-amber-600" />
                        Scanné (OCR)
                      </span>
                    ) : doc.status === 'processed' ? (
                      <span className="inline-flex items-center gap-1 text-[11px] font-medium text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                        <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                        Indexé
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 text-[11px] font-medium text-rose-700 bg-rose-50 px-2 py-0.5 rounded border border-rose-200">
                        <AlertTriangle className="w-3 h-3 text-rose-600" />
                        Erreur
                      </span>
                    )}
                  </td>

                  <td className="py-3 px-4 text-right">
                    <div className="flex items-center justify-end gap-2">
                      <button
                        onClick={() => handleViewDetail(doc.id)}
                        className="p-1.5 text-slate-500 hover:text-blue-600 rounded-lg hover:bg-blue-50 cursor-pointer"
                        title="Voir les détails et extraits"
                      >
                        <Eye className="w-4 h-4" />
                      </button>
                      <a
                        href={`/api/v1/documents/${doc.id}/download`}
                        download
                        className="p-1.5 text-slate-500 hover:text-emerald-600 rounded-lg hover:bg-emerald-50 cursor-pointer"
                        title="Télécharger le fichier original"
                      >
                        <Download className="w-4 h-4" />
                      </a>
                      <button
                        onClick={() => handleDelete(doc.id, doc.original_filename)}
                        className="p-1.5 text-slate-500 hover:text-rose-600 rounded-lg hover:bg-rose-50 cursor-pointer"
                        title="Supprimer"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Document Details & Chunks Modal / Drawer */}
      {selectedDocDetail && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl max-w-3xl w-full max-h-[85vh] flex flex-col p-6 shadow-xl border border-slate-200">
            <div className="flex items-start justify-between border-b border-slate-200 pb-4 mb-4">
              <div>
                <h3 className="font-bold text-base text-slate-900 flex items-center gap-2">
                  <FileText className="w-5 h-5 text-blue-600" />
                  {selectedDocDetail.original_filename}
                </h3>
                <p className="text-xs text-slate-500 mt-0.5">
                  {selectedDocDetail.page_count} pages • {selectedDocDetail.chunk_count} extraits indexés pour la recherche • {formatFileSize(selectedDocDetail.file_size)}
                </p>
              </div>
              <button
                onClick={() => setSelectedDocDetail(null)}
                className="text-xs font-semibold text-slate-500 hover:text-slate-800 cursor-pointer"
              >
                Fermer ✕
              </button>
            </div>

            {/* Chunks List */}
            <div className="flex-1 overflow-y-auto space-y-3 pr-2">
              <h4 className="font-bold text-xs text-slate-500 uppercase tracking-wider">
                Passages Indexés & Citations Disponibles
              </h4>
              {selectedDocDetail.chunks.length === 0 ? (
                <p className="text-xs text-slate-400">Aucun passage extrait.</p>
              ) : (
                selectedDocDetail.chunks.map((chunk) => (
                  <div key={chunk.id} className="p-3 rounded-lg border border-slate-200 bg-slate-50 space-y-1.5 text-xs">
                    <div className="flex items-center justify-between text-[11px] text-slate-500 font-mono">
                      <span className="font-semibold text-blue-700">
                        {chunk.section_title || (chunk.page_number ? `Page ${chunk.page_number}` : 'Section')}
                      </span>
                      <span>~{chunk.token_count} tokens</span>
                    </div>
                    <p className="text-slate-800 whitespace-pre-wrap font-sans leading-relaxed">
                      {chunk.text_content}
                    </p>
                  </div>
                ))
              )}
            </div>

            <div className="mt-4 pt-3 border-t border-slate-200 flex items-center justify-between">
              {onNavigateToWorkspace && (
                <button
                  onClick={() => {
                    setSelectedDocDetail(null);
                    onNavigateToWorkspace();
                  }}
                  className="flex items-center gap-1.5 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-xs font-semibold cursor-pointer"
                >
                  <BotMessageSquare className="w-4 h-4" />
                  Interroger ce document dans l'Espace IA
                </button>
              )}
              <button
                onClick={() => setSelectedDocDetail(null)}
                className="text-xs font-medium text-slate-600 hover:underline cursor-pointer"
              >
                Fermer
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

