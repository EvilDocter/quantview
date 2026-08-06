"""
NSE Ingestion Service — Pydantic V2 Domain Models
"""

from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, HttpUrl, ConfigDict


class ExchangeType(str, Enum):
    NSE = "NSE"
    BSE = "BSE"


class DocumentType(str, Enum):
    ANNUAL_REPORT = "Annual Report"
    QUARTERLY_RESULT = "Quarterly Financial Result"
    CONCALL_TRANSCRIPT = "Concall Transcript"
    INVESTOR_PRESENTATION = "Investor Presentation"


class ReportMetadata(BaseModel):
    model_config = ConfigDict(frozen=False)

    company: str
    symbol: str
    exchange: ExchangeType = ExchangeType.NSE
    isin: Optional[str] = None
    year: int
    document_type: DocumentType = DocumentType.ANNUAL_REPORT
    source: str = "NSE"
    downloaded_at: Optional[str] = None
    pdf_url: str
    file_path: Optional[str] = None
    hash: Optional[str] = None
    pages: int = 0
    size: int = 0
    status: str = "discovered"     # "discovered", "downloaded", "validated", "indexed", "skipped", "failed"
    error_message: Optional[str] = None


class IngestionResult(BaseModel):
    symbol: str
    reports_discovered: int = 0
    reports_downloaded: int = 0
    reports_skipped: int = 0
    reports_failed: int = 0
    details: List[ReportMetadata] = []


class SyncSummary(BaseModel):
    total_symbols_processed: int = 0
    total_downloaded: int = 0
    total_skipped: int = 0
    total_errors: int = 0
    results: Dict[str, IngestionResult] = {}
