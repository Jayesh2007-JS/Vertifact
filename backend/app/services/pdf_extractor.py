"""PDF extraction module preserving page metadata and handling corrupt/empty files."""

import io
from typing import NamedTuple
import pypdf
try:
    import pymupdf as fitz
except ImportError:
    try:
        import fitz
    except ImportError:
        fitz = None


class ExtractedPage(NamedTuple):
    page_number: int  # 1-indexed
    text: str


class PDFExtractionError(Exception):
    """Base exception for PDF extraction failures."""
    pass


class PDFPasswordProtectedError(PDFExtractionError):
    """Raised when PDF is encrypted or password-protected."""
    pass


class PDFEmptyError(PDFExtractionError):
    """Raised when PDF has 0 pages or is empty."""
    pass


class PDFNoExtractableTextError(PDFExtractionError):
    """Raised when PDF pages contain no extractable text (e.g. scanned image)."""
    pass


class PDFCorruptError(PDFExtractionError):
    """Raised when PDF binary is malformed or corrupted."""
    pass


def extract_text_from_pdf(file_bytes: bytes, filename: str = "document.pdf") -> list[ExtractedPage]:
    """
    Extracts text from PDF bytes page by page.
    Uses PyMuPDF (fitz) if available, with pypdf as a fallback.
    Throws specific exceptions for clean error reporting to the user.
    """
    if not file_bytes or len(file_bytes) == 0:
        raise PDFEmptyError(f"The uploaded file '{filename}' is completely empty (0 bytes).")

    # Basic magic header check
    if not file_bytes.startswith(b"%PDF-"):
        raise PDFCorruptError(
            f"The file '{filename}' does not appear to be a valid PDF format (missing %PDF header)."
        )

    pages: list[ExtractedPage] = []
    total_text_length = 0

    # Try PyMuPDF first
    if fitz is not None:
        try:
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            if doc.is_encrypted:
                raise PDFPasswordProtectedError(
                    f"The PDF '{filename}' is password-protected or encrypted. Please remove the password and re-upload."
                )
            if doc.page_count == 0:
                raise PDFEmptyError(f"The PDF '{filename}' contains 0 pages.")

            for page_idx in range(doc.page_count):
                page = doc.load_page(page_idx)
                page_text = page.get_text("text") or ""
                clean_text = page_text.strip()
                pages.append(ExtractedPage(page_number=page_idx + 1, text=clean_text))
                total_text_length += len(clean_text)

            doc.close()

            if total_text_length == 0:
                raise PDFNoExtractableTextError(
                    f"The document '{filename}' was opened successfully ({len(pages)} pages), but contains no extractable text. "
                    "This usually means the PDF consists of scanned images without an embedded OCR text layer."
                )

            return pages

        except (PDFPasswordProtectedError, PDFEmptyError, PDFNoExtractableTextError):
            raise
        except Exception as e:
            # Fall back to pypdf if PyMuPDF encounters unexpected parsing errors
            pass

    # Fallback to pypdf
    try:
        reader = pypdf.PdfReader(io.BytesIO(file_bytes))
        if reader.is_encrypted:
            raise PDFPasswordProtectedError(
                f"The PDF '{filename}' is password-protected or encrypted. Please remove password and re-upload."
            )
        if len(reader.pages) == 0:
            raise PDFEmptyError(f"The PDF '{filename}' contains 0 pages.")

        for idx, page in enumerate(reader.pages):
            extracted = page.extract_text() or ""
            clean_text = extracted.strip()
            pages.append(ExtractedPage(page_number=idx + 1, text=clean_text))
            total_text_length += len(clean_text)

        if total_text_length == 0:
            raise PDFNoExtractableTextError(
                f"The document '{filename}' contains {len(pages)} pages, but no extractable text was found. "
                "The PDF likely contains scanned images requiring OCR."
            )

        return pages

    except (PDFPasswordProtectedError, PDFEmptyError, PDFNoExtractableTextError):
        raise
    except pypdf.errors.PdfReadError as e:
        raise PDFCorruptError(f"Unable to read PDF '{filename}': File may be corrupted or truncated ({str(e)}).")
    except Exception as e:
        raise PDFCorruptError(f"Failed to process PDF '{filename}': {str(e)}")
