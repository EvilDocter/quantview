"""
QuantView — News & Document SQLAlchemy Models

News articles, company documents (annual reports, filings),
and document processing tracker.
"""

from sqlalchemy import (
    Column, Integer, String, Text, BigInteger, Numeric,
    DateTime, Date, Boolean, ForeignKey, Index, UniqueConstraint,
    JSON, ARRAY,
    func,
)
from app.db.postgres import Base


class News(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(500))
    content = Column(Text)
    source = Column(String(100))
    url = Column(String(1000))
    published_at = Column(DateTime)
    company_id = Column(Integer, ForeignKey("companies.id"), index=True)
    sentiment_score = Column(Numeric(5, 3))     # -1.0 to 1.0
    sentiment_label = Column(String(20))        # "positive", "negative", "neutral"
    category = Column(String(50))               # "earnings", "management", "sector", "macro"
    content_hash = Column(String(64), unique=True)
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        Index("idx_news_company_date", "company_id", "published_at"),
    )


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    document_type = Column(String(50))          # "annual_report", "quarterly_result", etc.
    title = Column(String(500))
    fiscal_year = Column(String(10))
    quarter = Column(String(5))
    file_url = Column(String(1000))             # R2/HF storage URL
    file_hash = Column(String(64), unique=True) # SHA-256 for dedup
    page_count = Column(Integer)

    # Processing status
    is_processed = Column(Boolean, default=False)
    processed_at = Column(DateTime)
    processing_error = Column(Text)

    # Extracted content
    extracted_text = Column(Text)
    summary = Column(Text)
    key_highlights = Column(JSON)

    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        Index("idx_docs_company", "company_id", "document_type", "fiscal_year"),
    )


class ProcessedDocument(Base):
    __tablename__ = "processed_documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    document_hash = Column(String(64), unique=True, nullable=False)
    document_type = Column(String(50))
    company_id = Column(Integer, ForeignKey("companies.id"), index=True)
    processed_at = Column(DateTime, server_default=func.now())
    extraction_results = Column(JSON)
    embedding_ids = Column(JSON)          # List of Qdrant point IDs
    neo4j_node_ids = Column(JSON)         # List of Neo4j node IDs
    opensearch_doc_id = Column(String(100))


class MacroData(Base):
    __tablename__ = "macro_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    indicator = Column(String(100))       # "GDP_GROWTH", "CPI_INFLATION", "REPO_RATE"
    period = Column(Date)
    value = Column(Numeric(12, 4))
    source = Column(String(100))          # "RBI", "MOSPI"

    __table_args__ = (
        UniqueConstraint("indicator", "period", name="uq_macro_indicator_period"),
    )
