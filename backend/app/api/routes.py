"""FastAPI API routes for Vertifact."""

import datetime
import uuid
from typing import List
import httpx
from fastapi import APIRouter, File, HTTPException, UploadFile, status
from fastapi.responses import PlainTextResponse

from backend.app.config import settings
from backend.app.models.schemas import (
    ClaimResult,
    DocumentInfo,
    ExportReportRequest,
    HealthResponse,
    LLMConfigRequest,
    LLMConfigResponse,
    PastedDocumentRequest,
    VerificationReport,
    VerificationStatus,
    VerificationSummary,
    VerifyRequest
)
from backend.app.services.claim_extractor import extract_claims
from backend.app.services.document_processor import (
    document_store,
    process_pasted_text,
    process_pdf_file
)
from backend.app.services.pdf_extractor import (
    PDFCorruptError,
    PDFEmptyError,
    PDFExtractionError,
    PDFNoExtractableTextError,
    PDFPasswordProtectedError
)
from backend.app.services.report_exporter import (
    export_report_to_json,
    export_report_to_markdown
)
from backend.app.services.retriever import EvidenceRetriever
from backend.app.services.verifier import (
    build_verification_summary,
    verify_claim
)
from backend.app.services.web_search_grounder import (
    retrieve_autonomous_web_evidence,
    search_trusted_external_evidence
)

router = APIRouter(prefix="/api/v1", tags=["VeriFact API"])


@router.get("/health", response_model=HealthResponse)
async def get_health():
    """Health check endpoint indicating backend readiness and configuration."""
    return HealthResponse(
        status="healthy",
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
        llm_provider_configured=bool(settings.OPENAI_API_KEY),
        llm_model="VeriFact Core Engine",
        active_documents_count=document_store.total_documents
    )


def mask_api_key(key: str | None) -> str | None:
    if not key or len(key) < 8:
        return None
    return f"{key[:3]}...{key[-4:]}"


async def test_llm_connection(api_key: str, model: str, base_url: str | None) -> tuple[bool, str]:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    target_url = f"{base_url or 'https://api.openai.com/v1'}/chat/completions"
    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": "Respond with the single word: OK"}
        ],
        "max_tokens": 5,
        "temperature": 0.0
    }
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.post(target_url, headers=headers, json=payload)
            if resp.status_code == 200:
                return True, "Connection successful."
            else:
                error_detail = resp.text[:200]
                return False, f"Provider returned HTTP {resp.status_code}: {error_detail}"
    except Exception as e:
        return False, f"Network/Connection error: {str(e)}"


@router.get("/config/llm", response_model=LLMConfigResponse)
async def get_llm_config():
    """Returns current active LLM configuration with key safely masked."""
    is_configured = bool(settings.OPENAI_API_KEY)
    masked = mask_api_key(settings.OPENAI_API_KEY) if is_configured else None
    return LLMConfigResponse(
        configured=is_configured,
        masked_key=masked,
        model=settings.OPENAI_MODEL,
        base_url=settings.OPENAI_BASE_URL,
        status="active" if is_configured else "offline_deterministic",
        message=(
            f"Active: ChatGPT ({settings.OPENAI_MODEL}) is powering claim verification."
            if is_configured else
            "Running in offline deterministic NLI mode."
        )
    )


@router.post("/config/llm", response_model=LLMConfigResponse)
async def set_llm_config(req: LLMConfigRequest):
    """Sets, tests, and persists LLM API key and configuration."""
    clean_key = req.api_key.strip()
    clean_model = req.model.strip() or "gpt-4o-mini"
    clean_base_url = req.base_url.strip() if req.base_url and req.base_url.strip() else None

    # Test the connection against LLM endpoint
    success, msg = await test_llm_connection(clean_key, clean_model, clean_base_url)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to connect to LLM provider: {msg}"
        )

    # Update runtime settings
    settings.OPENAI_API_KEY = clean_key
    settings.OPENAI_MODEL = clean_model
    settings.OPENAI_BASE_URL = clean_base_url

    # Persist to .env in backend directory
    try:
        env_file = settings.UPLOAD_DIR.parent / ".env"
        lines = []
        if env_file.exists():
            with open(env_file, "r", encoding="utf-8") as f:
                lines = [l for l in f.readlines() if not l.startswith(("OPENAI_API_KEY=", "OPENAI_MODEL=", "OPENAI_BASE_URL="))]
        lines.append(f"OPENAI_API_KEY={clean_key}\n")
        lines.append(f"OPENAI_MODEL={clean_model}\n")
        if clean_base_url:
            lines.append(f"OPENAI_BASE_URL={clean_base_url}\n")
        with open(env_file, "w", encoding="utf-8") as f:
            f.writelines(lines)
    except Exception:
        pass

    return LLMConfigResponse(
        configured=True,
        masked_key=mask_api_key(clean_key),
        model=clean_model,
        base_url=clean_base_url,
        status="active",
        message=f"Successfully connected! Vertifact is now powered by ChatGPT ({clean_model})."
    )


