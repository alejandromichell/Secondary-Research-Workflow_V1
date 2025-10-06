"""
Cache Manager for the Secondary Research Workflow System.

This module provides caching functionality to improve performance and reduce
external API calls by storing frequently accessed data.
"""

import json
import os
import time
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union
import hashlib
import pickle
from pathlib import Path


class CacheManager:
    """
    Manages caching for the research workflow system.
    
    Features:
    - TTL (Time To Live) based expiration
    - File-based storage with JSON serialization
    - Memory cache for frequently accessed items
    - Automatic cleanup of expired entries
    - Cache statistics and monitoring
    """
    
    def __init__(self, cache_dir: str = "cache", default_ttl: int = 3600):
        """
        Initialize the cache manager.
        
        Args:
            cache_dir: Directory to store cache files
            default_ttl: Default time-to-live in seconds (1 hour)
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.default_ttl = default_ttl
        self.memory_cache: Dict[str, Dict[str, Any]] = {}
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0,
            "expired": 0
        }
        print(f">>> CacheManager: Initialized with cache directory: {self.cache_dir}")
    
    def _generate_key(self, key: str) -> str:
        """Generate a cache key with hash for consistent naming."""
        return hashlib.md5(key.encode()).hexdigest()
    
    def _get_cache_file_path(self, key: str) -> Path:
        """Get the file path for a cache key."""
        hashed_key = self._generate_key(key)
        return self.cache_dir / f"{hashed_key}.json"
    
    def _is_expired(self, cache_entry: Dict[str, Any]) -> bool:
        """Check if a cache entry has expired."""
        if "expires_at" not in cache_entry:
            return True
        
        expires_at = datetime.fromisoformat(cache_entry["expires_at"])
        return datetime.now() > expires_at
    
    def _create_cache_entry(self, value: Any, ttl: Optional[int] = None) -> Dict[str, Any]:
        """Create a cache entry with metadata."""
        if ttl is None:
            ttl = self.default_ttl
        
        expires_at = datetime.now() + timedelta(seconds=ttl)
        
        return {
            "value": value,
            "created_at": datetime.now().isoformat(),
            "expires_at": expires_at.isoformat(),
            "ttl": ttl
        }
    
    def get(self, key: str, use_memory: bool = True) -> Optional[Any]:
        """
        Get a value from the cache.
        
        Args:
            key: Cache key
            use_memory: Whether to check memory cache first
            
        Returns:
            Cached value or None if not found/expired
        """
        # Check memory cache first if enabled
        if use_memory and key in self.memory_cache:
            entry = self.memory_cache[key]
            if not self._is_expired(entry):
                self.cache_stats["hits"] += 1
                return entry["value"]
            else:
                # Remove expired entry from memory
                del self.memory_cache[key]
                self.cache_stats["expired"] += 1
        
        # Check file cache
        cache_file = self._get_cache_file_path(key)
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    entry = json.load(f)
                
                if not self._is_expired(entry):
                    # Store in memory cache for faster access
                    if use_memory:
                        self.memory_cache[key] = entry
                    
                    self.cache_stats["hits"] += 1
                    return entry["value"]
                else:
                    # Remove expired file
                    cache_file.unlink()
                    self.cache_stats["expired"] += 1
            except (json.JSONDecodeError, KeyError, FileNotFoundError):
                # Remove corrupted cache file
                if cache_file.exists():
                    cache_file.unlink()
        
        self.cache_stats["misses"] += 1
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None, use_memory: bool = True) -> bool:
        """
        Set a value in the cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds
            use_memory: Whether to store in memory cache
            
        Returns:
            True if successful, False otherwise
        """
        try:
            entry = self._create_cache_entry(value, ttl)
            
            # Store in file cache
            cache_file = self._get_cache_file_path(key)
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(entry, f, indent=2, default=str)
            
            # Store in memory cache if enabled
            if use_memory:
                self.memory_cache[key] = entry
            
            self.cache_stats["sets"] += 1
            return True
            
        except Exception as e:
            print(f">>> CacheManager: Error setting cache for key '{key}': {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """
        Delete a value from the cache.
        
        Args:
            key: Cache key to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Remove from memory cache
            if key in self.memory_cache:
                del self.memory_cache[key]
            
            # Remove from file cache
            cache_file = self._get_cache_file_path(key)
            if cache_file.exists():
                cache_file.unlink()
            
            self.cache_stats["deletes"] += 1
            return True
            
        except Exception as e:
            print(f">>> CacheManager: Error deleting cache for key '{key}': {e}")
            return False
    
    def clear(self, expired_only: bool = False) -> int:
        """
        Clear cache entries.
        
        Args:
            expired_only: If True, only clear expired entries
            
        Returns:
            Number of entries cleared
        """
        cleared_count = 0
        
        # Clear memory cache
        if expired_only:
            expired_keys = [
                key for key, entry in self.memory_cache.items()
                if self._is_expired(entry)
            ]
            for key in expired_keys:
                del self.memory_cache[key]
                cleared_count += 1
        else:
            self.memory_cache.clear()
            cleared_count += len(self.memory_cache)
        
        # Clear file cache
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                if expired_only:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        entry = json.load(f)
                    if not self._is_expired(entry):
                        continue
                
                cache_file.unlink()
                cleared_count += 1
                
            except (json.JSONDecodeError, KeyError, FileNotFoundError):
                # Remove corrupted cache file
                cache_file.unlink()
                cleared_count += 1
        
        return cleared_count
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self.cache_stats["hits"] + self.cache_stats["misses"]
        hit_rate = (self.cache_stats["hits"] / total_requests * 100) if total_requests > 0 else 0
        
        # Count active cache files
        active_files = len(list(self.cache_dir.glob("*.json")))
        
        return {
            **self.cache_stats,
            "hit_rate_percent": round(hit_rate, 2),
            "memory_cache_size": len(self.memory_cache),
            "file_cache_size": active_files,
            "total_cache_size": len(self.memory_cache) + active_files
        }
    
    def cleanup_expired(self) -> int:
        """Clean up expired cache entries."""
        return self.clear(expired_only=True)
    
    def get_cache_info(self, key: str) -> Optional[Dict[str, Any]]:
        """Get information about a cache entry without returning the value."""
        # Check memory cache first
        if key in self.memory_cache:
            entry = self.memory_cache[key]
            return {
                "key": key,
                "created_at": entry.get("created_at"),
                "expires_at": entry.get("expires_at"),
                "ttl": entry.get("ttl"),
                "expired": self._is_expired(entry),
                "location": "memory"
            }
        
        # Check file cache
        cache_file = self._get_cache_file_path(key)
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    entry = json.load(f)
                
                return {
                    "key": key,
                    "created_at": entry.get("created_at"),
                    "expires_at": entry.get("expires_at"),
                    "ttl": entry.get("ttl"),
                    "expired": self._is_expired(entry),
                    "location": "file",
                    "file_size": cache_file.stat().st_size
                }
            except (json.JSONDecodeError, KeyError, FileNotFoundError):
                pass
        
        return None


# Global cache manager instance
cache_manager = CacheManager()


def get_cache_manager() -> CacheManager:
    """Get the global cache manager instance."""
    return cache_manager


# Decorator for caching function results
def cached(ttl: int = 3600, key_prefix: str = ""):
    """
    Decorator to cache function results.
    
    Args:
        ttl: Time-to-live in seconds
        key_prefix: Prefix for cache key
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            cache_key = f"{key_prefix}{func.__name__}_{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Try to get from cache
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result, ttl)
            return result
        
        return wrapper
    return decorator


# Async version of the cached decorator
def async_cached(ttl: int = 3600, key_prefix: str = ""):
    """
    Decorator to cache async function results.
    
    Args:
        ttl: Time-to-live in seconds
        key_prefix: Prefix for cache key
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            cache_key = f"{key_prefix}{func.__name__}_{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Try to get from cache
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            cache_manager.set(cache_key, result, ttl)
            return result
        
        return wrapper
    return decorator
