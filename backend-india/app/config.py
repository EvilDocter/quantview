"""
QuantView Indian Market Backend — Application Configuration

Centralized settings management using Pydantic Settings.
All values target the IIT server (10.250.101.68) and environment settings.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # ── Application ──────────────────────────────────────────────
    app_env: str = Field(default="production", alias="APP_ENV")
    app_secret_key: str = Field(default="quantview-iit-production-secret-key", alias="APP_SECRET_KEY")
    app_title: str = "QuantView Institutional Research API"
    app_version: str = "1.0.0"
    frontend_url: str = Field(default="http://quantview.in", alias="FRONTEND_URL")

    # ── PostgreSQL / SQLite Fallback ────────────────────────────────────────
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@10.250.101.68:5432/quantview_india",
        alias="DATABASE_URL",
    )
    database_url_sync: str = Field(
        default="postgresql://postgres:postgres@10.250.101.68:5432/quantview_india",
        alias="DATABASE_URL_SYNC",
    )

    # ── Qdrant Vector Store (IIT Server) ───────────────────────────
    qdrant_url: str = Field(default="http://10.250.101.68:6333", alias="QDRANT_URL")
    qdrant_api_key: Optional[str] = Field(default=None, alias="QDRANT_API_KEY")
    qdrant_collection: str = "company_documents"
    qdrant_embedding_dim: int = 1024  # BGE-large-en-v1.5

    # ── Neo4j Graph DB (IIT Server) ────────────────────────────────
    neo4j_uri: str = Field(default="bolt://10.250.101.68:7687", alias="NEO4J_URI")
    neo4j_user: str = Field(default="neo4j", alias="NEO4J_USER")
    neo4j_password: str = Field(default="password", alias="NEO4J_PASSWORD")

    # ── OpenSearch Full Text (IIT Server) ──────────────────────────
    opensearch_url: str = Field(default="http://10.250.101.68:9200", alias="OPENSEARCH_URL")
    opensearch_user: Optional[str] = Field(default=None, alias="OPENSEARCH_USER")
    opensearch_password: Optional[str] = Field(default=None, alias="OPENSEARCH_PASSWORD")
    opensearch_index: str = "quantview_documents"

    # ── Redis Cache (IIT Server) ───────────────────────────────────
    redis_url: str = Field(default="redis://10.250.101.68:6379", alias="REDIS_URL")

    # ── Cloudflare R2 ────────────────────────────────────────────
    r2_access_key_id: Optional[str] = Field(default=None, alias="R2_ACCESS_KEY_ID")
    r2_secret_access_key: Optional[str] = Field(default=None, alias="R2_SECRET_ACCESS_KEY")
    r2_bucket_name: str = Field(default="quantview-docs", alias="R2_BUCKET_NAME")
    r2_endpoint: Optional[str] = Field(default=None, alias="R2_ENDPOINT")

    # ── AI Model Server (IIT GPU Server) ───────────────────────────
    ai_server_url: str = Field(default="http://10.250.101.68:11434/api/generate", alias="AI_SERVER_URL")
    llm_provider: str = Field(default="ollama", alias="LLM_PROVIDER")
    llm_reasoning_model: str = "qwen2.5:7b"
    llm_extraction_model: str = "qwen2.5:7b"
    embedding_model: str = "BAAI/bge-large-en-v1.5"

    # ── Celery ───────────────────────────────────────────────────
    celery_broker_url: str = Field(default="redis://10.250.101.68:6379/0", alias="CELERY_BROKER_URL")
    celery_result_backend: str = Field(
        default="redis://10.250.101.68:6379/1", alias="CELERY_RESULT_BACKEND"
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
