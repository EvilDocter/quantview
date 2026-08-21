"""
QuantView — Peer Mapping Model
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Float
from sqlalchemy.dialects.postgresql import UUID
from app.db.postgres import Base


class PeerMapping(Base):
    __tablename__ = "peer_mappings"
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(String(50), index=True, nullable=False)
    symbol = Column(String(20), index=True, nullable=False)
    peer_symbol = Column(String(20), index=True, nullable=False)
    sector_name = Column(String(100))
    correlation_score = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow)
