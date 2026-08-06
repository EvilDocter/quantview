"""
QuantView Financial Knowledge Platform — Pydantic V2 Domain Schemas
"""

from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class SectionType(str, Enum):
    CEO_LETTER = "CEO Letter & Management Message"
    BUSINESS_OVERVIEW = "Business Overview & Segment Performance"
    RISK_FACTORS = "Risk Factors & Industry Challenges"
    FINANCIAL_STATEMENTS = "Financial Statements"
    BALANCE_SHEET = "Balance Sheet"
    PROFIT_AND_LOSS = "Profit & Loss Account"
    CASH_FLOW = "Cash Flow Statement"
    AUDITOR_REPORT = "Auditor Report & Key Audit Matters"
    CORPORATE_GOVERNANCE = "Corporate Governance Report"
    ESG = "ESG & Sustainability Disclosures"
    NOTES_TO_ACCOUNTS = "Notes to Financial Statements"
    GENERAL = "General Disclosures"


class ChunkMetadata(BaseModel):
    model_config = ConfigDict(frozen=False)

    company: str
    symbol: str
    exchange: str = "NSE"
    year: int
    document_type: str = "Annual Report"
    section: SectionType = SectionType.GENERAL
    subsection: Optional[str] = None
    heading: Optional[str] = None
    page_number: int = 1
    chunk_index: int = 0
    source_file: str = "raw.pdf"
    sha256_hash: str
    language: str = "en"
    embedding_version: str = "bge-large-en-v1.5"
    processed_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class DocumentChunk(BaseModel):
    chunk_id: str
    document_id: str
    text: str
    metadata: ChunkMetadata
    token_count: int = 0
    embedding: Optional[List[float]] = None


class ExtractedFinancials(BaseModel):
    company: str
    symbol: str
    year: int
    balance_sheet: Dict[str, Any] = {}
    profit_loss: Dict[str, Any] = {}
    cash_flow: Dict[str, Any] = {}
    key_ratios: Dict[str, Any] = {}
    audit_opinion: Optional[str] = None
    risk_summary: List[str] = []
    segment_revenue: Dict[str, Any] = {}


class SearchQuery(BaseModel):
    query: str
    symbol: Optional[str] = None
    year: Optional[int] = None
    section: Optional[SectionType] = None
    top_k: int = 5
    min_score: float = 0.35


class SearchHit(BaseModel):
    chunk_id: str
    text: str
    score: float
    metadata: ChunkMetadata


class SearchResponse(BaseModel):
    query: str
    total_hits: int
    hits: List[SearchHit]
    execution_time_ms: float
