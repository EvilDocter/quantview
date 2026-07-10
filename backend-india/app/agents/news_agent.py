"""
QuantView — News Intelligence Agent

Queries PostgreSQL and OpenSearch to extract recent news stories and analyze public sentiment.
"""

from sqlalchemy import select
from app.agents.state import AgentState
from app.db.postgres import AsyncSessionLocal
from app.models.company import Company
from app.models.document import News

class NewsAgent:
    """Specialist node resolving company news stories and sentiment dynamics."""

    @staticmethod
    async def execute(state: AgentState) -> dict:
        symbol = state["company_symbol"]
        session = AsyncSessionLocal()
        evidence = []
        try:
            stmt = select(Company).where(Company.symbol == symbol)
            res = await session.execute(stmt)
            company = res.scalar_one_or_none()
            
            if company:
                stmt_news = select(News).where(News.company_id == company.id).order_by(News.published_at.desc()).limit(5)
                news_res = await session.execute(stmt_news)
                articles = news_res.scalars().all()
                for article in articles:
                    evidence.append({
                        "source": "news",
                        "title": article.title,
                        "sentiment": article.sentiment_label,
                        "score": float(article.sentiment_score) if article.sentiment_score else 0.0,
                        "published_at": str(article.published_at)
                    })
        except Exception:
            pass
        finally:
            await session.close()

        return {
            "retrieved_evidence": [{
                "agent": "news_agent",
                "evidence": evidence
            }]
        }
