"""
QuantView — Financial Analysis Agent (Multi-Source Robust Extraction)

Retrieves real-time market quotes, local annual report financials.json artifacts,
and structured financial statements from PostgreSQL and web APIs.
"""

from app.agents.state import AgentState
import logging
import urllib.request
import json
import os
from pathlib import Path
from ddgs import DDGS
from app.config import get_settings

logger = logging.getLogger("financial_agent")


class FinancialAgent:
    """Specialist node resolving structured financial values from local artifacts, DB, and live web APIs."""

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
    def load_local_financials(symbol: str) -> dict:
        """Load financials.json from local Knowledge Storage if present."""
        base_dir = Path("documents/NSE") / symbol.upper()
        if not base_dir.exists():
            return {}

        for year_dir in sorted(base_dir.glob("*"), reverse=True):
            fin_path = year_dir / "annual_report" / "financials.json"
            if fin_path.exists():
                try:
                    with open(fin_path, "r", encoding="utf-8") as f:
                        return json.load(f)
                except Exception as e:
                    logger.warning(f"Failed reading {fin_path}: {e}")
        return {}

    @staticmethod
    async def execute(state: AgentState) -> dict:
        symbol = state["company_symbol"]
        evidence = []

        # 1. Fetch live market price
        chart_info = await FinancialAgent.fetch_chart_data(symbol)

        # 2. Load local financials artifact if ingested
        local_fin = FinancialAgent.load_local_financials(symbol)

        # 3. Search DDGS for fundamental financial metrics
        financial_snippets = []
        try:
            ddgs = DDGS()
            query = f"{symbol} stock revenue net profit PE ratio EPS debt equity market cap financial metrics"
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
            "source": "financial_agent",
            "symbol": symbol,
            "current_price": chart_info.get("current_price"),
            "previous_close": chart_info.get("previous_close"),
            "local_ingested_financials": local_fin,
            "financial_search_results": financial_snippets,
        })

        return {
            "retrieved_evidence": [{
                "agent": "financial_agent",
                "evidence": evidence,
            }]
        }
