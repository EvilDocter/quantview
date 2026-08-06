"""
NSE Ingestion Service — Configuration Settings

Centralized, non-hardcoded settings for rate limits, retry policies,
headers, directory paths, Playwright browser config, APScheduler cron,
and NSE endpoint mappings.
"""

from pathlib import Path
from typing import Dict
from pydantic_settings import BaseSettings
from pydantic import Field


class NSEIngestionSettings(BaseSettings):
    # Storage Configuration
    base_storage_dir: Path = Field(
        default=Path("/Users/mahant/quantview/documents"),
        alias="NSE_STORAGE_DIR"
    )

    # Network & Rate Limiting
    max_concurrent_downloads: int = Field(default=3, alias="NSE_MAX_CONCURRENT")
    request_delay_seconds: float = Field(default=1.5, alias="NSE_REQUEST_DELAY")
    timeout_seconds: float = Field(default=30.0, alias="NSE_TIMEOUT")

    # Retry Policy
    max_retries: int = Field(default=5, alias="NSE_MAX_RETRIES")
    backoff_factor: float = Field(default=2.0, alias="NSE_BACKOFF_FACTOR")
    jitter: bool = True

    # Playwright Browser Settings
    playwright_headless: bool = Field(default=True, alias="NSE_HEADLESS")
    playwright_timeout_ms: int = Field(default=30000, alias="NSE_PW_TIMEOUT_MS")

    # HTTP Headers for NSE Browser Simulation
    default_headers: Dict[str, str] = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.nseindia.com/",
        "Connection": "keep-alive",
    }

    # NSE Endpoints
    nse_base_url: str = "https://www.nseindia.com"
    nse_annual_reports_page: str = "https://www.nseindia.com/companies-listing/corporate-filings-annual-reports"
    annual_reports_endpoint: str = "https://www.nseindia.com/api/annual-reports"
    corporate_announcements_endpoint: str = "https://www.nseindia.com/api/corporate-announcements"
    equity_master_endpoint: str = "https://www.nseindia.com/api/equity-master"

    # APScheduler Cron Settings (daily at 6:00 AM IST by default)
    scheduler_enabled: bool = Field(default=False, alias="NSE_SCHEDULER_ENABLED")
    scheduler_cron_hour: int = Field(default=6, alias="NSE_CRON_HOUR")
    scheduler_cron_minute: int = Field(default=0, alias="NSE_CRON_MINUTE")
    scheduler_cron_day_of_week: str = Field(default="mon-fri", alias="NSE_CRON_DOW")

    # Default symbols for batch sync
    default_symbols: str = Field(
        default="INFY,RELIANCE,TCS,HDFCBANK,TATAMOTORS,ICICIBANK,WIPRO,SBIN,LT,BAJFINANCE",
        alias="NSE_DEFAULT_SYMBOLS"
    )

    model_config = {
        "env_prefix": "NSE_",
        "extra": "ignore",
    }

    def get_default_symbols_list(self):
        return [s.strip() for s in self.default_symbols.split(",") if s.strip()]


settings = NSEIngestionSettings()
