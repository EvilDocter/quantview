"""
QuantView Financial Knowledge Platform — Configuration Settings
"""

from pathlib import Path
from typing import List, Dict
from pydantic_settings import BaseSettings
from pydantic import Field


class KnowledgePlatformSettings(BaseSettings):
    # Storage paths
    storage_root: Path = Field(
        default=Path("/Users/mahant/quantview/documents"),
        alias="KNOWLEDGE_STORAGE_ROOT"
    )
    
    # Qdrant Vector Store Configuration
    # Supports both local Qdrant server (http://10.250.101.68:6333) and local embedded path fallback
    qdrant_host: str = Field(default="10.250.101.68", alias="QDRANT_HOST")
    qdrant_port: int = Field(default=6333, alias="QDRANT_PORT")
    qdrant_local_path: Path = Field(
        default=Path("/Users/mahant/quantview/documents/qdrant_storage"),
        alias="QDRANT_LOCAL_PATH"
    )
    qdrant_collection_annual_reports: str = "annual_reports"
    qdrant_collection_quarterly_reports: str = "quarterly_reports"
    qdrant_collection_announcements: str = "announcements"

    # Embedding Model Settings
    embedding_model_name: str = Field(default="BAAI/bge-large-en-v1.5", alias="EMBEDDING_MODEL_NAME")
    embedding_dimension: int = 1024
    embedding_batch_size: int = 32

    # Chunker & Search Parameters
    max_chunk_tokens: int = 800
    chunk_overlap: int = 100
    hybrid_top_k: int = 10
    vector_weight: float = 0.7
    keyword_weight: float = 0.3

    # Cron Bot
    nightly_cron_hour: int = 2        # 2:00 AM IST
    nightly_cron_minute: int = 0
    nightly_cron_symbols: str = "INFY,RELIANCE,TCS,HDFCBANK,TATAMOTORS,ICICIBANK,WIPRO,SBIN,LT,BAJFINANCE"

    model_config = {
        "env_prefix": "KNOWLEDGE_",
        "extra": "ignore",
    }

    def get_cron_symbols_list(self) -> List[str]:
        return [s.strip() for s in self.nightly_cron_symbols.split(",") if s.strip()]


knowledge_settings = KnowledgePlatformSettings()
