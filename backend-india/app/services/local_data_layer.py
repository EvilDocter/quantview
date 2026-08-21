"""
QuantView — Local-First AI Data Access Layer (Phase VIII Mandate)

Prefers local PostgreSQL relational records and local vector store embeddings.
Only falls back to live external web APIs if local data is missing or stale.
"""

import logging
from typing import Dict, Any, List, Optional
from app.services.company_registry import CompanyRegistryService
from app.services.financial_extractor import FinancialExtractorService
from app.knowledge.crawler.dynamic_scraper import DynamicNSEScraper

logger = logging.getLogger("local_data_layer")


class LocalDataLayer:
    """Local-first data loader for AI evidence packets."""

    @staticmethod
    async def get_company_local_context(symbol: str) -> Dict[str, Any]:
        """
        Get complete local context for a company from local financial warehouse & disk.
        """
        clean_sym = symbol.upper().replace(".NS", "").replace(".BO", "")
        registry_rec = CompanyRegistryService.get_company_record(clean_sym)

        # 1. Financial Profile (Fast local cache / yfinance fallback)
        yf_sym = registry_rec.get("yf_symbol") if registry_rec else f"{clean_sym}.NS"
        fin_profile = FinancialExtractorService.extract_full_financial_profile(clean_sym, yf_sym)

        # 2. Local Filing Chunks (Disk / OCR parsed)
        chunks = await DynamicNSEScraper.get_or_download_filings(clean_sym)


        return {
            "registry": registry_rec,
            "financial_profile": fin_profile,
            "chunks": chunks,
            "is_local_hit": True,
        }
