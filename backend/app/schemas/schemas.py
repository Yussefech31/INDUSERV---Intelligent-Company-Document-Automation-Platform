from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

# ==================== SYSTEM PROMPT SCHEMAS ====================
class SystemPromptBase(BaseModel):
    name: str = Field(..., max_length=120)
    description: Optional[str] = Field(None, max_length=255)
    content: str
    category: str = Field(default="general", max_length=60)
    is_default: bool = False

class SystemPromptCreate(SystemPromptBase):
    pass

class SystemPromptUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    is_default: Optional[bool] = None

class SystemPromptResponse(SystemPromptBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

# ==================== AI PROVIDER SCHEMAS ====================
class AIProviderSettingBase(BaseModel):
    provider_type: str = Field(..., description="free_api, ollama, openai_compatible")
    name: str = Field(..., max_length=120)
    base_url: str = Field(..., max_length=255)
    api_key: Optional[str] = None
    model_name: str = Field(..., max_length=120)
    is_active: bool = False
    temperature: float = 0.2
    max_tokens: int = 4096

class AIProviderSettingCreate(AIProviderSettingBase):
    pass

class AIProviderSettingUpdate(BaseModel):
    name: Optional[str] = None
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    model_name: Optional[str] = None
    is_active: Optional[bool] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None

class AIProviderSettingResponse(BaseModel):
    id: int
    provider_type: str
    name: str
    base_url: str
    model_name: str
    is_active: bool
    temperature: float
    max_tokens: int
    has_api_key: bool
    masked_key: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class AIProviderTestRequest(BaseModel):
    provider_type: str
    base_url: str
    api_key: Optional[str] = None
    model_name: str

class AIProviderTestResponse(BaseModel):
    success: bool
    message: str
    latency_ms: Optional[int] = None
    models_available: List[str] = []

# ==================== USER SETTING SCHEMAS ====================
class UserSettingUpdate(BaseModel):
    company_name: Optional[str] = None
    company_details: Optional[str] = None
    default_language: Optional[str] = None
    active_prompt_id: Optional[int] = None
    active_provider_id: Optional[int] = None

class UserSettingResponse(BaseModel):
    id: int
    company_name: str
    company_details: str
    default_language: str
    active_prompt_id: Optional[int] = None
    active_provider_id: Optional[int] = None
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

# ==================== DOCUMENT SCHEMAS ====================
class DocumentChunkResponse(BaseModel):
    id: int
    chunk_index: int
    text_content: str
    page_number: Optional[int] = None
    sheet_name: Optional[str] = None
    section_title: Optional[str] = None
    token_count: int

    model_config = ConfigDict(from_attributes=True)

class DocumentResponse(BaseModel):
    id: int
    filename: str
    original_filename: str
    file_type: str
    file_size: int
    mime_type: str
    page_count: int
    chunk_count: int
    status: str
    error_message: Optional[str] = None
    is_scanned_likely: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class DocumentDetailResponse(DocumentResponse):
    metadata: Dict[str, Any] = {}
    chunks: List[DocumentChunkResponse] = []

# ==================== CALCULATION SCHEMAS ====================
class CalculationItem(BaseModel):
    label: str
    amount: float
    quantity: float = 1.0
    unit_price: Optional[float] = None
    tva_rate: float = 20.0
    discount_rate: float = 0.0

class CalculationRequest(BaseModel):
    operation: str = Field(..., description="ht_to_ttc, vat_summary, discount, margin, budget_variance, sum, compound_financial")
    items: Optional[List[CalculationItem]] = None
    ht_amount: Optional[float] = None
    tva_rate: Optional[float] = 20.0
    discount_rate: Optional[float] = 0.0
    cost_price: Optional[float] = None
    selling_price: Optional[float] = None
    budget_planned: Optional[float] = None
    budget_actual: Optional[float] = None
    numbers: Optional[List[float]] = None
    currency: str = "EUR"

class CalculationAuditResponse(BaseModel):
    id: Optional[int] = None
    operation: str
    inputs: Dict[str, Any]
    formula: str
    result: Any
    currency_or_unit: str
    is_valid: bool
    details: Optional[Dict[str, Any]] = None

# ==================== WORKSPACE & CHAT SCHEMAS ====================
class WorkspaceChatRequest(BaseModel):
    message: str
    prompt_id: Optional[int] = None
    provider_id: Optional[int] = None
    document_ids: List[int] = []
    temperature: Optional[float] = None
    include_calculations: bool = True

class WorkspaceChatResponse(BaseModel):
    response: str
    referenced_chunks: List[Dict[str, Any]] = []
    calculation_audits: List[CalculationAuditResponse] = []
    task_id: int
    execution_time_ms: int
    provider_name: str
    model_name: str

# ==================== TEMPLATE & GENERATION SCHEMAS ====================
class TemplateResponse(BaseModel):
    id: int
    category: str
    name: str
    code: str
    description: str
    supported_formats: str
    default_prompt: str
    is_custom: bool

    model_config = ConfigDict(from_attributes=True)

class DocumentGenerateRequest(BaseModel):
    template_code: Optional[str] = None
    title: str
    category: str = "administrative"
    format: str = Field(..., description="docx, pdf, xlsx")
    content: Optional[str] = None
    prompt_id: Optional[int] = None
    document_ids: List[int] = []
    user_instructions: Optional[str] = None
    calculation_data: Optional[Dict[str, Any]] = None

class GeneratedDocumentResponse(BaseModel):
    id: int
    title: str
    filename: str
    format: str
    category: str
    file_size: int
    created_at: datetime
    download_url: str

    model_config = ConfigDict(from_attributes=True)

# ==================== TASK HISTORY SCHEMAS ====================
class TaskHistoryResponse(BaseModel):
    id: int
    title: str
    workflow_type: str
    user_instructions: str
    response_text: str
    referenced_doc_ids: str
    status: str
    execution_time_ms: int
    created_at: datetime
    generated_documents: List[GeneratedDocumentResponse] = []

    model_config = ConfigDict(from_attributes=True)

# ==================== DASHBOARD STATS ====================
class DashboardStatsResponse(BaseModel):
    total_documents: int
    total_generated: int
    total_tasks: int
    total_calculations: int
    active_provider: str
    active_model: str
    category_distribution: Dict[str, int]
    recent_tasks: List[TaskHistoryResponse]
    recent_generated: List[GeneratedDocumentResponse]
