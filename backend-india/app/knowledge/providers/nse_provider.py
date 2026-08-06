"""
QuantView Financial Knowledge Platform — Document Providers

Extensible provider architecture allowing addition of BSE, SEBI, and IR portals.
"""

from abc import ABC, abstractmethod
from typing import List
from app.knowledge.models import ChunkMetadata
from app.knowledge.crawler.nse.client import NSEClient
from app.knowledge.crawler.nse.models import ReportMetadata


class BaseProvider(ABC):
    @abstractmethod
    async def discover_reports(self, symbol: str) -> List[ReportMetadata]:
        pass

    @abstractmethod
    def download_pdf(self, pdf_url: str) -> bytes:
        pass


class NSEProvider(BaseProvider):
    """NSE Document Provider utilizing Akamai WAF bypass via curl_cffi."""

    def __init__(self):
        self.client = NSEClient()

    async def discover_reports(self, symbol: str) -> List[ReportMetadata]:
        return await self.client.discover_annual_reports(symbol)

    def download_pdf(self, pdf_url: str) -> bytes:
        return self.client.download_pdf_bytes(pdf_url)

    async def close(self):
        await self.client.close()
