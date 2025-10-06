"""
Monitoring and Logging System for the Secondary Research Workflow System.

This module provides comprehensive monitoring, logging, and health check
functionality for the research workflow system.
"""

import asyncio
import json
import logging
import os
import psutil
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
import threading
from collections import defaultdict, deque
from functools import wraps


class SystemMonitor:
    """
    System monitoring and health check functionality.
    
    Features:
    - CPU, memory, and disk usage monitoring
    - Process monitoring
    - Performance metrics collection
    - Health check endpoints
    - Alerting capabilities
    """
    
    def __init__(self, log_file: str = "logs/system_monitor.log"):
        """
        Initialize system monitor.
        
        Args:
            log_file: Path to log file
        """
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Performance metrics storage
        self.metrics_history: Dict[str, deque] = {
            "cpu_percent": deque(maxlen=100),
            "memory_percent": deque(maxlen=100),
            "disk_percent": deque(maxlen=100),
            "response_times": deque(maxlen=1000)
        }
        
        # Health check results
        self.health_checks: Dict[str, Dict] = {}
        
        # Monitoring configuration
        self.monitoring_config = {
            "cpu_threshold": 80.0,
            "memory_threshold": 85.0,
            "disk_threshold": 90.0,
            "response_time_threshold": 5.0,
            "health_check_interval": 30.0
        }
        
        # Start monitoring thread
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        print(f">>> SystemMonitor: Initialized with log file: {self.log_file}")
    
    def _monitoring_loop(self):
        """Main monitoring loop."""
        while self.monitoring_active:
            try:
                self._collect_system_metrics()
                self._perform_health_checks()
                time.sleep(self.monitoring_config["health_check_interval"])
            except Exception as e:
                print(f">>> SystemMonitor: Error in monitoring loop: {e}")
                time.sleep(5)  # Wait before retrying
    
    def _collect_system_metrics(self):
        """Collect system performance metrics."""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            self.metrics_history["cpu_percent"].append({
                "timestamp": datetime.now().isoformat(),
                "value": cpu_percent
            })
            
            # Memory usage
            memory = psutil.virtual_memory()
            self.metrics_history["memory_percent"].append({
                "timestamp": datetime.now().isoformat(),
                "value": memory.percent
            })
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            self.metrics_history["disk_percent"].append({
                "timestamp": datetime.now().isoformat(),
                "value": disk_percent
            })
            
            # Check for threshold violations
            self._check_thresholds(cpu_percent, memory.percent, disk_percent)
            
        except Exception as e:
            print(f">>> SystemMonitor: Error collecting metrics: {e}")
    
    def _check_thresholds(self, cpu_percent: float, memory_percent: float, disk_percent: float):
        """Check if metrics exceed thresholds."""
        alerts = []
        
        if cpu_percent > self.monitoring_config["cpu_threshold"]:
            alerts.append(f"High CPU usage: {cpu_percent:.1f}%")
        
        if memory_percent > self.monitoring_config["memory_threshold"]:
            alerts.append(f"High memory usage: {memory_percent:.1f}%")
        
        if disk_percent > self.monitoring_config["disk_threshold"]:
            alerts.append(f"High disk usage: {disk_percent:.1f}%")
        
        if alerts:
            self._log_alert("System thresholds exceeded", alerts)
    
    def _perform_health_checks(self):
        """Perform health checks on system components."""
        health_checks = {
            "system_resources": self._check_system_resources(),
            "disk_space": self._check_disk_space(),
            "process_health": self._check_process_health(),
            "network_connectivity": self._check_network_connectivity()
        }
        
        self.health_checks = health_checks
    
    def _check_system_resources(self) -> Dict[str, Any]:
        """Check system resource availability."""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            
            return {
                "status": "healthy" if cpu_percent < 90 and memory.percent < 95 else "warning",
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_gb": memory.available / (1024**3),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _check_disk_space(self) -> Dict[str, Any]:
        """Check disk space availability."""
        try:
            disk = psutil.disk_usage('/')
            free_percent = (disk.free / disk.total) * 100
            
            return {
                "status": "healthy" if free_percent > 10 else "warning",
                "free_percent": free_percent,
                "free_gb": disk.free / (1024**3),
                "total_gb": disk.total / (1024**3),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _check_process_health(self) -> Dict[str, Any]:
        """Check process health."""
        try:
            current_process = psutil.Process()
            process_info = {
                "pid": current_process.pid,
                "cpu_percent": current_process.cpu_percent(),
                "memory_percent": current_process.memory_percent(),
                "memory_mb": current_process.memory_info().rss / (1024**2),
                "num_threads": current_process.num_threads(),
                "status": current_process.status()
            }
            
            return {
                "status": "healthy",
                "process_info": process_info,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _check_network_connectivity(self) -> Dict[str, Any]:
        """Check network connectivity."""
        try:
            # Simple connectivity check
            import socket
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            
            return {
                "status": "healthy",
                "connectivity": "available",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "warning",
                "connectivity": "limited",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _log_alert(self, alert_type: str, details: List[str]):
        """Log system alerts."""
        alert_data = {
            "timestamp": datetime.now().isoformat(),
            "type": alert_type,
            "details": details,
            "severity": "warning"
        }
        
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(alert_data) + '\n')
        except Exception as e:
            print(f">>> SystemMonitor: Error logging alert: {e}")
    
    def record_response_time(self, operation: str, response_time: float):
        """Record response time for an operation."""
        self.metrics_history["response_times"].append({
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "response_time": response_time
        })
        
        # Check for slow responses
        if response_time > self.monitoring_config["response_time_threshold"]:
            self._log_alert("Slow response", [f"{operation}: {response_time:.2f}s"])
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of collected metrics."""
        summary = {}
        
        for metric_name, history in self.metrics_history.items():
            if history:
                values = [entry["value"] for entry in history]
                summary[metric_name] = {
                    "current": values[-1] if values else 0,
                    "average": sum(values) / len(values) if values else 0,
                    "min": min(values) if values else 0,
                    "max": max(values) if values else 0,
                    "count": len(values)
                }
        
        return summary
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get overall health status."""
        if not self.health_checks:
            return {"status": "unknown", "message": "No health checks performed"}
        
        # Determine overall status
        statuses = [check.get("status", "unknown") for check in self.health_checks.values()]
        
        if "error" in statuses:
            overall_status = "error"
        elif "warning" in statuses:
            overall_status = "warning"
        else:
            overall_status = "healthy"
        
        return {
            "status": overall_status,
            "checks": self.health_checks,
            "timestamp": datetime.now().isoformat()
        }
    
    def stop_monitoring(self):
        """Stop the monitoring loop."""
        self.monitoring_active = False
        if self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=5)


class PerformanceLogger:
    """
    Performance logging and analysis.
    
    Features:
    - Operation timing
    - Performance metrics collection
    - Bottleneck identification
    - Performance reporting
    """
    
    def __init__(self, log_file: str = "logs/performance.log"):
        """
        Initialize performance logger.
        
        Args:
            log_file: Path to performance log file
        """
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Performance data storage
        self.operation_times: Dict[str, List[float]] = defaultdict(list)
        self.operation_counts: Dict[str, int] = defaultdict(int)
        self.operation_errors: Dict[str, int] = defaultdict(int)
        
        print(f">>> PerformanceLogger: Initialized with log file: {self.log_file}")
    
    def log_operation(self, operation: str, duration: float, success: bool = True, details: Optional[Dict] = None):
        """Log an operation's performance."""
        self.operation_times[operation].append(duration)
        self.operation_counts[operation] += 1
        
        if not success:
            self.operation_errors[operation] += 1
        
        # Log to file
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "duration": duration,
            "success": success,
            "details": details or {}
        }
        
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            print(f">>> PerformanceLogger: Error logging operation: {e}")
    
    def get_operation_stats(self, operation: str) -> Dict[str, Any]:
        """Get statistics for a specific operation."""
        if operation not in self.operation_times:
            return {"error": "Operation not found"}
        
        times = self.operation_times[operation]
        count = self.operation_counts[operation]
        errors = self.operation_errors[operation]
        
        return {
            "operation": operation,
            "total_calls": count,
            "successful_calls": count - errors,
            "error_count": errors,
            "success_rate": ((count - errors) / count * 100) if count > 0 else 0,
            "average_time": sum(times) / len(times) if times else 0,
            "min_time": min(times) if times else 0,
            "max_time": max(times) if times else 0,
            "total_time": sum(times)
        }
    
    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all operations."""
        return {operation: self.get_operation_stats(operation) for operation in self.operation_times}
    
    def get_slowest_operations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get the slowest operations."""
        stats = self.get_all_stats()
        sorted_ops = sorted(stats.values(), key=lambda x: x["average_time"], reverse=True)
        return sorted_ops[:limit]
    
    def get_most_called_operations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get the most frequently called operations."""
        stats = self.get_all_stats()
        sorted_ops = sorted(stats.values(), key=lambda x: x["total_calls"], reverse=True)
        return sorted_ops[:limit]


# Global instances
system_monitor = SystemMonitor()
performance_logger = PerformanceLogger()


def get_system_monitor() -> SystemMonitor:
    """Get the global system monitor instance."""
    return system_monitor


def get_performance_logger() -> PerformanceLogger:
    """Get the global performance logger instance."""
    return performance_logger


# Decorator for performance logging
def log_performance(operation: str):
    """
    Decorator to log function performance.
    
    Args:
        operation: Operation name for logging
    """
    def decorator(func):
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)
                    duration = time.time() - start_time
                    performance_logger.log_operation(operation, duration, True)
                    return result
                except Exception as e:
                    duration = time.time() - start_time
                    performance_logger.log_operation(operation, duration, False, {"error": str(e)})
                    raise e
            return async_wrapper
        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    duration = time.time() - start_time
                    performance_logger.log_operation(operation, duration, True)
                    return result
                except Exception as e:
                    duration = time.time() - start_time
                    performance_logger.log_operation(operation, duration, False, {"error": str(e)})
                    raise e
            return sync_wrapper
    return decorator


# Context manager for performance logging
class PerformanceContext:
    """Context manager for performance logging."""
    
    def __init__(self, operation: str, details: Optional[Dict] = None):
        self.operation = operation
        self.details = details or {}
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        success = exc_type is None
        
        if not success:
            self.details["error"] = str(exc_val)
        
        performance_logger.log_operation(self.operation, duration, success, self.details)
