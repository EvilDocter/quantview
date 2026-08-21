"""
QuantView — Full Batch Idempotent Document Reindexing Script

Processes all raw.pdf documents in documents/NSE/, generates 1500-1800 character
chunks via StructuralChunker, computes 1024-dim BGE embeddings, and upserts
into local Qdrant collection with deterministic UUID5 point IDs.
"""

import sys
import os
import json
import logging
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.knowledge.crawler.dynamic_scraper import BASE_DIR
from app.knowledge.ocr_engine import OCREngine
from app.knowledge.embeddings import EmbeddingService
from app.knowledge.vector import QdrantVectorStore
from app.knowledge.models import DocumentChunk, ChunkMetadata, SectionType

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("reindex_script")


def main():
    logger.info("=== Starting Full Batch Reindexing Pipeline ===")
    docs_dir = BASE_DIR / "documents" / "NSE"
    if not docs_dir.exists():
        logger.error(f"Documents directory does not exist: {docs_dir}")
        return

    vector_store = QdrantVectorStore()
    embedding_service = EmbeddingService()

    total_reports = 0
    total_chunks = 0

    for company_dir in sorted(docs_dir.iterdir()):
        if not company_dir.is_dir():
            continue

        symbol = company_dir.name
        for year_dir in sorted(company_dir.iterdir()):
            if not year_dir.is_dir():
                continue

            year = int(year_dir.name) if year_dir.name.isdigit() else 2024
            
            # Check both naming conventions
            pdf_path = None
            for sub in ["annual_report", "AnnualReport"]:
                p = year_dir / sub / "raw.pdf"
                if p.exists():
                    pdf_path = p
                    break

            if not pdf_path:
                continue

            logger.info(f"Processing PDF: {symbol} ({year}) at {pdf_path}...")
            total_reports += 1

            try:
                ocr_res = OCREngine.process_pdf(str(pdf_path), symbol)
                raw_chunks = ocr_res.get("chunks", [])

                if not raw_chunks:
                    continue

                doc_chunks = []
                for idx, c in enumerate(raw_chunks):
                    sec_str = c.get("section", "GENERAL")
                    try:
                        sec_enum = SectionType(sec_str)
                    except Exception:
                        sec_enum = SectionType.GENERAL

                    meta = ChunkMetadata(
                        company=f"{symbol} Limited",
                        symbol=symbol,
                        exchange="NSE",
                        year=year,
                        document_type="Annual Report",
                        section=sec_enum,
                        heading=f"Page {c.get('page_number', 1)}",
                        page_number=c.get("page_number", 1),
                        chunk_index=idx + 1,
                        sha256_hash=f"{symbol}_{year}",
                    )

                    doc_chunks.append(
                        DocumentChunk(
                            chunk_id=c.get("chunk_id", f"{symbol}_{year}_p{c.get('page_number',1)}_c{idx+1}"),
                            document_id=f"doc_{symbol}_{year}",
                            text=c.get("text", ""),
                            metadata=meta,
                            token_count=len(c.get("text", "").split()),
                        )
                    )

                # Generate embeddings
                embedded_chunks = embedding_service.generate_chunk_embeddings(doc_chunks)

                # Upsert into Qdrant
                vector_store.upsert_chunks(embedded_chunks)
                total_chunks += len(embedded_chunks)
                logger.info(f"Upserted {len(embedded_chunks)} chunks for {symbol} ({year}) into Qdrant.")

            except Exception as e:
                logger.error(f"Error reindexing {symbol} ({year}): {e}")

    logger.info(f"=== Reindexing complete: {total_reports} reports processed, {total_chunks} chunks indexed. ===")


if __name__ == "__main__":
    main()
