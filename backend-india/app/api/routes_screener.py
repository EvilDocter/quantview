"""
QuantView — Screener API Routes

Traditional and natural language stock screener.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.postgres import get_db
from app.core.schemas import ScreenerRequest, ScreenerResult

router = APIRouter()


@router.post("/filter")
async def filter_stocks(
    filters: dict,
    db: AsyncSession = Depends(get_db),
):
    """Traditional filter-based stock screening."""
    return {"results": [], "total": 0}


@router.post("/natural-language", response_model=ScreenerResult)
async def natural_language_screen(
    request: ScreenerRequest,
    db: AsyncSession = Depends(get_db),
):
    """Convert natural language query to stock filters and return results."""
    return ScreenerResult(
        companies=[],
        query_interpretation="",
        total_results=0,
    )


@router.get("/presets")
async def get_preset_screens():
    """Get pre-built screening strategies."""
    return {
        "presets": [
            {"id": "value", "name": "Value Picks", "description": "Low PE, High ROE, Low Debt"},
            {"id": "growth", "name": "Growth Stocks", "description": "High revenue & profit growth"},
            {"id": "dividend", "name": "Dividend Aristocrats", "description": "Consistent high dividend yield"},
            {"id": "quality", "name": "Quality Stocks", "description": "High ROCE, Low Debt, Consistent earnings"},
            {"id": "momentum", "name": "Momentum Leaders", "description": "Near 52-week highs with volume"},
            {"id": "small_cap_gems", "name": "Small Cap Gems", "description": "Small caps with improving fundamentals"},
        ]
    }
