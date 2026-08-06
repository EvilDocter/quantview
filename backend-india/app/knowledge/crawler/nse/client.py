"""
NSE Ingestion Service — curl_cffi + BeautifulSoup Client

Uses curl_cffi (Chrome TLS fingerprint impersonation) to bypass NSE's
Akamai WAF. This works because curl_cffi sends the exact same TLS
ClientHello as a real Chrome browser at the socket level.

Playwright was tested but NSE's Akamai kills HTTP/2 connections from
headless browsers. curl_cffi is lighter (no 170MB browser) and actually works.
"""

import time
import random
import logging
import json
from typing import Optional, List, Dict
from curl_cffi import requests as cffi_requests

from app.knowledge.crawler.nse.config import settings
from app.knowledge.crawler.nse.exceptions import NSEClientError, NSERateLimitError
from app.knowledge.crawler.nse.utils import sanitize_symbol, extract_year_from_text
from app.knowledge.crawler.nse.models import ReportMetadata, DocumentType, ExchangeType

logger = logging.getLogger("nse_client")


class NSEClient:
    """
    Production NSE scraper using curl_cffi to impersonate Chrome's TLS fingerprint.
    
    How it works:
    1. curl_cffi.Session(impersonate="chrome") spoofs Chrome's exact JA3/TLS fingerprint
    2. First request to nseindia.com captures Akamai cookies (AKA_A2, _abck, ak_bmsc, bm_sz)
    3. Subsequent API calls to /api/annual-reports use those cookies
    4. PDF downloads from nsearchives.nseindia.com use the same session
    """

    def __init__(self):
        self._session: Optional[cffi_requests.Session] = None
        self._cookies_initialized = False

    def _ensure_session(self):
        """Create curl_cffi session with Chrome impersonation if needed."""
        if self._session is None:
            self._session = cffi_requests.Session(impersonate="chrome")
            self._cookies_initialized = False

        if not self._cookies_initialized:
            self._init_cookies()

    def _init_cookies(self):
        """Visit NSE homepage to capture Akamai session cookies."""
        logger.info("Initializing NSE session: visiting homepage for Akamai cookies...")
        try:
            resp = self._session.get(
                settings.nse_base_url,
                timeout=settings.timeout_seconds,
            )
            if resp.status_code == 200:
                cookie_names = list(self._session.cookies.keys())
                logger.info(f"NSE cookies captured: {cookie_names}")
                self._cookies_initialized = True
            else:
                logger.warning(f"NSE homepage returned HTTP {resp.status_code}")
        except Exception as e:
            logger.warning(f"Failed to initialize NSE cookies: {e}")

    def _request_with_retry(self, url: str, **kwargs) -> cffi_requests.Response:
        """Execute GET request with exponential backoff retry logic."""
        self._ensure_session()
        last_exception = None

        for attempt in range(1, settings.max_retries + 1):
            try:
                # Rate limit delay
                time.sleep(settings.request_delay_seconds)

                resp = self._session.get(
                    url,
                    timeout=settings.timeout_seconds,
                    **kwargs,
                )

                if resp.status_code == 200:
                    return resp
                elif resp.status_code == 429:
                    logger.warning(f"Attempt {attempt}: Rate limited (429) on {url}")
                    if attempt == settings.max_retries:
                        raise NSERateLimitError(f"NSE rate limit exceeded on {url}")
                elif resp.status_code == 403:
                    logger.warning(f"Attempt {attempt}: Forbidden (403) on {url}. Re-initializing cookies...")
                    self._cookies_initialized = False
                    self._init_cookies()
                else:
                    logger.warning(f"Attempt {attempt}: HTTP {resp.status_code} on {url}")

            except (NSERateLimitError,):
                raise
            except Exception as e:
                logger.warning(f"Attempt {attempt}/{settings.max_retries} failed for {url}: {e}")
                last_exception = e

            # Exponential backoff with jitter
            backoff = (settings.backoff_factor ** attempt) + (random.uniform(0.5, 2.0) if settings.jitter else 0)
            time.sleep(backoff)

        raise NSEClientError(f"Failed GET {url} after {settings.max_retries} retries. Last error: {last_exception}")

    async def discover_annual_reports(self, symbol: str) -> List[ReportMetadata]:
        """
        Discover annual reports for a symbol by hitting NSE's JSON API.
        curl_cffi handles Akamai bypass transparently.
        """
        clean_sym = sanitize_symbol(symbol)
        reports: List[ReportMetadata] = []

        api_url = f"{settings.annual_reports_endpoint}?index=equities&symbol={clean_sym}"

        try:
            logger.info(f"Discovering annual reports for {clean_sym} via NSE API...")
            response = self._request_with_retry(api_url)
            data = response.json()

            # NSE returns {"data": [...]} structure
            items = data if isinstance(data, list) else data.get("data", [])

            for item in items:
                file_url = (
                    item.get("fileName")
                    or item.get("attachment")
                    or item.get("url")
                    or ""
                )
                if not file_url:
                    continue

                if not file_url.startswith("http"):
                    file_url = f"{settings.nse_base_url}/{file_url.lstrip('/')}"

                company_name = item.get("companyName") or clean_sym
                from_yr = item.get("fromYr", "")
                to_yr = item.get("toYr", "")
                title = f"Annual Report {from_yr}-{to_yr}"
                year = int(to_yr) if to_yr and to_yr.isdigit() else extract_year_from_text(file_url)

                # Determine document type from URL
                is_pdf = file_url.lower().endswith(".pdf")
                is_zip = file_url.lower().endswith(".zip")

                report = ReportMetadata(
                    company=company_name,
                    symbol=clean_sym,
                    exchange=ExchangeType.NSE,
                    year=year,
                    document_type=DocumentType.ANNUAL_REPORT,
                    source="NSE",
                    pdf_url=file_url,
                    status="discovered",
                )
                reports.append(report)

            logger.info(f"Discovered {len(reports)} annual reports for {clean_sym}")

        except Exception as e:
            logger.error(f"Failed to discover reports for {clean_sym}: {e}")

        return reports

    def download_pdf_bytes(self, pdf_url: str) -> bytes:
        """
        Download PDF/ZIP bytes from nsearchives.nseindia.com.
        Uses the same curl_cffi session with valid Akamai cookies.
        """
        logger.info(f"Downloading: {pdf_url}")
        response = self._request_with_retry(pdf_url)
        content = response.content
        logger.info(f"Downloaded {len(content)} bytes ({len(content)/1024/1024:.1f} MB)")
        return content

    async def close(self):
        """Close the session."""
        if self._session:
            self._session.close()
            self._session = None
        logger.info("NSE client closed.")
