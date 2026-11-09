export interface SystemPrompt {
  id: number;
  name: string;
  description?: string;
  content: string;
  category: string;
  is_default: boolean;
  created_at: string;
  updated_at: string;
}

export interface AIProviderSetting {
  id: number;
  provider_type: 'free_api' | 'ollama' | 'openai_compatible';
  name: string;
  base_url: string;
  model_name: string;
  is_active: boolean;
  temperature: number;
  max_tokens: number;
  has_api_key: boolean;
  masked_key?: string;
  created_at: string;
  updated_at: string;
}

export interface UserSetting {
  id: number;
  company_name: string;
  company_details: string;
  default_language: string;
  active_prompt_id?: number;
  active_provider_id?: number;
  updated_at: string;
}

export interface DocumentItem {
  id: number;
  filename: string;
  original_filename: string;
  file_type: 'pdf' | 'docx' | 'xlsx' | 'csv' | 'txt';
  file_size: number;
  mime_type: string;
  page_count: number;
  chunk_count: number;
  status: 'pending' | 'processed' | 'error';
  error_message?: string;
  is_scanned_likely: boolean;
  created_at: string;
}

export interface DocumentChunk {
  id: number;
  chunk_index: number;
  text_content: string;
  page_number?: number;
  sheet_name?: string;
  section_title?: string;
  token_count: number;
}

export interface DocumentDetail extends DocumentItem {
  metadata: Record<string, any>;
  chunks: DocumentChunk[];
}

export interface CalculationItem {
  label: string;
  amount: number;
  quantity?: number;
  unit_price?: number;
  tva_rate?: number;
  discount_rate?: number;
}

export interface CalculationRequest {
  operation: string;
  items?: CalculationItem[];
  ht_amount?: number;
  tva_rate?: number;
  discount_rate?: number;
  cost_price?: number;
  selling_price?: number;
  budget_planned?: number;
  budget_actual?: number;
  numbers?: number[];
  currency?: string;
}

export interface CalculationAudit {
  id?: number;
  operation: string;
  inputs: Record<string, any>;
  formula: string;
  result: any;
  currency_or_unit: string;
  is_valid: boolean;
  details?: Record<string, any>;
}

export interface WorkspaceChatRequest {
  message: string;
  prompt_id?: number;
  provider_id?: number;
  document_ids?: number[];
  temperature?: number;
  include_calculations?: boolean;
}

export interface WorkspaceChatResponse {
  response: string;
  referenced_chunks: Array<{
    document_id: number;
    filename: string;
    page_number?: number;
    sheet_name?: string;
    content_snippet: string;
  }>;
  calculation_audits: CalculationAudit[];
  task_id: number;
  execution_time_ms: number;
  provider_name: string;
  model_name: string;
}

export interface TemplateItem {
  id: number;
  category: string;
  name: string;
  code: string;
  description: string;
  supported_formats: string;
  default_prompt: string;
  is_custom: boolean;
}

export interface GeneratedDocumentItem {
  id: number;
  title: string;
  filename: string;
  format: 'docx' | 'pdf' | 'xlsx';
  category: string;
  file_size: number;
  created_at: string;
  download_url: string;
}

export interface TaskHistoryItem {
  id: number;
  title: string;
  workflow_type: string;
  user_instructions: string;
  response_text: string;
  referenced_doc_ids: string;
  status: string;
  execution_time_ms: number;
  created_at: string;
  generated_documents?: GeneratedDocumentItem[];
}

export interface DashboardStats {
  total_documents: number;
  total_generated: number;
  total_tasks: number;
  total_calculations: number;
  active_provider: string;
  active_model: string;
  category_distribution: Record<string, number>;
  recent_tasks: TaskHistoryItem[];
  recent_generated: GeneratedDocumentItem[];
}

