from fastapi import APIRouter
from app.services.social_service import SocialService

router = APIRouter()

social_service = SocialService()


@router.get("/social")
def get_social(symbol: str = "BTC"):

    data = social_service.get_combined_sentiment(symbol)

    return data