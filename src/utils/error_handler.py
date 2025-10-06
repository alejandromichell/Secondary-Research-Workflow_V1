"""
Enhanced Error Handling and Retry Mechanisms for the Secondary Research Workflow System.

This module provides comprehensive error handling, retry logic, and resilience
patterns for the research workflow system.
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
import traceback
from functools import wraps
import random


class RetryConfig:
    """Configuration for retry behavior."""
    
    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
        retryable_exceptions: Optional[List[type]] = None
    ):
        """
        Initialize retry configuration.
        
        Args:
            max_attempts: Maximum number of retry attempts
            base_delay: Base delay between retries in seconds
            max_delay: Maximum delay between retries in seconds
            exponential_base: Base for exponential backoff
            jitter: Whether to add random jitter to delays
            retryable_exceptions: List of exception types that should be retried
        """
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
        self.retryable_exceptions = retryable_exceptions or [
            ConnectionError,
            TimeoutError,
            asyncio.TimeoutError,
            OSError
        ]


class ErrorHandler:
    """
    Comprehensive error handling and retry mechanism.
    
    Features:
    - Exponential backoff with jitter
    - Configurable retry policies
    - Circuit breaker pattern
    - Error classification and handling
    - Detailed logging and monitoring
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize error handler.
        
        Args:
            logger: Logger instance for error logging
        """
        self.logger = logger or logging.getLogger(__name__)
        self.circuit_breakers: Dict[str, Dict] = {}
        self.error_stats: Dict[str, Dict] = {}
        
        # Default retry configurations for different operations
        self.retry_configs = {
            "api_call": RetryConfig(
                max_attempts=3,
                base_delay=1.0,
                max_delay=30.0,
                retryable_exceptions=[ConnectionError, TimeoutError, asyncio.TimeoutError]
            ),
            "data_collection": RetryConfig(
                max_attempts=5,
                base_delay=2.0,
                max_delay=60.0,
                retryable_exceptions=[ConnectionError, TimeoutError, asyncio.TimeoutError, OSError]
            ),
            "file_operation": RetryConfig(
                max_attempts=3,
                base_delay=0.5,
                max_delay=10.0,
                retryable_exceptions=[OSError, PermissionError]
            ),
            "default": RetryConfig()
        }
        
        print(f">>> ErrorHandler: Initialized with {len(self.retry_configs)} retry configurations")
    
    def _calculate_delay(self, attempt: int, config: RetryConfig) -> float:
        """Calculate delay for the given attempt."""
        # Exponential backoff
        delay = config.base_delay * (config.exponential_base ** (attempt - 1))
        
        # Apply maximum delay limit
        delay = min(delay, config.max_delay)
        
        # Add jitter if enabled
        if config.jitter:
            jitter_range = delay * 0.1  # 10% jitter
            delay += random.uniform(-jitter_range, jitter_range)
        
        return max(0, delay)
    
    def _is_retryable_exception(self, exception: Exception, config: RetryConfig) -> bool:
        """Check if an exception should be retried."""
        return any(isinstance(exception, exc_type) for exc_type in config.retryable_exceptions)
    
    def _update_error_stats(self, operation: str, exception: Exception, success: bool):
        """Update error statistics."""
        if operation not in self.error_stats:
            self.error_stats[operation] = {
                "total_attempts": 0,
                "successful_attempts": 0,
                "failed_attempts": 0,
                "exceptions": {},
                "last_error": None,
                "last_success": None
            }
        
        stats = self.error_stats[operation]
        stats["total_attempts"] += 1
        
        if success:
            stats["successful_attempts"] += 1
            stats["last_success"] = datetime.now().isoformat()
        else:
            stats["failed_attempts"] += 1
            stats["last_error"] = datetime.now().isoformat()
            
            exception_name = type(exception).__name__
            if exception_name not in stats["exceptions"]:
                stats["exceptions"][exception_name] = 0
            stats["exceptions"][exception_name] += 1
    
    def _is_circuit_breaker_open(self, operation: str) -> bool:
        """Check if circuit breaker is open for an operation."""
        if operation not in self.circuit_breakers:
            return False
        
        breaker = self.circuit_breakers[operation]
        
        # Check if we're in the timeout period
        if time.time() - breaker["last_failure"] < breaker["timeout"]:
            return True
        
        # Reset circuit breaker if timeout has passed
        del self.circuit_breakers[operation]
        return False
    
    def _update_circuit_breaker(self, operation: str, success: bool):
        """Update circuit breaker state."""
        if success:
            # Reset circuit breaker on success
            if operation in self.circuit_breakers:
                del self.circuit_breakers[operation]
        else:
            # Update circuit breaker on failure
            if operation not in self.circuit_breakers:
                self.circuit_breakers[operation] = {
                    "failure_count": 0,
                    "last_failure": time.time(),
                    "timeout": 60.0  # 1 minute timeout
                }
            
            breaker = self.circuit_breakers[operation]
            breaker["failure_count"] += 1
            breaker["last_failure"] = time.time()
            
            # Increase timeout with each failure
            breaker["timeout"] = min(300.0, 60.0 * (breaker["failure_count"] ** 1.5))
    
    async def retry_async(
        self,
        func: Callable,
        *args,
        operation: str = "default",
        config: Optional[RetryConfig] = None,
        **kwargs
    ) -> Any:
        """
        Execute an async function with retry logic.
        
        Args:
            func: Async function to execute
            *args: Function arguments
            operation: Operation name for logging and circuit breaker
            config: Retry configuration
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            Last exception if all retries fail
        """
        if config is None:
            config = self.retry_configs.get(operation, self.retry_configs["default"])
        
        # Check circuit breaker
        if self._is_circuit_breaker_open(operation):
            raise Exception(f"Circuit breaker is open for operation: {operation}")
        
        last_exception = None
        
        for attempt in range(1, config.max_attempts + 1):
            try:
                self.logger.debug(f"Attempting {operation} (attempt {attempt}/{config.max_attempts})")
                
                result = await func(*args, **kwargs)
                
                # Success - update stats and circuit breaker
                self._update_error_stats(operation, None, True)
                self._update_circuit_breaker(operation, True)
                
                if attempt > 1:
                    self.logger.info(f"Operation {operation} succeeded on attempt {attempt}")
                
                return result
                
            except Exception as e:
                last_exception = e
                
                # Update error stats
                self._update_error_stats(operation, e, False)
                
                # Check if exception is retryable
                if not self._is_retryable_exception(e, config):
                    self.logger.error(f"Non-retryable exception in {operation}: {e}")
                    self._update_circuit_breaker(operation, False)
                    raise e
                
                # Check if this is the last attempt
                if attempt == config.max_attempts:
                    self.logger.error(f"Operation {operation} failed after {config.max_attempts} attempts: {e}")
                    self._update_circuit_breaker(operation, False)
                    raise e
                
                # Calculate delay and wait
                delay = self._calculate_delay(attempt, config)
                self.logger.warning(f"Operation {operation} failed (attempt {attempt}), retrying in {delay:.2f}s: {e}")
                
                await asyncio.sleep(delay)
        
        # This should never be reached, but just in case
        if last_exception:
            raise last_exception
    
    def retry_sync(
        self,
        func: Callable,
        *args,
        operation: str = "default",
        config: Optional[RetryConfig] = None,
        **kwargs
    ) -> Any:
        """
        Execute a sync function with retry logic.
        
        Args:
            func: Sync function to execute
            *args: Function arguments
            operation: Operation name for logging and circuit breaker
            config: Retry configuration
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            Last exception if all retries fail
        """
        if config is None:
            config = self.retry_configs.get(operation, self.retry_configs["default"])
        
        # Check circuit breaker
        if self._is_circuit_breaker_open(operation):
            raise Exception(f"Circuit breaker is open for operation: {operation}")
        
        last_exception = None
        
        for attempt in range(1, config.max_attempts + 1):
            try:
                self.logger.debug(f"Attempting {operation} (attempt {attempt}/{config.max_attempts})")
                
                result = func(*args, **kwargs)
                
                # Success - update stats and circuit breaker
                self._update_error_stats(operation, None, True)
                self._update_circuit_breaker(operation, True)
                
                if attempt > 1:
                    self.logger.info(f"Operation {operation} succeeded on attempt {attempt}")
                
                return result
                
            except Exception as e:
                last_exception = e
                
                # Update error stats
                self._update_error_stats(operation, e, False)
                
                # Check if exception is retryable
                if not self._is_retryable_exception(e, config):
                    self.logger.error(f"Non-retryable exception in {operation}: {e}")
                    self._update_circuit_breaker(operation, False)
                    raise e
                
                # Check if this is the last attempt
                if attempt == config.max_attempts:
                    self.logger.error(f"Operation {operation} failed after {config.max_attempts} attempts: {e}")
                    self._update_circuit_breaker(operation, False)
                    raise e
                
                # Calculate delay and wait
                delay = self._calculate_delay(attempt, config)
                self.logger.warning(f"Operation {operation} failed (attempt {attempt}), retrying in {delay:.2f}s: {e}")
                
                time.sleep(delay)
        
        # This should never be reached, but just in case
        if last_exception:
            raise last_exception
    
    def get_error_stats(self, operation: Optional[str] = None) -> Dict[str, Any]:
        """Get error statistics."""
        if operation:
            return self.error_stats.get(operation, {})
        return self.error_stats
    
    def get_circuit_breaker_status(self) -> Dict[str, Dict]:
        """Get circuit breaker status for all operations."""
        return self.circuit_breakers.copy()
    
    def reset_circuit_breaker(self, operation: str) -> None:
        """Reset circuit breaker for an operation."""
        if operation in self.circuit_breakers:
            del self.circuit_breakers[operation]
            self.logger.info(f"Circuit breaker reset for operation: {operation}")
    
    def reset_all_circuit_breakers(self) -> None:
        """Reset all circuit breakers."""
        self.circuit_breakers.clear()
        self.logger.info("All circuit breakers reset")


# Global error handler instance
error_handler = ErrorHandler()


def get_error_handler() -> ErrorHandler:
    """Get the global error handler instance."""
    return error_handler


# Decorators for easy retry usage
def retry_async(operation: str = "default", config: Optional[RetryConfig] = None):
    """
    Decorator for async functions with retry logic.
    
    Args:
        operation: Operation name for logging and circuit breaker
        config: Retry configuration
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await error_handler.retry_async(
                func, *args, operation=operation, config=config, **kwargs
            )
        return wrapper
    return decorator


def retry_sync(operation: str = "default", config: Optional[RetryConfig] = None):
    """
    Decorator for sync functions with retry logic.
    
    Args:
        operation: Operation name for logging and circuit breaker
        config: Retry configuration
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return error_handler.retry_sync(
                func, *args, operation=operation, config=config, **kwargs
            )
        return wrapper
    return decorator


# Context manager for error handling
class ErrorHandlingContext:
    """Context manager for error handling operations."""
    
    def __init__(self, operation: str, config: Optional[RetryConfig] = None):
        self.operation = operation
        self.config = config
        self.start_time = None
    
    async def __aenter__(self):
        self.start_time = time.time()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            # Log the error
            error_handler.logger.error(
                f"Error in {self.operation}: {exc_val}",
                exc_info=(exc_type, exc_val, exc_tb)
            )
            
            # Update error stats
            error_handler._update_error_stats(self.operation, exc_val, False)
            error_handler._update_circuit_breaker(self.operation, False)
        
        return False  # Don't suppress the exception