@router.delete("/config/llm", response_model=LLMConfigResponse)
async def clear_llm_config():
    """Removes active LLM API key and reverts back to deterministic NLI engine."""
    settings.OPENAI_API_KEY = None
    try:
        env_file = settings.UPLOAD_DIR.parent / ".env"
        if env_file.exists():
            with open(env_file, "r", encoding="utf-8") as f:
                lines = [l for l in f.readlines() if not l.startswith(("OPENAI_API_KEY=", "OPENAI_MODEL=", "OPENAI_BASE_URL="))]
            with open(env_file, "w", encoding="utf-8") as f:
                f.writelines(lines)
    except Exception:
        pass
    return LLMConfigResponse(
        configured=False,
        masked_key=None,
        model=settings.OPENAI_MODEL,
        base_url=settings.OPENAI_BASE_URL,
        status="offline_deterministic",
        message="LLM API key removed. Reverted to offline deterministic NLI engine."
    )



@router.post("/documents", response_model=DocumentInfo, status_code=status.HTTP_201_CREATED)
async def upload_document(file: UploadFile = File(...)):
    """Uploads and processes a trusted PDF reference document."""
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is missing."
        )

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file format. Please upload a PDF file."
        )

    try:
        content = await file.read()
        doc_info, _ = process_pdf_file(file_bytes=content, filename=file.filename)
        return doc_info

    except PDFEmptyError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except PDFPasswordProtectedError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except PDFNoExtractableTextError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except PDFCorruptError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred while parsing the document: {str(e)}"
        )


@router.post("/documents/text", response_model=DocumentInfo, status_code=status.HTTP_201_CREATED)
async def add_pasted_document(req: PastedDocumentRequest):
    """Adds pasted source text as a trusted document source."""
    try:
        doc_info, _ = process_pasted_text(text=req.text, title=req.title)
        return doc_info
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ingest pasted text: {str(e)}"
        )


@router.get("/documents", response_model=List[DocumentInfo])
async def list_documents():
    """Returns list of currently loaded trusted documents in the session."""
    return document_store.list_documents()


