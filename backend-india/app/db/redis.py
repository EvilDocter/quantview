"""
QuantView — Redis Cache Connection

Client for Upstash free tier — handles caching, session storage,
and serves as Celery broker.
"""

import json
import redis.asyncio as aioredis
from typing import Optional, Any
from app.config import get_settings

settings = get_settings()

# ── Redis Client ─────────────────────────────────────────────────
_redis_client: Optional[aioredis.Redis] = None


async def get_redis() -> aioredis.Redis:
    """Get or create the async Redis client."""
    global _redis_client
    if _redis_client is None:
        _redis_client = aioredis.from_url(
            settings.redis_url,
            decode_responses=True,
            socket_timeout=10,
            retry_on_timeout=True,
        )
    return _redis_client


async def close_redis():
    """Close the Redis connection."""
    global _redis_client
    if _redis_client is not None:
        await _redis_client.close()
        _redis_client = None


# ── Cache Helpers ────────────────────────────────────────────────


async def cache_get(key: str) -> Optional[Any]:
    """Get a cached value, auto-deserializing JSON."""
    r = await get_redis()
    value = await r.get(key)
    if value is None:
        return None
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return value


async def cache_set(key: str, value: Any, ttl: int = 3600):
    """
    Set a cache value with TTL (default: 1 hour).
    Automatically serializes dicts/lists to JSON.
    """
    r = await get_redis()
    if isinstance(value, (dict, list)):
        value = json.dumps(value, default=str)
    await r.set(key, value, ex=ttl)


async def cache_delete(key: str):
    """Delete a cached value."""
    r = await get_redis()
    await r.delete(key)


async def cache_get_or_set(key: str, factory, ttl: int = 3600) -> Any:
    """
    Get from cache or compute via factory function and cache the result.
    Factory can be async.
    """
    cached = await cache_get(key)
    if cached is not None:
        return cached

    import asyncio

    if asyncio.iscoroutinefunction(factory):
        value = await factory()
    else:
        value = factory()

    await cache_set(key, value, ttl=ttl)
    return value


# ── Cache Key Builders ───────────────────────────────────────────


def company_cache_key(symbol: str) -> str:
    return f"india:company:{symbol}"


def market_overview_cache_key() -> str:
    return "india:market:overview"


def ai_response_cache_key(query_hash: str) -> str:
    return f"india:ai:response:{query_hash}"


def daily_intelligence_cache_key() -> str:
    return "india:ai:daily_intelligence"


def company_scores_cache_key(symbol: str) -> str:
    return f"india:scores:{symbol}"
