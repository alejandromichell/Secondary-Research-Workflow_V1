"""
Base agent implementation for secondary research workflow.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from claude_agent import ClaudeSDKClient, ClaudeAgentOptions, Tool
from config.settings import get_settings


class BaseResearchAgent(ABC):
    """Base class for all research agents."""
    
    def __init__(self, name: str, model: str = None):
        self.name = name
        self.settings = get_settings()
        self.model = model or self.settings.default_model
        self._agent_client: Optional[ClaudeSDKClient] = None

    @property
    def agent_client(self) -> ClaudeSDKClient:
        """Get the Claude SDK client instance."""
        if self._agent_client is None:
            self._agent_client = self._create_client()
        return self._agent_client

    def _create_client(self) -> ClaudeSDKClient:
        """Create the Claude SDK client instance."""
        agent_options = ClaudeAgentOptions(
            model=self.model,
            system_prompt=self.get_instruction(),
            tools=self.get_tools(),
        )
        return ClaudeSDKClient(agent_options=agent_options)

    @abstractmethod
    def get_tools(self) -> List[Tool]:
        """Get the tools for this agent."""
        pass

    @abstractmethod
    def get_instruction(self) -> str:
        """Get the agent instruction."""
        pass

    async def run(self, query: str) -> str:
        """Run the agent with a given query."""
        return await self.agent_client.query(query)

    def validate_input(self, data: Dict[str, Any]) -> bool:
        """Validate input data for the agent."""
        return True

    def format_output(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Format the agent output."""
        return result