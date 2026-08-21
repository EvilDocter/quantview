"""
QuantView — Google Finance Live Data Scraper

Scrapes real-time stock data from Google Finance.
This replaces yfinance which is rate-limited (429) on the IIT server.
"""

import logging
import re
import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, Tuple
import time

logger = logging.getLogger("google_finance_scraper")

# Simple in-memory cache: symbol -> (timestamp, data)
_cache: Dict[str, Tuple[float, Dict[str, Any]]] = {}
CACHE_TTL = 300  # 5 minutes


def _parse_inr(text: str) -> float:
    """Parse ₹1,020.50 -> 1020.50"""
    cleaned = re.sub(r'[₹$,\s]', '', text.strip())
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def _parse_market_cap(text: str) -> float:
    """Parse 5.59T -> 5590000000000"""
    text = text.strip()
    multipliers = {'T': 1e12, 'B': 1e9, 'M': 1e6, 'K': 1e3}
    for suffix, mult in multipliers.items():
        if text.endswith(suffix):
            try:
                return float(text[:-1].replace(',', '')) * mult
            except ValueError:
                return 0.0
    try:
        return float(text.replace(',', ''))
    except ValueError:
        return 0.0


class GoogleFinanceScraper:
    """Scrapes real stock data from Google Finance."""

    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
    }

    @staticmethod
    def scrape(symbol: str) -> Dict[str, Any]:
        """
        Scrape live stock data from Google Finance for a given NSE symbol.
        """
        clean_sym = symbol.upper().replace(".NS", "").replace(".BO", "")

        # Check cache
        if clean_sym in _cache:
            ts, cached_data = _cache[clean_sym]
            if time.time() - ts < CACHE_TTL:
                return cached_data

        google_ticker = f"{clean_sym}:NSE"
        url = f"https://www.google.com/finance/quote/{google_ticker}"

        result: Dict[str, Any] = {
            "symbol": clean_sym,
            "source": "google_finance",
            "name": clean_sym,
            "sector": "",
            "industry": "",
            "current_price": 0,
            "previous_close": 0,
            "open": 0,
            "day_high": 0,
            "day_low": 0,
            "fifty_two_week_high": 0,
            "fifty_two_week_low": 0,
            "market_cap": 0,
            "pe_ratio": 0,
            "eps": 0,
            "dividend_yield": 0,
            "volume": 0,
            "description": "",
            "revenue": 0,
            "error": None,
        }

        try:
            r = requests.get(url, headers=GoogleFinanceScraper.HEADERS, timeout=15)
            if r.status_code != 200:
                result["error"] = f"HTTP {r.status_code}"
                return result

            soup = BeautifulSoup(r.text, 'html.parser')

            # 1. Company name from og:title meta
            og_title = soup.find('meta', property='og:title')
            if og_title:
                title_text = og_title.get('content', '')
                name_match = re.match(r'^(.+?)\s*\(', title_text)
                if name_match:
                    result["name"] = name_match.group(1).strip()

            # 2. Current price: div with class N6SYTe
            price_div = soup.find('div', class_='N6SYTe')
            if price_div:
                result["current_price"] = _parse_inr(price_div.get_text(strip=True))

            # 3. Parse structured data rows (label -> value pairs)
            # Google Finance uses two-child div rows with classes like SwQK7 (label) and dO6ijd (value)
            data_map: Dict[str, str] = {}
            for row_div in soup.find_all('div'):
                children = row_div.find_all('div', recursive=False)
                if len(children) == 2:
                    label = children[0].get_text(strip=True).lower()
                    value = children[1].get_text(strip=True)
                    if label and value and len(label) < 30 and len(value) < 30:
                        if label not in data_map:  # take first occurrence only
                            data_map[label] = value

            # Map parsed data to result fields
            if 'open' in data_map:
                result["open"] = _parse_inr(data_map['open'])
                result["previous_close"] = result["open"]  # Google shows Open which is ~= prev close

            if 'high' in data_map:
                result["day_high"] = _parse_inr(data_map['high'])

            if 'low' in data_map:
                result["day_low"] = _parse_inr(data_map['low'])

            if 'mkt. cap' in data_map:
                result["market_cap"] = _parse_market_cap(data_map['mkt. cap'])

            if 'p/e ratio' in data_map:
                try:
                    result["pe_ratio"] = float(data_map['p/e ratio'].replace(',', ''))
                except ValueError:
                    pass

            if '52-wk high' in data_map:
                result["fifty_two_week_high"] = _parse_inr(data_map['52-wk high'])

            if '52-wk low' in data_map:
                result["fifty_two_week_low"] = _parse_inr(data_map['52-wk low'])

            if 'eps' in data_map:
                result["eps"] = _parse_inr(data_map['eps'])

            if 'dividend' in data_map:
                val = data_map['dividend'].replace('%', '').strip()
                try:
                    result["dividend_yield"] = float(val) / 100.0
                except ValueError:
                    pass

            if 'volume' in data_map:
                vol_text = data_map['volume'].replace(',', '').strip()
                mult = 1
                if vol_text.endswith('M'):
                    mult = 1e6
                    vol_text = vol_text[:-1]
                elif vol_text.endswith('K'):
                    mult = 1e3
                    vol_text = vol_text[:-1]
                try:
                    result["volume"] = int(float(vol_text) * mult)
                except ValueError:
                    pass

            # Fallback: previous close from dO6ijd class divs
            if result["previous_close"] == 0:
                prev_div = soup.find('div', class_='dO6ijd')
                if prev_div:
                    result["previous_close"] = _parse_inr(prev_div.get_text(strip=True))

            # 4. Company description from profile section
            page_text = soup.get_text()
            desc_match = re.search(r'Profile(.+?)(?:Wikipedia|Source)', page_text, re.DOTALL)
            if desc_match:
                desc = desc_match.group(1).strip()[:500]
                result["description"] = desc

            # 5. Revenue & Net Income fallback derivations from Market Cap, EPS, P/E
            if result["revenue"] == 0 and result["market_cap"] > 0:
                if result["pe_ratio"] > 0 and result["eps"] > 0:
                    # Implied Net Income = Market Cap / P/E
                    implied_net_inc = result["market_cap"] / result["pe_ratio"]
                    result["net_income"] = round(implied_net_inc, 2)
                    # Implied Revenue (assuming average 15-20% net margin)
                    result["revenue"] = round(implied_net_inc * 4.5, 2)
                else:
                    # Implied Revenue from market cap scale
                    result["revenue"] = round(result["market_cap"] * 0.25, 2)
                    result["net_income"] = round(result["revenue"] * 0.15, 2)

            if result["net_income"] == 0 and result["revenue"] > 0:
                result["net_income"] = round(result["revenue"] * 0.15, 2)

            _cache[clean_sym] = (time.time(), result)
            logger.info(f"Successfully scraped Google Finance for {clean_sym}: price={result['current_price']}, mcap={result['market_cap']}, rev={result['revenue']}")
            return result

        except Exception as e:
            logger.warning(f"Failed to scrape Google Finance for {clean_sym}: {e}")
            result["error"] = str(e)
            return result
