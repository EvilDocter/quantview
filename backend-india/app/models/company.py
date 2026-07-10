"""
QuantView — Company SQLAlchemy Model

Core company entity and related metadata.
"""

from sqlalchemy import (
    Column, Integer, String, Text, BigInteger, Numeric,
    DateTime, Date, Boolean, Index,
    func,
)
from app.db.postgres import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), unique=True, nullable=False, index=True)
    bse_code = Column(String(10), index=True)
    nse_symbol = Column(String(20), index=True)
    isin = Column(String(12), unique=True)
    name = Column(String(200), nullable=False)
    industry = Column(String(100))
    sector = Column(String(100), index=True)
    market_cap = Column(BigInteger)  # in lakhs
    market_cap_category = Column(String(20))  # Large Cap, Mid Cap, Small Cap
    listing_date = Column(Date)
    face_value = Column(Numeric(10, 2))
    website = Column(String(500))
    description = Column(Text)
    logo_url = Column(String(500))

    # AI-generated fields
    ai_summary = Column(Text)
    ai_moat_score = Column(Numeric(3, 2))
    ai_health_score = Column(Numeric(3, 2))
    ai_updated_at = Column(DateTime)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index("idx_companies_market_cap", "market_cap"),
    )

    def __repr__(self):
        return f"<Company {self.symbol}: {self.name}>"
