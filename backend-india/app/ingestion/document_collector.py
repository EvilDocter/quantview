"""
QuantView — Document Collector

Crawls company investor relations portals and exchanges (BSE/NSE)
to download PDFs (Annual Reports, Earnings Calls, Presentations) and store them in R2.
"""

import logging
import os
import httpx
from sqlalchemy import select
from app.ingestion.base_collector import BaseCollector
from app.models.company import Company
from app.models.document import Document
from app.core.utils import generate_hash

logger = logging.getLogger("document_collector")

class DocumentCollector(BaseCollector):
    """Downloads corporate reports, saves metadata, and transfers raw files to Object Storage."""

    def __init__(self):
        super().__init__("document_collector")
        self.download_dir = "data/downloads"
        os.makedirs(self.download_dir, exist_ok=True)

    async def download_pdf(self, url: str, filename: str) -> Optional[str]:
        """Downloads a PDF from a URL and saves it locally or to Object Storage."""
        filepath = os.path.join(self.download_dir, filename)
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.get(url, follow_redirects=True)
                if response.status_code == 200:
                    with open(filepath, "wb") as f:
                        f.write(response.content)
                    logger.info(f"Downloaded PDF: {filepath}")
                    return filepath
        except Exception as e:
            logger.error(f"Failed to download document from {url}: {e}")
        return None

    async def collect_documents_for_company(self, symbol: str):
        """Fetches PDFs for a given company symbol (mocked/stubbed URLs for free indexation)."""
        session = await self.get_db_session()
        try:
            stmt = select(Company).where(Company.symbol == symbol)
            res = await session.execute(stmt)
            company = res.scalar_one_or_none()
            if not company:
                return

            # Example document stub
            doc_url = "https://www.bseindia.com/bseplus/AnnualReport/500325/5003250324.pdf" # Reliance AR FY24 placeholder
            file_hash = generate_hash(symbol, "annual_report", "FY24")

            # Check if document already exists
            stmt_check = select(Document).where(Document.file_hash == file_hash)
            existing = (await session.execute(stmt_check)).scalar_one_or_none()

            if not existing:
                filename = f"{symbol}_AR_FY24.pdf"
                
                # In production, calls download_pdf
                # local_path = await self.download_pdf(doc_url, filename)
                local_path = os.path.join(self.download_dir, filename)
                # Create empty file as placeholder for testing/extraction
                with open(local_path, "w") as f:
                    f.write("QuantView Financial Document PDF Extraction Source Placeholder text.")

                doc = Document(
                    company_id=company.id,
                    document_type="annual_report",
                    title=f"Annual Report FY24 - {symbol}",
                    fiscal_year="FY24",
                    quarter="Q4",
                    file_url=local_path, # Using local path as stub
                    file_hash=file_hash,
                    page_count=1,
                    is_processed=False
                )
                session.add(doc)
                await session.commit()
                logger.info(f"Registered document metadata for {symbol}")
        except Exception as e:
            await session.rollback()
            logger.error(f"Error collecting documents for {symbol}: {e}")
        finally:
            await session.close()

    async def collect(self, *args, **kwargs) -> Any:
        session = await self.get_db_session()
        try:
            stmt = select(Company)
            res = await session.execute(stmt)
            companies = res.scalars().all()
            for company in companies:
                await self.collect_documents_for_company(company.symbol)
        finally:
            await session.close()
