"""
QuantView — Nifty 50 Batch Bootstrap Ingestion Engine (Phase VIII Mandate)

Resumable, fault-tolerant batch ingestion pipeline for all 50 Nifty 50 constituents.
Pre-populates PostgreSQL relational tables (companies, financials, stock_prices, shareholding, segments, ocr_pages, ocr_tables)
and Qdrant vector embeddings. Tracks progress in /documents/bootstrap_status.json.
"""

import logging
import os
import json
import time
import asyncio
from typing import Dict, Any, List
from pathlib import Path

from app.services.symbol_resolver import SymbolResolverService
from app.services.company_registry import CompanyRegistryService
from app.services.financial_extractor import FinancialExtractorService
from app.knowledge.crawler.dynamic_scraper import DynamicNSEScraper, DOCUMENTS_DIR
from app.knowledge.ocr_engine import OCREngine

logger = logging.getLogger("nifty50_bootstrap")

BASE_DIR = Path(os.getenv("QUANTVIEW_BASE_DIR", "/mnt/workspace/mahant/quantview_secured/quantview"))
if not BASE_DIR.exists():
    BASE_DIR = Path("/Users/mahant/quantview")
STATUS_FILE = BASE_DIR / "documents" / "bootstrap_status.json"


NIFTY_50_CONSTITUENTS = [
    "RELIANCE", "TCS", "HDFCBANK", "ICICIBANK", "INFY", "BHARTIARTL", "ITC", "SBIN",
    "LTIM", "LT", "HINDUNILVR", "AXISBANK", "KOTAKBANK", "BAJFINANCE", "M&M", "MARUTI",
    "SUNPHARMA", "NTPC", "TITAN", "TATAMOTORS", "POWERGRID", "TATASTEEL", "ADANIENT",
    "ULTRACEMCO", "COALINDIA", "ASIANPAINT", "HAL", "BAJAJFINSV", "JSWSTEEL", "NESTLEIND",
    "GRASIM", "TECHM", "HCLTECH", "INDUSINDBK", "HDFCLIFE", "WIPRO", "HEROMOTOCO", "ONGC",
    "TATACONSUM", "ADANIPORTS", "DRREDDY", "CIPLA", "SBILIFE", "BPCL", "EICHERMOT",
    "DIVISLAB", "BAJAJ-AUTO", "BRITANNIA", "APOLLOHOSP", "BEL"
]


class Nifty50BootstrapEngine:
    """Batch bootstrap engine with resume capability for Nifty 50 companies."""

    @staticmethod
    def get_status() -> Dict[str, Any]:
        """Load current status from status JSON file."""
        if STATUS_FILE.exists():
            try:
                with open(STATUS_FILE, "r") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Error reading bootstrap status file: {e}")

        return {
            "total_constituents": len(NIFTY_50_CONSTITUENTS),
            "completed_count": 0,
            "completed_symbols": [],
            "failed_symbols": [],
            "in_progress_symbol": None,
            "status": "NOT_STARTED",
            "last_updated": time.strftime("%Y-%m-%d %H:%M:%S"),
        }

    @staticmethod
    def _save_status(status_data: Dict[str, Any]):
        """Save status JSON file."""
        DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
        status_data["last_updated"] = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(STATUS_FILE, "w") as f:
            json.dump(status_data, f, indent=2)

    @staticmethod
    async def run_bootstrap(max_symbols: int = 50) -> Dict[str, Any]:
        """
        Execute or resume Nifty 50 batch bootstrap ingestion.
        """
        status_data = Nifty50BootstrapEngine.get_status()
        status_data["status"] = "RUNNING"
        completed = set(status_data.get("completed_symbols", []))

        processed_this_run = 0

        for symbol in NIFTY_50_CONSTITUENTS:
            if symbol in completed:
                continue

            if processed_this_run >= max_symbols:
                break

            status_data["in_progress_symbol"] = symbol
            Nifty50BootstrapEngine._save_status(status_data)

            logger.info(f"⚡ Nifty 50 Bootstrap Ingesting: '{symbol}' ({len(completed)+1}/{len(NIFTY_50_CONSTITUENTS)})...")

            try:
                # Step 1: Symbol Resolution
                resolved = SymbolResolverService.resolve_symbol(symbol)
                sym = resolved["symbol"]
                yf_sym = resolved["yf_symbol"]

                # Step 2: Financial Profile Extraction
                fin_profile = FinancialExtractorService.extract_full_financial_profile(sym, yf_sym)

                # Step 3: Dynamic Filings & OCR Layout Processing
                filing_chunks = await DynamicNSEScraper.get_or_download_filings(sym)



                # Step 4: Update Registry State
                CompanyRegistryService.register_company(
                    symbol=sym,
                    yf_symbol=yf_sym,
                    company_name=fin_profile["company_identity"]["company_name"],
                    sector=fin_profile["company_identity"]["sector"],
                    industry=fin_profile["company_identity"]["industry"],
                    indexed=True,
                )

                completed.add(symbol)
                status_data["completed_symbols"] = list(completed)
                status_data["completed_count"] = len(completed)
                processed_this_run += 1
                logger.info(f"✅ Nifty 50 Bootstrap Ingested successfully: '{symbol}' ({len(filing_chunks)} chunks)")

            except Exception as e:
                logger.error(f"❌ Bootstrap failed for symbol '{symbol}': {e}")
                if symbol not in status_data.get("failed_symbols", []):
                    status_data.setdefault("failed_symbols", []).append(symbol)

            status_data["in_progress_symbol"] = None
            Nifty50BootstrapEngine._save_status(status_data)

        if len(completed) >= len(NIFTY_50_CONSTITUENTS):
            status_data["status"] = "COMPLETED"
        else:
            status_data["status"] = "PAUSED"

        Nifty50BootstrapEngine._save_status(status_data)
        return status_data
