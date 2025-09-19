"""
Caching service for market data to reduce government API calls.
Implements in-memory caching with TTL and request deduplication.
"""

import asyncio
import json
import time
from typing import Dict, Any, Optional, Callable
from datetime import datetime, timedelta
from functools import wraps
import hashlib
import logging

logger = logging.getLogger(__name__)


class MarketDataCache:
    """
    In-memory cache for market data with TTL and request deduplication.
    """
    
    def __init__(self):
        """Initialize the cache."""
        self._cache = {}
        self._pending_requests = {}
        self._default_ttl = 900  # 15 minutes for market data
        self._weather_ttl = 3600  # 1 hour for weather data
        self._analytics_ttl = 1800  # 30 minutes for analytics
        
    def _generate_cache_key(self, *args, **kwargs) -> str:
        """Generate a unique cache key from arguments."""
        key_data = f"{args}_{sorted(kwargs.items())}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _is_expired(self, cache_entry: Dict[str, Any]) -> bool:
        """Check if cache entry is expired."""
        return time.time() > cache_entry['expires_at']
    
    def _get_ttl_for_data_type(self, data_type: str) -> int:
        """Get TTL based on data type."""
        ttl_map = {
            'market': self._default_ttl,
            'weather': self._weather_ttl,
            'analytics': self._analytics_ttl,
            'government': self._default_ttl,
            'agmarknet': self._default_ttl
        }
        return ttl_map.get(data_type, self._default_ttl)
    
    async def get_or_set(self, 
                        key: str, 
                        fetch_func: Callable, 
                        ttl: Optional[int] = None,
                        data_type: str = 'market',
                        *args, **kwargs) -> Any:
        """
        Get from cache or fetch and cache the result.
        Implements request deduplication for concurrent requests.
        """
        cache_key = self._generate_cache_key(key, *args, **kwargs)
        
        # Check if data exists in cache and is not expired
        if cache_key in self._cache:
            cache_entry = self._cache[cache_key]
            if not self._is_expired(cache_entry):
                logger.info(f"Cache HIT for key: {key}")
                return cache_entry['data']
            else:
                # Remove expired entry
                del self._cache[cache_key]
                logger.info(f"Cache EXPIRED for key: {key}")
        
        # Check if the same request is already in progress
        if cache_key in self._pending_requests:
            logger.info(f"Request DEDUPLICATION for key: {key}")
            return await self._pending_requests[cache_key]
        
        # Create a future for this request to handle concurrent requests
        future = asyncio.Future()
        self._pending_requests[cache_key] = future
        
        try:
            logger.info(f"Cache MISS for key: {key} - Fetching fresh data")
            
            # Fetch fresh data
            data = await fetch_func(*args, **kwargs)
            
            # Cache the result
            if ttl is None:
                ttl = self._get_ttl_for_data_type(data_type)
            
            self._cache[cache_key] = {
                'data': data,
                'created_at': time.time(),
                'expires_at': time.time() + ttl,
                'ttl': ttl,
                'key': key
            }
            
            # Resolve the future
            future.set_result(data)
            return data
            
        except Exception as e:
            # If fetch fails, set exception on future
            future.set_exception(e)
            raise
        finally:
            # Clean up pending request
            if cache_key in self._pending_requests:
                del self._pending_requests[cache_key]
    
    def invalidate(self, pattern: str = None) -> int:
        """
        Invalidate cache entries.
        
        Args:
            pattern: If provided, only invalidate keys containing this pattern
            
        Returns:
            Number of entries invalidated
        """
        if pattern is None:
            count = len(self._cache)
            self._cache.clear()
            logger.info(f"Invalidated all {count} cache entries")
            return count
        
        keys_to_remove = [
            key for key in self._cache.keys() 
            if pattern in self._cache[key].get('key', '')
        ]
        
        for key in keys_to_remove:
            del self._cache[key]
        
        logger.info(f"Invalidated {len(keys_to_remove)} cache entries matching pattern: {pattern}")
        return len(keys_to_remove)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        now = time.time()
        total_entries = len(self._cache)
        expired_entries = sum(1 for entry in self._cache.values() if entry['expires_at'] < now)
        active_entries = total_entries - expired_entries
        
        return {
            'total_entries': total_entries,
            'active_entries': active_entries,
            'expired_entries': expired_entries,
            'pending_requests': len(self._pending_requests),
            'cache_hit_ratio': getattr(self, '_hit_ratio', 0.0)
        }
    
    def cleanup_expired(self) -> int:
        """Remove expired entries from cache."""
        now = time.time()
        expired_keys = [
            key for key, entry in self._cache.items() 
            if entry['expires_at'] < now
        ]
        
        for key in expired_keys:
            del self._cache[key]
        
        logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
        return len(expired_keys)


# Global cache instance
market_cache = MarketDataCache()


def cached_market_data(ttl: int = None, data_type: str = 'market'):
    """
    Decorator for caching market data fetching functions.
    
    Args:
        ttl: Time to live in seconds
        data_type: Type of data for TTL selection
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            cache_key = f"{func.__name__}_{hash(str(args) + str(sorted(kwargs.items())))}"
            
            return await market_cache.get_or_set(
                key=cache_key,
                fetch_func=func,
                ttl=ttl,
                data_type=data_type,
                *args,
                **kwargs
            )
        return wrapper
    return decorator


async def warm_cache_for_districts(districts: list, market_service):
    """
    Warm up cache for frequently accessed districts.
    
    Args:
        districts: List of district names
        market_service: Market service instance
    """
    logger.info(f"Warming cache for {len(districts)} districts")
    
    tasks = []
    for district in districts:
        # Cache market data for each district
        task = market_service.get_mandi_prices(district)
        tasks.append(task)
    
    try:
        await asyncio.gather(*tasks, return_exceptions=True)
        logger.info("Cache warming completed")
    except Exception as e:
        logger.error(f"Error during cache warming: {e}")


# Cleanup task to remove expired entries periodically
async def periodic_cache_cleanup():
    """Periodic task to clean up expired cache entries."""
    while True:
        try:
            await asyncio.sleep(300)  # Run every 5 minutes
            market_cache.cleanup_expired()
        except Exception as e:
            logger.error(f"Error in periodic cache cleanup: {e}")