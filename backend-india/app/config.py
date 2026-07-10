"""
QuantView Indian Market Backend — Application Configuration

Centralized settings management using Pydantic Settings.
All values are loaded from environment variables or .env file.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # ── Application ──────────────────────────────────────────────
    app_env: str = Field(default="development", alias="APP_ENV")
    app_secret_key: str = Field(default="change-me-in-production", alias="APP_SECRET_KEY")
    app_title: str = "QuantView India API"
    app_version: str = "0.1.0"
    frontend_url: str = Field(default="http://localhost:3000", alias="FRONTEND_URL")

    # ── PostgreSQL (Neon) ────────────────────────────────────────
    database_url: str = Field(
        default="postgresql+asyncpg://localhost:5432/quantview_india",
        alias="DATABASE_URL",
    )
    database_url_sync: str = Field(
        default="postgresql://localhost:5432/quantview_india",
        alias="DATABASE_URL_SYNC",
    )

    # ── Qdrant Cloud ─────────────────────────────────────────────
    qdrant_url: str = Field(default="http://localhost:6333", alias="QDRANT_URL")
    qdrant_api_key: Optional[str] = Field(default=None, alias="QDRANT_API_KEY")
    qdrant_collection: str = "company_documents"
    qdrant_embedding_dim: int = 1024  # BGE-large-en-v1.5

    # ── Neo4j Aura ───────────────────────────────────────────────
    neo4j_uri: str = Field(default="bolt://localhost:7687", alias="NEO4J_URI")
    neo4j_user: str = Field(default="neo4j", alias="NEO4J_USER")
    neo4j_password: str = Field(default="password", alias="NEO4J_PASSWORD")

    # ── OpenSearch (Bonsai) ──────────────────────────────────────
    opensearch_url: str = Field(default="http://localhost:9200", alias="OPENSEARCH_URL")
    opensearch_user: Optional[str] = Field(default=None, alias="OPENSEARCH_USER")
    opensearch_password: Optional[str] = Field(default=None, alias="OPENSEARCH_PASSWORD")
    opensearch_index: str = "quantview_documents"

    # ── Redis (Upstash) ──────────────────────────────────────────
    redis_url: str = Field(default="redis://localhost:6379", alias="REDIS_URL")

    # ── Cloudflare R2 ────────────────────────────────────────────
    r2_access_key_id: Optional[str] = Field(default=None, alias="R2_ACCESS_KEY_ID")
    r2_secret_access_key: Optional[str] = Field(default=None, alias="R2_SECRET_ACCESS_KEY")
    r2_bucket_name: str = Field(default="quantview-docs", alias="R2_BUCKET_NAME")
    r2_endpoint: Optional[str] = Field(default=None, alias="R2_ENDPOINT")

    # ── AI Model Server ─────────────────────────────────────────
    ai_server_url: str = Field(default="http://localhost:7861", alias="AI_SERVER_URL")
    llm_reasoning_model: str = "qwen2.5:7b"
    llm_extraction_model: str = "qwen2.5:3b"
    embedding_model: str = "BAAI/bge-large-en-v1.5"

    # ── Celery ───────────────────────────────────────────────────
    celery_broker_url: str = Field(default="redis://localhost:6379/0", alias="CELERY_BROKER_URL")
    celery_result_backend: str = Field(
        default="redis://localhost:6379/1", alias="CELERY_RESULT_BACKEND"
    )

    # ── Data Ingestion ───────────────────────────────────────────
    scraper_rate_limit: float = 1.0  # seconds between requests
    max_retries: int = 3
    historical_years: int = 10  # years of historical data to ingest

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


@lru_cache()
def get_settings() -> Settings:
    """Cached settings singleton."""
    return Settings()
