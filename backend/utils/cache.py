"""Caching utilities"""
import redis
import json
from typing import Any, Optional

class CacheManager:
    """Manages caching operations"""
    
    def __init__(self, redis_url: str):
        self.redis_client = redis.from_url(redis_url)
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached value"""
        value = self.redis_client.get(key)
        if value:
            return json.loads(value)
        return None
    
    def set(self, key: str, value: Any, ttl: int = 3600):
        """Set cached value"""
        self.redis_client.setex(key, ttl, json.dumps(value))
    
    def delete(self, key: str):
        """Delete cached value"""
        self.redis_client.delete(key)
