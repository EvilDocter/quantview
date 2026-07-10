"""
QuantView — Ingestion Base Collector

Standard interface and common utilities for all data collectors in the platform.
Handles logging, rate-limiting, retries, and database session setup.
"""

import time
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import get_settings
from app.db.postgres import AsyncSessionLocal
from app.core.exceptions import IngestionError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ingestion")

settings = get_settings()

class BaseCollector(ABC):
    """
    Base class that all ingestion modules must inherit from.
    Provides standard lifecycle hooks and robust API fetch wrapper methods.
    """

    def __init__(self, name: str):
        self.name = name
        self.settings = settings
        self.rate_limit_delay = settings.scraper_rate_limit

    @abstractmethod
    async def collect(self, *args, **kwargs) -> Any:
        """
        Subclasses must implement this method to execute the ingestion.
        Should fetch, normalize, and save the data to database systems.
        """
        pass

    async def get_db_session(self) -> AsyncSession:
        """Yields an async database session for storage operations."""
        return AsyncSessionLocal()

    def enforce_rate_limit(self):
        """Sleeps briefly to prevent spamming endpoints and avoid IP bans."""
        if self.rate_limit_delay > 0:
            time.sleep(self.rate_limit_delay)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    def fetch_with_retry(self, fetch_func, *args, **kwargs) -> Any:
        """
        Generic synchronous fetch wrapper with exponential backoff retries.
        """
        try:
            self.enforce_rate_limit()
            return fetch_func(*args, **kwargs)
        except Exception as e:
            logger.error(f"[{self.name}] Error fetching data, retrying: {e}")
            raise IngestionError(str(e), source=self.name)
