import json
import redis
from typing import Any, Optional, Dict
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

class CacheService:
    def __init__(self, redis_url: str = "redis://redis:6379"):
        self.redis = redis.from_url(redis_url, decode_responses=True)
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached value"""
        try:
            value = self.redis.get(key)
            return json.loads(value) if value else None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set cached value with TTL in seconds"""
        try:
            return self.redis.setex(key, ttl, json.dumps(value, default=str))
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete cached value"""
        try:
            return bool(self.redis.delete(key))
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False
    
    def get_or_set(self, key: str, func, ttl: int = 3600) -> Any:
        """Get from cache or execute function and cache result"""
        cached = self.get(key)
        if cached is not None:
            return cached
        
        result = func()
        self.set(key, result, ttl)
        return result
    
    def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate all keys matching pattern"""
        try:
            keys = self.redis.keys(pattern)
            return self.redis.delete(*keys) if keys else 0
        except Exception as e:
            logger.error(f"Cache invalidate error: {e}")
            return 0

# Global cache instance
cache = CacheService()