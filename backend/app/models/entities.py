from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.database.session import Base

def utc_now():
    return datetime.now(timezone.utc)

class SystemPrompt(Base):
    __tablename__ = "system_prompts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    description = Column(String(255), nullable=True)
    content = Column(Text, nullable=False)
    category = Column(String(60), default="general")
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

class AIProviderSetting(Base):
    __tablename__ = "ai_provider_settings"

    id = Column(Integer, primary_key=True, index=True)
    provider_type = Column(String(60), nullable=False)  # "free_api", "ollama", "openai_compatible"
    name = Column(String(120), nullable=False)
    base_url = Column(String(255), nullable=False)
    api_key = Column(String(255), nullable=True)
    model_name = Column(String(120), nullable=False)
    is_active = Column(Boolean, default=False)
    temperature = Column(Float, default=0.2)
    max_tokens = Column(Integer, default=4096)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

class UserSetting(Base):
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(150), default="INDUSERV Technologies")
    company_details = Column(Text, default="123 Boulevard Industriel, 75008 Paris - France\nSIRET: 892 451 098 00014 - TVA: FR 34 892451098\nEmail: contact@induserv.com - Tél: +33 1 42 68 55 00")
    default_language = Column(String(10), default="fr")
    active_prompt_id = Column(Integer, ForeignKey("system_prompts.id", ondelete="SET NULL"), nullable=True)
    active_provider_id = Column(Integer, ForeignKey("ai_provider_settings.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(20), nullable=False)  # pdf, docx, xlsx, csv, txt
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=False)
    page_count = Column(Integer, default=1)
    chunk_count = Column(Integer, default=0)
    status = Column(String(30), default="pending")  # pending, processed, error
    error_message = Column(Text, nullable=True)
    metadata_json = Column(Text, default="{}")
    is_scanned_likely = Column(Boolean, default=False)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    text_content = Column(Text, nullable=False)
    page_number = Column(Integer, nullable=True)
    sheet_name = Column(String(100), nullable=True)
    section_title = Column(String(255), nullable=True)
    token_count = Column(Integer, default=0)

    document = relationship("Document", back_populates="chunks")

class Template(Base):
    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(60), nullable=False)  # administrative, procurement, financial, etc.
    name = Column(String(150), nullable=False)
    code = Column(String(80), unique=True, nullable=False)
    description = Column(Text, nullable=False)
    supported_formats = Column(String(50), default="docx,pdf")
    default_prompt = Column(Text, nullable=False)
    schema_json = Column(Text, default="{}")
    sample_inputs_json = Column(Text, default="{}")
    is_custom = Column(Boolean, default=False)
    created_at = Column(DateTime, default=utc_now)

class TaskHistory(Base):
    __tablename__ = "task_history"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    workflow_type = Column(String(80), default="general_chat")
    system_prompt_used = Column(Text, nullable=True)
    user_instructions = Column(Text, nullable=False)
    response_text = Column(Text, nullable=False)
    referenced_doc_ids = Column(String(255), default="")
    status = Column(String(30), default="completed")
    execution_time_ms = Column(Integer, default=0)
    calculation_audit_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)

    generated_documents = relationship("GeneratedDocument", back_populates="task")
    calculation_audits = relationship("CalculationAudit", back_populates="task")

class GeneratedDocument(Base):
    __tablename__ = "generated_documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    format = Column(String(20), nullable=False)  # docx, pdf, xlsx
    category = Column(String(60), default="general")
    file_size = Column(Integer, default=0)
    template_id = Column(Integer, ForeignKey("templates.id", ondelete="SET NULL"), nullable=True)
    task_id = Column(Integer, ForeignKey("task_history.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=utc_now)

    task = relationship("TaskHistory", back_populates="generated_documents")

class CalculationAudit(Base):
    __tablename__ = "calculation_audits"

    id = Column(Integer, primary_key=True, index=True)
    operation = Column(String(80), nullable=False)
    inputs_json = Column(Text, nullable=False)
    formula = Column(String(255), nullable=False)
    result = Column(String(100), nullable=False)
    currency_or_unit = Column(String(30), default="EUR")
    is_valid = Column(Boolean, default=True)
    task_id = Column(Integer, ForeignKey("task_history.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=utc_now)

    task = relationship("TaskHistory", back_populates="calculation_audits")
