"""
NSE Ingestion Service — APScheduler + Async Concurrent Scheduler

Provides:
1. On-demand batch sync via sync_symbols()
2. APScheduler cron-based automatic daily scraping
"""

import asyncio
import logging
from typing import List, Optional
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.knowledge.crawler.nse.config import settings
from app.knowledge.crawler.nse.crawler import NSECrawler
from app.knowledge.crawler.nse.models import SyncSummary, IngestionResult

logger = logging.getLogger("nse_scheduler")


class NSEScheduler:
    def __init__(self, crawler: Optional[NSECrawler] = None):
        self.crawler = crawler or NSECrawler()
        self.semaphore = asyncio.Semaphore(settings.max_concurrent_downloads)
        self._apscheduler: Optional[BackgroundScheduler] = None

    # ── On-demand batch sync ─────────────────────────────────────
    async def sync_symbols(self, symbols: List[str]) -> SyncSummary:
        """Sync annual reports for a list of company symbols with rate limits."""
        summary = SyncSummary()
        logger.info(f"Starting batch sync for {len(symbols)} symbols: {symbols}")

        # Process sequentially to avoid overwhelming NSE
        # (Playwright shares a single browser instance)
        for sym in symbols:
            try:
                result = await self._sync_single_guarded(sym)
                summary.total_symbols_processed += 1
                summary.total_downloaded += result.reports_downloaded
                summary.total_skipped += result.reports_skipped
                summary.total_errors += result.reports_failed
                summary.results[result.symbol] = result
            except Exception as e:
                logger.error(f"Failed to sync {sym}: {e}")
                summary.total_symbols_processed += 1
                summary.total_errors += 1

        logger.info(
            f"Batch sync complete: {summary.total_downloaded} downloaded, "
            f"{summary.total_skipped} skipped, {summary.total_errors} errors "
            f"across {summary.total_symbols_processed} symbols."
        )
        return summary

    async def _sync_single_guarded(self, symbol: str) -> IngestionResult:
        """Process single symbol bounded by semaphore."""
        async with self.semaphore:
            try:
                return await self.crawler.sync_company(symbol)
            except Exception as e:
                logger.error(f"Scheduler error for {symbol}: {e}")
                return IngestionResult(symbol=symbol, reports_failed=1)

    # ── APScheduler cron-based automatic scraping ────────────────
    def start_cron_job(self):
        """
        Start APScheduler BackgroundScheduler with a cron trigger
        that runs the batch sync at the configured time.
        """
        if not settings.scheduler_enabled:
            logger.info("NSE cron scheduler is DISABLED (set NSE_SCHEDULER_ENABLED=true to enable)")
            return

        if self._apscheduler is not None:
            logger.warning("Cron scheduler already running.")
            return

        self._apscheduler = BackgroundScheduler()
        trigger = CronTrigger(
            hour=settings.scheduler_cron_hour,
            minute=settings.scheduler_cron_minute,
            day_of_week=settings.scheduler_cron_day_of_week,
        )

        self._apscheduler.add_job(
            self._cron_sync_job,
            trigger=trigger,
            id="nse_annual_report_sync",
            name="NSE Annual Report Cron Sync",
            replace_existing=True,
        )

        self._apscheduler.start()
        logger.info(
            f"NSE cron scheduler STARTED: "
            f"runs at {settings.scheduler_cron_hour:02d}:{settings.scheduler_cron_minute:02d} "
            f"on {settings.scheduler_cron_day_of_week}"
        )

    def stop_cron_job(self):
        """Stop the APScheduler cron job."""
        if self._apscheduler:
            self._apscheduler.shutdown(wait=False)
            self._apscheduler = None
            logger.info("NSE cron scheduler STOPPED.")

    def _cron_sync_job(self):
        """Sync job invoked by APScheduler (runs in a thread, bridges to async)."""
        logger.info("=== CRON TRIGGERED: Starting scheduled NSE Annual Report sync ===")
        symbols = settings.get_default_symbols_list()

        # Bridge from sync APScheduler thread to async crawler
        loop = asyncio.new_event_loop()
        try:
            summary = loop.run_until_complete(self.sync_symbols(symbols))
            logger.info(
                f"=== CRON COMPLETE: {summary.total_downloaded} downloaded, "
                f"{summary.total_skipped} skipped, {summary.total_errors} errors ==="
            )
        except Exception as e:
            logger.error(f"CRON JOB FAILED: {e}")
        finally:
            loop.close()

    async def close(self):
        """Shutdown everything."""
        self.stop_cron_job()
        await self.crawler.close()
