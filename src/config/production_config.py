"""
Production Configuration Management for the Secondary Research Workflow System.

This module provides comprehensive configuration management for production
deployment, including environment-specific settings, security configurations,
and deployment parameters.
"""

import os
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum


class Environment(Enum):
    """Environment types."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


@dataclass
class DatabaseConfig:
    """Database configuration."""
    host: str = "localhost"
    port: int = 5432
    name: str = "research_workflow"
    user: str = "postgres"
    password: str = ""
    pool_size: int = 10
    max_overflow: int = 20
    echo: bool = False


@dataclass
class RedisConfig:
    """Redis configuration for caching."""
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    max_connections: int = 10


@dataclass
class APIConfig:
    """API configuration."""
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    reload: bool = False
    log_level: str = "info"
    cors_origins: List[str] = None
    rate_limit: int = 1000  # requests per hour
    
    def __post_init__(self):
        if self.cors_origins is None:
            self.cors_origins = ["*"]


@dataclass
class SecurityConfig:
    """Security configuration."""
    secret_key: str = ""
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    password_min_length: int = 8
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 15
    enable_2fa: bool = False
    session_timeout_minutes: int = 60


@dataclass
class DataCollectionConfig:
    """Data collection configuration."""
    max_concurrent_requests: int = 10
    request_timeout: int = 30
    retry_attempts: int = 3
    retry_delay: float = 1.0
    rate_limit_per_source: Dict[str, float] = None
    cache_ttl: int = 3600
    enable_caching: bool = True
    
    def __post_init__(self):
        if self.rate_limit_per_source is None:
            self.rate_limit_per_source = {
                "yahoo_finance": 0.5,
                "google_news": 0.2,
                "pubmed": 0.3,
                "arxiv": 0.4,
                "sec_edgar": 0.1,
                "default": 1.0
            }


@dataclass
class LoggingConfig:
    """Logging configuration."""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: str = "logs/app.log"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    enable_console: bool = True
    enable_file: bool = True
    enable_remote: bool = False
    remote_endpoint: Optional[str] = None


@dataclass
class MonitoringConfig:
    """Monitoring configuration."""
    enable_metrics: bool = True
    metrics_port: int = 9090
    health_check_interval: int = 30
    alert_thresholds: Dict[str, float] = None
    enable_alerting: bool = False
    alert_webhook: Optional[str] = None
    
    def __post_init__(self):
        if self.alert_thresholds is None:
            self.alert_thresholds = {
                "cpu_percent": 80.0,
                "memory_percent": 85.0,
                "disk_percent": 90.0,
                "response_time": 5.0
            }


@dataclass
class ProductionConfig:
    """Main production configuration."""
    environment: Environment = Environment.DEVELOPMENT
    debug: bool = False
    database: DatabaseConfig = None
    redis: RedisConfig = None
    api: APIConfig = None
    security: SecurityConfig = None
    data_collection: DataCollectionConfig = None
    logging: LoggingConfig = None
    monitoring: MonitoringConfig = None
    
    def __post_init__(self):
        if self.database is None:
            self.database = DatabaseConfig()
        if self.redis is None:
            self.redis = RedisConfig()
        if self.api is None:
            self.api = APIConfig()
        if self.security is None:
            self.security = SecurityConfig()
        if self.data_collection is None:
            self.data_collection = DataCollectionConfig()
        if self.logging is None:
            self.logging = LoggingConfig()
        if self.monitoring is None:
            self.monitoring = MonitoringConfig()


class ConfigManager:
    """
    Configuration manager for production deployment.
    
    Features:
    - Environment-specific configuration loading
    - Environment variable override support
    - Configuration validation
    - Hot reloading capabilities
    - Configuration export/import
    """
    
    def __init__(self, config_dir: str = "config"):
        """
        Initialize configuration manager.
        
        Args:
            config_dir: Directory containing configuration files
        """
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        
        self.current_config: Optional[ProductionConfig] = None
        self.environment = self._detect_environment()
        
        print(f">>> ConfigManager: Initialized for environment: {self.environment.value}")
    
    def _detect_environment(self) -> Environment:
        """Detect the current environment."""
        env_str = os.getenv("ENVIRONMENT", "development").lower()
        
        try:
            return Environment(env_str)
        except ValueError:
            print(f">>> ConfigManager: Unknown environment '{env_str}', defaulting to development")
            return Environment.DEVELOPMENT
    
    def load_config(self, config_name: Optional[str] = None) -> ProductionConfig:
        """
        Load configuration from file or environment.
        
        Args:
            config_name: Name of configuration file (without extension)
            
        Returns:
            Loaded configuration
        """
        if config_name is None:
            config_name = f"{self.environment.value}_config"
        
        config_file = self.config_dir / f"{config_name}.json"
        
        # Start with default configuration
        config = ProductionConfig()
        config.environment = self.environment
        
        # Load from file if it exists
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                # Update configuration with file data
                config = self._update_config_from_dict(config, config_data)
                print(f">>> ConfigManager: Loaded configuration from {config_file}")
                
            except Exception as e:
                print(f">>> ConfigManager: Error loading config file {config_file}: {e}")
        
        # Override with environment variables
        config = self._apply_environment_overrides(config)
        
        # Validate configuration
        self._validate_config(config)
        
        self.current_config = config
        return config
    
    def _update_config_from_dict(self, config: ProductionConfig, data: Dict[str, Any]) -> ProductionConfig:
        """Update configuration from dictionary data."""
        # Update main config fields
        for field_name, field_value in data.items():
            if hasattr(config, field_name):
                if field_name == "environment":
                    config.environment = Environment(field_value)
                elif field_name in ["database", "redis", "api", "security", "data_collection", "logging", "monitoring"]:
                    # Handle nested dataclass fields
                    current_field = getattr(config, field_name)
                    if isinstance(field_value, dict):
                        for nested_field, nested_value in field_value.items():
                            if hasattr(current_field, nested_field):
                                setattr(current_field, nested_field, nested_value)
                else:
                    setattr(config, field_name, field_value)
        
        return config
    
    def _apply_environment_overrides(self, config: ProductionConfig) -> ProductionConfig:
        """Apply environment variable overrides."""
        # API configuration
        if os.getenv("API_HOST"):
            config.api.host = os.getenv("API_HOST")
        if os.getenv("API_PORT"):
            config.api.port = int(os.getenv("API_PORT"))
        if os.getenv("API_WORKERS"):
            config.api.workers = int(os.getenv("API_WORKERS"))
        if os.getenv("LOG_LEVEL"):
            config.api.log_level = os.getenv("LOG_LEVEL")
        
        # Database configuration
        if os.getenv("DATABASE_HOST"):
            config.database.host = os.getenv("DATABASE_HOST")
        if os.getenv("DATABASE_PORT"):
            config.database.port = int(os.getenv("DATABASE_PORT"))
        if os.getenv("DATABASE_NAME"):
            config.database.name = os.getenv("DATABASE_NAME")
        if os.getenv("DATABASE_USER"):
            config.database.user = os.getenv("DATABASE_USER")
        if os.getenv("DATABASE_PASSWORD"):
            config.database.password = os.getenv("DATABASE_PASSWORD")
        
        # Redis configuration
        if os.getenv("REDIS_HOST"):
            config.redis.host = os.getenv("REDIS_HOST")
        if os.getenv("REDIS_PORT"):
            config.redis.port = int(os.getenv("REDIS_PORT"))
        if os.getenv("REDIS_PASSWORD"):
            config.redis.password = os.getenv("REDIS_PASSWORD")
        
        # Security configuration
        if os.getenv("SECRET_KEY"):
            config.security.secret_key = os.getenv("SECRET_KEY")
        
        # Data collection configuration
        if os.getenv("MAX_CONCURRENT_REQUESTS"):
            config.data_collection.max_concurrent_requests = int(os.getenv("MAX_CONCURRENT_REQUESTS"))
        if os.getenv("REQUEST_TIMEOUT"):
            config.data_collection.request_timeout = int(os.getenv("REQUEST_TIMEOUT"))
        
        # Logging configuration
        if os.getenv("LOG_LEVEL"):
            config.logging.level = os.getenv("LOG_LEVEL")
        if os.getenv("LOG_FILE"):
            config.logging.file_path = os.getenv("LOG_FILE")
        
        return config
    
    def _validate_config(self, config: ProductionConfig) -> None:
        """Validate configuration settings."""
        errors = []
        
        # Validate API configuration
        if config.api.port < 1 or config.api.port > 65535:
            errors.append("API port must be between 1 and 65535")
        
        if config.api.workers < 1:
            errors.append("API workers must be at least 1")
        
        # Validate database configuration
        if config.database.port < 1 or config.database.port > 65535:
            errors.append("Database port must be between 1 and 65535")
        
        if not config.database.name:
            errors.append("Database name is required")
        
        # Validate security configuration
        if not config.security.secret_key:
            errors.append("Secret key is required for security")
        
        if len(config.security.secret_key) < 32:
            errors.append("Secret key must be at least 32 characters long")
        
        # Validate data collection configuration
        if config.data_collection.max_concurrent_requests < 1:
            errors.append("Max concurrent requests must be at least 1")
        
        if config.data_collection.request_timeout < 1:
            errors.append("Request timeout must be at least 1 second")
        
        if errors:
            raise ValueError(f"Configuration validation failed: {'; '.join(errors)}")
    
    def save_config(self, config: ProductionConfig, config_name: Optional[str] = None) -> None:
        """
        Save configuration to file.
        
        Args:
            config: Configuration to save
            config_name: Name of configuration file
        """
        if config_name is None:
            config_name = f"{config.environment.value}_config"
        
        config_file = self.config_dir / f"{config_name}.json"
        
        try:
            # Convert to dictionary
            config_dict = asdict(config)
            
            # Convert enum to string
            config_dict["environment"] = config.environment.value
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, indent=2, default=str)
            
            print(f">>> ConfigManager: Saved configuration to {config_file}")
            
        except Exception as e:
            print(f">>> ConfigManager: Error saving config file {config_file}: {e}")
    
    def get_config(self) -> ProductionConfig:
        """Get the current configuration."""
        if self.current_config is None:
            return self.load_config()
        return self.current_config
    
    def reload_config(self) -> ProductionConfig:
        """Reload configuration from file."""
        return self.load_config()
    
    def export_config(self, file_path: str) -> None:
        """Export configuration to a file."""
        config = self.get_config()
        config_dict = asdict(config)
        config_dict["environment"] = config.environment.value
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, indent=2, default=str)
        
        print(f">>> ConfigManager: Exported configuration to {file_path}")
    
    def import_config(self, file_path: str) -> ProductionConfig:
        """Import configuration from a file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        config = ProductionConfig()
        config = self._update_config_from_dict(config, config_data)
        self._validate_config(config)
        
        self.current_config = config
        print(f">>> ConfigManager: Imported configuration from {file_path}")
        
        return config


