# INDUSERV - Implementation Plan & Roadmap

## Phase Overview & Milestones

### Phase 1: Foundation (Core Backend & Frontend Scaffolding)
- Backend:
  - Create Python project with `uv` virtual environment and `requirements.txt`.
  - Setup FastAPI application, CORS, error handling middleware, logging.
  - Setup SQLAlchemy database engine with SQLite and automated table migrations.
  - Implement initial database models (`SystemPrompt`, `AIProviderSetting`, `UserSetting`).
  - Implement `AIProvider` base interface with `FreeAPIProvider` (OpenRouter/Groq/free OpenAI-compatible endpoint) and mock fallback for zero-downtime testing.
  - Implement System Prompt management API (CRUD, default prompt selection).
  - Implement Provider testing and configuration API.
- Frontend:
  - Initialize React + TypeScript + Vite project with Tailwind CSS and Lucide icons.
  - Implement SaaS layout: Sidebar navigation, top header, status indicators, notification toasts.
  - Implement Dashboard overview page.
  - Implement AI Settings & System Prompt Manager pages.
  - Build AI Chat / Workspace interface with prompt selector and provider status.
- Verification:
  - Unit tests for database models, AI provider connection & generation.
  - Frontend build verification.

### Phase 2: Document Ingestion & Modular Retrieval
- Backend:
  - Implement document upload API supporting PDF, DOCX, XLSX, CSV, TXT.
  - Implement PyMuPDF extractor with page tracking and OCR-readiness checks.
  - Implement `python-docx` extractor for paragraphs and tables.
  - Implement `openpyxl`/`pandas` extractor for Excel workbooks and sheets.
  - Implement text chunking engine preserving page/sheet context.
  - Implement inverted index / BM25 keyword retrieval engine with passage ranking.
  - Implement document preview, metadata extraction, and deletion endpoints.
- Frontend:
  - Build "My Documents" page: file drag-and-drop, upload progress, file list table with badge statuses, preview drawer, delete confirmation.
  - Connect AI Workspace to document selector: select specific documents as ground-truth context for AI tasks.
- Verification:
  - Test PDF, DOCX, XLSX extraction with sample test documents.
  - Test retrieval accuracy and context assembly.

### Phase 3: Mathematical & Analytical Engine
- Backend:
  - Implement Python calculation module using `decimal.Decimal`.
  - Financial calculations: HT/TVA/TTC, discounts, commercial margins, markups, currency conversions.
  - Quantitative analysis: budget variance, percentage changes, statistical summaries, weighted averages.
  - Calculation auditing: every calculation records inputs, formula, deterministic result, and traceability.
  - Calculation tool integration with AI workspace so the LLM invokes verified calculation endpoints rather than performing mental math.
- Frontend:
  - Build "Calculations & Analysis" page with financial calculator widgets, VAT simulator, budget variance calculator, and audit log.
- Verification:
  - Unit tests comparing known financial formulas with deterministic outputs.
  - Zero-error floating point assertions (exact decimal precision).

### Phase 4: Document Generation Engine (DOCX, PDF, XLSX)
- Backend:
  - Implement DOCX generator: customized headers, footers, metadata tables, styled headings, corporate styling.
  - Implement PDF generator: ReportLab canvas builder with French character support, running headers/footers, dynamic page numbers, corporate layout.
  - Implement Excel (XLSX) generator: multi-tab workbooks, active Excel formulas, cell formats (accounting, percentages), table formatting.
  - Template repository and document export service.
- Frontend:
  - Build "Document Generation" page: select format, input parameters or prompt, choose template, preview summary, download generated files.
- Verification:
  - Generate sample DOCX, PDF, and XLSX files and verify valid binary file formats and content fidelity.

### Phase 5: Business Workflows & Document Catalog
- Backend:
  - Implement pre-built document workflows across 8 company categories:
    1. Administrative (Official letters, attestations, meeting minutes, memos).
    2. Public Tenders & Procurement (Tender requirement extraction, compliance gap matrix, administrative/technical bid proposals).
    3. Financial & Accounting (Invoices, pro forma, financial summaries, expense reports).
    4. Commercial & Sales (Quotations, commercial proposals, service agreements).
    5. Human Resources (Employment contracts, job descriptions, mission letters).
    6. Operations, Quality, Legal.
  - Task execution and history tracking: save run details, referenced docs, outputs.
- Frontend:
  - Build Document Catalog interface with search, category filtering, one-click workflow triggers.
  - Build History page showing previous tasks, prompt used, documents referenced, download links.
- Verification:
  - End-to-end execution of a full tender compliance analysis workflow and an administrative letter generation.

### Phase 6: Local AI Migration (Ollama Integration) & Final Hardening
- Backend:
  - Implement `OllamaProvider` connecting to local Ollama daemon (`http://localhost:11434`).
  - Model detection, health checks, temperature/parameter controls.
  - Seamless toggle between Free API and Ollama without touching business logic.
- Frontend:
  - AI Settings toggle to select between Local Ollama and External API.
  - Local model auto-detection.
- Verification:
  - Comprehensive automated test suite.
  - Complete documentation and execution guide.

