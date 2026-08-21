"""
QuantView — Filing Analysis Agent (Dynamic On-Demand NSE Scraper RAG Engine)

Dynamically retrieves corporate filing data and annual reports.
If annual report files do not exist locally, automatically triggers real-time
NSE document discovery, PDF download, text extraction, and RAG chunking on-the-fly!
"""

from app.agents.state import AgentState
import logging
import asyncio
from typing import List, Dict, Any

from app.knowledge.crawler.dynamic_scraper import DynamicNSEScraper
from duckduckgo_search import DDGS

logger = logging.getLogger("filing_agent")


class FilingAgent:
    """Specialist node resolving corporate filing data via dynamic on-demand NSE scraping & RAG."""

    @staticmethod
    async def execute(state: AgentState) -> dict:
        symbol = state["company_symbol"]
        query = state["query"]
        evidence: List[Dict[str, Any]] = []

        if not symbol or symbol == "NIFTY50":
            symbol = "RELIANCE"

        # 1. Dynamic On-Demand NSE Scraper (Loads cached or scrapes & downloads on-the-fly)
        try:
            logger.info(f"Querying Dynamic NSE Scraper RAG for '{symbol}'...")
            chunks = await DynamicNSEScraper.get_or_download_filings(symbol)

            if chunks:
                logger.info(f"Retrieved {len(chunks)} dynamic filing chunks for {symbol}")
                # Pick top matching chunks for context
                for chunk in chunks[:6]:
                    text_content = chunk.get("text", "")
                    evidence.append({
                        "source": f"QuantView Knowledge RAG (NSE {symbol} Annual Report)",
                        "title": f"Doc: {chunk.get('document', symbol)} | Chunk: {chunk.get('chunk_id')}",
                        "url": f"https://www.nseindia.com/companies-listing/corporate-filings-annual-reports",
                        "content": text_content,
                    })
        except Exception as e:
            logger.warning(f"Dynamic NSE RAG lookup error for {symbol}: {e}")

        # 2. Live DuckDuckGo Web Search Fallback if needed
        if not evidence:
            try:
                logger.info(f"Live DuckDuckGo search fallback for {symbol}")
                ddgs = DDGS()
                results = list(ddgs.text(keywords=f"{symbol} NSE annual report financial filings key risks", max_results=4))
                for item in results:
                    evidence.append({
                        "source": f"Live Web Search ({symbol} Filings)",
                        "title": item.get("title", ""),
                        "url": item.get("href", ""),
                        "content": item.get("body", ""),
                    })
            except Exception as e:
                logger.warning(f"DDGS web search fallback failed for {symbol}: {e}")

        return {
            "retrieved_evidence": [{
                "agent": "filing_agent",
                "evidence": evidence,
            }]
        }
