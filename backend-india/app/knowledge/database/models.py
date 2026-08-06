"""
QuantView Financial Knowledge Platform — PostgreSQL Database Models
"""

from sqlalchemy import (
    Column, Integer, String, Text, BigInteger, Numeric,
    DateTime, Boolean, ForeignKey, Index, UniqueConstraint, JSON, func
)
from app.db.postgres import Base


class KnowledgeDocument(Base):
    __tablename__ = "knowledge_documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, index=True)
    company_name = Column(String(255))
    exchange = Column(String(10), default="NSE")
    fiscal_year = Column(Integer, nullable=False)
    document_type = Column(String(50), default="Annual Report")
    
    file_path = Column(String(1000), nullable=False)
    file_hash = Column(String(64), unique=True, nullable=False)
    file_size_bytes = Column(BigInteger, default=0)
    page_count = Column(Integer, default=0)
    
    is_parsed = Column(Boolean, default=False)
    is_embedded = Column(Boolean, default=False)
    status = Column(String(50), default="discovered")   # "discovered", "downloaded", "parsed", "embedded", "failed"
    error_message = Column(Text)
    
    downloaded_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index("idx_kdoc_symbol_year", "symbol", "fiscal_year", "document_type"),
    )


class IngestionJob(Base):
    __tablename__ = "ingestion_jobs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, index=True)
    job_type = Column(String(50), default="annual_report_sync")
    status = Column(String(50), default="pending")       # "pending", "running", "completed", "failed"
    records_discovered = Column(Integer, default=0)
    records_downloaded = Column(Integer, default=0)
    records_skipped = Column(Integer, default=0)
    error_log = Column(Text)
    started_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime)
