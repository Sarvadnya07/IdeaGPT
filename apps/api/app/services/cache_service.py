import hashlib
import json
import logging
from typing import Optional, Dict, Any
import redis
import os

logger = logging.getLogger(__name__)

class EvaluationCacheManager:
    def __init__(self):
        self.redis_url = os.getenv("REDIS_URL")
        self.redis_client = None
        self.local_cache: Dict[str, str] = {}  # In-memory fallback
        
        if self.redis_url:
            try:
                self.redis_client = redis.from_url(self.redis_url, socket_timeout=2)
                # Test connection
                self.redis_client.ping()
                logger.info("Evaluation cache connected to Redis.")
            except Exception as e:
                logger.warning(f"Redis cache connection failed: {e}. Falling back to in-memory cache.")
                self.redis_client = None

    def _generate_key(self, idea_text: str, prompt_version: str, model: str, provider: str) -> str:
        """
        Creates a deterministic hash key.
        """
        idea_hash = hashlib.sha256(idea_text.encode("utf-8")).hexdigest()
        raw_key = f"eval:{prompt_version}:{provider}:{model}:{idea_hash}"
        return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

    def get(self, idea_text: str, prompt_version: str, model: str, provider: str) -> Optional[dict]:
        """
        Retrieves cached evaluation if it exists.
        """
        key = self._generate_key(idea_text, prompt_version, model, provider)
        
        if self.redis_client:
            try:
                cached_val = self.redis_client.get(key)
                if cached_val:
                    logger.info("Evaluation cache hit (Redis).")
                    return json.loads(cached_val.decode("utf-8"))
            except Exception as e:
                logger.warning(f"Redis get failed: {e}")
                
        # Local fallback
        if key in self.local_cache:
            logger.info("Evaluation cache hit (In-Memory).")
            return json.loads(self.local_cache[key])
            
        return None

    def set(self, idea_text: str, prompt_version: str, model: str, provider: str, result_payload: dict, expire_seconds: int = 86400):
        """
        Stores evaluation result in cache.
        """
        key = self._generate_key(idea_text, prompt_version, model, provider)
        serialized = json.dumps(result_payload)
        
        if self.redis_client:
            try:
                self.redis_client.set(key, serialized, ex=expire_seconds)
                logger.info("Evaluation cached successfully (Redis).")
                return
            except Exception as e:
                logger.warning(f"Redis set failed: {e}")

        # Local fallback
        self.local_cache[key] = serialized
        logger.info("Evaluation cached successfully (In-Memory).")

# Global cache instance
evaluation_cache = EvaluationCacheManager()
