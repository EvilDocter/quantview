"""
QuantView — Sectors API Routes

Endpoints for sector overview, individual sector analysis,
and sector rotation.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.postgres import get_db

router = APIRouter()


@router.get("/")
async def list_sectors(db: AsyncSession = Depends(get_db)):
    """Get overview of all sectors with performance metrics."""
    return {"sectors": []}


@router.get("/{sector}")
async def get_sector_detail(sector: str, db: AsyncSession = Depends(get_db)):
    """Get detailed analysis for a specific sector."""
    return {"sector": sector, "companies": [], "metrics": {}}


@router.get("/{sector}/rotation")
async def get_sector_rotation(sector: str, db: AsyncSession = Depends(get_db)):
    """Get sector rotation analysis data."""
    return {"sector": sector, "rotation": {}}
