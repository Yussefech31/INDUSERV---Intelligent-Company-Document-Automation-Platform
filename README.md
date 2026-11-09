# INDUSERV - Intelligent Company Document Automation Platform

> **Enterprise-grade, AI-driven document automation platform for administrative, financial, commercial, HR, procurement, and operational workflows.**
> Built with strict mathematical determinism, document ground-truth verification, and seamless support for external free AI APIs and 100% private local Ollama inference.

---

## 🌟 Key Features & Capabilities

- **Multi-Format Ingestion**: High-fidelity text, table, and metadata extraction from **PDF** (via PyMuPDF), **Word (.docx)** (headings, hierarchy & tables), **Excel (.xlsx)** (multi-tab & numbers), **CSV**, and **TXT** files.
- **Auditable Mathematical & Analytical Engine**: AI models are strictly barred from mental arithmetic. All VAT, discounts, HT/TTC, margins, and budget variances are computed deterministically using Python's `Decimal` with full traceability and legal `ROUND_HALF_UP` rounding.
- **Enterprise Document Generation**: Export professionally styled **Word (DOCX)**, **PDF** (via ReportLab with full French UTF-8 accent support and dynamic `Page X sur Y`), and **Excel (XLSX)** with live formulas (`=SUM()`, `=C4*D4`) and styled financial tables.
- **AI Provider Abstraction**:
  - **Free / Open API Provider**: Preconfigured for Groq, OpenRouter, Google Gemini, or any OpenAI-compatible provider.
  - **Local Ollama Provider**: Run 100% offline and securely with local models (`llama3.2`, `mistral`, `qwen2.5`) with zero business logic changes.
  - **OpenAI-Compatible Provider**: Universal provider for custom local or hosted gateways.
- **Comprehensive Document Catalog**: Over 50 pre-mapped enterprise document types organized across 8 corporate domains:
  1. *Administrative Documents* (Official letters, attestations, meeting minutes, memos)
  2. *Procurement & Public Tenders (Appels d'offres)* (Tender requirement extraction, compliance gap matrix, missing documents checklist, bid response generation)
  3. *Financial & Accounting* (Invoices, pro forma, VAT reports, budget variance, cash flow)
  4. *Human Resources* (Contracts, job descriptions, mission letters, onboarding)
  5. *Commercial & Sales* (Quotations/devis, commercial proposals, service agreements)
  6. *Legal & Contractual* (NDAs, contract reviews, amendment drafts)
  7. *Operations & Project Management* (Project charters, action plans, status reports)
  8. *Quality & Compliance* (Audit reports, non-conformity trackers, safety procedures)
- **Interactive Modern SaaS UI**: React 18, TypeScript, Vite, Tailwind CSS, Lucide icons, responsive sidebar, toast notifications, and calculation simulators.

---

## 🏗️ Architecture

```
INDUSERV/
├── backend/
│   ├── app/
│   │   ├── api/routes/          # FastAPI REST endpoints (health, workspace, documents, calculations, etc.)
│   │   ├── core/                # Config, logging, security
│   │   ├── database/            # SQLAlchemy database, session & seeders
│   │   ├── models/              # ORM data models
│   │   ├── schemas/             # Pydantic validation schemas
│   │   ├── services/
│   │   │   ├── ai/              # AIProvider abstraction (Free API, Ollama, OpenAI)
│   │   │   ├── calculations/    # Deterministic financial & analytical math
│   │   │   ├── documents/       # PDF, DOCX, XLSX extraction & parsing
│   │   │   ├── generation/      # DOCX, PDF, XLSX generation engines
│   │   │   ├── retrieval/       # Chunking & BM25 keyword retrieval
│   │   │   └── workflows/       # Tender analysis & compliance workflows
│   │   └── main.py              # Application entry point
│   ├── tests/                   # 26 automated unit & integration tests
│   ├── requirements.txt         # Python dependencies
│   └── .env.example             # Environment variable template
├── frontend/
│   ├── src/
│   │   ├── components/          # Reusable UI widgets & layouts (Sidebar, Header)
│   │   ├── pages/               # Dashboard, AI Workspace, Documents, Catalog, Calculations, History, Settings
│   │   ├── services/            # Typed API client services
│   │   ├── types/               # TypeScript interfaces
│   │   └── App.tsx              # Router & main application
│   ├── package.json
│   ├── vite.config.ts
│   └── tailwind.config.js
├── storage/
│   ├── uploads/                 # Stored source documents
│   ├── generated/               # Generated DOCX, PDF, XLSX documents
│   └── templates/               # Document templates
├── docs/                        # Architecture & implementation specs
└── README.md
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- **Python**: 3.11+ (verified on Python 3.13)
- **Node.js**: v18+ (verified on Node v24)
- Optional: **Ollama** installed locally for 100% offline, confidential inference.

### 2. Backend Setup & Startup
```bash
# Navigate to backend
cd backend

# Create virtual environment and install dependencies (using uv or standard venv)
uv venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
# source .venv/bin/activate

uv pip install -r requirements.txt

# Run the backend server
.venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
The backend API documentation is available at `http://127.0.0.1:8000/docs`.

### 3. Frontend Setup & Startup
```bash
# Navigate to frontend (in a separate terminal)
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```
Open `http://localhost:5173` in your browser.

---

## 🧪 Running the Automated Test Suite

A comprehensive test suite of 26 tests covers all 6 implementation phases:
```bash
cd backend
.venv\Scripts\python -m pytest tests/ -v
```
All tests validate:
- **Phase 1**: System prompt CRUD, provider settings, fallback generation, health check.
- **Phase 2**: High-fidelity extraction of PDF, DOCX, XLSX, chunking, BM25 retrieval ranking, and file upload API.
- **Phase 3**: Deterministic financial math (`compute_ht_to_ttc`, margins, budget variances, multi-rate invoices, and audit persistence).
- **Phase 4**: Word (`.docx`), PDF (with French accented glyphs & `NumberedCanvas`), Excel (`.xlsx` with formulas), and document download API.
- **Phase 5**: Template catalog filtering, custom template creation, tender requirement & compliance gap workflow analysis, task history.
- **Phase 6**: Local Ollama provider offline diagnostics and zero-downtime provider factory switching.

---

## 🔒 Security & Privacy Notice
- When running in **External API mode**, user queries and selected document excerpts are transmitted to the configured API provider.
- For maximum confidentiality, switch to the **Ollama Provider** to run inference completely offline on your local machine with zero external network transmission.
- Uploaded files and generated documents are stored locally in the `storage/` directory and are never executed.

---

## 📄 License
Internal Enterprise License - INDUSERV 2026.