# Global configuration manager instance
config_manager = ConfigManager()


def get_config() -> ProductionConfig:
    """Get the current configuration."""
    return config_manager.get_config()


def load_config(config_name: Optional[str] = None) -> ProductionConfig:
    """Load configuration."""
    return config_manager.load_config(config_name)


def save_config(config: ProductionConfig, config_name: Optional[str] = None) -> None:
    """Save configuration."""
    config_manager.save_config(config, config_name)


# Environment-specific configuration templates
def create_development_config() -> ProductionConfig:
    """Create development configuration."""
    config = ProductionConfig()
    config.environment = Environment.DEVELOPMENT
    config.debug = True
    config.api.reload = True
    config.api.workers = 1
    config.logging.level = "DEBUG"
    config.monitoring.enable_metrics = False
    return config


def create_staging_config() -> ProductionConfig:
    """Create staging configuration."""
    config = ProductionConfig()
    config.environment = Environment.STAGING
    config.debug = False
    config.api.reload = False
    config.api.workers = 2
    config.logging.level = "INFO"
    config.monitoring.enable_metrics = True
    return config


def create_production_config() -> ProductionConfig:
    """Create production configuration."""
    config = ProductionConfig()
    config.environment = Environment.PRODUCTION
    config.debug = False
    config.api.reload = False
    config.api.workers = 4
    config.logging.level = "WARNING"
    config.monitoring.enable_metrics = True
    config.monitoring.enable_alerting = True
    config.security.enable_2fa = True
    return config
