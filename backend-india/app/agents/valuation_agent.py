"""
QuantView — Valuation Agent (Unblocked Live Web)

Retrieves valuation multiples (PE Ratio, Price-to-Book, EPS) by querying DDGS.
"""

from app.agents.state import AgentState
import logging
from ddgs import DDGS

logger = logging.getLogger("valuation_agent")


class ValuationAgent:
    """Specialist node resolving company valuation metrics via DDGS search."""

    @staticmethod
    async def execute(state: AgentState) -> dict:
        symbol = state["company_symbol"]
        evidence = []
        try:
            logger.info(f"Live DDGS valuation scraping for {symbol}")
            ddgs = DDGS()
            query = f"{symbol} stock PE ratio EPS price to book value market cap TipRanks Screener"
            results = list(ddgs.text(keywords=query, max_results=4))

            valuation_snippets = []
            for item in results:
                valuation_snippets.append({
                    "title": item.get("title", ""),
                    "snippet": item.get("body", ""),
                    "url": item.get("href", ""),
                })

            evidence.append({
                "source": "duckduckgo_valuation_scraper",
                "valuation_data": valuation_snippets,
            })
        except Exception as e:
            logger.error(f"Valuation scraping failed for {symbol}: {e}")

        return {
            "retrieved_evidence": [{
                "agent": "valuation_agent",
                "evidence": evidence,
            }]
        }
