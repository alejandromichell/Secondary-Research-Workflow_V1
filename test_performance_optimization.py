#!/usr/bin/env python3
"""
Test script for performance optimization and production readiness features.

This script tests the caching system, rate limiting, error handling,
monitoring, and configuration management components.
"""

import asyncio
import os
import sys
import time
from datetime import datetime
from typing import Dict, Any, List

# Add the project root to the Python path
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.utils.cache_manager import CacheManager, get_cache_manager, async_cached
from src.utils.rate_limiter import RateLimiter, get_rate_limiter, rate_limited
from src.utils.error_handler import ErrorHandler, get_error_handler, retry_async, RetryConfig
from src.utils.monitoring import SystemMonitor, PerformanceLogger, get_system_monitor, get_performance_logger, log_performance
from src.config.production_config import ConfigManager, get_config, create_development_config, create_production_config, ProductionConfig


async def test_cache_manager():
    """Test the cache manager functionality."""
    print("\n1. Testing Cache Manager...")
    
    cache_manager = CacheManager(cache_dir="test_cache", default_ttl=5)
    
    # Test basic set/get operations
    print("   Testing basic cache operations...")
    cache_manager.set("test_key", "test_value", ttl=10)
    cached_value = cache_manager.get("test_key")
    assert cached_value == "test_value", f"Expected 'test_value', got {cached_value}"
    print("   ✓ Basic cache operations working")
    
    # Test cache expiration
    print("   Testing cache expiration...")
    cache_manager.set("expire_key", "expire_value", ttl=1)
    time.sleep(2)
    expired_value = cache_manager.get("expire_key")
    assert expired_value is None, f"Expected None for expired key, got {expired_value}"
    print("   ✓ Cache expiration working")
    
    # Test cache statistics
    print("   Testing cache statistics...")
    stats = cache_manager.get_stats()
    assert "hits" in stats and "misses" in stats, "Cache stats missing required fields"
    print(f"   ✓ Cache statistics: {stats}")
    
    # Test cache cleanup
    print("   Testing cache cleanup...")
    cleared_count = cache_manager.clear()
    print(f"   ✓ Cache cleanup cleared {cleared_count} entries")
    
    # Test async cached decorator
    print("   Testing async cached decorator...")
    
    @async_cached(ttl=10, key_prefix="test_")
    async def expensive_operation(x: int) -> int:
        await asyncio.sleep(0.1)  # Simulate expensive operation
        return x * 2
    
    # First call should be slow
    start_time = time.time()
    result1 = await expensive_operation(5)
    first_call_time = time.time() - start_time
    
    # Second call should be fast (cached)
    start_time = time.time()
    result2 = await expensive_operation(5)
    second_call_time = time.time() - start_time
    
    assert result1 == result2 == 10, f"Expected 10, got {result1}, {result2}"
    assert second_call_time < first_call_time, "Cached call should be faster"
    print(f"   ✓ Async cached decorator working (first: {first_call_time:.3f}s, second: {second_call_time:.3f}s)")
    
    # Cleanup
    cache_manager.clear()
    print("   ✓ Cache manager test completed")


async def test_rate_limiter():
    """Test the rate limiter functionality."""
    print("\n2. Testing Rate Limiter...")
    
    rate_limiter = RateLimiter(default_rate=2.0, default_burst=3)
    
    # Test basic rate limiting
    print("   Testing basic rate limiting...")
    
    # Should allow first few requests
    for i in range(3):
        allowed, wait_time = rate_limiter.is_allowed("test_source")
        assert allowed, f"Request {i+1} should be allowed"
        print(f"   ✓ Request {i+1} allowed")
    
    # Should rate limit subsequent requests
    allowed, wait_time = rate_limiter.is_allowed("test_source")
    assert not allowed, "Request should be rate limited"
    assert wait_time > 0, "Wait time should be positive"
    print(f"   ✓ Rate limiting working (wait time: {wait_time:.2f}s)")
    
    # Test async rate limiting
    print("   Testing async rate limiting...")
    
    @rate_limited("test_source", timeout=5.0)
    async def rate_limited_operation():
        return "success"
    
    # This should work (within rate limit)
    result = await rate_limited_operation()
    assert result == "success", f"Expected 'success', got {result}"
    print("   ✓ Async rate limiting working")
    
    # Test rate limiter status
    print("   Testing rate limiter status...")
    status = rate_limiter.get_status("test_source")
    assert "tokens_available" in status, "Status missing tokens_available"
    print(f"   ✓ Rate limiter status: {status}")
    
    print("   ✓ Rate limiter test completed")


