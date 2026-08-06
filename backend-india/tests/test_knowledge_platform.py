"""
QuantView Financial Knowledge Platform — Unit & Integration Test Suite
"""

import pytest
import asyncio
from pathlib import Path

from app.knowledge.models import (
    SectionType, ChunkMetadata, DocumentChunk, SearchQuery, SearchHit, SearchResponse
)
from app.knowledge.parser import DocumentParser, ParsedDocument, ParsedPage
from app.knowledge.extractor import FinancialExtractor
from app.knowledge.chunker import StructuralChunker
from app.knowledge.embeddings import EmbeddingService
from app.knowledge.vector import QdrantVectorStore
from app.knowledge.storage import KnowledgeStorageManager
from app.knowledge.retrieval import HybridSearchEngine
from app.knowledge.pipeline import IngestionPipeline


# ── Unit Tests ───────────────────────────────────────────────────

def test_document_parser():
    text = "BUSINESS OVERVIEW\nInfosys generates revenue from IT services.\nMANAGEMENT DISCUSSION\nThe company expanded digital services."
    clean, headings = DocumentParser._extract_headings_and_clean(text)
    assert len(headings) > 0
    assert "BUSINESS OVERVIEW" in headings


def test_financial_extractor():
    sample_md = """
    ## MANAGEMENT DISCUSSION AND ANALYSIS
    The company faces global macroeconomic slowdown risk and currency volatility.
    ## BALANCE SHEET
    Total Assets: Rs. 100,000 Crores
    """
    fin = FinancialExtractor.extract_financials("Infosys Limited", "INFY", 2025, sample_md)
    assert fin.company == "Infosys Limited"
    assert fin.symbol == "INFY"
    assert fin.year == 2025
    assert len(fin.risk_summary) > 0


def test_structural_chunker():
    page = ParsedPage(page_num=1, text="RISK FACTORS\nForeign currency volatility and client IT spending slowdown.", headings=["RISK FACTORS"], tables=[])
    doc = ParsedDocument(full_markdown="RISK FACTORS\nForeign currency volatility", pages=[page], total_pages=1)
    chunks = StructuralChunker.chunk_parsed_document(doc, "Infosys Limited", "INFY", 2025, "hash123")
    assert len(chunks) > 0
    assert chunks[0].metadata.symbol == "INFY"
    assert chunks[0].metadata.year == 2025


def test_knowledge_storage_manager(tmp_path):
    storage = KnowledgeStorageManager(root_dir=tmp_path)
    pdf_path = storage.save_raw_pdf("NSE", "INFY", 2025, b"%PDF-1.4 raw pdf bytes")
    md_path = storage.save_parsed_markdown("NSE", "INFY", 2025, "# Infosys Parsed Markdown")
    
    assert pdf_path.exists()
    assert md_path.exists()
    assert storage.is_document_processed("NSE", "INFY", 2025) is False  # requires chunks.json & processing.json


def test_embedding_service():
    embedder = EmbeddingService()
    vec = embedder.generate_single_embedding("Analyze Infosys Q4 performance and revenue metrics.")
    assert len(vec) > 0
    assert isinstance(vec, list)


def test_qdrant_vector_store(tmp_path):
    # Test embedded local Qdrant vector store
    vstore = QdrantVectorStore()
    vstore._client = None  # force re-init
    vstore.vector_dim = 1024
    
    meta = ChunkMetadata(
        company="Infosys Limited",
        symbol="INFY",
        exchange="NSE",
        year=2025,
        document_type="Annual Report",
        section=SectionType.RISK_FACTORS,
        heading="Key Risks",
        page_number=12,
        chunk_index=1,
        sha256_hash="hash123456789",
    )
    
    chunk = DocumentChunk(
        chunk_id="chunk_infy_2025_0001",
        document_id="doc_infy_2025",
        text="Infosys faces foreign currency volatility and client IT spending risks.",
        metadata=meta,
        token_count=10,
        embedding=[0.1] * 1024,
    )
    
    vstore.upsert_chunks([chunk])
    hits = vstore.search_similar_vectors([0.1] * 1024, symbol="INFY", year=2025, top_k=3)
    assert len(hits) > 0
    assert hits[0].metadata.symbol == "INFY"


# ── Integration Tests ────────────────────────────────────────────

@pytest.mark.asyncio
async def test_full_knowledge_pipeline(tmp_path):
    from unittest.mock import AsyncMock, MagicMock
    from io import BytesIO
    from pypdf import PdfWriter
    from app.knowledge.crawler.nse.models import ReportMetadata, ExchangeType, DocumentType

    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    buf = BytesIO()
    writer.write(buf)
    dummy_pdf_bytes = buf.getvalue() + b" " * 1000  # valid pdf bytes > 1KB

    mock_provider = MagicMock()
    fake_report = ReportMetadata(
        company="Infosys Limited",
        symbol="INFY",
        exchange=ExchangeType.NSE,
        year=2025,
        document_type=DocumentType.ANNUAL_REPORT,
        source="NSE",
        pdf_url="http://example.com/infy2025.pdf",
    )
    mock_provider.discover_reports = AsyncMock(return_value=[fake_report])
    mock_provider.download_pdf = MagicMock(return_value=dummy_pdf_bytes)
    mock_provider.close = AsyncMock()

    storage = KnowledgeStorageManager(root_dir=tmp_path)
    pipeline = IngestionPipeline(provider=mock_provider, storage=storage)
    result = await pipeline.ingest_company("INFY")
    
    assert result.symbol == "INFY"
    assert result.reports_discovered == 1
    assert result.reports_downloaded == 1


@pytest.mark.asyncio
async def test_hybrid_search():
    engine = HybridSearchEngine()
    req = SearchQuery(query="Infosys IT spending risks", symbol="INFY", top_k=3, min_score=0.0)
    resp = engine.search(req)
    assert isinstance(resp, SearchResponse)