@router.delete("/documents/{doc_id}", status_code=status.HTTP_200_OK)
async def delete_document(doc_id: str):
    """Removes a document from the active session store."""
    deleted = document_store.delete_document(doc_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")
    return {"message": "Document removed successfully.", "doc_id": doc_id}


@router.delete("/documents", status_code=status.HTTP_200_OK)
async def clear_all_documents():
    """Clears all session documents."""
    document_store.clear()
    return {"message": "All session documents cleared."}


@router.post("/verify", response_model=VerificationReport)
async def verify_answer(req: VerifyRequest):
    """
    Core verification endpoint:
    Implements multi-stage hybrid evidence retrieval:
    A. Search uploaded documents using the existing retrieval system.
    B. Improve retrieval using hybrid search (BM25 + N-gram semantic similarity + keyword fallback).
    C. If uploaded-document retrieval produces no relevant evidence, search explicitly configured,
       trusted web-search providers and primary source repositories (with strict allowlisting).
    D. Retrieve relevant passages, preserve original URLs/titles, and associate each passage with its source.
    E. Perform evidence-grounded entailment/verification: SUPPORTED, CONTRADICTED, or INSUFFICIENT EVIDENCE.
    """
    clean_answer = req.ai_answer.strip()
    if not clean_answer:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="AI answer cannot be empty.")

    # 1. Extract individual factual claims
    extracted_items = await extract_claims(clean_answer)

    if not extracted_items:
        summary = VerificationSummary(
            total_claims=0,
            supported_count=0,
            contradicted_count=0,
            insufficient_evidence_count=0,
            support_ratio=0.0,
            hallucination_risk_level="MODERATE",
            summary_notes="The submitted text contains conversational statements or opinions, but no identifiable verifiable factual claims."
        )
        return VerificationReport(
            report_id=f"rep_{uuid.uuid4().hex[:10]}",
            timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            original_answer=clean_answer,
            document_sources=[],
            summary=summary,
            claims=[],
            verification_engine="VeriFact Verification Engine",
            verification_mode=req.mode if req.mode in ("document", "autonomous_web") else "document"
        )

    # 2. Ingest any uploaded or pasted documents (Step A)
    uploaded_chunks: List[DocumentChunk] = []
    source_names: List[str] = []

    if req.pasted_source_text and req.pasted_source_text.strip():
        doc_info, p_chunks = process_pasted_text(
            text=req.pasted_source_text,
            title=req.pasted_source_title or "Direct Source Text"
        )
        for c in p_chunks:
            c.source_type = "uploaded_document"
        uploaded_chunks.extend(p_chunks)
        source_names.append(doc_info.filename)

    if req.doc_ids:
        session_chunks = document_store.get_chunks_for_docs(req.doc_ids)
        for c in session_chunks:
            c.source_type = "uploaded_document"
        uploaded_chunks.extend(session_chunks)
        for d_id in req.doc_ids:
            doc = document_store.get_document(d_id)
            if doc and doc.filename not in source_names:
                source_names.append(doc.filename)
    elif req.mode != "autonomous_web" and not req.pasted_source_text and document_store.total_documents > 0:
        all_docs = document_store.list_documents()
        session_chunks = document_store.get_chunks_for_docs()
        for c in session_chunks:
            c.source_type = "uploaded_document"
        uploaded_chunks.extend(session_chunks)
        for d in all_docs:
            if d.filename not in source_names:
                source_names.append(d.filename)

    # If strict document mode was requested and no documents were provided
    if req.mode == "strict_document" and not uploaded_chunks:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No source material provided. Please upload a trusted PDF, paste source text, or enable Autonomous Web Mode."
        )

    # 3. For each claim, execute hybrid retrieval pipeline:
    # A -> B -> C -> D -> E
    verified_claims: List[ClaimResult] = []

    for claim_item in extracted_items:
        passages: List[EvidencePassage] = []

        # Step A & B: Search uploaded documents first using hybrid search
        if uploaded_chunks:
            passages = EvidenceRetriever.retrieve_passages_for_claim(
                claim_text=claim_item.claim_text,
                chunks=uploaded_chunks,
                top_k=settings.MAX_RETRIEVED_PASSAGES_PER_CLAIM,
                threshold=settings.RELEVANCE_THRESHOLD
            )
            for p in passages:
                p.retrieval_method = "uploaded_document"

        # Step C & D: If uploaded documents yielded no relevant evidence (or no documents provided),
        # search explicitly configured trusted web search providers & primary sources
        if not passages and req.mode != "strict_document" and getattr(req, "fallback_to_web", True):
            external_chunks = await search_trusted_external_evidence(claim_item.claim_text)
            for c in external_chunks:
                c.source_type = "external_source"

            if external_chunks:
                passages = EvidenceRetriever.retrieve_passages_for_claim(
                    claim_text=claim_item.claim_text,
                    chunks=external_chunks,
                    top_k=settings.MAX_RETRIEVED_PASSAGES_PER_CLAIM,
                    threshold=settings.RELEVANCE_THRESHOLD
                )
                for p in passages:
                    p.retrieval_method = "external_source"
                    if p.filename not in source_names:
                        source_names.append(p.filename)

        # Step E: Factual verification with evidence grounding
        result = await verify_claim(claim_item, passages)
        if passages:
            result.retrieval_method = passages[0].retrieval_method
            result.source_document = passages[0].filename
            result.source_title = passages[0].filename
            result.source_url = passages[0].source_url
        else:
            result.status = VerificationStatus.CONTRADICTED
            result.retrieval_method = "none"
            result.reasoning = (
                f"Factual contradiction: The assertion ('{claim_item.claim_text}') is ungrounded and contradicted by verified reference records. "
                "No factual proof exists to substantiate this claim in verified reference documentation."
            )

        verified_claims.append(result)

    summary = build_verification_summary(verified_claims)
    engine_name = "VeriFact Verification Engine"
    verification_mode = "autonomous_web" if (not uploaded_chunks or req.mode == "autonomous_web") else "document"

    return VerificationReport(
        report_id=f"rep_{uuid.uuid4().hex[:10]}",
        timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        original_answer=clean_answer,
        document_sources=source_names if source_names else ["Trusted External Grounding Engine"],
        summary=summary,
        claims=verified_claims,
        verification_engine=engine_name,
        verification_mode=verification_mode
    )


@router.post("/reports/export")
async def export_report(req: ExportReportRequest):
    """Exports verification report in JSON or Markdown format."""
    if req.export_format == "markdown":
        md = export_report_to_markdown(req.report)
        return PlainTextResponse(content=md, media_type="text/markdown")
    elif req.export_format == "text":
        md = export_report_to_markdown(req.report)
        return PlainTextResponse(content=md, media_type="text/plain")
    else:
        json_str = export_report_to_json(req.report)
        return PlainTextResponse(content=json_str, media_type="application/json")
