"""
QuantView — News RSS Ingestion Collector

Fetches market and company-related news feeds via RSS (Google News, Mint, ET)
and performs basic sentiment analysis (Vader/Qwen) before loading into PostgreSQL and OpenSearch.
"""

import logging
import feedparser
from datetime import datetime
from sqlalchemy import select
from time import mktime

from app.ingestion.base_collector import BaseCollector
from app.models.company import Company
from app.models.document import News
from app.core.constants import NEWS_RSS_FEEDS
from app.core.utils import generate_hash
from app.db.opensearch import index_document

logger = logging.getLogger("news_collector")

class NewsCollector(BaseCollector):
    """Collector for market and company news RSS feeds."""

    def __init__(self):
        super().__init__("news_collector")

    async def collect_feed(self, feed_name: str, feed_url: str):
        """Parses a specific RSS feed and inserts unique news items."""
        session = await self.get_db_session()
        try:
            logger.info(f"Parsing news RSS feed: {feed_name}")
            feed = feedparser.parse(feed_url)
            
            # Resolve companies list to tag news
            comp_stmt = select(Company)
            comp_res = await session.execute(comp_stmt)
            companies = comp_res.scalars().all()

            for entry in feed.entries:
                title = entry.get("title", "")
                content = entry.get("summary", entry.get("description", ""))
                url = entry.get("link", "")
                
                # Deduplication hash
                content_hash = generate_hash(title, url)
                
                # Check duplication
                stmt_check = select(News).where(News.content_hash == content_hash)
                existing = (await session.execute(stmt_check)).scalar_one_or_none()
                if existing:
                    continue

                # Parse publication time
                published_at = datetime.now()
                if "published_parsed" in entry:
                    published_at = datetime.fromtimestamp(mktime(entry.published_parsed))

                # Identify tagged company if mentioned in title/summary
                tagged_company_id = None
                tagged_symbol = None
                for company in companies:
                    if company.symbol.lower() in title.lower() or company.name.lower() in title.lower():
                        tagged_company_id = company.id
                        tagged_symbol = company.symbol
                        break

                # Simple sentiment categorization stub (vader/llm in production)
                sentiment_score = 0.0
                sentiment_label = "neutral"
                if "buy" in title.lower() or "profit" in title.lower() or "rally" in title.lower():
                    sentiment_score = 0.5
                    sentiment_label = "positive"
                elif "loss" in title.lower() or "decline" in title.lower() or "fall" in title.lower():
                    sentiment_score = -0.5
                    sentiment_label = "negative"

                news_record = News(
                    title=title,
                    content=content,
                    source=feed_name,
                    url=url,
                    published_at=published_at,
                    company_id=tagged_company_id,
                    sentiment_score=sentiment_score,
                    sentiment_label=sentiment_label,
                    category="market" if not tagged_company_id else "company",
                    content_hash=content_hash
                )
                session.add(news_record)
                await session.flush()  # populate ID

                # Index into OpenSearch (Layer 4)
                try:
                    index_document(str(news_record.id), {
                        "company_id": tagged_company_id,
                        "company_symbol": tagged_symbol,
                        "document_type": "news",
                        "title": title,
                        "content": content,
                        "published_at": published_at.isoformat(),
                        "sentiment_score": float(sentiment_score),
                        "sentiment_label": sentiment_label,
                        "source": feed_name,
                        "url": url
                    })
                except Exception as ex:
                    logger.warning(f"OpenSearch index failed for news {news_record.id}: {ex}")

            await session.commit()
            logger.info(f"Finished processing feed {feed_name}")
        except Exception as e:
            await session.rollback()
            logger.error(f"Error parsing feed {feed_name}: {e}")
        finally:
            await session.close()

    async def collect(self, *args, **kwargs) -> Any:
        """Scheduled task to crawl all feeds."""
        for name, url in NEWS_RSS_FEEDS.items():
            await self.collect_feed(name, url)
            self.enforce_rate_limit()
