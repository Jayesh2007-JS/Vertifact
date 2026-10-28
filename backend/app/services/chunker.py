"""Text chunking module with paragraph preservation and overlapping windows."""

import re
import uuid
from backend.app.models.schemas import DocumentChunk
from backend.app.services.pdf_extractor import ExtractedPage


def chunk_document_pages(
    pages: list[ExtractedPage],
    doc_id: str,
    filename: str,
    target_words: int = 180,
    overlap_words: int = 35
) -> list[DocumentChunk]:
    """
    Chunks document pages into coherent context windows.
    Groups small paragraphs together to avoid breaking context,
    and splits large paragraphs with sliding window overlap.
    Preserves page number references.
    """
    chunks: list[DocumentChunk] = []

    for page in pages:
        page_chunks = chunk_text(
            text=page.text,
            doc_id=doc_id,
            filename=filename,
            page_number=page.page_number,
            target_words=target_words,
            overlap_words=overlap_words
        )
        chunks.extend(page_chunks)

    # Edge case: if whole document yielded no chunks but had some text
    if not chunks:
        combined_text = "\n\n".join([p.text for p in pages if p.text.strip()]).strip()
        if combined_text:
            chunks.append(
                DocumentChunk(
                    chunk_id=f"chk_{uuid.uuid4().hex[:8]}",
                    doc_id=doc_id,
                    filename=filename,
                    page_number=1,
                    text=combined_text,
                    word_count=len(combined_text.split())
                )
            )

    return chunks


def chunk_text(
    text: str,
    doc_id: str,
    filename: str,
    page_number: int | None = None,
    target_words: int = 180,
    overlap_words: int = 35
) -> list[DocumentChunk]:
    """
    Chunks arbitrary text while respecting paragraph boundaries where possible.
    """
    clean_text = text.strip()
    if not clean_text:
        return []

    # Split into raw paragraphs (delimited by 2 or more newlines)
    raw_paras = [p.strip() for p in re.split(r"\n\s*\n", clean_text) if p.strip()]

    # If no double newlines, try splitting on single newlines or sentence boundaries
    if len(raw_paras) <= 1:
        words = clean_text.split()
        if len(words) <= target_words + overlap_words:
            return [
                DocumentChunk(
                    chunk_id=f"chk_{uuid.uuid4().hex[:8]}",
                    doc_id=doc_id,
                    filename=filename,
                    page_number=page_number,
                    text=clean_text,
                    word_count=len(words)
                )
            ]
        # Sliding window for single long block
        chunks = []
        step = max(1, target_words - overlap_words)
        for i in range(0, len(words), step):
            window = words[i : i + target_words]
            chunk_str = " ".join(window)
            chunks.append(
                DocumentChunk(
                    chunk_id=f"chk_{uuid.uuid4().hex[:8]}",
                    doc_id=doc_id,
                    filename=filename,
                    page_number=page_number,
                    text=chunk_str,
                    word_count=len(window)
                )
            )
        return chunks

    # Multiple paragraphs: merge small ones, split large ones
    chunks: list[DocumentChunk] = []
    current_para_acc: list[str] = []
    current_word_count = 0

    for para in raw_paras:
        para_words = para.split()
        para_len = len(para_words)

        if para_len > target_words * 1.5:
            # First flush any accumulated paragraphs
            if current_para_acc:
                acc_text = "\n\n".join(current_para_acc)
                chunks.append(
                    DocumentChunk(
                        chunk_id=f"chk_{uuid.uuid4().hex[:8]}",
                        doc_id=doc_id,
                        filename=filename,
                        page_number=page_number,
                        text=acc_text,
                        word_count=len(acc_text.split())
                    )
                )
                current_para_acc = []
                current_word_count = 0

            # Split large paragraph with overlap
            step = max(1, target_words - overlap_words)
            for i in range(0, para_len, step):
                window = para_words[i : i + target_words]
                chunk_str = " ".join(window)
                chunks.append(
                    DocumentChunk(
                        chunk_id=f"chk_{uuid.uuid4().hex[:8]}",
                        doc_id=doc_id,
                        filename=filename,
                        page_number=page_number,
                        text=chunk_str,
                        word_count=len(window)
                    )
                )
        else:
            # Accumulate paragraphs until reaching target_words
            if current_word_count + para_len > target_words and current_para_acc:
                acc_text = "\n\n".join(current_para_acc)
                chunks.append(
                    DocumentChunk(
                        chunk_id=f"chk_{uuid.uuid4().hex[:8]}",
                        doc_id=doc_id,
                        filename=filename,
                        page_number=page_number,
                        text=acc_text,
                        word_count=len(acc_text.split())
                    )
                )
                current_para_acc = [para]
                current_word_count = para_len
            else:
                current_para_acc.append(para)
                current_word_count += para_len

    if current_para_acc:
        acc_text = "\n\n".join(current_para_acc)
        chunks.append(
            DocumentChunk(
                chunk_id=f"chk_{uuid.uuid4().hex[:8]}",
                doc_id=doc_id,
                filename=filename,
                page_number=page_number,
                text=acc_text,
                word_count=len(acc_text.split())
            )
        )

    return chunks
