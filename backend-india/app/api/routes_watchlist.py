"""
QuantView — Watchlist API Routes

Endpoints for watchlist CRUD operations.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.postgres import get_db

router = APIRouter()


@router.get("/")
async def list_watchlists(
    user_id: str = "anonymous",
    db: AsyncSession = Depends(get_db),
):
    """List all watchlists for a user."""
    return {"watchlists": []}


@router.post("/")
async def create_watchlist(
    name: str,
    user_id: str = "anonymous",
    db: AsyncSession = Depends(get_db),
):
    """Create a new watchlist."""
    return {"id": 1, "name": name, "message": "Watchlist created"}


@router.put("/{watchlist_id}")
async def update_watchlist(
    watchlist_id: int,
    name: str,
    db: AsyncSession = Depends(get_db),
):
    """Update watchlist name."""
    return {"id": watchlist_id, "message": "Watchlist updated"}


@router.delete("/{watchlist_id}")
async def delete_watchlist(
    watchlist_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete a watchlist."""
    return {"message": "Watchlist deleted"}


@router.post("/{watchlist_id}/add")
async def add_to_watchlist(
    watchlist_id: int,
    symbol: str,
    db: AsyncSession = Depends(get_db),
):
    """Add a company to a watchlist."""
    return {"watchlist_id": watchlist_id, "symbol": symbol, "message": "Added"}


@router.delete("/{watchlist_id}/remove/{symbol}")
async def remove_from_watchlist(
    watchlist_id: int,
    symbol: str,
    db: AsyncSession = Depends(get_db),
):
    """Remove a company from a watchlist."""
    return {"message": f"{symbol} removed from watchlist"}
