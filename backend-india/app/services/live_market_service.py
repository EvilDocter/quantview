"""
QuantView — Live Market Data Service (curl_cffi Unblocked Engine)

Scrapes real-time market indices, stock quotes, top gainers/losers,
sector performance, and FII/DII institutional flows from live exchange endpoints.
"""

import logging
import time
from typing import Dict, Any, List
from curl_cffi import requests as cffi_requests
from app.knowledge.crawler.nse.client import NSEClient

logger = logging.getLogger("live_market_service")

# Simple in-memory cache to prevent overloading endpoints (60s TTL)
_CACHE: Dict[str, Any] = {}
_CACHE_EXPIRY: Dict[str, float] = {}
CACHE_TTL_SECONDS = 60.0


class LiveMarketService:
    @staticmethod
    def _get_cached(key: str) -> Any:
        if key in _CACHE and time.time() < _CACHE_EXPIRY.get(key, 0):
            return _CACHE[key]
        return None

    @staticmethod
    def _set_cache(key: str, data: Any):
        _CACHE[key] = data
        _CACHE_EXPIRY[key] = time.time() + CACHE_TTL_SECONDS

    @staticmethod
    def fetch_live_indices() -> List[Dict[str, Any]]:
        cached = LiveMarketService._get_cached("indices")
        if cached:
            return cached

        # 1. Try NSE allIndices endpoint via curl_cffi Chrome impersonation
        try:
            client = NSEClient()
            client._ensure_session()
            resp = client._session.get("https://www.nseindia.com/api/allIndices", timeout=10)
            if resp.status_code == 200:
                data = resp.json().get("data", [])
                mapped = {}
                for idx in data:
                    name = idx.get("index")
                    mapped[name] = idx

                indices_list = []
                target_map = {
                    "NIFTY 50": "NIFTY 50",
                    "NIFTY BANK": "BANK NIFTY",
                    "NIFTY IT": "NIFTY IT",
                    "NIFTY NEXT 50": "NIFTY NEXT 50"
                }

                for nse_key, display_name in target_map.items():
                    if nse_key in mapped:
                        item = mapped[nse_key]
                        last_val = item.get("last", 0)
                        pct_change = item.get("percentChange", 0)
                        indices_list.append({
                            "name": display_name,
                            "symbol": nse_key,
                            "value": f"{last_val:,.2f}",
                            "pct": f"{pct_change:+.2f}%",
                            "status": "up" if pct_change >= 0 else "down"
                        })

                # Add SENSEX via Yahoo Chart API
                try:
                    s_resp = client._session.get("https://query1.finance.yahoo.com/v8/finance/chart/%5EBSESN?interval=1d&range=2d", timeout=5)
                    if s_resp.status_code == 200:
                        meta = s_resp.json()["chart"]["result"][0]["meta"]
                        price = meta.get("regularMarketPrice")
                        prev = meta.get("chartPreviousClose")
                        if price and prev:
                            pct = ((price - prev) / prev) * 100
                            indices_list.insert(1, {
                                "name": "SENSEX",
                                "symbol": "^BSESN",
                                "value": f"{price:,.2f}",
                                "pct": f"{pct:+.2f}%",
                                "status": "up" if pct >= 0 else "down"
                            })
                except Exception as e:
                    logger.warning(f"Sensex fetch failed: {e}")

                if indices_list:
                    LiveMarketService._set_cache("indices", indices_list)
                    return indices_list
        except Exception as e:
            logger.warning(f"NSE allIndices live fetch failed: {e}")

        # 2. Fallback to Yahoo Finance Chart API via curl_cffi
        try:
            session = cffi_requests.Session(impersonate="chrome")
            symbols_map = {
                "^NSEI": "NIFTY 50",
                "^BSESN": "SENSEX",
                "^NSEBANK": "BANK NIFTY",
                "^CNXIT": "NIFTY IT"
            }
            indices_list = []
            for yf_sym, name in symbols_map.items():
                try:
                    res = session.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{yf_sym}?interval=1d&range=2d", timeout=5)
                    if res.status_code == 200:
                        meta = res.json()["chart"]["result"][0]["meta"]
                        price = meta.get("regularMarketPrice")
                        prev = meta.get("chartPreviousClose")
                        if price and prev:
                            pct = ((price - prev) / prev) * 100
                            indices_list.append({
                                "name": name,
                                "symbol": yf_sym,
                                "value": f"{price:,.2f}",
                                "pct": f"{pct:+.2f}%",
                                "status": "up" if pct >= 0 else "down"
                            })
                except Exception:
                    pass

            if indices_list:
                LiveMarketService._set_cache("indices", indices_list)
                return indices_list
        except Exception as e:
            logger.warning(f"Yahoo indices fallback failed: {e}")

        return []

    @staticmethod
    def fetch_live_movers() -> Dict[str, List[Dict[str, Any]]]:
        cached = LiveMarketService._get_cached("movers")
        if cached:
            return cached

        # Query liquid Nifty universe for real-time price & % change
        symbols = [
            "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "BHARTIARTL.NS", "INFY.NS",
            "ICICIBANK.NS", "TATAMOTORS.NS", "SBIN.NS", "LT.NS", "ITC.NS",
            "AXISBANK.NS", "MARUTI.NS", "SUNPHARMA.NS", "TITAN.NS", "ULTRACEMCO.NS"
        ]
        quotes = []
        try:
            session = cffi_requests.Session(impersonate="chrome")
            for sym in symbols:
                try:
                    res = session.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?interval=1d&range=2d", timeout=4)
                    if res.status_code == 200:
                        meta = res.json()["chart"]["result"][0]["meta"]
                        price = meta.get("regularMarketPrice")
                        prev = meta.get("chartPreviousClose")
                        if price and prev:
                            pct = ((price - prev) / prev) * 100
                            clean_sym = sym.replace(".NS", "")
                            quotes.append({
                                "symbol": clean_sym,
                                "price": f"₹{price:,.2f}",
                                "change": f"{pct:+.2f}%",
                                "pct_val": pct
                            })
                except Exception:
                    pass
        except Exception as e:
            logger.warning(f"Live movers fetch failed: {e}")

        if quotes:
            # Sort for Top Gainers
            gainers = sorted(quotes, key=lambda x: x["pct_val"], reverse=True)[:3]
            # Sort for Top Losers
            losers = sorted(quotes, key=lambda x: x["pct_val"])[:3]

            result = {"gainers": gainers, "losers": losers}
            LiveMarketService._set_cache("movers", result)
            return result

        return {"gainers": [], "losers": []}

    @staticmethod
    def fetch_live_sector_performance() -> List[Dict[str, Any]]:
        cached = LiveMarketService._get_cached("sectors")
        if cached:
            return cached

        try:
            client = NSEClient()
            client._ensure_session()
            resp = client._session.get("https://www.nseindia.com/api/allIndices", timeout=10)
            if resp.status_code == 200:
                data = resp.json().get("data", [])
                mapped = {x.get("index"): x for x in data}

                sector_map = [
                    ("NIFTY AUTO", "Automobile"),
                    ("NIFTY IT", "IT Services"),
                    ("NIFTY BANK", "Private Banks"),
                    ("NIFTY ENERGY", "Power"),
                    ("NIFTY FMCG", "FMCG"),
                    ("NIFTY OIL & GAS", "Oil & Gas"),
                ]

                sectors_list = []
                for nse_key, display_name in sector_map:
                    if nse_key in mapped:
                        item = mapped[nse_key]
                        pct = item.get("percentChange", 0.0)
                        sectors_list.append({
                            "name": display_name,
                            "change": f"{pct:+.2f}%",
                            "status": "up" if pct >= 0 else "down"
                        })

                if sectors_list:
                    LiveMarketService._set_cache("sectors", sectors_list)
                    return sectors_list
        except Exception as e:
            logger.warning(f"Sector performance live fetch failed: {e}")

        return []
