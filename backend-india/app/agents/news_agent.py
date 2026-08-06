"""
QuantView — News Intelligence Agent (Live Web)

Uses DDGS to find and read the latest news articles from the live internet.
"""

from app.agents.state import AgentState
import logging
import asyncio
from ddgs import DDGS
import trafilatura

logger = logging.getLogger("news_agent")


class NewsAgent:
    """Specialist node resolving company news stories and sentiment via live web scraping."""

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
            logger.info(f"Live DDGS scraping news for {symbol}")
            ddgs = DDGS()
            results = list(ddgs.news(keywords=f"{symbol} stock news India", max_results=3))

            for item in results:
                url = item.get("url", "")
                title = item.get("title", "")

                content = await NewsAgent.fetch_article_text(url)
                if not content:
                    content = item.get("body", "")

                evidence.append({
                    "source": "duckduckgo_live_news",
                    "title": title,
                    "url": url,
                    "publisher": item.get("source", ""),
                    "content": content,
                })
        except Exception as e:
            logger.error(f"Live news scraping failed for {symbol}: {e}")

        return {
            "retrieved_evidence": [{
                "agent": "news_agent",
                "evidence": evidence,
            }]
        }
