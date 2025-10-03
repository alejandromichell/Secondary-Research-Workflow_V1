"""
Application configuration management.
"""

import os
from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""
    
    # API Keys
    # Make Google optional so the app can run with Anthropic/Perplexity only
    google_api_key: Optional[str] = Field(default=None, env="GOOGLE_API_KEY")
    anthropic_api_key: str = Field(..., env="ANTHROPIC_API_KEY")
    perplexity_api_key: str = Field(..., env="PERPLEXITY_API_KEY")
    notion_api_key: str = Field(..., env="NOTION_API_KEY")
    
    # Google configuration
    google_sheets_credentials: str = Field(
        default="./credentials/google_credentials.json",
        env="GOOGLE_SHEETS_CREDENTIALS"
    )
    google_genai_use_vertexai: bool = Field(default=False, env="GOOGLE_GENAI_USE_VERTEXAI")
    
    # Model configuration
    # Default to an Anthropic model since Google is optional
    default_model: str = Field(default="claude-3-5-sonnet-20240620", env="DEFAULT_MODEL")
    
    # Workflow configuration
    max_concurrent_agents: int = Field(default=5, env="MAX_CONCURRENT_AGENTS")
    agent_timeout: int = Field(default=300, env="AGENT_TIMEOUT")
    workflow_timeout: int = Field(default=1800, env="WORKFLOW_TIMEOUT")
    
    # Logging
    log_level: str = Field(default="info", env="LOG_LEVEL")
    
    # Server
    host: str = Field(default="localhost", env="HOST")
    port: int = Field(default=8000, env="PORT")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()