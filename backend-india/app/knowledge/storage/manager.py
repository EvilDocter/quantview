"""
QuantView Financial Knowledge Platform — Storage Manager

Manages versioned, non-overwriting document directory layouts under:
documents/NSE/<symbol>/<year>/annual_report/
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from datetime import datetime

from app.knowledge.config import knowledge_settings
from app.knowledge.models import DocumentChunk, ExtractedFinancials, ChunkMetadata

logger = logging.getLogger("knowledge_storage")


class KnowledgeStorageManager:
    def __init__(self, root_dir: Optional[Path] = None):
        self.root_dir = root_dir or knowledge_settings.storage_root

    def get_document_dir(self, exchange: str, symbol: str, year: int, doc_type: str = "annual_report") -> Path:
        """Construct directory path: documents/{EXCHANGE}/{SYMBOL}/{YEAR}/{DOC_TYPE}/"""
        clean_doc_type = doc_type.lower().replace(" ", "_")
        doc_dir = self.root_dir / exchange.upper() / symbol.upper() / str(year) / clean_doc_type
        doc_dir.mkdir(parents=True, exist_ok=True)
        return doc_dir

    def is_document_processed(self, exchange: str, symbol: str, year: int, doc_type: str = "annual_report") -> bool:
        """Check if raw.pdf, parsed.md, chunks.json, and processing.json exist."""
        doc_dir = self.get_document_dir(exchange, symbol, year, doc_type)
        return (
            (doc_dir / "raw.pdf").exists() and
            (doc_dir / "chunks.json").exists() and
            (doc_dir / "processing.json").exists()
        )

    def save_raw_pdf(self, exchange: str, symbol: str, year: int, pdf_bytes: bytes, doc_type: str = "annual_report") -> Path:
        """Save raw downloaded PDF to disk without overwriting if hash matches."""
        doc_dir = self.get_document_dir(exchange, symbol, year, doc_type)
        pdf_path = doc_dir / "raw.pdf"
        with open(pdf_path, "wb") as f:
            f.write(pdf_bytes)
        logger.info(f"Saved raw PDF to {pdf_path}")
        return pdf_path

    def save_parsed_markdown(self, exchange: str, symbol: str, year: int, markdown_text: str, doc_type: str = "annual_report") -> Path:
        """Save parsed markdown text preserving document hierarchy."""
        doc_dir = self.get_document_dir(exchange, symbol, year, doc_type)
        md_path = doc_dir / "parsed.md"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(markdown_text)
        logger.info(f"Saved parsed.md to {md_path}")
        return md_path

    def save_json_artifact(self, exchange: str, symbol: str, year: int, filename: str, data: Any, doc_type: str = "annual_report") -> Path:
        """Save a structured JSON artifact (metadata.json, financials.json, sections.json, chunks.json, processing.json)."""
        doc_dir = self.get_document_dir(exchange, symbol, year, doc_type)
        json_path = doc_dir / filename
        with open(json_path, "w", encoding="utf-8") as f:
            if hasattr(data, "model_dump"):
                json.dump(data.model_dump(), f, indent=2, default=str)
            else:
                json.dump(data, f, indent=2, default=str)
        logger.info(f"Saved {filename} to {json_path}")
        return json_path

    def load_json_artifact(self, exchange: str, symbol: str, year: int, filename: str, doc_type: str = "annual_report") -> Optional[Dict[str, Any]]:
        """Load JSON artifact from disk if it exists."""
        doc_dir = self.get_document_dir(exchange, symbol, year, doc_type)
        json_path = doc_dir / filename
        if json_path.exists():
            with open(json_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return None
