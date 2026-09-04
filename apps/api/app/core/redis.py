"""
IdeaGPT Core — Resilient Async Redis Client Provider.
Provides centralized, bounded, timeout-safe Redis connections with automatic fallback.
"""

import logging
from typing import Optional
import redis.asyncio as aioredis
from app.core.config import settings

logger = logging.getLogger(__name__)

_redis_pool: Optional[aioredis.ConnectionPool] = None


def get_redis_pool() -> Optional[aioredis.ConnectionPool]:
    """Returns the singleton Redis connection pool if REDIS_URL is configured."""
    global _redis_pool
    if not settings.REDIS_URL:
        return None

    if _redis_pool is None:
        try:
            _redis_pool = aioredis.ConnectionPool.from_url(
                settings.REDIS_URL,
                max_connections=20,
                socket_timeout=2.0,
                socket_connect_timeout=2.0,
                decode_responses=True,
            )
            logger.info("Initialized shared async Redis connection pool.")
        except Exception as e:
            logger.warning(f"Failed to initialize Redis pool: {e}. Operating in memory-fallback mode.")
            _redis_pool = None

    return _redis_pool


async def get_async_redis() -> Optional[aioredis.Redis]:
    """
    Returns an async Redis client from the shared connection pool.
    Returns None if REDIS_URL is not configured or connection fails.
    """
    pool = get_redis_pool()
    if not pool:
        return None

    try:
        client = aioredis.Redis(connection_pool=pool)
        # Fast health check ping
        await client.ping()
        return client
    except Exception as e:
        logger.debug(f"Redis connectivity unavailable: {e}. Falling back to bounded local state.")
        return None


async def close_redis_pool() -> None:
    """Gracefully closes Redis connection pool on server shutdown."""
    global _redis_pool
    if _redis_pool:
        try:
            await _redis_pool.disconnect()
            logger.info("Disconnected shared Redis connection pool.")
        except Exception as e:
            logger.warning(f"Error disconnecting Redis pool: {e}")
        _redis_pool = None
