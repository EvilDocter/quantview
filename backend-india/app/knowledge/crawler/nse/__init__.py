"""
QuantView — NSE Annual Report Ingestion Service (Public API)

Uses curl_cffi for Chrome TLS fingerprint impersonation to bypass NSE Akamai WAF,
BeautifulSoup for DOM parsing, and APScheduler for cron-based automated ingestion.
"""

from typing import List, Optional
from app.knowledge.crawler.nse.crawler import NSECrawler
from app.knowledge.crawler.nse.client import NSEClient
from app.knowledge.crawler.nse.scheduler import NSEScheduler
from app.knowledge.crawler.nse.models import ReportMetadata, IngestionResult, SyncSummary


async def discover_company_reports(symbol: str) -> List[ReportMetadata]:
    """Discover available annual reports for a company symbol from NSE."""
    client = NSEClient()
    try:
        return await client.discover_annual_reports(symbol)
    finally:
        await client.close()


async def sync_company(symbol: str) -> IngestionResult:
    """Full pipeline: discover, download, validate, and store all annual reports for a symbol."""
    crawler = NSECrawler()
    try:
        return await crawler.sync_company(symbol)
    finally:
        await crawler.close()


async def download_all_reports(symbol: str) -> IngestionResult:
    """Alias for sync_company(symbol)."""
    return await sync_company(symbol)


async def sync_all(symbols: Optional[List[str]] = None) -> SyncSummary:
    """Batch sync annual reports for multiple company symbols with rate limits."""
    from app.knowledge.crawler.nse.config import settings
    target_symbols = symbols or settings.get_default_symbols_list()
    scheduler = NSEScheduler()
    try:
        return await scheduler.sync_symbols(target_symbols)
    finally:
        await scheduler.close()


def start_scheduled_sync():
    """Start APScheduler cron job for automatic daily scraping."""
    scheduler = NSEScheduler()
    scheduler.start_cron_job()
    return scheduler
