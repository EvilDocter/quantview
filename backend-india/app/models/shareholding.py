"""
QuantView — Shareholding Pattern Model
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Float
from sqlalchemy.dialects.postgresql import UUID
from app.db.postgres import Base


class ShareholdingPattern(Base):
    __tablename__ = "shareholding"
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(String(50), index=True, nullable=False)
    symbol = Column(String(20), index=True, nullable=False)
    quarter_date = Column(String(20), index=True, nullable=False)
    promoter_pct = Column(Float, default=0.0)
    fii_pct = Column(Float, default=0.0)
    dii_pct = Column(Float, default=0.0)
    public_pct = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
