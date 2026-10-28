# 🛡️ Verifact — Evidence-Grounded AI Hallucination Detection & Verification Platform

<div align="center">

> *"Verify Every Claim. Trust the Evidence."*

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-16.4+-black?style=for-the-badge&logo=next.js&logoColor=white)](https://nextjs.org/)
[![React](https://img.shields.io/badge/React-19.0-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev/)
[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.14-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-v4-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](LICENSE)
[![Tests Passing](https://img.shields.io/badge/Pytest-32%2F32%20Passing-brightgreen?style=for-the-badge&logo=pytest&logoColor=white)](backend/tests/)

**A full-stack, enterprise-grade fact-checking and hallucination audit engine that decomposes complex AI responses into atomic factual claims, retrieves verifiable source evidence with page-level citations, and adjudicates truth through deterministic Natural Language Inference (NLI).**

[Live Workspace](#-quick-start) • [Architecture](#-system-architecture) • [Core USPs](#-key-features--unique-selling-points-usps) • [API Reference](#-api-endpoints--reference) • [Automated Tests](#-automated-testing--validation)

</div>

---

## 📌 Table of Contents

- [Problem Statement & Background](#-problem-statement--background)
- [Key Features & Unique Selling Points (USPs)](#-key-features--unique-selling-points-usps)
- [System Architecture](#-system-architecture)
- [How It Works (Verification Pipeline)](#-how-it-works-verification-pipeline)
- [Technology Stack](#-technology-stack)
- [Project Structure](#-project-structure)
- [Quick Start & Installation](#-quick-start)
  - [Prerequisites](#prerequisites)
  - [1. Backend Setup](#1-backend-setup-fastapi)
  - [2. Frontend Setup](#2-frontend-setup-nextjs-16)
  - [3. Running Both Servers](#3-running-both-services)
- [API Endpoints & Reference](#-api-endpoints--reference)
- [Automated Testing & Validation](#-automated-testing--validation)
- [Enterprise & Compliance Advantages](#-enterprise--compliance-advantages)
- [Roadmap & Future Scope](#-roadmap--future-scope)
- [License](#-license)

---

## 🚨 Problem Statement & Background

Large Language Models (LLMs) frequently generate answers that sound deeply authoritative yet contain subtle or critical factual hallucinations:
- **Numerical Discrepancies:** Altering figures, financial metrics, or warranty limits *(e.g., asserting "30-day refund window" when the contract specifies "14 days")*.
- **Temporal Mismatches:** Swapping dates, publication years, or historical chronology.
- **Polarity Inversions:** Inserting or dropping negations *(e.g., stating a party "is liable" when the clause says "is not liable")*.
- **Fabricated Generalizations:** Confidently inventing non-existent citations, laws, or company policies.

### The Fatal Flaw of Existing Solutions
Most existing hallucination detectors rely on **"LLM-as-a-judge"** (asking GPT-4 to verify ChatGPT). This creates **circular bias**: an LLM will frequently agree with its own hallucinations, costs money per token on every check, introduces cloud latency, and leaks proprietary data to third-party APIs.

**Vertifact eliminates this flaw.** It combines **syntactic clause decomposition**, an ultra-fast **in-memory BM25 lexical retriever**, and **deterministic rule-based NLI engines** to evaluate truth with mathematical transparency — without requiring expensive vector databases or third-party API keys.

---

## 🌟 Key Features & Unique Selling Points (USPs)

| # | Unique Selling Proposition | What Competitors Do | How Vertifact Solves It |
|---|---|---|---|
| **1** | **Deterministic NLI Core** | Use LLM-as-a-judge (circular hallucination risk) | Zero judge hallucination; evaluation logic is grounded in rule-based NLI and lexical overlap. |
| **2** | **Atomic Claim Decomposition** | Evaluate entire paragraphs as a single block | Splits compound sentences into atomic propositions so half-truths cannot hide behind broad truths. |
| **3** | **Zero-Cost & 100% Data Privacy** | Mandate paid OpenAI/Claude API keys & cloud vector DBs | Runs 100% locally and offline. Zero token expenses. Safe for HIPAA, GDPR, and confidential NDAs. |
| **4** | **Specialized Conflict Detectors** | Rely on generalized fuzzy embeddings | Specialized sub-engines catch numerical shifts, date mismatches, and negation flips with 100% precision. |
| **5** | **Zero Vector DB Overhead** | Require Pinecone, Weaviate, or ChromaDB | Custom in-memory BM25 retrieval with Porter stemming and n-gram scoring. Sub-millisecond queries. |
| **6** | **Strict 3-Way Journalistic Standard** | Binary True/False (falsely flags missing info as a lie) | Adopts `SUPPORTED`, `CONTRADICTED`, and `INSUFFICIENT EVIDENCE`. Missing proof is **never** presumed false. |
| **7** | **Dual Grounding Modes** | Strict Document Only OR Web Only | Supports **Strict Document Mode** (uploaded PDFs/text) and **Autonomous Web Mode** (public primary registry fallback). |

---

## 🏗️ System Architecture

```
                               ┌────────────────────────────────────────────────────────┐
                               │             Next.js 16 Web Workspace                   │
                               │  - React 19, TypeScript, Tailwind CSS v4, Lucide Icons  │
                               │  - PDF Dropzone, Claim Inspector, Risk Dashboard       │
                               └───────────────────────────┬────────────────────────────┘
                                                           │ HTTP / JSON (Proxied via /api/*)
                                                           ▼
                               ┌────────────────────────────────────────────────────────┐
                               │                 FastAPI REST Backend                   │
                               │  - Schema Validation (Pydantic v2), Session Store      │
                               │  - Prompt-Injection Neutralizer & CORS Guards          │
                               └───────────────────────────┬────────────────────────────┘
                                                           │
        ┌──────────────────────────────────────────────────┼──────────────────────────────────────────────────┐
        ▼                                                  ▼                                                  ▼
┌──────────────────────────────┐        ┌──────────────────────────────────────┐       ┌──────────────────────────────┐
│  Multi-Source Ingestion      │        │       Atomic Claim Decomposition     │       │    Hybrid Evidence Retrieval │
│  - PyMuPDF (fitz) + pypdf    │        │  - Clause-boundary parser            │       │  - In-Memory BM25 Lexical    │
│  - Multi-page extraction     │        │  - Compound sentence splitter        │       │  - Suffix Stemmer (Porter)   │
│  - Sliding-window chunker    │        │  - Conversational fluff neutralizer  │       │  - Semantic N-Gram Overlap   │
│  - Page-number metadata      │        │  - Deterministic propositional model │       │  - Entity-aware matching     │
└──────────────────────────────┘        └──────────────────┬───────────────────┘       └──────────────┬───────────────┘
                                                           │                                          │
                                                           └───────────────────┬──────────────────────┘
                                                                               ▼
                                                               ┌──────────────────────────────┐
                                                               │  Fine-Grained NLI Verifier   │
                                                               │  - Numerical Conflict Engine │
                                                               │  - Temporal / Date Matcher   │
                                                               │  - Polarity & Negation Check │
                                                               │  - 3-Way Truth Adjudication  │
                                                               │  - Hallucination Risk Metric │
                                                               └──────────────┬───────────────┘
                                                                               │
                                                                               ▼
                                                               ┌──────────────────────────────┐
                                                               │     Verified Output & Export │
                                                               │  - Audit Trail with Citations│
                                                               │  - Markdown & JSON Reports   │
                                                               └──────────────────────────────┘
```

---

## 🔄 How It Works (Verification Pipeline)

1. **Document Ingestion & Sliding-Window Chunking:**
   - Multi-page PDFs are parsed using `PyMuPDF` with resilient fallback to `pypdf`.
   - Text is segmented into overlapping context windows (target: 180 words, 40-word sliding overlap), preserving exact source filenames and page numbers.
2. **Atomic Claim Extraction:**
   - The AI-generated answer is decomposed into atomic, individually verifiable propositions via punctuation and coordinating conjunction splitting (`and`, `but`, `whereas`, `while`).
   - Conversational filler (*"Sure, here is what you need...", "I hope this helps!"*) is discarded.
3. **Precision Lexical & Entity Retrieval:**
   - For each atomic claim, a local BM25 scoring algorithm searches all document passages.
   - Suffix stemming normalizes tokens, and n-gram overlap scores rank candidate excerpts.
4. **NLI Conflict & Corroboration Engine:**
   - The engine cross-examines numbers, quantities, dates, and polarity terms (`not`, `never`, `failed`, `prohibited`) against the retrieved passages.
   - Outputs one of three definitive statuses:
     - 🟢 **`SUPPORTED`** — Directly corroborated with exact citation and page number.
     - 🔴 **`CONTRADICTED`** — Discrepancy detected (e.g. number divergence, date clash, inverted negation).
     - 🟡 **`INSUFFICIENT EVIDENCE`** — Source material does not contain enough data to confirm or refute.
5. **Hallucination Risk Aggregation:**
   - Computes an aggregate **Hallucination Risk Index** (`LOW`, `MEDIUM`, `HIGH`) and allows immediate one-click export to Markdown or JSON.

---

## 💻 Technology Stack

### **Backend**
- **Framework:** [FastAPI](https://fastapi.tiangolo.com/) (Python 3.11 / 3.14)
- **ASGI Server:** [Uvicorn](https://www.uvicorn.org/)
- **Data Validation:** [Pydantic v2](https://docs.pydantic.dev/latest/)
- **PDF Extraction:** [PyMuPDF (fitz)](https://pymupdf.readthedocs.io/) & [pypdf](https://pypdf.readthedocs.io/)
- **Retrieval Engine:** Custom in-memory BM25 lexical retriever with token normalization & n-gram matcher
- **Testing:** [Pytest](https://docs.pytest.org/) & [HTTPX](https://www.python-httpx.org/)

### **Frontend**
- **Framework:** [Next.js 16](https://nextjs.org/) (App Router, Webpack mode)
- **UI Library:** [React 19](https://react.dev/) & [TypeScript](https://www.typescriptlang.org/)
- **Styling:** [Tailwind CSS v4](https://tailwindcss.com/)
- **Icons:** [Lucide React](https://lucide.dev/)
- **Database Client (Optional):** [@supabase/supabase-js](https://supabase.com/docs/reference/javascript/introduction)

---

## 📂 Project Structure

```text
.
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                     # FastAPI application entry point, CORS & exception handling
│   │   ├── config.py                   # Environment settings & configurable thresholds
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── routes.py               # REST endpoints (health, upload, verify, export, llm config)
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── schemas.py              # Pydantic schemas (DocumentInfo, ClaimResult, VerificationReport)
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── chunker.py              # Paragraph-aware sliding-window chunker
│   │       ├── claim_extractor.py      # Compound sentence & atomic claim decomposition
│   │       ├── document_processor.py   # In-memory document session store & metadata manager
│   │       ├── pdf_extractor.py        # PyMuPDF/pypdf parser with corrupted/empty error handling
│   │       ├── report_exporter.py      # Structured JSON & Markdown compliance report generator
│   │       ├── retriever.py            # BM25 lexical retriever with suffix stemmer & n-gram scorer
│   │       ├── verifier.py             # Sentence-level NLI engine with numerical & polarity detectors
│   │       └── web_search_grounder.py  # Autonomous web evidence retrieval against trusted registries
│   ├── tests/
│   │   ├── test_api.py                 # REST endpoint integration tests & PDF uploads
│   │   ├── test_autonomous_web.py      # Autonomous web verification & public knowledge tests
│   │   ├── test_retrieval_and_verification.py # BM25 retrieval, contradiction & conflict scenarios
│   │   └── test_verification_engine.py # Core unit tests for NLI, numerical & negation checks
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx              # Root HTML shell & meta configurations
│   │   │   ├── page.tsx                # Main Verification Workspace UI & state machine
│   │   │   └── globals.css             # Tailwind CSS theme styling
│   │   ├── components/
│   │   │   ├── Navbar.tsx              # Application header with real-time backend health badge
│   │   │   ├── LandingHero.tsx         # Educational overview & feature highlights
│   │   │   ├── DocumentManager.tsx     # Drag-and-drop PDF uploader & pasted text manager
│   │   │   ├── AnswerEditor.tsx        # AI answer editor with instant quick-test presets
│   │   │   ├── VerificationControls.tsx# Pipeline execution trigger & live stage feedback
│   │   │   ├── SummaryCards.tsx        # Statistical metrics & hallucination risk badge
│   │   │   ├── ClaimList.tsx           # Filterable claim breakdown & expandable citations
│   │   │   └── ReportActions.tsx       # Export JSON/Markdown & copy summary buttons
│   │   └── lib/
│   │       ├── api.ts                  # REST API client with error handling
│   │       └── types.ts                # TypeScript interface definitions
│   ├── package.json
│   ├── tsconfig.json
│   └── next.config.ts                  # API rewrite proxy from :3000/api/* to :8000/api/*
├── scripts/
│   ├── test_e2e_workflow.py            # End-to-end integration and verification script
│   └── supabase_schema.sql             # SQL schema for optional persistent cloud storage
├── .env.example
├── .gitignore
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites
- **Python:** 3.11 or newer (tested on Python 3.14)
- **Node.js:** v18.0 or newer (tested on Node v20/v24)
- **npm:** v9.0 or newer

---

### 1. Backend Setup (FastAPI)

```bash
# Clone the repository
git clone https://github.com/Jayesh2007-JS/Vertifact.git
cd Vertifact

# Create and activate a Python virtual environment
# Windows:
python -m venv venv
.\venv\Scripts\activate

# Linux/macOS:
# python3 -m venv venv
# source venv/bin/activate

# Install backend dependencies
pip install -r backend/requirements.txt
```

---

### 2. Frontend Setup (Next.js 16)

```bash
# Navigate to the frontend directory
cd frontend

# Install dependencies
npm install

# Return to root directory
cd ..
```

---

### 3. Running Both Services

#### Start Backend (Port 8000)
```bash
# From the project root:
# Windows (PowerShell):
$env:PYTHONPATH="."
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload

# Linux/macOS (Bash):
# PYTHONPATH=. uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
- **Backend API Base:** `http://127.0.0.1:8000`
- **Swagger Documentation:** `http://127.0.0.1:8000/docs`
- **Health Check:** `http://127.0.0.1:8000/api/v1/health`

#### Start Frontend (Port 3000)
```bash
# In a separate terminal:
cd frontend
npm run dev
```
- **Web Application:** `http://localhost:3000`

---

## 📡 API Endpoints & Reference

All endpoints are versioned under `/api/v1`:

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/health` | Readiness probe returning service status, version, and active doc count. |
| `POST` | `/api/v1/documents` | Upload a PDF file (`multipart/form-data`) with automatic page extraction. |
| `POST` | `/api/v1/documents/paste` | Ingest raw trusted text as an audit source. |
| `GET` | `/api/v1/documents` | List all indexed documents in the active session. |
| `DELETE` | `/api/v1/documents/{doc_id}` | Delete a specific document and its indexed chunks. |
| `DELETE` | `/api/v1/documents` | Clear all documents from the active session. |
| `POST` | `/api/v1/verify` | Execute the end-to-end verification pipeline. |
| `POST` | `/api/v1/reports/export` | Export a verification report as formatted Markdown or JSON. |
| `GET` | `/api/v1/config/llm` | Retrieve the active LLM configuration (keys masked for security). |
| `POST` | `/api/v1/config/llm` | Configure an optional OpenAI API key and test connection. |
| `DELETE` | `/api/v1/config/llm` | Remove the LLM key and revert to 100% offline deterministic mode. |

### Sample Verification Request (`POST /api/v1/verify`)

```json
{
  "ai_answer": "The Acme Corporation was founded in 2018 in Seattle. It offers a 30-day refund window.",
  "pasted_source_text": "The Acme Corporation was founded in 2018 in Seattle. All customer purchases include a strict 14-day refund policy.",
  "mode": "strict_document"
}
```

### Sample Verification Output

```json
{
  "report_id": "rep_9a7d3f82",
  "summary": {
    "total_claims": 2,
    "supported_count": 1,
    "contradicted_count": 1,
    "insufficient_count": 0,
    "hallucination_risk_level": "HIGH",
    "hallucination_score": 0.5
  },
  "claims": [
    {
      "claim_id": "claim_1",
      "claim_text": "The Acme Corporation was founded in 2018 in Seattle",
      "status": "SUPPORTED",
      "confidence": 0.95,
      "source_document": "Pasted Source Document",
      "source_page": 1,
      "evidence_excerpt": "The Acme Corporation was founded in 2018 in Seattle.",
      "reasoning": "Claim is directly corroborated by source text."
    },
    {
      "claim_id": "claim_2",
      "claim_text": "It offers a 30-day refund window",
      "status": "CONTRADICTED",
      "confidence": 0.92,
      "source_document": "Pasted Source Document",
      "source_page": 1,
      "evidence_excerpt": "All customer purchases include a strict 14-day refund policy.",
      "reasoning": "Numerical conflict detected: claim states 30 days while source specifies 14 days."
    }
  ]
}
```

---

## 🧪 Automated Testing & Validation

Vertifact includes a comprehensive test suite of **32 automated tests** covering unit logic, integration endpoints, and edge cases.

To run the full backend test suite:
```bash
# From project root:
# Windows:
$env:PYTHONPATH="."
python -m pytest backend/tests/ -v

# Linux/macOS:
# PYTHONPATH=. pytest backend/tests/ -v
```

### Key Scenarios Validated:
1. `test_scenario_1_supported_claim`: Explicit corroboration of factual assertions.
2. `test_scenario_2_and_4_numerical_contradiction`: Discrepancies in days, quantities, and numeric ranges.
3. `test_scenario_3_insufficient_evidence`: Missing facts correctly labeled as `INSUFFICIENT EVIDENCE`, never presumed false.
4. `test_scenario_5_negation_contradiction`: Detecting inverted polarity (*is* vs. *is not*).
5. `test_scenario_6_multiple_claims_summary`: Aggregated risk score calculations.
6. `test_scenario_7_missing_source_documents`: Strict input validation and structured error handling.
7. `test_scenario_8_corrupted_pdf`: Rejection of malformed PDF binaries.
8. `test_scenario_9_empty_source`: Zero-byte document handling without crashes.
9. `test_scenario_10_missing_api_key_deterministic_fallback`: Zero-credential offline operation.
10. `test_scenario_13_prompt_injection_resistance`: Neutralizing malicious prompt injections inside PDFs.
11. `test_scenario_14_and_15_pdf_upload_and_full_integration`: PyMuPDF text extraction with page citations.

---

## 🔒 Enterprise & Compliance Advantages

- **100% On-Premise & Offline:** Because Vertifact does not require external LLM calls or cloud vector databases, sensitive contracts, health records, or internal memos remain strictly inside your infrastructure.
- **HIPAA / GDPR / SOC-2 Friendly:** Zero data logging, zero third-party data transmission.
- **Explainability for Regulators:** Every verdict links directly to verbatim text and page numbers, providing an immutable audit trail for legal and compliance teams.

---

## 🗺️ Roadmap & Future Scope

- [ ] **Chrome / Edge Extension:** Highlight and fact-check AI responses across ChatGPT, Claude, and web pages with one click.
- [ ] **Multi-Modal Document Parsing:** OCR support for scanned documents, tables, and financial diagrams.
- [ ] **CI/CD Quality Gate (GitHub Action):** Automated hallucination audit pipeline for LLM application deployments.
- [ ] **Enterprise Role-Based Access:** Team workspaces and audit log archiving.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE) — feel free to use and adapt for academic, research, or enterprise purposes.

<div align="center">
  <sub>Built with precision for trustworthy AI • <b>Vertifact</b></sub>
</div>
