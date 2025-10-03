"""
Base agent implementation for secondary research workflow.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from google.adk.agents import Agent
from google.adk.tools.tool_context import ToolContext
from config.settings import get_settings


class BaseResearchAgent(ABC):
    """Base class for all research agents."""
    
    def __init__(self, name: str, model: str = None):
        self.name = name
        self.settings = get_settings()
        self.model = model or self.settings.default_model
        self._agent = None
    
    @property
    def agent(self) -> Agent:
        """Get the ADK agent instance."""
        if self._agent is None:
            self._agent = self._create_agent()
        return self._agent
    
    @abstractmethod
    def _create_agent(self) -> Agent:
        """Create the ADK agent instance."""
        pass
    
    @abstractmethod
    def get_tools(self) -> List:
        """Get the tools for this agent."""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """Get the agent description."""
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