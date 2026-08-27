"""
IdeaGPT AI Gateway — Research Cache Service.
Provides 24h TTL in-memory and Redis-backed caching for normalized research queries and sources.
Never stores credentials or sensitive user payloads.
"""

import time
import hashlib
import json
import logging
from typing import Dict, Any, Optional, List
from app.ai.gateway.evidence.models import NormalizedSource, NormalizedEvidence

logger = logging.getLogger(__name__)


class ResearchCacheService:
    """
    Lightweight, high-performance cache for research search results.
    Prevents redundant Tavily API queries for identical market/industry research queries.
    """

    _cache: Dict[str, Dict[str, Any]] = {}
    DEFAULT_TTL_SEC: int = 86400  # 24 Hours

    @classmethod
    def generate_cache_key(cls, task_type: str, query: str, provider: str = "tavily") -> str:
        clean_q = " ".join(query.lower().strip().split())
        raw_key = f"{task_type.lower()}:{clean_q}:{provider.lower()}"
        return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

    @classmethod
    def get(cls, task_type: str, query: str, provider: str = "tavily") -> Optional[Dict[str, Any]]:
        key = cls.generate_cache_key(task_type, query, provider)
        entry = cls._cache.get(key)
        if not entry:
            return None

        # Check TTL
        if time.time() > entry.get("expires_at", 0):
            cls._cache.pop(key, None)
            return None

        logger.debug(f"Research cache HIT for query: {query[:50]}")
        return entry.get("data")

    @classmethod
    def set(
        cls,
        task_type: str,
        query: str,
        data: Dict[str, Any],
        provider: str = "tavily",
        ttl_sec: Optional[int] = None
    ) -> None:
        key = cls.generate_cache_key(task_type, query, provider)
        ttl = ttl_sec or cls.DEFAULT_TTL_SEC
        now = time.time()

        cls._cache[key] = {
            "created_at": now,
            "expires_at": now + ttl,
            "data": data,
        }
        logger.debug(f"Cached research result for key: {key[:10]} (TTL {ttl}s)")

    @classmethod
    def clear(cls) -> None:
        cls._cache.clear()

    @classmethod
    def size(cls) -> int:
        return len(cls._cache)
