"""
QuantView — Market Data API Routes

Endpoints for market overview, indices, gainers/losers,
heatmap, FII/DII activity, and daily intelligence.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.postgres import get_db
from app.core.schemas import MarketOverview, IndexData

router = APIRouter()


@router.get("/overview", response_model=MarketOverview)
async def get_market_overview(db: AsyncSession = Depends(get_db)):
    """Get complete market overview: indices, gainers, losers, FII/DII."""
    # TODO: Implement in Day 12
    return MarketOverview()


@router.get("/indices")
async def get_all_indices(db: AsyncSession = Depends(get_db)):
    """Get all index values with change percentages."""
    return {"indices": []}


@router.get("/indices/{symbol}")
async def get_index_detail(symbol: str, db: AsyncSession = Depends(get_db)):
    """Get detailed data for a specific index including historical."""
    return {"symbol": symbol, "data": []}


@router.get("/gainers")
async def get_top_gainers(limit: int = 20, db: AsyncSession = Depends(get_db)):
    """Get top gaining stocks by percentage change."""
    return {"gainers": []}


@router.get("/losers")
async def get_top_losers(limit: int = 20, db: AsyncSession = Depends(get_db)):
    """Get top losing stocks by percentage change."""
    return {"losers": []}


@router.get("/most-active")
async def get_most_active(limit: int = 20, db: AsyncSession = Depends(get_db)):
    """Get most active stocks by volume."""
    return {"most_active": []}


@router.get("/heatmap")
async def get_sector_heatmap(db: AsyncSession = Depends(get_db)):
    """Get sector-level performance data for heatmap visualization."""
    return {"sectors": []}


@router.get("/fii-dii")
async def get_fii_dii_activity(days: int = 30, db: AsyncSession = Depends(get_db)):
    """Get FII/DII buy/sell activity for the last N days."""
    return {"data": []}


@router.get("/bulk-deals")
async def get_bulk_deals(days: int = 7, db: AsyncSession = Depends(get_db)):
    """Get recent block/bulk deals."""
    return {"deals": []}
