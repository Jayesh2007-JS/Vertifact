"""Document processing and session document store."""

import datetime
import uuid
from typing import Dict, List, Optional
from backend.app.config import settings
from backend.app.models.schemas import DocumentChunk, DocumentInfo
from backend.app.services.chunker import chunk_document_pages, chunk_text
from backend.app.services.pdf_extractor import (
    extract_text_from_pdf,
    PDFEmptyError,
    PDFExtractionError
)


class DocumentStore:
    """In-memory session document store for managing ingested files and chunks."""
    def __init__(self):
        self._docs: Dict[str, DocumentInfo] = {}
        self._chunks: Dict[str, List[DocumentChunk]] = {}

    def add_document(self, doc_info: DocumentInfo, chunks: List[DocumentChunk]):
        self._docs[doc_info.doc_id] = doc_info
        self._chunks[doc_info.doc_id] = chunks

    def get_document(self, doc_id: str) -> Optional[DocumentInfo]:
        return self._docs.get(doc_id)

    def list_documents(self) -> List[DocumentInfo]:
        return list(self._docs.values())

    def delete_document(self, doc_id: str) -> bool:
        removed = self._docs.pop(doc_id, None)
        self._chunks.pop(doc_id, None)
        return removed is not None

    def get_chunks_for_docs(self, doc_ids: Optional[List[str]] = None) -> List[DocumentChunk]:
        """Returns all chunks belonging to specified doc_ids (or all docs if None)."""
        result: List[DocumentChunk] = []
        if doc_ids:
            for d_id in doc_ids:
                if d_id in self._chunks:
                    result.extend(self._chunks[d_id])
        else:
            for chunks in self._chunks.values():
                result.extend(chunks)
        return result

    def clear(self):
        self._docs.clear()
        self._chunks.clear()

    @property
    def total_documents(self) -> int:
        return len(self._docs)


# Global document store instance for the active backend process
document_store = DocumentStore()


def process_pdf_file(file_bytes: bytes, filename: str) -> tuple[DocumentInfo, list[DocumentChunk]]:
    """
    Validates, extracts, and chunks a PDF file.
    """
    if len(file_bytes) > settings.MAX_UPLOAD_SIZE_BYTES:
        max_mb = settings.MAX_UPLOAD_SIZE_BYTES / (1024 * 1024)
        raise ValueError(f"File size exceeds maximum permitted limit of {max_mb:.0f} MB.")

    if not filename.lower().endswith(".pdf"):
        raise ValueError(f"Invalid file type. Only PDF files are supported for upload.")

    pages = extract_text_from_pdf(file_bytes=file_bytes, filename=filename)

    total_chars = sum(len(p.text) for p in pages)
    doc_id = f"doc_{uuid.uuid4().hex[:10]}"

    chunks = chunk_document_pages(
        pages=pages,
        doc_id=doc_id,
        filename=filename,
        target_words=settings.CHUNK_SIZE_WORDS,
        overlap_words=settings.CHUNK_OVERLAP_WORDS
    )

    doc_info = DocumentInfo(
        doc_id=doc_id,
        filename=filename,
        file_size_bytes=len(file_bytes),
        page_count=len(pages),
        extracted_characters=total_chars,
        chunk_count=len(chunks),
        source_type="pdf",
        created_at=datetime.datetime.now(datetime.timezone.utc).isoformat()
    )

    document_store.add_document(doc_info, chunks)
    return doc_info, chunks


def process_pasted_text(text: str, title: str = "Pasted Source Document") -> tuple[DocumentInfo, list[DocumentChunk]]:
    """
    Processes directly pasted trusted text into document chunks.
    """
    clean_text = text.strip()
    if not clean_text:
        raise ValueError("Source text cannot be empty.")

    doc_id = f"doc_{uuid.uuid4().hex[:10]}"
    filename = f"{title}.txt" if not title.endswith(".txt") else title

    chunks = chunk_text(
        text=clean_text,
        doc_id=doc_id,
        filename=filename,
        page_number=1,
        target_words=settings.CHUNK_SIZE_WORDS,
        overlap_words=settings.CHUNK_OVERLAP_WORDS
    )

    doc_info = DocumentInfo(
        doc_id=doc_id,
        filename=filename,
        file_size_bytes=len(clean_text.encode("utf-8")),
        page_count=1,
        extracted_characters=len(clean_text),
        chunk_count=len(chunks),
        source_type="pasted_text",
        created_at=datetime.datetime.now(datetime.timezone.utc).isoformat()
    )

    document_store.add_document(doc_info, chunks)
    return doc_info, chunks
