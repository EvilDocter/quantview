"""
QuantView — Company Data API Routes

Live company data endpoints using yfinance for real-time metrics.
"""

import logging
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.db.postgres import get_db
import yfinance as yf
import requests_cache
from fake_useragent import UserAgent

router = APIRouter()
logger = logging.getLogger("routes_company")


def _get_ticker(symbol: str):
    """Create a yfinance Ticker with a cached, anti-rate-limit session."""
    session = requests_cache.CachedSession("yf_company.cache", expire_after=300)
    session.headers["User-agent"] = UserAgent().random
    yf_sym = symbol + ".NS" if symbol != "NIFTY50" else "^NSEI"
    return yf.Ticker(yf_sym, session=session)


@router.get("/{symbol}")
async def get_company_overview(symbol: str):
    """Get live company overview with price, sector, and key metrics."""
    try:
        ticker = _get_ticker(symbol)
        info = ticker.info
        return {
            "symbol": symbol,
            "name": info.get("longName", symbol),
            "sector": info.get("sector", "Unknown"),
            "industry": info.get("industry", "Unknown"),
            "market_cap": info.get("marketCap", 0),
            "current_price": info.get("currentPrice", 0),
            "previous_close": info.get("previousClose", 0),
            "day_high": info.get("dayHigh", 0),
            "day_low": info.get("dayLow", 0),
            "fifty_two_week_high": info.get("fiftyTwoWeekHigh", 0),
            "fifty_two_week_low": info.get("fiftyTwoWeekLow", 0),
            "pe_ratio": info.get("trailingPE", 0),
            "eps": info.get("trailingEps", 0),
            "book_value": info.get("bookValue", 0),
            "dividend_yield": info.get("dividendYield", 0),
            "roe": info.get("returnOnEquity", 0),
            "debt_to_equity": info.get("debtToEquity", 0),
            "revenue": info.get("totalRevenue", 0),
            "net_income": info.get("netIncomeToCommon", 0),
            "ebitda": info.get("ebitda", 0),
            "summary": info.get("longBusinessSummary", ""),
        }
    except Exception as e:
        logger.error(f"Company overview failed for {symbol}: {e}")
        return {"symbol": symbol, "name": symbol, "error": str(e)}


@router.get("/{symbol}/financials")
async def get_company_financials(
    symbol: str,
    period_type: str = Query("annual", regex="^(annual|quarterly)$"),
):
    """Get financial statements from yfinance."""
    try:
        ticker = _get_ticker(symbol)
        if period_type == "annual":
            income = ticker.financials
            balance = ticker.balance_sheet
        else:
            income = ticker.quarterly_financials
            balance = ticker.quarterly_balance_sheet

        result = {"symbol": symbol, "period_type": period_type, "income_statement": {}, "balance_sheet": {}}

        if income is not None and not income.empty:
            result["income_statement"] = {
                str(col.date()): {str(idx): float(val) if val == val else 0 for idx, val in income[col].items()}
                for col in income.columns[:4]
            }

        if balance is not None and not balance.empty:
            result["balance_sheet"] = {
                str(col.date()): {str(idx): float(val) if val == val else 0 for idx, val in balance[col].items()}
                for col in balance.columns[:4]
            }

        return result
    except Exception as e:
        logger.error(f"Financials failed for {symbol}: {e}")
        return {"symbol": symbol, "financials": [], "error": str(e)}


@router.get("/{symbol}/ratios")
async def get_company_ratios(symbol: str):
    """Get key financial ratios from yfinance."""
    try:
        ticker = _get_ticker(symbol)
        info = ticker.info
        return {
            "symbol": symbol,
            "ratios": {
                "pe_ratio": info.get("trailingPE", 0),
                "forward_pe": info.get("forwardPE", 0),
                "peg_ratio": info.get("pegRatio", 0),
                "price_to_book": info.get("priceToBook", 0),
                "price_to_sales": info.get("priceToSalesTrailing12Months", 0),
                "roe": info.get("returnOnEquity", 0),
                "roa": info.get("returnOnAssets", 0),
                "profit_margin": info.get("profitMargins", 0),
                "operating_margin": info.get("operatingMargins", 0),
                "debt_to_equity": info.get("debtToEquity", 0),
                "current_ratio": info.get("currentRatio", 0),
                "quick_ratio": info.get("quickRatio", 0),
            },
        }
    except Exception as e:
        logger.error(f"Ratios failed for {symbol}: {e}")
        return {"symbol": symbol, "ratios": {}, "error": str(e)}


@router.get("/{symbol}/prices")
async def get_company_prices(
    symbol: str,
    period: str = Query("1y", regex="^(1m|3m|6m|1y|3y|5y|10y|max)$"),
):
    """Get historical stock prices."""
    try:
        ticker = _get_ticker(symbol)
        hist = ticker.history(period=period)
        prices = []
        for date, row in hist.iterrows():
            prices.append({
                "date": str(date.date()),
                "open": round(float(row["Open"]), 2),
                "high": round(float(row["High"]), 2),
                "low": round(float(row["Low"]), 2),
                "close": round(float(row["Close"]), 2),
                "volume": int(row["Volume"]),
            })
        return {"symbol": symbol, "period": period, "prices": prices}
    except Exception as e:
        logger.error(f"Prices failed for {symbol}: {e}")
        return {"symbol": symbol, "prices": [], "error": str(e)}


@router.get("/{symbol}/news")
async def get_company_news(symbol: str, limit: int = 10):
    """Get company news from DuckDuckGo."""
    try:
        from duckduckgo_search import DDGS
        ddgs = DDGS()
        results = list(ddgs.news(keywords=f"{symbol} India stock", max_results=limit))
        news = []
        for item in results:
            news.append({
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "source": item.get("source", ""),
                "date": item.get("date", ""),
                "body": item.get("body", ""),
            })
        return {"symbol": symbol, "news": news}
    except Exception as e:
        logger.error(f"News failed for {symbol}: {e}")
        return {"symbol": symbol, "news": [], "error": str(e)}


@router.get("/{symbol}/peers")
async def get_peer_comparison(symbol: str):
    """Get peer comparison — returns basic peer info."""
    # TODO: Implement proper peer lookup via sector matching
    return {"symbol": symbol, "peers": []}


@router.get("/{symbol}/scores")
async def get_company_scores(symbol: str):
    """Get AI-generated scores for a company."""
    return None


@router.get("/{symbol}/graph")
async def get_company_graph(symbol: str):
    """Get knowledge graph data."""
    return {"nodes": [], "edges": []}
