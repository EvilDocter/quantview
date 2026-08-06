"""
QuantView — Financial Analysis Agent (Unblocked Live Web)

Retrieves real-time market quotes via Yahoo chart API and searches DDGS
for fundamental financials (Revenue, Profit, Margins, PE, EPS).
"""

from app.agents.state import AgentState
import logging
import urllib.request
import json
from ddgs import DDGS

logger = logging.getLogger("financial_agent")


class FinancialAgent:
    """Specialist node resolving structured financial values from unblocked web APIs."""

    @staticmethod
    async def fetch_chart_data(symbol: str) -> dict:
        yf_sym = symbol + ".NS" if symbol != "NIFTY50" else "^NSEI"
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{yf_sym}?interval=1d&range=5d"
        try:
            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
                },
            )
            with urllib.request.urlopen(req, timeout=10) as res:
                data = json.loads(res.read().decode())
                meta = data["chart"]["result"][0]["meta"]
                return {
                    "current_price": meta.get("regularMarketPrice"),
                    "previous_close": meta.get("chartPreviousClose"),
                    "currency": meta.get("currency", "INR"),
                    "symbol": meta.get("symbol"),
                }
        except Exception as e:
            logger.warning(f"Yahoo chart fetch failed for {symbol}: {e}")
            return {}

    @staticmethod
    async def execute(state: AgentState) -> dict:
        symbol = state["company_symbol"]
        evidence = []

        # 1. Fetch live market price
        chart_info = await FinancialAgent.fetch_chart_data(symbol)

        # 2. Search DDGS for fundamental financial metrics
        financial_snippets = []
        try:
            ddgs = DDGS()
            query = f"{symbol} financial statements revenue net profit PE ratio EPS market cap"
            results = list(ddgs.text(keywords=query, max_results=4))
            for item in results:
                financial_snippets.append({
                    "title": item.get("title", ""),
                    "snippet": item.get("body", ""),
                    "url": item.get("href", ""),
                })
        except Exception as e:
            logger.warning(f"DDGS financial search failed for {symbol}: {e}")

        evidence.append({
            "source": "live_market_data",
            "current_price": chart_info.get("current_price"),
            "previous_close": chart_info.get("previous_close"),
            "financial_search_results": financial_snippets,
        })

        return {
            "retrieved_evidence": [{
                "agent": "financial_agent",
                "evidence": evidence,
            }]
        }
