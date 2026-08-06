"""
QuantView Financial Knowledge Platform — Ingestion Pipeline Orchestrator

Executes full end-to-end pipeline:
Discovery → Download → Validation → Deduplication → Disk Storage → Parsing
→ Financial Extraction → Structural Chunking → Embedding Generation → Qdrant Vector Upsert.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.knowledge.providers.nse_provider import NSEProvider
from app.knowledge.parser import DocumentParser
from app.knowledge.extractor import FinancialExtractor
from app.knowledge.chunker import StructuralChunker
from app.knowledge.embeddings import EmbeddingService
from app.knowledge.vector import QdrantVectorStore
from app.knowledge.storage import KnowledgeStorageManager
from app.knowledge.models import ReportMetadata, IngestionResult
from app.knowledge.crawler.nse.parser import PDFValidator
from app.knowledge.crawler.nse.utils import compute_bytes_sha256, sanitize_symbol

logger = logging.getLogger("knowledge_pipeline")


class IngestionPipeline:
    """Orchestrates end-to-end document ingestion into Knowledge Platform."""

    def __init__(
        self,
        provider: Optional[NSEProvider] = None,
        storage: Optional[KnowledgeStorageManager] = None,
        embedding_service: Optional[EmbeddingService] = None,
        vector_store: Optional[QdrantVectorStore] = None,
    ):
        self.provider = provider or NSEProvider()
        self.storage = storage or KnowledgeStorageManager()
        self.embedding_service = embedding_service or EmbeddingService()
        self.vector_store = vector_store or QdrantVectorStore()

    async def ingest_company(self, symbol: str) -> IngestionResult:
        """Full end-to-end ingestion for a stock symbol."""
        clean_sym = sanitize_symbol(symbol)
        result = IngestionResult(symbol=clean_sym)

        logger.info(f"=== Starting Knowledge Pipeline Ingestion for {clean_sym} ===")

        # 1. Discover available reports
        try:
            reports = await self.provider.discover_reports(clean_sym)
            result.reports_discovered = len(reports)
        except Exception as e:
            logger.error(f"Provider discovery failed for {clean_sym}: {e}")
            return result

        # 2. Process each report
        for report in reports:
            try:
                # Deduplication Check
                if self.storage.is_document_processed("NSE", report.symbol, report.year):
                    logger.info(f"SKIP: {report.symbol} ({report.year}) already processed & stored.")
                    report.status = "skipped"
                    result.reports_skipped += 1
                    result.details.append(report)
                    continue

                # Download PDF bytes
                pdf_bytes = self.provider.download_pdf(report.pdf_url)

                # Validate PDF bytes
                sha256_hash, page_count = PDFValidator.validate_pdf_bytes(pdf_bytes)

                # Save raw PDF
                pdf_path = self.storage.save_raw_pdf("NSE", report.symbol, report.year, pdf_bytes)

                # Parse PDF into Markdown
                parsed_doc = DocumentParser.parse_pdf_bytes(pdf_bytes)
                md_path = self.storage.save_parsed_markdown("NSE", report.symbol, report.year, parsed_doc.full_markdown)

                # Extract financial JSON statements
                financials = FinancialExtractor.extract_financials(report.company, report.symbol, report.year, parsed_doc.full_markdown)
                self.storage.save_json_artifact("NSE", report.symbol, report.year, "financials.json", financials)

                # Generate structural semantic chunks
                chunks = StructuralChunker.chunk_parsed_document(
                    doc=parsed_doc,
                    company=report.company,
                    symbol=report.symbol,
                    year=report.year,
                    sha256_hash=sha256_hash,
                )
                self.storage.save_json_artifact("NSE", report.symbol, report.year, "chunks.json", [c.model_dump() for c in chunks])

                # Generate 1024-dim dense embeddings
                embedded_chunks = self.embedding_service.generate_chunk_embeddings(chunks)

                # Upsert into local Qdrant Vector Store
                self.vector_store.upsert_chunks(embedded_chunks)

                # Save processing log artifact
                proc_log = {
                    "symbol": report.symbol,
                    "year": report.year,
                    "sha256": sha256_hash,
                    "pages": page_count,
                    "chunks": len(chunks),
                    "status": "completed",
                    "timestamp": datetime.utcnow().isoformat(),
                }
                self.storage.save_json_artifact("NSE", report.symbol, report.year, "processing.json", proc_log)

                report.status = "downloaded"
                result.reports_downloaded += 1
                result.details.append(report)

            except Exception as e:
                logger.error(f"Pipeline error processing {report.symbol} ({report.year}): {e}")
                report.status = "failed"
                report.error_message = str(e)
                result.reports_failed += 1
                result.details.append(report)

        logger.info(f"=== Knowledge Pipeline complete for {clean_sym}: {result.reports_downloaded} downloaded, {result.reports_skipped} skipped ===")
        return result

    async def close(self):
        """Clean provider resources."""
        await self.provider.close()
