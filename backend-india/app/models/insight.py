"""
QuantView — Hidden Insight Model
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, Float, JSON
from sqlalchemy.dialects.postgresql import UUID
from app.db.postgres import Base


class HiddenInsight(Base):
    __tablename__ = "hidden_insights"
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(String(50), index=True, nullable=False)
    symbol = Column(String(20), index=True, nullable=False)
    category = Column(String(100), index=True, nullable=False)
    severity = Column(String(50), default="MEDIUM")
    insight_text = Column(Text, nullable=False)
    metric_proof = Column(JSON)
    year_range = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
