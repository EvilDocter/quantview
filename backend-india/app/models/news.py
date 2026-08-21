"""
QuantView — News Article Model
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, Float
from sqlalchemy.dialects.postgresql import UUID
from app.db.postgres import Base


class NewsArticle(Base):
    __tablename__ = "news"
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(String(50), index=True, nullable=False)
    symbol = Column(String(20), index=True, nullable=False)
    title = Column(String(500), nullable=False)
    publisher = Column(String(255))
    url = Column(Text)
    published_at = Column(DateTime, default=datetime.utcnow)
    summary = Column(Text)
    sentiment = Column(String(50), default="NEUTRAL")
    relevance_score = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow)
