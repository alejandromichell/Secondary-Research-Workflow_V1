"""
Orchestration Agent implementation for coordinating data collection.
"""
import os
from typing import Dict, Any, List
from claude_agent import Tool, tool

from .base_agent import BaseResearchAgent
from tools.anthropic_research_client import AnthropicResearchClient


class OrchestrationAgent(BaseResearchAgent):
    """Agent responsible for orchestrating multi-source data collection."""
    
    def __init__(self):
        super().__init__("orchestration_agent")
        self.anthropic_client = AnthropicResearchClient()
    
    def get_tools(self) -> List[Tool]:
        """Get tools for data orchestration."""
        return [self.coordinate_research_execution_tool]
    
    def get_instruction(self) -> str:
        """Get agent instruction from file."""
        prompt_path = os.path.join(os.path.dirname(__file__), '..', 'prompts', "orchestration_agent_instruction.txt")
        with open(prompt_path, 'r') as f:
            return f.read()

    @tool
    async def coordinate_research_execution_tool(
        self,
        research_plan: dict,
    ) -> Dict[str, Any]:
        """Tool for coordinating research data collection."""
        
        print(f"--- Tool: coordinate_research_execution_tool called ---")
        
        research_id = research_plan.get("research_id", "unknown")
        
        # Perform real data collection using Anthropic
        orchestration_results = await self.anthropic_client.conduct_research(research_plan)
        
        print(f"--- Tool: Data collection completed for {research_id} ---")
        
        return {
            "status": "success",
            "orchestration_results": orchestration_results,
            "ready_for_synthesis": True,
            "next_phase": "data_synthesis_and_analysis"
        }


def create_orchestration_agent() -> OrchestrationAgent:
    """Factory function to create orchestration agent."""
    return OrchestrationAgent()