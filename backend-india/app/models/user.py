"""
QuantView — User Data SQLAlchemy Models

Watchlists, portfolios, and research history.
Extends the NextAuth user schema (users are managed by the frontend).
"""

from sqlalchemy import (
    Column, Integer, String, Text, Numeric,
    DateTime, Date, ForeignKey, UniqueConstraint, ARRAY,
    func,
)
from app.db.postgres import Base


class Watchlist(Base):
    __tablename__ = "watchlists"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(50), nullable=False, index=True)
    name = Column(String(100))
    created_at = Column(DateTime, server_default=func.now())


class WatchlistItem(Base):
    __tablename__ = "watchlist_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    watchlist_id = Column(Integer, ForeignKey("watchlists.id", ondelete="CASCADE"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    added_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("watchlist_id", "company_id", name="uq_watchlist_item"),
    )


class Portfolio(Base):
    __tablename__ = "portfolios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(50), nullable=False, index=True)
    name = Column(String(100))
    created_at = Column(DateTime, server_default=func.now())


class PortfolioHolding(Base):
    __tablename__ = "portfolio_holdings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id", ondelete="CASCADE"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    avg_buy_price = Column(Numeric(12, 2), nullable=False)
    buy_date = Column(Date)

    __table_args__ = (
        UniqueConstraint("portfolio_id", "company_id", name="uq_portfolio_holding"),
    )


class ResearchHistory(Base):
    __tablename__ = "research_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(50), nullable=False, index=True)
    query = Column(Text, nullable=False)
    response = Column(Text)
    agents_used = Column(ARRAY(String(200)))
    confidence = Column(Numeric(3, 2))
    created_at = Column(DateTime, server_default=func.now())
