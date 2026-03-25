from functools import wraps
from typing import Optional, Any
import json
import hashlib
from datetime import timedelta
import asyncio

# In-memory cache (production mein Redis use karein)
_cache = {}
_cache_expiry = {}

class CacheManager:
    """Simple in-memory cache manager"""
    
    @staticmethod
    def _generate_key(prefix: str, *args, **kwargs) -> str:
        """Generate cache key from function arguments"""
        key_data = f"{prefix}:{str(args)}:{str(sorted(kwargs.items()))}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    @staticmethod
    async def get(key: str) -> Optional[Any]:
        """Get value from cache"""
        if key in _cache:
            # Check expiry
            if key in _cache_expiry:
                import time
                if time.time() > _cache_expiry[key]:
                    del _cache[key]
                    del _cache_expiry[key]
                    return None
            return _cache[key]
        return None
    
    @staticmethod
    async def set(key: str, value: Any, ttl: int = 300):
        """Set value in cache with TTL (seconds)"""
        _cache[key] = value
        if ttl:
            import time
            _cache_expiry[key] = time.time() + ttl
    
    @staticmethod
    async def delete(key: str):
        """Delete key from cache"""
        _cache.pop(key, None)
        _cache_expiry.pop(key, None)
    
    @staticmethod
    async def clear():
        """Clear all cache"""
        _cache.clear()
        _cache_expiry.clear()

def cache_result(prefix: str, ttl: int = 300):
    """Decorator to cache function results"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = CacheManager._generate_key(prefix, *args, **kwargs)
            
            # Try to get from cache
            cached = await CacheManager.get(cache_key)
            if cached is not None:
                return cached
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Store in cache
            await CacheManager.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator

# Cache invalidation helpers
async def invalidate_course_cache(course_id: str = None):
    """Invalidate course-related caches"""
    # Clear all course caches when any course is modified
    keys_to_delete = [k for k in _cache.keys() if 'course' in k.lower()]
    for key in keys_to_delete:
        await CacheManager.delete(key)

async def invalidate_category_cache():
    """Invalidate category caches"""
    keys_to_delete = [k for k in _cache.keys() if 'category' in k.lower()]
    for key in keys_to_delete:
        await CacheManager.delete(key)
