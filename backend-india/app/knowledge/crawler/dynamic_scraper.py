"""
QuantView — On-Demand Dynamic NSE Scraper & RAG Ingestion Pipeline

When a user queries a company, this service dynamically:
1. Checks if annual report chunks exist in /documents/NSE/{symbol}/.
2. If missing, scrapes nseindia.com for the company's latest annual report / financial filings PDF.
3. Downloads the PDF, extracts text into structured markdown, and chunks it for RAG.
4. Returns chunked RAG evidence for Qwen 2.5 14B model inference.
"""

import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Any
import pypdf

from app.knowledge.crawler.nse.client import NSEClient

logger = logging.getLogger("dynamic_scraper")

BASE_DIR = Path(os.getenv("QUANTVIEW_BASE_DIR", "/mnt/workspace/mahant/quantview_secured/quantview"))
if not BASE_DIR.exists():
    BASE_DIR = Path("/Users/mahant/quantview")
DOCUMENTS_DIR = BASE_DIR / "documents" / "NSE"



class DynamicNSEScraper:
    """On-demand scraper for fetching, parsing, and chunking company filings from NSE site."""

    @staticmethod
    async def get_or_download_filings(symbol: str) -> List[Dict[str, Any]]:
        """
        Fetch RAG chunks for a company symbol.
        Downloads and parses PDF from NSE site on-the-fly if not already cached.
        """
        clean_sym = symbol.upper().replace(".NS", "").replace(".BO", "")
        company_dir = DOCUMENTS_DIR / clean_sym

        # 1. Check if cached chunks.json exists in any year folder
        if company_dir.exists():
            for year_dir in sorted(company_dir.iterdir(), reverse=True):
                if year_dir.is_dir():
                    chunks_file = year_dir / "annual_report" / "chunks.json"
                    if not chunks_file.exists():
                        chunks_file = year_dir / "chunks.json"

                    if chunks_file.exists():
                        try:
                            with open(chunks_file, "r", encoding="utf-8") as f:
                                chunks_data = json.load(f)
                                logger.info(f"Loaded {len(chunks_data)} cached filing chunks for {clean_sym} ({year_dir.name})")
                                return chunks_data
                        except Exception as e:
                            logger.warning(f"Error reading cached chunks file {chunks_file}: {e}")

        # 2. On-demand dynamic download from NSE site
        logger.info(f"Filing chunks for '{clean_sym}' not found locally. Triggering dynamic NSE scraper...")
        downloaded_chunks = DynamicNSEScraper._scrape_and_parse_nse(clean_sym)
        return downloaded_chunks

    @staticmethod
    def _scrape_and_parse_nse(symbol: str) -> List[Dict[str, Any]]:
        """Download annual report PDF from NSE site and parse text chunks."""
        target_dir = DOCUMENTS_DIR / symbol / "2026" / "annual_report"
        target_dir.mkdir(parents=True, exist_ok=True)
        pdf_path = target_dir / "raw.pdf"

        # Step A: Download PDF from NSE using NSEClient
        downloaded = False
        try:
            client = NSEClient()
            client._ensure_session()
            
            # Query NSE annual reports endpoint for symbol
            url = f"https://www.nseindia.com/api/annual-reports?index=equities&symbol={symbol}"
            resp = client._session.get(url, timeout=10)
            if resp.status_code == 200:
                data = resp.json().get("data", [])
                if data:
                    first = data[0]
                    pdf_url = first.get("fileName") or first.get("attachment")
                    if pdf_url:
                        if not pdf_url.startswith("http"):
                            pdf_url = "https://www.nseindia.com" + pdf_url
                        pdf_resp = client._session.get(pdf_url, timeout=20)
                        if pdf_resp.status_code == 200 and len(pdf_resp.content) > 1000:
                            with open(pdf_path, "wb") as f:
                                f.write(pdf_resp.content)
                            downloaded = True
                            logger.info(f"Successfully downloaded dynamic annual report PDF for {symbol} ({len(pdf_resp.content)} bytes)")
        except Exception as e:
            logger.warning(f"Dynamic NSE PDF download failed for {symbol}: {e}")

        # Step B: Extract text using OCREngine
        chunks = []
        if downloaded and pdf_path.exists():
            try:
                from app.knowledge.ocr_engine import OCREngine
                ocr_result = OCREngine.process_pdf(str(pdf_path), symbol)
                chunks = ocr_result.get("chunks", [])
            except Exception as e:
                logger.warning(f"OCR PDF extraction failed for {symbol}: {e}")

        # Step C: Save chunks to JSON file for persistent local cache
        if chunks:
            try:
                chunks_file = target_dir / "chunks.json"
                with open(chunks_file, "w", encoding="utf-8") as f:
                    json.dump(chunks, f, indent=2)
                logger.info(f"Persisted {len(chunks)} filing chunks to local cache: {chunks_file}")
            except Exception as e:
                logger.warning(f"Failed persisting chunks JSON for {symbol}: {e}")

        return chunks

        # Fallback RAG chunk if PDF not available or unparseable
        fallback_chunk = [
            {
                "chunk_id": f"{symbol}_overview_0",
                "symbol": symbol,
                "document": f"{symbol} Financial Intelligence",
                "text": f"{symbol} is an equity listed on the National Stock Exchange (NSE) / Bombay Stock Exchange (BSE) of India. Real-time market metrics, historical valuation ratios, daily stock price movements, and recent news feeds are compiled from live exchange market data."
            }
        ]
        return fallback_chunk
