"""
Base agent implementation for secondary research workflow.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from config.settings import get_settings


class BaseResearchAgent(ABC):
    """Base class for all research agents."""
    
    def __init__(self, name: str, model: str = None):
        self.name = name
        self.settings = get_settings()
        self.model = model or self.settings.default_model

    @abstractmethod
    def get_tools(self) -> List:
        """Get the tools for this agent."""
        pass

    @abstractmethod
    def get_instruction(self) -> str:
        """Get the agent instruction."""
        pass

    def validate_input(self, data: Dict[str, Any]) -> bool:
        """Validate input data for the agent."""
        return True

    def format_output(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Format the agent output."""
        return result