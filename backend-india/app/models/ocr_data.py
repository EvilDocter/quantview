"""
QuantView — OCR Page & Table Intelligence Models
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, Float, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID
from app.db.postgres import Base


class OCRPage(Base):
    __tablename__ = "ocr_pages"
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(String(50), index=True, nullable=False)
    symbol = Column(String(20), index=True, nullable=False)
    document_id = Column(String(100), index=True)
    page_number = Column(Integer, nullable=False)
    ocr_text = Column(Text)
    layout_type = Column(String(100), default="TEXT")
    confidence = Column(Float, default=0.95)
    created_at = Column(DateTime, default=datetime.utcnow)


class OCRTable(Base):
    __tablename__ = "ocr_tables"
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(String(50), index=True, nullable=False)
    symbol = Column(String(20), index=True, nullable=False)
    document_id = Column(String(100), index=True)
    page_number = Column(Integer, nullable=False)
    table_title = Column(String(255))
    table_json = Column(JSON)
    markdown_text = Column(Text)
    confidence = Column(Float, default=0.95)
    created_at = Column(DateTime, default=datetime.utcnow)
