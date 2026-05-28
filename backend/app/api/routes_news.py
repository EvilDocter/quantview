from fastapi import APIRouter
from app.services.news_service import NewsService

router = APIRouter()

news_service = NewsService()


@router.get("/news")
def get_news(symbol: str = "BTC/USD"):

    articles = news_service.get_news(symbol)

    return {
        "symbol": symbol,
        "articles": articles
    }