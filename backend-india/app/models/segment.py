"""
QuantView — Segment Reporting Model
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Float, Numeric
from sqlalchemy.dialects.postgresql import UUID
from app.db.postgres import Base


class SegmentReporting(Base):
    __tablename__ = "segments"
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(String(50), index=True, nullable=False)
    symbol = Column(String(20), index=True, nullable=False)
    fiscal_year = Column(String(20), index=True, nullable=False)
    segment_name = Column(String(255), nullable=False)
    revenue = Column(Numeric(20, 2), default=0.0)
    profit = Column(Numeric(20, 2), default=0.0)
    assets = Column(Numeric(20, 2), default=0.0)
    liabilities = Column(Numeric(20, 2), default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
