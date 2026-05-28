import requests
import xml.etree.ElementTree as ET
from datetime import datetime


class MacroNewsService:

    RSS_FEEDS = {
        "default": [
            "https://feeds.finance.yahoo.com/rss/2.0/headline?s=EURUSD%3DX&region=US&lang=en-US",
            "https://feeds.bbci.co.uk/news/business/rss.xml",
        ],
        "BTC/USD": [
            "https://feeds.finance.yahoo.com/rss/2.0/headline?s=BTC-USD&region=US&lang=en-US",
            "https://cointelegraph.com/rss",
            "https://feeds.bbci.co.uk/news/technology/rss.xml",
        ],
        "ETH/USD": [
            "https://feeds.finance.yahoo.com/rss/2.0/headline?s=ETH-USD&region=US&lang=en-US",
            "https://cointelegraph.com/rss",
        ],
        "SOL/USD": ["https://feeds.finance.yahoo.com/rss/2.0/headline?s=SOL-USD&region=US&lang=en-US"],
        "XRP/USD": ["https://feeds.finance.yahoo.com/rss/2.0/headline?s=XRP-USD&region=US&lang=en-US"],
        "XAU/USD": [
            "https://feeds.finance.yahoo.com/rss/2.0/headline?s=GC%3DF&region=US&lang=en-US",
        ],
        "AAPL": ["https://feeds.finance.yahoo.com/rss/2.0/headline?s=AAPL&region=US&lang=en-US"],
        "TSLA": ["https://feeds.finance.yahoo.com/rss/2.0/headline?s=TSLA&region=US&lang=en-US"],
        "NVDA": ["https://feeds.finance.yahoo.com/rss/2.0/headline?s=NVDA&region=US&lang=en-US"],
        "MSFT": ["https://feeds.finance.yahoo.com/rss/2.0/headline?s=MSFT&region=US&lang=en-US"],
        "AMZN": ["https://feeds.finance.yahoo.com/rss/2.0/headline?s=AMZN&region=US&lang=en-US"],
    }

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/124.0 Safari/537.36"
    }

    def __init__(self):
        self._cache: dict = {}
        self._cache_ts: dict = {}

    def get_news_for_symbol(self, symbol: str):
        now = datetime.utcnow().timestamp()
        # 5-minute cache per symbol
        if symbol in self._cache and (now - self._cache_ts.get(symbol, 0)) < 300:
            return self._cache[symbol]

        feeds = self.RSS_FEEDS.get(symbol, self.RSS_FEEDS["default"])
        articles = []

        for feed_url in feeds:
            try:
                resp = requests.get(feed_url, headers=self.HEADERS, timeout=8)
                if resp.status_code != 200:
                    continue
                root = ET.fromstring(resp.content)

                for item in root.findall(".//item")[:6]:
                    title = (item.findtext("title") or "").strip()
                    link = (item.findtext("link") or "#").strip()
                    pub = (item.findtext("pubDate") or "Recently").strip()
                    desc = (item.findtext("description") or "").strip()
                    source_el = item.find("source")
                    source = source_el.text.strip() if source_el is not None and source_el.text else "Finance News"

                    if not title:
                        continue

                    intelligence = self._generate_macro_intelligence(title, desc)
                    articles.append({
                        "title": title,
                        "summary": desc[:200] if desc else "",
                        "link": link,
                        "published": pub,
                        "source": source,
                        "sentiment": intelligence["sentiment"],
                        "impact": intelligence["impact"],
                        "macro_theme": intelligence["macro_theme"],
                        "ai_summary": intelligence["ai_summary"],
                        "risk_level": intelligence["risk_level"],
                        "timestamp": datetime.utcnow().isoformat(),
                    })

            except Exception as e:
                print(f"RSS fetch error for {feed_url}: {e}")
                continue

        # Filter by relevance — fall back to all if none match
        keywords = self._symbol_keywords(symbol)
        filtered = [a for a in articles if any(k in (a["title"] + a.get("summary", "")).lower() for k in keywords)]
        result = filtered[:10] if filtered else articles[:10]

        self._cache[symbol] = result
        self._cache_ts[symbol] = now
        return result

    def _symbol_keywords(self, symbol: str):
        mapping = {
            "EUR/USD": ["eur", "euro", "ecb", "usd", "fed", "powell", "inflation", "cpi", "forex"],
            "GBP/USD": ["gbp", "pound", "boe", "bank of england", "usd", "forex"],
            "USD/JPY": ["boj", "yen", "japan", "usd", "fed"],
            "XAU/USD": ["gold", "inflation", "fed", "rates", "treasury", "safe haven"],
            "BTC/USD": ["bitcoin", "btc", "crypto", "etf", "fed", "liquidity"],
            "ETH/USD": ["ethereum", "eth", "crypto", "staking", "defi"],
            "SOL/USD": ["solana", "sol", "crypto"],
            "XRP/USD": ["xrp", "ripple", "crypto"],
            "AAPL": ["apple", "aapl", "iphone", "tech"],
            "TSLA": ["tesla", "tsla", "elon", "ev"],
            "NVDA": ["nvidia", "nvda", "ai", "chip", "gpu"],
            "MSFT": ["microsoft", "msft", "azure", "ai"],
        }
        return mapping.get(symbol, ["market", "economy", "fed", "rate", "trade", "stock", "finance"])

    def _generate_macro_intelligence(self, title: str, summary: str):
        text = f"{title} {summary}".lower()

        bullish_words = ["growth", "rally", "bullish", "strong", "surge", "recovery", "rise", "gain", "beats"]
        bearish_words = ["recession", "crash", "selloff", "inflation", "risk", "weakness", "fall", "drop", "miss"]
        high_impact_words = ["fed", "ecb", "boj", "inflation", "cpi", "rates", "powell", "payrolls", "gdp"]

        sentiment = "Neutral"
        if any(w in text for w in bullish_words):
            sentiment = "Bullish"
        if any(w in text for w in bearish_words):
            sentiment = "Bearish"

        impact = "HIGH" if any(w in text for w in high_impact_words) else "LOW"
        risk_level = 85 if impact == "HIGH" else 35

        macro_theme = "Market Update"
        if "inflation" in text or "cpi" in text:
            macro_theme = "Inflation Shock"
        elif "fed" in text or "rates" in text:
            macro_theme = "Monetary Policy"
        elif "recession" in text:
            macro_theme = "Recession Risk"
        elif "bitcoin" in text or "crypto" in text:
            macro_theme = "Crypto Markets"

        ai_summary = (
            f"{impact} impact development detected. "
            f"AI reads {sentiment.lower()} pressure on {macro_theme}."
        )

        return {
            "sentiment": sentiment,
            "impact": impact,
            "macro_theme": macro_theme,
            "ai_summary": ai_summary,
            "risk_level": risk_level,
        }