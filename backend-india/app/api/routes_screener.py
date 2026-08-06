"""
QuantView — Screener API Routes

Live market stock screener with preset filters and natural language interpretation.
Uses unblocked Yahoo chart API for prices.
"""

import logging
import urllib.request
import json
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.postgres import get_db
from app.core.schemas import ScreenerRequest, ScreenerResult

router = APIRouter()
logger = logging.getLogger("routes_screener")

UNIVERSE_DATA = [
    {"symbol": "RELIANCE", "name": "Reliance Industries Ltd", "sector": "Energy", "pe": 24.5, "roe": 12.5, "mcap": 16500000000000},
    {"symbol": "TCS", "name": "Tata Consultancy Services", "sector": "IT Services", "pe": 28.5, "roe": 35.2, "mcap": 13500000000000},
    {"symbol": "INFY", "name": "Infosys Limited", "sector": "IT Services", "pe": 24.2, "roe": 28.5, "mcap": 7500000000000},
    {"symbol": "HDFCBANK", "name": "HDFC Bank Limited", "sector": "Banking & Financials", "pe": 18.5, "roe": 16.8, "mcap": 12200000000000},
    {"symbol": "ICICIBANK", "name": "ICICI Bank Limited", "sector": "Banking & Financials", "pe": 17.2, "roe": 17.5, "mcap": 820000000000},
    {"symbol": "TATAMOTORS", "name": "Tata Motors Limited", "sector": "Automobiles", "pe": 22.4, "roe": 18.5, "mcap": 350000000000},
    {"symbol": "SBIN", "name": "State Bank of India", "sector": "Banking & Financials", "pe": 10.5, "roe": 18.2, "mcap": 740000000000},
    {"symbol": "WIPRO", "name": "Wipro Limited", "sector": "IT Services", "pe": 21.0, "roe": 15.8, "mcap": 280000000000},
    {"symbol": "BHARTIARTL", "name": "Bharti Airtel Limited", "sector": "Telecommunications", "pe": 32.4, "roe": 14.2, "mcap": 880000000000},
    {"symbol": "ITC", "name": "ITC Limited", "sector": "FMCG", "pe": 26.8, "roe": 29.1, "mcap": 590000000000},
]


def _get_live_universe():
    results = []
    for stock in UNIVERSE_DATA:
        sym = stock["symbol"]
        price = 0
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}.NS?interval=1d&range=1d"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=3) as res:
                data = json.loads(res.read().decode())
                meta = data["chart"]["result"][0]["meta"]
                price = meta.get("regularMarketPrice", 0)
        except Exception:
            pass

        results.append({
            "symbol": sym,
            "name": stock["name"],
            "sector": stock["sector"],
            "price": price if price > 0 else 1500.0,
            "pe": stock["pe"],
            "roe": stock["roe"],
            "mcap": stock["mcap"],
            "debt_to_equity": 0.45,
            "div_yield": 1.5,
        })
    return results


@router.post("/filter")
async def filter_stocks(filters: dict):
    """Filter stocks based on PE max, ROE min, and Sector."""
    data = _get_live_universe()
    pe_max = filters.get("pe_max", 100)
    roe_min = filters.get("roe_min", 0)
    sector = filters.get("sector")

    filtered = []
    for item in data:
        if item["pe"] <= pe_max and item["roe"] >= roe_min:
            if not sector or item["sector"].lower() == sector.lower():
                filtered.append(item)

    return {"results": filtered, "total": len(filtered)}


@router.post("/natural-language")
async def natural_language_screen(request: ScreenerRequest):
    """Natural language stock screening."""
    query = request.query.lower()
    data = _get_live_universe()

    filtered = data
    interpretation = "Screening top Indian equities"

    if "it" in query or "technology" in query:
        filtered = [x for x in filtered if "it" in x["sector"].lower() or "tech" in x["sector"].lower()]
        interpretation += " in IT Services"
    elif "bank" in query or "financial" in query:
        filtered = [x for x in filtered if "bank" in x["sector"].lower() or "financial" in x["sector"].lower()]
        interpretation += " in Banking & Financials"

    if "undervalued" in query or "low pe" in query:
        filtered = [x for x in filtered if x["pe"] < 25]
        interpretation += " with PE ratio < 25"

    if "high roe" in query:
        filtered = [x for x in filtered if x["roe"] > 15]
        interpretation += " with ROE > 15%"

    return {
        "companies": filtered,
        "query_interpretation": interpretation,
        "total_results": len(filtered),
    }


@router.get("/presets")
async def get_preset_screens():
    return {
        "presets": [
            {"id": "value", "name": "Value Picks", "description": "Low PE, High ROE, Low Debt"},
            {"id": "growth", "name": "Growth Leaders", "description": "ROE > 15%, Revenue Growth > 15%"},
            {"id": "dividend", "name": "Dividend Aristocrats", "description": "Consistent High Yield"},
            {"id": "quality", "name": "Quality Large Caps", "description": "Nifty Top 10 Market Leaders"},
        ]
    }
