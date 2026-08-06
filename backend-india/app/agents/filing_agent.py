"""
QuantView — Filing Analysis Agent (Live Web)

Uses DDGS to find SEBI reports, annual filings, or investor presentations.
"""

from app.agents.state import AgentState
import logging
import asyncio
from ddgs import DDGS
import trafilatura

logger = logging.getLogger("filing_agent")


class FilingAgent:
    """Specialist node resolving corporate filing data via live scraping."""

    @staticmethod
    async def fetch_article_text(url: str) -> str:
        try:
            downloaded = await asyncio.to_thread(trafilatura.fetch_url, url)
            if downloaded:
                text = await asyncio.to_thread(trafilatura.extract, downloaded)
                return text[:1500] if text else ""
        except Exception as e:
            logger.warning(f"Failed to extract {url}: {e}")
        return ""

    @staticmethod
    async def execute(state: AgentState) -> dict:
        symbol = state["company_symbol"]
        evidence = []
        try:
            logger.info(f"Live DDGS scraping filings for {symbol}")
            ddgs = DDGS()
            query = f"{symbol} stock annual report investor presentation quarterly results statutory filing"
            results = list(ddgs.text(keywords=query, max_results=3))

            for item in results:
                url = item.get("href", "")
                title = item.get("title", "")

                content = await FilingAgent.fetch_article_text(url)
                if not content:
                    content = item.get("body", "")

                evidence.append({
                    "source": "duckduckgo_filing_scraper",
                    "title": title,
                    "url": url,
                    "content": content,
                })
        except Exception as e:
            logger.error(f"Live filing scraping failed for {symbol}: {e}")

        return {
            "retrieved_evidence": [{
                "agent": "filing_agent",
                "evidence": evidence,
            }]
        }
