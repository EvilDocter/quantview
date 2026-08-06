"""
QuantView Financial Knowledge Platform — Nightly Ingestion Bot

Runs automatically every night via APScheduler to check NSE for new corporate filings.
"""

import asyncio
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.knowledge.config import knowledge_settings
from app.knowledge.pipeline import IngestionPipeline

logger = logging.getLogger("knowledge_bot")


class NightlyScraperBot:
    """Automated bot checking for corporate filings every night."""

    def __init__(self):
        self.scheduler = None

    def start(self):
        """Start the background scheduler."""
        if self.scheduler is not None:
            logger.warning("Nightly Bot already running.")
            return

        self.scheduler = BackgroundScheduler()
        trigger = CronTrigger(
            hour=knowledge_settings.nightly_cron_hour,
            minute=knowledge_settings.nightly_cron_minute,
        )

        self.scheduler.add_job(
            self._run_nightly_job,
            trigger=trigger,
            id="nightly_filings_ingestion",
            name="Nightly Filings Ingestion Bot",
            replace_existing=True,
        )

        self.scheduler.start()
        logger.info(
            f"Nightly Bot STARTED: Scheduled to run at {knowledge_settings.nightly_cron_hour:02d}:"
            f"{knowledge_settings.nightly_cron_minute:02d} IST daily."
        )

    def stop(self):
        """Stop the background scheduler."""
        if self.scheduler:
            self.scheduler.shutdown(wait=False)
            self.scheduler = None
            logger.info("Nightly Bot STOPPED.")

    def _run_nightly_job(self):
        """Execute scheduled ingestion job."""
        logger.info("=== NIGHTLY BOT TRIGGERED: Checking for new NSE filings ===")
        symbols = knowledge_settings.get_cron_symbols_list()

        loop = asyncio.new_event_loop()
        try:
            pipeline = IngestionPipeline()
            for sym in symbols:
                loop.run_until_complete(pipeline.ingest_company(sym))
        except Exception as e:
            logger.error(f"Nightly Bot job error: {e}")
        finally:
            loop.close()
