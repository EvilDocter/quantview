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

# ── Async Engine (for FastAPI request handling) ──────────────────
async_engine = create_async_engine(
    settings.database_url,
    echo=settings.app_env == "development",
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
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
