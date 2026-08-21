"""
QuantView — Chronological Timeline Event Model
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, Float
from sqlalchemy.dialects.postgresql import UUID
from app.db.postgres import Base


class TimelineEvent(Base):
    __tablename__ = "timeline_events"
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(String(50), index=True, nullable=False)
    symbol = Column(String(20), index=True, nullable=False)
    event_date = Column(DateTime, index=True, nullable=False)
    title = Column(String(255), nullable=False)
    category = Column(String(100), default="GENERAL")
    impact_score = Column(Float, default=0.0)
    summary = Column(Text)
    source_url = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
