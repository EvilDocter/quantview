"""
QuantView — Self-Growing Dynamic Indexing Pipeline

Manages the on-demand ingestion lifecycle:
1. Checks canonical registry for indexing status.
2. On cache miss: downloads financials, scrapes NSE annual reports, extracts section chunks, and persists assets permanently.
3. Fires background peer prefetching task.
4. Updates registry `indexed_flag = True`.
"""

import time
import logging
from typing import Dict, Any, List
from app.services.company_registry import CompanyRegistryService
from app.services.financial_extractor import FinancialExtractorService
from app.knowledge.crawler.dynamic_scraper import DynamicNSEScraper
from app.services.peer_prefetcher import PeerPrefetcher

logger = logging.getLogger("dynamic_indexer")


class DynamicIndexerPipeline:
    """Dynamic ingestion pipeline for on-demand equity indexing."""

    @staticmethod
    async def ensure_indexed(symbol: str) -> Dict[str, Any]:
        """
        Ensure company is indexed. If unindexed, runs full ingestion and marks indexed.
        """
        clean_sym = symbol.upper().replace(".NS", "").replace(".BO", "")
        record = CompanyRegistryService.get_company_record(clean_sym)
        is_already_indexed = record.get("indexed_flag", False)

        start_time = time.time()

        if is_already_indexed:
            logger.info(f"Equity '{clean_sym}' is ALREADY INDEXED in canonical registry. Using persistent cache.")
            return {
                "symbol": clean_sym,
                "cache_status": "HIT_INDEXED",
                "indexed_flag": True,
                "ingestion_latency_sec": 0.0,
            }

        logger.info(f"Equity '{clean_sym}' is UNINDEXED. Triggering dynamic on-demand ingestion pipeline...")

        # 1. Download & extract financial metrics
        fin_profile = FinancialExtractorService.extract_full_financial_profile(clean_sym)

        # 2. Download & parse NSE annual report filing chunks
        chunks = await DynamicNSEScraper.get_or_download_filings(clean_sym)

        # 3. Mark company permanently indexed in canonical registry
        CompanyRegistryService.mark_indexed(clean_sym)

        # 4. Trigger non-blocking background prefetch for sector peers
        PeerPrefetcher.trigger_peer_prefetch(clean_sym)

        ingestion_latency = round(time.time() - start_time, 3)
        logger.info(f"Completed dynamic ingestion for '{clean_sym}' in {ingestion_latency}s ({len(chunks)} chunks persisted).")

        return {
            "symbol": clean_sym,
            "cache_status": "MISS_DYNAMICALLY_INDEXED",
            "indexed_flag": True,
            "chunks_count": len(chunks),
            "ingestion_latency_sec": ingestion_latency,
        }
