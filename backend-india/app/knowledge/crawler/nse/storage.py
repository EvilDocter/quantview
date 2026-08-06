"""
NSE Ingestion Service — Storage & Database Persistence Manager

Manages disk storage under `documents/NSE/{SYMBOL}/{YEAR}/AnnualReport/`,
writes metadata.json, and persists document records into PostgreSQL.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

from app.knowledge.crawler.nse.config import settings
from app.knowledge.crawler.nse.models import ReportMetadata
from app.knowledge.crawler.nse.exceptions import NSEStorageError
from app.db.postgres import AsyncSessionLocal
from app.models.document import Document
from app.models.company import Company
from sqlalchemy import select

logger = logging.getLogger("nse_storage")


class StorageManager:
    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = base_dir or settings.base_storage_dir

    def get_report_directory(self, symbol: str, year: int) -> Path:
        """Construct directory path: documents/NSE/{SYMBOL}/{YEAR}/AnnualReport/"""
        path = self.base_dir / "NSE" / symbol.upper() / str(year) / "AnnualReport"
        path.mkdir(parents=True, exist_ok=True)
        return path

    def is_already_stored(self, symbol: str, year: int) -> bool:
        """Check if raw.pdf and metadata.json already exist on disk."""
        report_dir = self.get_report_directory(symbol, year)
        pdf_path = report_dir / "raw.pdf"
        meta_path = report_dir / "metadata.json"
        return pdf_path.exists() and meta_path.exists()

    def store_report(
        self, report: ReportMetadata, content: bytes, hash_val: str, page_count: int
    ) -> Tuple[Path, Path]:
        """
        Store raw.pdf and metadata.json on disk.
        Returns (pdf_path, metadata_path).
        """
        report_dir = self.get_report_directory(report.symbol, report.year)
        pdf_path = report_dir / "raw.pdf"
        meta_path = report_dir / "metadata.json"

        # Update metadata object
        report.file_path = str(pdf_path)
        report.hash = hash_val
        report.pages = page_count
        report.size = len(content)
        report.downloaded_at = datetime.utcnow().isoformat()
        report.status = "downloaded"

        try:
            # Write raw.pdf
            with open(pdf_path, "wb") as f:
                f.write(content)
            logger.info(f"Saved raw PDF to {pdf_path}")

            # Write metadata.json
            with open(meta_path, "w", encoding="utf-8") as f:
                json.dump(report.model_dump(), f, indent=2)
            logger.info(f"Saved metadata JSON to {meta_path}")

            return pdf_path, meta_path
        except Exception as e:
            raise NSEStorageError(f"Failed to store report for {report.symbol} ({report.year}): {e}")

    async def persist_to_database(self, report: ReportMetadata) -> Optional[int]:
        """
        Insert or update metadata record in PostgreSQL `documents` table.
        Does NOT store raw PDF bytes in DB. Returns document record ID.
        """
        try:
            async with AsyncSessionLocal() as db:
                # Find or resolve company_id
                comp_stmt = select(Company).where(Company.symbol == report.symbol)
                comp_res = await db.execute(comp_stmt)
                company = comp_res.scalars().first()

                company_id = company.id if company else 1  # Fallback company_id = 1

                # Check existing document record by file_hash or symbol+year
                doc_stmt = select(Document).where(
                    (Document.file_hash == report.hash) |
                    ((Document.company_id == company_id) & (Document.fiscal_year == str(report.year)))
                )
                doc_res = await db.execute(doc_stmt)
                existing_doc = doc_res.scalars().first()

                if existing_doc:
                    existing_doc.file_url = report.file_path
                    existing_doc.file_hash = report.hash
                    existing_doc.page_count = report.pages
                    existing_doc.is_processed = True
                    existing_doc.processed_at = datetime.utcnow()
                    await db.commit()
                    logger.info(f"Updated PostgreSQL Document ID {existing_doc.id} for {report.symbol}")
                    return existing_doc.id
                else:
                    new_doc = Document(
                        company_id=company_id,
                        document_type="annual_report",
                        title=f"{report.company} Annual Report {report.year}",
                        fiscal_year=str(report.year),
                        file_url=report.file_path,
                        file_hash=report.hash,
                        page_count=report.pages,
                        is_processed=True,
                        processed_at=datetime.utcnow(),
                    )
                    db.add(new_doc)
                    await db.commit()
                    await db.refresh(new_doc)
                    logger.info(f"Inserted new PostgreSQL Document ID {new_doc.id} for {report.symbol}")
                    return new_doc.id
        except Exception as e:
            logger.warning(f"Database persistence skipped/failed for {report.symbol}: {e}")
            return None