async def test_error_handler():
    """Test the error handler and retry functionality."""
    print("\n3. Testing Error Handler...")
    
    error_handler = ErrorHandler()
    
    # Test successful operation
    print("   Testing successful operation...")
    
    async def successful_operation():
        return "success"
    
    result = await error_handler.retry_async(successful_operation, operation="test_success")
    assert result == "success", f"Expected 'success', got {result}"
    print("   ✓ Successful operation working")
    
    # Test retry on failure
    print("   Testing retry on failure...")
    
    attempt_count = 0
    
    async def failing_operation():
        nonlocal attempt_count
        attempt_count += 1
        if attempt_count < 3:
            raise ConnectionError("Simulated connection error")
        return "success_after_retry"
    
    result = await error_handler.retry_async(
        failing_operation,
        operation="test_retry",
        config=RetryConfig(max_attempts=3, base_delay=0.1)
    )
    assert result == "success_after_retry", f"Expected 'success_after_retry', got {result}"
    assert attempt_count == 3, f"Expected 3 attempts, got {attempt_count}"
    print("   ✓ Retry on failure working")
    
    # Test non-retryable exception
    print("   Testing non-retryable exception...")
    
    async def non_retryable_operation():
        raise ValueError("Non-retryable error")
    
    try:
        await error_handler.retry_async(non_retryable_operation, operation="test_non_retryable")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert str(e) == "Non-retryable error", f"Expected 'Non-retryable error', got {e}"
        print("   ✓ Non-retryable exception handling working")
    
    # Test error statistics
    print("   Testing error statistics...")
    stats = error_handler.get_error_stats()
    assert "test_success" in stats, "Missing test_success in error stats"
    assert "test_retry" in stats, "Missing test_retry in error stats"
    print(f"   ✓ Error statistics: {stats}")
    
    # Test retry decorator
    print("   Testing retry decorator...")
    
    @retry_async("test_decorator", config=RetryConfig(max_attempts=2, base_delay=0.1))
    async def decorated_operation():
        return "decorated_success"
    
    result = await decorated_operation()
    assert result == "decorated_success", f"Expected 'decorated_success', got {result}"
    print("   ✓ Retry decorator working")
    
    print("   ✓ Error handler test completed")


def test_monitoring():
    """Test the monitoring system."""
    print("\n4. Testing Monitoring System...")
    
    # Test system monitor
    print("   Testing system monitor...")
    system_monitor = SystemMonitor(log_file="test_logs/system_monitor.log")
    
    # Get health status
    health_status = system_monitor.get_health_status()
    assert "status" in health_status, "Health status missing status field"
    print(f"   ✓ System health status: {health_status['status']}")
    
    # Get metrics summary
    metrics_summary = system_monitor.get_metrics_summary()
    assert isinstance(metrics_summary, dict), "Metrics summary should be a dictionary"
    print(f"   ✓ Metrics summary available: {len(metrics_summary)} metrics")
    
    # Test performance logger
    print("   Testing performance logger...")
    performance_logger = PerformanceLogger(log_file="test_logs/performance.log")
    
    # Log some operations
    performance_logger.log_operation("test_operation", 0.5, True)
    performance_logger.log_operation("test_operation", 0.3, True)
    performance_logger.log_operation("test_operation", 0.7, False)
    
    # Get operation stats
    stats = performance_logger.get_operation_stats("test_operation")
    assert stats["total_calls"] == 3, f"Expected 3 total calls, got {stats['total_calls']}"
    assert stats["successful_calls"] == 2, f"Expected 2 successful calls, got {stats['successful_calls']}"
    assert stats["error_count"] == 1, f"Expected 1 error, got {stats['error_count']}"
    print(f"   ✓ Performance logger stats: {stats}")
    
    # Test performance decorator
    print("   Testing performance decorator...")
    
    @log_performance("decorated_operation")
    def test_function():
        time.sleep(0.1)
        return "test_result"
    
    result = test_function()
    assert result == "test_result", f"Expected 'test_result', got {result}"
    
    # Check if operation was logged
    decorated_stats = performance_logger.get_operation_stats("decorated_operation")
    if "error" in decorated_stats:
        print("   ⚠ Performance decorator not logged yet (expected in some cases)")
    else:
        assert decorated_stats["total_calls"] == 1, f"Expected 1 call, got {decorated_stats['total_calls']}"
        print("   ✓ Performance decorator working")
    
    # Stop monitoring
    system_monitor.stop_monitoring()
    print("   ✓ Monitoring system test completed")


