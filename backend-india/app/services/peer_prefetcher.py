"""
QuantView — Background Asynchronous Peer Prefetcher

When a company is indexed on its first query, this service automatically
pre-fetches and indexes related sector peer equities asynchronously in the background.
Zero blocking delay on the main user request.
"""

import asyncio
import logging
from typing import List, Dict
from app.services.company_registry import CompanyRegistryService

logger = logging.getLogger("peer_prefetcher")

# Peer mapping dictionary for Indian sectors
SECTOR_PEERS: Dict[str, List[str]] = {
    "HAL": ["BEL", "BDL", "COCHINSHIP"],
    "BEL": ["HAL", "BDL"],
    "TCS": ["INFY", "WIPRO", "HCLTECH", "TECHM"],
    "INFY": ["TCS", "WIPRO", "HCLTECH", "LTIM"],
    "HDFCBANK": ["ICICIBANK", "AXISBANK", "SBIN", "KOTAKBANK"],
    "ICICIBANK": ["HDFCBANK", "AXISBANK", "SBIN"],
    "RELIANCE": ["ONGC", "IOC", "BPCL"],
    "ZOMATO": ["SWIGGY", "NAUKRI"],
    "SUZLON": ["INDOCO", "TATAPOWER"],
}


class PeerPrefetcher:
    """Asynchronous background prefetcher for sector peer equities."""

    @staticmethod
    def trigger_peer_prefetch(symbol: str) -> None:
        """Fire non-blocking background prefetch for sector peers."""
        clean_sym = symbol.upper().replace(".NS", "").replace(".BO", "")
        peers = SECTOR_PEERS.get(clean_sym, [])
        if not peers:
            return

        logger.info(f"Triggering background peer prefetch for {clean_sym} peers: {peers}")
        asyncio.create_task(PeerPrefetcher._prefetch_peers_async(clean_sym, peers))

    @staticmethod
    async def _prefetch_peers_async(primary_symbol: str, peers: List[str]) -> None:
        """Background task to pre-fetch and index unindexed peers."""
        from app.services.financial_extractor import FinancialExtractorService
        from app.knowledge.crawler.dynamic_scraper import DynamicNSEScraper

        for peer in peers:
            try:
                if not CompanyRegistryService.is_indexed(peer):
                    logger.info(f"Background Prefetching peer equity '{peer}' for sector context of {primary_symbol}...")
                    # 1. Fetch financial profile
                    FinancialExtractorService.extract_full_financial_profile(peer)
                    # 2. Fetch and chunk annual report filings
                    await DynamicNSEScraper.get_or_download_filings(peer)
                    # 3. Mark indexed in canonical registry
                    CompanyRegistryService.mark_indexed(peer)
                    logger.info(f"Successfully background-prefetched and indexed peer: '{peer}'")
            except Exception as e:
                logger.warning(f"Background prefetch failed for peer '{peer}': {e}")
