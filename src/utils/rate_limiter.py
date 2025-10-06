"""
Rate Limiter for the Secondary Research Workflow System.

This module provides rate limiting functionality to manage external API calls
and prevent hitting rate limits from external services.
"""

import asyncio
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
import threading


class RateLimiter:
    """
    Rate limiter implementation using token bucket algorithm.
    
    Features:
    - Token bucket algorithm for smooth rate limiting
    - Per-source rate limiting
    - Burst capacity support
    - Thread-safe operations
    - Configurable rates and burst sizes
    """
    
    def __init__(self, default_rate: float = 1.0, default_burst: int = 10):
        """
        Initialize the rate limiter.
        
        Args:
            default_rate: Default requests per second
            default_burst: Default burst capacity
        """
        self.default_rate = default_rate
        self.default_burst = default_burst
        self.buckets: Dict[str, Dict] = {}
        self.lock = threading.Lock()
        
        # Rate limit configurations for different sources
        self.source_configs = {
            "yahoo_finance": {"rate": 0.5, "burst": 5},
            "google_news": {"rate": 0.2, "burst": 3},
            "pubmed": {"rate": 0.3, "burst": 4},
            "arxiv": {"rate": 0.4, "burst": 5},
            "sec_edgar": {"rate": 0.1, "burst": 2},
            "crunchbase": {"rate": 0.2, "burst": 3},
            "reddit": {"rate": 0.1, "burst": 2},
            "linkedin": {"rate": 0.1, "burst": 2},
            "default": {"rate": default_rate, "burst": default_burst}
        }
        
        print(f">>> RateLimiter: Initialized with default rate {default_rate}/s, burst {default_burst}")
    
    def _get_bucket(self, source: str) -> Dict:
        """Get or create a token bucket for a source."""
        if source not in self.buckets:
            config = self.source_configs.get(source, self.source_configs["default"])
            self.buckets[source] = {
                "tokens": config["burst"],
                "rate": config["rate"],
                "burst": config["burst"],
                "last_update": time.time()
            }
        return self.buckets[source]
    
    def _refill_tokens(self, bucket: Dict) -> None:
        """Refill tokens based on elapsed time."""
        now = time.time()
        elapsed = now - bucket["last_update"]
        
        # Add tokens based on rate
        tokens_to_add = elapsed * bucket["rate"]
        bucket["tokens"] = min(bucket["burst"], bucket["tokens"] + tokens_to_add)
        bucket["last_update"] = now
    
    def is_allowed(self, source: str) -> Tuple[bool, float]:
        """
        Check if a request is allowed for the given source.
        
        Args:
            source: Source identifier
            
        Returns:
            Tuple of (is_allowed, wait_time_seconds)
        """
        with self.lock:
            bucket = self._get_bucket(source)
            self._refill_tokens(bucket)
            
            if bucket["tokens"] >= 1:
                bucket["tokens"] -= 1
                return True, 0.0
            else:
                # Calculate wait time until next token is available
                wait_time = (1.0 - bucket["tokens"]) / bucket["rate"]
                return False, wait_time
    
    async def wait_for_token(self, source: str, timeout: float = 30.0) -> bool:
        """
        Wait for a token to become available.
        
        Args:
            source: Source identifier
            timeout: Maximum time to wait in seconds
            
        Returns:
            True if token obtained, False if timeout
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            is_allowed, wait_time = self.is_allowed(source)
            
            if is_allowed:
                return True
            
            # Wait for the calculated time or 0.1 seconds, whichever is smaller
            sleep_time = min(wait_time, 0.1)
            await asyncio.sleep(sleep_time)
        
        return False
    
    def get_status(self, source: str) -> Dict:
        """Get rate limiter status for a source."""
        with self.lock:
            bucket = self._get_bucket(source)
            self._refill_tokens(bucket)
            
            return {
                "source": source,
                "tokens_available": bucket["tokens"],
                "rate": bucket["rate"],
                "burst": bucket["burst"],
                "utilization": (bucket["burst"] - bucket["tokens"]) / bucket["burst"] * 100
            }
    
    def get_all_status(self) -> Dict[str, Dict]:
        """Get rate limiter status for all sources."""
        with self.lock:
            status = {}
            for source in self.buckets:
                status[source] = self.get_status(source)
            return status
    
    def reset_source(self, source: str) -> None:
        """Reset rate limiter for a specific source."""
        with self.lock:
            if source in self.buckets:
                bucket = self.buckets[source]
                bucket["tokens"] = bucket["burst"]
                bucket["last_update"] = time.time()
    
    def update_source_config(self, source: str, rate: float, burst: int) -> None:
        """Update rate limiter configuration for a source."""
        with self.lock:
            self.source_configs[source] = {"rate": rate, "burst": burst}
            
            # Update existing bucket if it exists
            if source in self.buckets:
                bucket = self.buckets[source]
                bucket["rate"] = rate
                bucket["burst"] = burst
                # Don't exceed new burst limit
                bucket["tokens"] = min(bucket["tokens"], burst)


class RequestTracker:
    """
    Tracks request patterns and provides analytics.
    """
    
    def __init__(self, window_size: int = 100):
        """
        Initialize request tracker.
        
        Args:
            window_size: Number of recent requests to track
        """
        self.window_size = window_size
        self.requests: Dict[str, deque] = defaultdict(lambda: deque(maxlen=window_size))
        self.lock = threading.Lock()
    
    def record_request(self, source: str, success: bool, response_time: float) -> None:
        """Record a request."""
        with self.lock:
            self.requests[source].append({
                "timestamp": time.time(),
                "success": success,
                "response_time": response_time
            })
    
    def get_stats(self, source: str, window_minutes: int = 5) -> Dict:
        """Get request statistics for a source."""
        with self.lock:
            if source not in self.requests:
                return {
                    "source": source,
                    "total_requests": 0,
                    "success_rate": 0,
                    "avg_response_time": 0,
                    "requests_per_minute": 0
                }
            
            cutoff_time = time.time() - (window_minutes * 60)
            recent_requests = [
                req for req in self.requests[source]
                if req["timestamp"] > cutoff_time
            ]
            
            if not recent_requests:
                return {
                    "source": source,
                    "total_requests": 0,
                    "success_rate": 0,
                    "avg_response_time": 0,
                    "requests_per_minute": 0
                }
            
            total_requests = len(recent_requests)
            successful_requests = sum(1 for req in recent_requests if req["success"])
            success_rate = (successful_requests / total_requests) * 100
            avg_response_time = sum(req["response_time"] for req in recent_requests) / total_requests
            requests_per_minute = total_requests / window_minutes
            
            return {
                "source": source,
                "total_requests": total_requests,
                "success_rate": round(success_rate, 2),
                "avg_response_time": round(avg_response_time, 3),
                "requests_per_minute": round(requests_per_minute, 2)
            }
    
    def get_all_stats(self, window_minutes: int = 5) -> Dict[str, Dict]:
        """Get request statistics for all sources."""
        with self.lock:
            stats = {}
            for source in self.requests:
                stats[source] = self.get_stats(source, window_minutes)
            return stats


# Global instances
rate_limiter = RateLimiter()
request_tracker = RequestTracker()


def get_rate_limiter() -> RateLimiter:
    """Get the global rate limiter instance."""
    return rate_limiter


def get_request_tracker() -> RequestTracker:
    """Get the global request tracker instance."""
    return request_tracker


# Decorator for rate-limited requests
def rate_limited(source: str, timeout: float = 30.0):
    """
    Decorator to add rate limiting to async functions.
    
    Args:
        source: Source identifier for rate limiting
        timeout: Maximum time to wait for rate limit
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Wait for rate limit
            if not await rate_limiter.wait_for_token(source, timeout):
                raise Exception(f"Rate limit timeout for source: {source}")
            
            # Execute function and track request
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                response_time = time.time() - start_time
                request_tracker.record_request(source, True, response_time)
                return result
            except Exception as e:
                response_time = time.time() - start_time
                request_tracker.record_request(source, False, response_time)
                raise e
        
        return wrapper
    return decorator


# Context manager for rate-limited requests
class RateLimitedRequest:
    """Context manager for rate-limited requests."""
    
    def __init__(self, source: str, timeout: float = 30.0):
        self.source = source
        self.timeout = timeout
        self.start_time = None
    
    async def __aenter__(self):
        if not await rate_limiter.wait_for_token(self.source, self.timeout):
            raise Exception(f"Rate limit timeout for source: {self.source}")
        self.start_time = time.time()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            response_time = time.time() - self.start_time
            success = exc_type is None
            request_tracker.record_request(self.source, success, response_time)
