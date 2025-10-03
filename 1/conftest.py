"""
Pytest configuration and fixtures.
"""

import pytest
import asyncio
import os
from typing import Dict, Any
from google.adk.sessions import InMemorySessionService


@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def session_service():
    """Create a test session service."""
    return InMemorySessionService()


@pytest.fixture
def sample_research_request():
    """Sample research request for testing."""
    return {
        "topic": "Test AI Market Analysis",
        "objectives": [
            "Analyze market size and growth",
            "Identify key competitors",
            "Assess market opportunities"
        ],
        "questions": [
            "What is the current market size?",
            "Who are the main competitors?",
            "What growth opportunities exist?"
        ]
    }


@pytest.fixture
def mock_api_keys(monkeypatch):
    """Mock API keys for testing."""
    monkeypatch.setenv("GOOGLE_API_KEY", "test_google_key")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test_anthropic_key")
    monkeypatch.setenv("NOTION_API_KEY", "test_notion_key")
    monkeypatch.setenv("PERPLEXITY_API_KEY", "test_perplexity_key")