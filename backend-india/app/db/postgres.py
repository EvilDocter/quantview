"""
QuantView — PostgreSQL Database Connection

Async SQLAlchemy engine and session management for Neon PostgreSQL.
"""

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import create_engine
from app.config import get_settings

settings = get_settings()

from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode

def clean_async_db_url(url: str) -> str:
    """Removes sslmode parameter from database URL since asyncpg does not support it."""
    if not url:
        return url
    parsed = urlparse(url)
    # Remove sslmode from query parameters
    query_params = dict(parse_qsl(parsed.query))
    query_params.pop("sslmode", None)
    
    # Reconstruct the URL without sslmode
    new_query = urlencode(query_params)
    return urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        new_query,
        parsed.fragment
    ))

db_url = clean_async_db_url(settings.database_url)

# ── Async Engine (for FastAPI request handling) ──────────────────
async_engine = create_async_engine(
    db_url,
    echo=settings.app_env == "development",
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    connect_args={"ssl": True} if "localhost" not in db_url and "127.0.0.1" not in db_url else {}
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# ── Sync Engine (for Alembic migrations & Celery tasks) ─────────
sync_engine = create_engine(
    settings.database_url_sync,
    echo=False,
    pool_pre_ping=True,
)


# ── Base Model ───────────────────────────────────────────────────
class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


# ── Dependency Injection ─────────────────────────────────────────
async def get_db() -> AsyncSession:
    """FastAPI dependency that provides an async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
