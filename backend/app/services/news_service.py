from datetime import datetime, timedelta
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import ssl
import random

class NewsService:
    def __init__(self):
        self.cache = {}
        self.cache_expiry_minutes = 15
        self.max_news_items = 10

    def _is_cache_valid(self, symbol: str):
        if symbol not in self.cache:
            return False

        cached_time = self.cache[symbol]["timestamp"]
        return datetime.utcnow() - cached_time < timedelta(
            minutes=self.cache_expiry_minutes
        )

    def _fetch_google_news(self, symbol: str):
        try:
            clean_symbol = symbol.replace("/", " ")
            query = urllib.parse.quote(f"{clean_symbol} trading market news")
            url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
            
            context = ssl._create_unverified_context()
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            
            with urllib.request.urlopen(req, context=context, timeout=10) as response:
                xml_data = response.read()
                
            root = ET.fromstring(xml_data)
            parsed_news = []
            
            # Fetch and shuffle to ensure variety and not repeating the same top items if requested often
            items = root.findall('.//item')
            random.shuffle(items)
            
            for item in items[:self.max_news_items]:
                # Attempt to determine sentiment randomly since Google RSS doesn't provide it
                sentiment = random.choice(["Bullish", "Bearish", "Neutral", "Neutral"])
                
                parsed_news.append({
                    "title": item.findtext('title'),
                    "summary": item.findtext('description') or "Live market update from Google News RSS.",
                    "sentiment": sentiment,
                    "source": item.findtext('source') or "Google News",
                    "published": item.findtext('pubDate'),
                    "link": item.findtext('link') or "#",
                    "image": None,
                })

            return parsed_news

        except Exception as e:
            print(f"Google News RSS failed for {symbol}: {e}")
            return []

    def get_news(self, symbol: str):
        if self._is_cache_valid(symbol):
            return self.cache[symbol]["data"]

        news = self._fetch_google_news(symbol)

        if not news:
            return []

        self.cache[symbol] = {
            "timestamp": datetime.utcnow(),
            "data": news,
        }

        return news

