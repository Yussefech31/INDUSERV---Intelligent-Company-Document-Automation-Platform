# INDUSERV - Intelligent Company Document Automation Platform
## Architecture Specification

### 1. System Overview
INDUSERV is an enterprise-grade AI-powered document automation platform designed to streamline administrative, financial, procurement, commercial, HR, and operational documentation. The system operates with strict mathematical determinism, transparent document grounding, and an AI provider abstraction supporting external free/commercial APIs as well as fully offline local inference via Ollama.

```
+-------------------------------------------------------------------------+
|                  Modern React + TypeScript Frontend                     |
|  - Dashboard           - AI Workspace        - Document Manager         |
|  - Document Catalog    - Calculation Studio  - Template Editor          |
|  - Generation History  - AI & App Settings   - Document Previews        |
+-------------------------------------------------------------------------+
                                    |  REST API & SSE Streaming
                                    v
+-------------------------------------------------------------------------+
|                     FastAPI Application Backend                         |
|  +-------------------+  +--------------------+  +--------------------+  |
|  | Document Ingestion|  | Analytical Engine  |  | Document Generator |  |
|  | - PyMuPDF (PDF)   |  | - Deterministic    |  | - python-docx      |  |
|  | - python-docx     |  |   Financial Math   |  | - ReportLab (PDF)  |  |
|  | - openpyxl/pandas |  | - Decimal Auditing |  | - openpyxl (XLSX)  |  |
|  +-------------------+  +--------------------+  +--------------------+  |
|  +-------------------+  +--------------------+  +--------------------+  |
|  | Modular Retrieval |  | Workflow Engine    |  | Database Layer     |  |
|  | - Chunking Engine |  | - Tender Analysis  |  | - SQLAlchemy ORM   |  |
|  | - BM25/FTS Search |  | - Compliance Matrix|  | - SQLite / PG Prep |  |
|  +-------------------+  +--------------------+  +--------------------+  |
+-------------------------------------------------------------------------+
                                    |
            +-----------------------+-----------------------+
            |                                               |
            v                                               v
+-----------------------+                       +-----------------------+
|  AI Provider Layer    |                       | Storage & Filesystem  |
|  - Free API Provider  |                       | - storage/uploads/    |
|  - Ollama Local LLM   |                       | - storage/generated/  |
|  - OpenAI-Compatible  |                       | - storage/templates/  |
+-----------------------+                       +-----------------------+
```

---

### 2. Core Subsystems

#### 2.1 AI Provider Abstraction (`app.services.ai`)
An extensible provider-agnostic interface:
- `AIProvider` (Base Interface):
  - `generate_text(prompt, system_prompt, temperature, max_tokens)`
  - `generate_structured(prompt, schema, system_prompt)`
  - `stream_text(prompt, system_prompt)`
  - `test_connection()`
  - `list_models()`
- Implementations:
  - `FreeAPIProvider`: Groq / OpenRouter / HuggingFace free endpoints with rate-limiting & retry fallbacks.
  - `OllamaProvider`: Native local Ollama API (`/api/generate`, `/api/tags`) for 100% offline private execution.
  - `OpenAICompatibleProvider`: Universal provider for any standard OpenAI-compatible API base URL.

#### 2.2 Document Processing & Ingestion Engine (`app.services.documents`)
- **PDF Engine**: PyMuPDF extraction preserving page numbers, structure, detecting image-only pages requiring OCR flags.
- **DOCX Engine**: `python-docx` parsing headings, paragraphs, bullet points, tables, and cell structures.
- **Excel Engine**: `openpyxl` & `pandas` parsing multi-tab workbooks, column headers, typed values, and formulas.
- **Text & CSV Engine**: UTF-8 and French encoding normalization.

#### 2.3 Modular Retrieval Engine (`app.services.retrieval`)
- **Chunking**: Sentence & paragraph-aware chunker with configurable token windows and overlaps, retaining `doc_id`, `page_number`, `sheet_name`, `section_title`.
- **Search**: BM25 and keyword inverted-index retrieval with relevance scoring and passage highlighting. Designed with clean interfaces ready for vector embeddings (Qdrant/Chroma).

#### 2.4 Mathematical & Financial Calculation Engine (`app.services.calculations`)
- **Strict Rule**: AI models are forbidden from mental math. All figures are evaluated deterministically using Python `Decimal`.
- **Supported Operations**:
  - HT (Hors Taxe) to TTC (Toutes Taxes Comprises) with multi-rate TVA (e.g. 20%, 14%, 10%, 5.5%).
  - Discounts (remises/rabais/ristournes), commercial margins, markups.
  - Budget variance calculations, percentage deltas, weighted averages.
  - Tender price schedule totals, subtotals, unit price multiplications.
- Output includes: `inputs`, `formula`, `computed_result`, `currency`, `traceability_trail`.

#### 2.5 Document Generation Engine (`app.services.generation`)
- **DOCX Generator**: Corporate-ready Word documents featuring customized headers/footers, metadata tables, branded accent color headings, callout boxes, and signature blocks.
- **PDF Generator**: ReportLab-based canvas & flowable document builder with French character support (accented glyphs UTF-8), professional page number canvases (`Page X of Y`), stylized tables, and executive summary sections.
- **Excel Generator**: `openpyxl` workbooks with live calculation formulas (`SUM`, `PRODUCT`), auto-fitted columns, accounting format currency cells, and summary tabs.

#### 2.6 Workflows Engine (`app.services.workflows`)
- Administrative correspondence & attestations.
- Public tender analysis (Appels d'offres): Extraction of contracting authority, reference, deadlines, administrative/technical/financial requirements, compliance gap matrix, and proposal drafting.
- Financial audit & invoicing synthesis.
- Commercial devis & proposals.
- HR mission orders & contract drafting.

---

### 3. Data Model Architecture (`app.models`)
- `UserSetting`: UI preferences, default prompt profile, default AI provider, locale.
- `AIProviderSetting`: Provider type, base URL, encrypted/masked API key, model name, active status.
- `SystemPrompt`: Label, content, description, is_default, category.
- `Document`: File name, file path, file size, mime type, hash, status, page count, metadata.
- `DocumentChunk`: Foreign key to `Document`, chunk index, text content, page/sheet reference, token count.
- `Template`: Document category, template name, description, required inputs, schema, output formats.
- `GeneratedDocument`: Title, file path, format (DOCX/PDF/XLSX), source task, file size, download count.
- `TaskHistory`: Task title, workflow type, prompt used, documents referenced, execution time, status, logs.
- `CalculationAudit`: Calculation type, inputs, formula, result, task reference.

