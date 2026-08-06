"""
NSE Ingestion Service — Core Ingestion Orchestrator

Coordinates discovery via Playwright, deduplication checks against disk
and database, PDF download via requests with stolen cookies, validation
via PDFValidator, and storage persistence.
"""

import logging
from typing import List, Optional
from app.knowledge.crawler.nse.client import NSEClient
from app.knowledge.crawler.nse.parser import PDFValidator
from app.knowledge.crawler.nse.storage import StorageManager
from app.knowledge.crawler.nse.models import ReportMetadata, IngestionResult
from app.knowledge.crawler.nse.utils import sanitize_symbol
from app.knowledge.crawler.nse.exceptions import NSEValidationError, NSEStorageError

logger = logging.getLogger("nse_crawler")


class NSECrawler:
    def __init__(self, client: Optional[NSEClient] = None, storage: Optional[StorageManager] = None):
        self.client = client or NSEClient()
        self.storage = storage or StorageManager()

    async def sync_company(self, symbol: str) -> IngestionResult:
        """
        Full pipeline: discover → deduplicate → download → validate → store.
        Never crashes on single file failure.
        """
        clean_sym = sanitize_symbol(symbol)
        result = IngestionResult(symbol=clean_sym)

        logger.info(f"=== Starting Annual Report sync for {clean_sym} ===")

        # 1. Discover available reports via Playwright + BeautifulSoup
        try:
            discovered_reports = await self.client.discover_annual_reports(clean_sym)
            result.reports_discovered = len(discovered_reports)
            logger.info(f"Discovered {len(discovered_reports)} reports for {clean_sym}")
        except Exception as e:
            logger.error(f"Discovery failed for {clean_sym}: {e}")
            return result

        if not discovered_reports:
            logger.warning(f"No annual reports found for {clean_sym}")
            return result

        # 2. Process each discovered report
        for report in discovered_reports:
            try:
                # Deduplication: skip if already on disk
                if self.storage.is_already_stored(report.symbol, report.year):
                    logger.info(f"SKIP: {report.symbol} ({report.year}) already exists on disk.")
                    report.status = "skipped"
                    result.reports_skipped += 1
                    result.details.append(report)
                    continue

                # Download PDF bytes using requests with stolen browser cookies
                logger.info(f"Downloading: {report.symbol} ({report.year}) from {report.pdf_url}")
                pdf_bytes = self.client.download_pdf_bytes(report.pdf_url)

                # Validate PDF integrity
                sha256_hash, page_count = PDFValidator.validate_pdf_bytes(pdf_bytes)
                logger.info(f"Validated: {report.symbol} ({report.year}) — {page_count} pages, SHA256={sha256_hash[:16]}...")

                # Store raw.pdf + metadata.json on disk
                pdf_path, meta_path = self.storage.store_report(report, pdf_bytes, sha256_hash, page_count)
                logger.info(f"Stored: {pdf_path}")

                # Persist metadata to PostgreSQL
                await self.storage.persist_to_database(report)

                report.status = "downloaded"
                result.reports_downloaded += 1
                result.details.append(report)

            except (NSEValidationError, NSEStorageError) as ve:
                logger.warning(f"FAIL (validation/storage): {report.symbol} ({report.year}): {ve}")
                report.status = "failed"
                report.error_message = str(ve)
                result.reports_failed += 1
                result.details.append(report)

            except Exception as e:
                logger.error(f"FAIL (unexpected): {report.symbol} ({report.year}): {e}")
                report.status = "failed"
                report.error_message = str(e)
                result.reports_failed += 1
                result.details.append(report)

        logger.info(
            f"=== Sync complete for {clean_sym}: "
            f"discovered={result.reports_discovered}, "
            f"downloaded={result.reports_downloaded}, "
            f"skipped={result.reports_skipped}, "
            f"failed={result.reports_failed} ==="
        )
        return result

    async def close(self):
        """Clean up Playwright browser resources."""
        await self.client.close()
