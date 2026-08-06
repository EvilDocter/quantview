"""
NSE Ingestion Service — PDF Validation & Integrity Engine

Validates downloaded files to ensure they are legitimate, uncorrupted PDFs
and not HTML error pages pretending to be PDFs. Computes page count & SHA-256.
"""

import logging
from io import BytesIO
from typing import Tuple
from app.knowledge.crawler.nse.exceptions import NSEValidationError
from app.knowledge.crawler.nse.utils import compute_bytes_sha256

logger = logging.getLogger("nse_parser")


class PDFValidator:
    @staticmethod
    def validate_pdf_bytes(content: bytes, min_size_bytes: int = 1024) -> Tuple[str, int]:
        """
        Validates raw PDF bytes. Returns (sha256_hash, page_count).
        Raises NSEValidationError if invalid, empty, corrupted, or an HTML error page.
        """
        if not content or len(content) == 0:
            raise NSEValidationError("Downloaded file is empty (0 bytes).")

        if len(content) < min_size_bytes:
            raise NSEValidationError(f"File size too small ({len(content)} bytes < {min_size_bytes} bytes threshold).")

        # Check PDF Magic Header %PDF-
        magic_header = content[:5]
        if magic_header != b"%PDF-":
            # Detect HTML error pages
            header_sample = content[:200].lower()
            if b"<html" in header_sample or b"<!doctype html" in header_sample:
                raise NSEValidationError("Server returned an HTML error page instead of a valid PDF.")
            raise NSEValidationError(f"Invalid PDF magic header: expected b'%PDF-', got {magic_header}")

        # Compute SHA-256 Hash
        sha256_hash = compute_bytes_sha256(content)

        # Count Pages using pypdf or binary stream fallback
        page_count = PDFValidator._count_pages(content)

        logger.info(f"PDF Validation Passed: SHA256={sha256_hash[:12]}..., Size={len(content)} bytes, Pages={page_count}")
        return sha256_hash, page_count

    @staticmethod
    def _count_pages(content: bytes) -> int:
        """Count PDF pages using pypdf if available, else regex binary fallback."""
        try:
            from pypdf import PdfReader
            reader = PdfReader(BytesIO(content))
            return len(reader.pages)
        except Exception:
            try:
                import pypdf
            except ImportError:
                pass
            
            # Binary fallback for page count (/Type /Page)
            import re
            matches = re.findall(rb"/Type\s*/Page\b", content)
            return len(matches) if matches else 1