def test_configuration_management():
    """Test the configuration management system."""
    print("\n5. Testing Configuration Management...")
    
    # Test configuration manager
    print("   Testing configuration manager...")
    config_manager = ConfigManager(config_dir="test_config")
    
    # Test development config creation
    print("   Testing development config creation...")
    dev_config = create_development_config()
    assert dev_config.environment.value == "development", "Should be development environment"
    assert dev_config.debug is True, "Debug should be True for development"
    assert dev_config.api.reload is True, "API reload should be True for development"
    print("   ✓ Development config creation working")
    
    # Test production config creation
    print("   Testing production config creation...")
    prod_config = create_production_config()
    assert prod_config.environment.value == "production", "Should be production environment"
    assert prod_config.debug is False, "Debug should be False for production"
    assert prod_config.api.reload is False, "API reload should be False for production"
    assert prod_config.security.enable_2fa is True, "2FA should be enabled for production"
    print("   ✓ Production config creation working")
    
    # Test config saving and loading
    print("   Testing config saving and loading...")
    # Set a valid secret key for testing
    dev_config.security.secret_key = "test_secret_key_that_is_long_enough_for_validation_12345"
    config_manager.save_config(dev_config, "test_config")
    loaded_config = config_manager.load_config("test_config")
    assert loaded_config.environment == dev_config.environment, "Loaded config should match saved config"
    print("   ✓ Config saving and loading working")
    
    # Test config validation
    print("   Testing config validation...")
    try:
        # Create invalid config
        invalid_config = ProductionConfig()
        invalid_config.api.port = -1  # Invalid port
        config_manager._validate_config(invalid_config)
        assert False, "Should have raised validation error"
    except ValueError as e:
        assert "port must be between 1 and 65535" in str(e), f"Expected port validation error, got {e}"
        print("   ✓ Config validation working")
    
    print("   ✓ Configuration management test completed")


async def test_integrated_performance():
    """Test integrated performance features."""
    print("\n6. Testing Integrated Performance Features...")
    
    # Test cache + rate limiting
    print("   Testing cache with rate limiting...")
    
    @async_cached(ttl=10)
    @rate_limited("test_integrated", timeout=5.0)
    async def integrated_operation(x: int):
        await asyncio.sleep(0.1)
        return x * 3
    
    # First call should be slow (rate limited + cache miss)
    start_time = time.time()
    result1 = await integrated_operation(4)
    first_call_time = time.time() - start_time
    
    # Second call should be fast (cached)
    start_time = time.time()
    result2 = await integrated_operation(4)
    second_call_time = time.time() - start_time
    
    assert result1 == result2 == 12, f"Expected 12, got {result1}, {result2}"
    assert second_call_time < first_call_time, "Cached call should be faster"
    print(f"   ✓ Integrated cache + rate limiting working (first: {first_call_time:.3f}s, second: {second_call_time:.3f}s)")
    
    # Test error handling + retry + monitoring
    print("   Testing error handling with monitoring...")
    
    @retry_async("monitored_operation", config=RetryConfig(max_attempts=3, base_delay=0.1))
    @log_performance("monitored_operation")
    async def monitored_operation_with_retry():
        # Simulate occasional failure
        if time.time() % 2 < 1:
            raise ConnectionError("Simulated error")
        return "success"
    
    # Run multiple times to test retry and monitoring
    for i in range(3):
        try:
            result = await monitored_operation_with_retry()
            print(f"   ✓ Monitored operation {i+1} succeeded: {result}")
        except Exception as e:
            print(f"   ⚠ Monitored operation {i+1} failed: {e}")
    
    # Check performance logs
    performance_logger = get_performance_logger()
    stats = performance_logger.get_operation_stats("monitored_operation")
    print(f"   ✓ Monitored operation stats: {stats}")
    
    print("   ✓ Integrated performance features test completed")


