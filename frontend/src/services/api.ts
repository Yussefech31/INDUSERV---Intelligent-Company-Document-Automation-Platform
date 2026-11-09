import {
  SystemPrompt,
  AIProviderSetting,
  UserSetting,
  DocumentItem,
  DocumentDetail,
  CalculationRequest,
  CalculationAudit,
  WorkspaceChatRequest,
  WorkspaceChatResponse,
  TemplateItem,
  GeneratedDocumentItem,
  TaskHistoryItem,
  DashboardStats,
} from '../types';

const API_BASE = '/api/v1';

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let errorDetail = 'Une erreur est survenue';
    try {
      const errorJson = await res.json();
      errorDetail = errorJson.detail || errorDetail;
    } catch {
      errorDetail = await res.text();
    }
    throw new Error(errorDetail || `Erreur HTTP ${res.status}`);
  }
  return res.json();
}

export const api = {
  // Health
  checkHealth: async () => {
    const res = await fetch(`${API_BASE}/health/`);
    return handleResponse<{ status: string; counts: Record<string, number> }>(res);
  },

  // Dashboard
  getDashboardStats: async (): Promise<DashboardStats> => {
    const res = await fetch(`${API_BASE}/dashboard/stats`);
    return handleResponse<DashboardStats>(res);
  },

  // System Prompts
  getPrompts: async (): Promise<SystemPrompt[]> => {
    const res = await fetch(`${API_BASE}/prompts/`);
    return handleResponse<SystemPrompt[]>(res);
  },

  createPrompt: async (data: Partial<SystemPrompt>): Promise<SystemPrompt> => {
    const res = await fetch(`${API_BASE}/prompts/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return handleResponse<SystemPrompt>(res);
  },

  updatePrompt: async (id: number, data: Partial<SystemPrompt>): Promise<SystemPrompt> => {
    const res = await fetch(`${API_BASE}/prompts/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return handleResponse<SystemPrompt>(res);
  },

  deletePrompt: async (id: number): Promise<void> => {
    const res = await fetch(`${API_BASE}/prompts/${id}`, { method: 'DELETE' });
    if (!res.ok) throw new Error('Impossible de supprimer ce prompt');
  },

  setDefaultPrompt: async (id: number): Promise<SystemPrompt> => {
    const res = await fetch(`${API_BASE}/prompts/${id}/set-default`, { method: 'POST' });
    return handleResponse<SystemPrompt>(res);
  },

  // AI Providers
  getProviders: async (): Promise<AIProviderSetting[]> => {
    const res = await fetch(`${API_BASE}/providers/`);
    return handleResponse<AIProviderSetting[]>(res);
  },

  updateProvider: async (id: number, data: Partial<AIProviderSetting> & { api_key?: string }): Promise<AIProviderSetting> => {
    const res = await fetch(`${API_BASE}/providers/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return handleResponse<AIProviderSetting>(res);
  },

  activateProvider: async (id: number): Promise<AIProviderSetting> => {
    const res = await fetch(`${API_BASE}/providers/${id}/activate`, { method: 'POST' });
    return handleResponse<AIProviderSetting>(res);
  },

  testProvider: async (data: { provider_type: string; base_url: string; api_key?: string; model_name: string }) => {
    const res = await fetch(`${API_BASE}/providers/test`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return handleResponse<{ success: boolean; message: string; latency_ms?: number; models_available: string[] }>(res);
  },

  // Settings
  getUserSettings: async (): Promise<UserSetting> => {
    const res = await fetch(`${API_BASE}/settings/`);
    return handleResponse<UserSetting>(res);
  },

  updateUserSettings: async (data: Partial<UserSetting>): Promise<UserSetting> => {
    const res = await fetch(`${API_BASE}/settings/`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return handleResponse<UserSetting>(res);
  },

  // AI Workspace
  chatWorkspace: async (data: WorkspaceChatRequest): Promise<WorkspaceChatResponse> => {
    const res = await fetch(`${API_BASE}/workspace/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return handleResponse<WorkspaceChatResponse>(res);
  },

  // Documents
  getDocuments: async (): Promise<DocumentItem[]> => {
    const res = await fetch(`${API_BASE}/documents/`);
    return handleResponse<DocumentItem[]>(res);
  },

  getDocumentDetail: async (id: number): Promise<DocumentDetail> => {
    const res = await fetch(`${API_BASE}/documents/${id}`);
    return handleResponse<DocumentDetail>(res);
  },

  uploadDocuments: async (files: FileList | File[]): Promise<DocumentItem[]> => {
    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
      formData.append('files', files[i]);
    }
    const res = await fetch(`${API_BASE}/documents/upload`, {
      method: 'POST',
      body: formData,
    });
    return handleResponse<DocumentItem[]>(res);
  },

  deleteDocument: async (id: number): Promise<void> => {
    const res = await fetch(`${API_BASE}/documents/${id}`, { method: 'DELETE' });
    if (!res.ok) throw new Error('Échec de la suppression du document');
  },

  // Calculations
  calculate: async (data: CalculationRequest): Promise<CalculationAudit> => {
    const res = await fetch(`${API_BASE}/calculations/compute`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return handleResponse<CalculationAudit>(res);
  },

  getCalculationAudits: async (): Promise<CalculationAudit[]> => {
    const res = await fetch(`${API_BASE}/calculations/audits`);
    return handleResponse<CalculationAudit[]>(res);
  },

  // Templates & Catalog
  getTemplates: async (category?: string): Promise<TemplateItem[]> => {
    const url = category ? `${API_BASE}/templates/?category=${category}` : `${API_BASE}/templates/`;
    const res = await fetch(url);
    return handleResponse<TemplateItem[]>(res);
  },

  // Generation
  generateDocument: async (data: any): Promise<GeneratedDocumentItem> => {
    const res = await fetch(`${API_BASE}/generation/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return handleResponse<GeneratedDocumentItem>(res);
  },

  getGeneratedDocuments: async (): Promise<GeneratedDocumentItem[]> => {
    const res = await fetch(`${API_BASE}/generation/list`);
    return handleResponse<GeneratedDocumentItem[]>(res);
  },

  // History
  getTaskHistory: async (): Promise<TaskHistoryItem[]> => {
    const res = await fetch(`${API_BASE}/history/`);
    return handleResponse<TaskHistoryItem[]>(res);
  },
};

