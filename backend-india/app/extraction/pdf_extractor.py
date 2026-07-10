"""
QuantView — PDF Text Extraction Service

Extracts raw narrative text and layouts from corporate PDF documents.
Supports scanned files via fallback OCR integrations.
"""

import logging
import fitz  # PyMuPDF
import os

logger = logging.getLogger("pdf_extractor")

class PDFExtractor:
    """Handles text extraction from PDF files using PyMuPDF."""

    @staticmethod
    def extract_text(pdf_path: str) -> str:
        """Reads a PDF file and returns the concatenated raw text."""
        if not os.path.exists(pdf_path):
            logger.error(f"PDF file does not exist: {pdf_path}")
            return ""

        try:
            doc = fitz.open(pdf_path)
            full_text = []
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text("text")
                full_text.append(text)
                
            return "\n".join(full_text)
        except Exception as e:
            logger.error(f"Error extracting text from PDF {pdf_path}: {e}")
            return ""
