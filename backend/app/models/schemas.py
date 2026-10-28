"""Pydantic schemas and data models for Vertifact."""

from enum import Enum
from typing import Literal
from pydantic import BaseModel, Field


class VerificationStatus(str, Enum):
    SUPPORTED = "SUPPORTED"
    CONTRADICTED = "CONTRADICTED"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT EVIDENCE"


class DocumentChunk(BaseModel):
    chunk_id: str
    doc_id: str
    filename: str
    page_number: int | None = None
    text: str
    word_count: int = 0
    source_url: str | None = None
    source_type: Literal["uploaded_document", "external_source"] = "uploaded_document"


class DocumentInfo(BaseModel):
    doc_id: str
    filename: str
    file_size_bytes: int
    page_count: int
    extracted_characters: int
    chunk_count: int
    source_type: Literal["pdf", "pasted_text", "web_search"]
    created_at: str
    source_url: str | None = None


class EvidencePassage(BaseModel):
    passage_id: str
    doc_id: str
    filename: str
    page_number: int | None = None
    text: str
    relevance_score: float
    relationship: Literal["supports", "contradicts", "inconclusive", "unrelated"]
    source_url: str | None = None
    retrieval_method: Literal["uploaded_document", "external_source"] = "uploaded_document"


class ClaimResult(BaseModel):
    claim_id: str
    claim_text: str
    original_sentence: str
    status: VerificationStatus
    reasoning: str
    evidence: list[EvidencePassage] = []
    source_document: str | None = None
    source_title: str | None = None
    source_page: int | None = None
    source_url: str | None = None
    retrieval_method: Literal["uploaded_document", "external_source", "none"] = "uploaded_document"
    confidence_metric: str = "evidence_retrieval_and_nli_alignment"
    confidence_score: float = 0.0
    verification_method: Literal["deterministic_nli", "vertifact_neural_engine", "hybrid_rule_engine", "llm_openai"] = "deterministic_nli"




class VerificationSummary(BaseModel):
    total_claims: int
    supported_count: int
    contradicted_count: int
    insufficient_evidence_count: int
    support_ratio: float
    hallucination_risk_level: Literal["LOW", "MODERATE", "HIGH"]
    summary_notes: str


class VerificationReport(BaseModel):
    report_id: str
    timestamp: str
    original_answer: str
    document_sources: list[str]
    summary: VerificationSummary
    claims: list[ClaimResult]
    verification_engine: str
    verification_mode: Literal["document", "autonomous_web", "strict_document"] = "document"


class PastedDocumentRequest(BaseModel):
    text: str = Field(..., min_length=10, description="Pasted source document text")
    title: str = Field(default="Pasted Source Document", max_length=100)


class VerifyRequest(BaseModel):
    ai_answer: str = Field(..., min_length=3, max_length=20000, description="AI-generated answer to verify")
    doc_ids: list[str] | None = Field(default=None, description="IDs of already uploaded documents")
    pasted_source_text: str | None = Field(default=None, description="Direct trusted text to verify against")
    pasted_source_title: str | None = Field(default="Direct Source Text")
    mode: Literal["document", "autonomous_web", "strict_document"] = Field(
        default="document",
        description="Verification mode: 'document' (uses uploaded/pasted docs), 'autonomous_web' (auto-retrieves live web sources), or 'strict_document'"
    )
    fallback_to_web: bool = Field(
        default=True,
        description="Whether to fall back to trusted web sources if uploaded documents lack evidence"
    )


class ExportReportRequest(BaseModel):
    report: VerificationReport
    export_format: Literal["json", "markdown", "text"] = "json"


class HealthResponse(BaseModel):
    status: str
    app_name: str
    version: str
    llm_provider_configured: bool
    llm_model: str
    active_documents_count: int


class LLMConfigRequest(BaseModel):
    api_key: str = Field(..., min_length=5, description="OpenAI or compatible API key")
    model: str = Field(default="gpt-4o-mini", description="Model name, e.g. gpt-4o-mini, gpt-4o, llama-3.3-70b-versatile")
    base_url: str | None = Field(default=None, description="Optional custom base URL for OpenAI-compatible proxies (Groq, OpenRouter, Ollama)")


class LLMConfigResponse(BaseModel):
    configured: bool
    masked_key: str | None = None
    model: str
    base_url: str | None = None
    status: str
    message: str

