"""
QuantView — Price Data SQLAlchemy Models

Stock prices, index prices, and index constituents.
"""

from sqlalchemy import (
    Column, Integer, String, BigInteger, Numeric,
    Date, ForeignKey, UniqueConstraint, Index,
)
from app.db.postgres import Base


class StockPrice(Base):
    __tablename__ = "stock_prices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    date = Column(Date, nullable=False)
    open = Column(Numeric(12, 2))
    high = Column(Numeric(12, 2))
    low = Column(Numeric(12, 2))
    close = Column(Numeric(12, 2))
    adj_close = Column(Numeric(12, 2))
    volume = Column(BigInteger)
    delivery_pct = Column(Numeric(5, 2))

    __table_args__ = (
        UniqueConstraint("company_id", "date", name="uq_price_company_date"),
        Index("idx_prices_date", "company_id", "date"),
    )


class IndexMaster(Base):
    __tablename__ = "indices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    symbol = Column(String(50), unique=True, nullable=False)
    exchange = Column(String(10))


class IndexPrice(Base):
    __tablename__ = "index_prices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    index_id = Column(Integer, ForeignKey("indices.id"), nullable=False)
    date = Column(Date, nullable=False)
    open = Column(Numeric(12, 2))
    high = Column(Numeric(12, 2))
    low = Column(Numeric(12, 2))
    close = Column(Numeric(12, 2))
    volume = Column(BigInteger)

    __table_args__ = (
        UniqueConstraint("index_id", "date", name="uq_index_price_date"),
        Index("idx_index_prices_date", "index_id", "date"),
    )


class IndexConstituent(Base):
    __tablename__ = "index_constituents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    index_id = Column(Integer, ForeignKey("indices.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    weight = Column(Numeric(6, 3))
    as_of_date = Column(Date)

    __table_args__ = (
        UniqueConstraint("index_id", "company_id", "as_of_date",
                         name="uq_index_constituent"),
    )