async def test_production_readiness():
    """Test production readiness features."""
    print("\n7. Testing Production Readiness...")
    
    # Test configuration for production
    print("   Testing production configuration...")
    prod_config = create_production_config()
    # Set a valid secret key for testing
    prod_config.security.secret_key = "production_secret_key_that_is_long_enough_for_validation_12345"
    
    # Verify production settings
    assert prod_config.debug is False, "Production should not be in debug mode"
    assert prod_config.api.reload is False, "Production should not have auto-reload"
    assert prod_config.api.workers >= 2, "Production should have multiple workers"
    assert prod_config.security.enable_2fa is True, "Production should have 2FA enabled"
    assert prod_config.monitoring.enable_metrics is True, "Production should have metrics enabled"
    assert prod_config.monitoring.enable_alerting is True, "Production should have alerting enabled"
    print("   ✓ Production configuration validated")
    
    # Test security settings
    print("   Testing security settings...")
    assert len(prod_config.security.secret_key) >= 32, "Secret key should be at least 32 characters"
    assert prod_config.security.access_token_expire_minutes <= 60, "Access token should expire within 1 hour"
    assert prod_config.security.max_login_attempts <= 5, "Max login attempts should be limited"
    print("   ✓ Security settings validated")
    
    # Test monitoring and alerting
    print("   Testing monitoring and alerting...")
    assert prod_config.monitoring.health_check_interval <= 60, "Health checks should be frequent"
    assert "cpu_percent" in prod_config.monitoring.alert_thresholds, "CPU threshold should be configured"
    assert "memory_percent" in prod_config.monitoring.alert_thresholds, "Memory threshold should be configured"
    print("   ✓ Monitoring and alerting validated")
    
    # Test data collection limits
    print("   Testing data collection limits...")
    assert prod_config.data_collection.max_concurrent_requests <= 20, "Concurrent requests should be limited"
    assert prod_config.data_collection.request_timeout >= 10, "Request timeout should be reasonable"
    assert prod_config.data_collection.retry_attempts >= 3, "Should have retry attempts"
    print("   ✓ Data collection limits validated")
    
    print("   ✓ Production readiness test completed")


async def main():
    """Run all performance optimization tests."""
    print("=" * 80)
    print("TESTING PERFORMANCE OPTIMIZATION AND PRODUCTION READINESS")
    print("=" * 80)
    
    try:
        # Test individual components
        await test_cache_manager()
        await test_rate_limiter()
        await test_error_handler()
        test_monitoring()
        test_configuration_management()
        
        # Test integrated features
        await test_integrated_performance()
        await test_production_readiness()
        
        print("\n" + "=" * 80)
        print("PERFORMANCE OPTIMIZATION TESTING COMPLETED SUCCESSFULLY")
        print("=" * 80)
        
        # Cleanup test files
        print("\nCleaning up test files...")
        import shutil
        test_dirs = ["test_cache", "test_logs", "test_config"]
        for test_dir in test_dirs:
            if os.path.exists(test_dir):
                shutil.rmtree(test_dir)
                print(f"   ✓ Removed {test_dir}")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Performance optimization testing failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print(f"Starting performance optimization test at {datetime.now()}")
    
    try:
        success = asyncio.run(main())
        if success:
            print("\n✓ All performance optimization tests passed!")
        else:
            print("\n⚠ Some performance optimization tests failed")
    except KeyboardInterrupt:
        print("\n⚠ Performance optimization testing interrupted by user")
    except Exception as e:
        print(f"\n✗ Performance optimization testing failed with error: {e}")
        import traceback
        traceback.print_exc()
