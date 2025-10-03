"""
Orchestration Agent implementation for coordinating data collection.
"""
import os
from typing import Dict, Any, List
from google.adk.agents import Agent
from google.adk.tools.tool_context import ToolContext

from .base_agent import BaseResearchAgent
from tools.perplexity_client import PerplexityClient
from tools.claude_client import ClaudeClient


class OrchestrationAgent(BaseResearchAgent):
    """Agent responsible for orchestrating multi-source data collection."""
    
    def __init__(self):
        super().__init__("orchestration_agent")
        self.perplexity_client = PerplexityClient()
        self.claude_client = ClaudeClient()
    
    def _create_agent(self) -> Agent:
        """Create the orchestration agent."""
        return Agent(
            name=self.name,
            model=self.model,
            description=self.get_description(),
            instruction=self.get_instruction(),
            tools=self.get_tools(),
            output_key="data_collection_complete"
        )
    
    def get_tools(self) -> List:
        """Get tools for data orchestration."""
        return [coordinate_research_execution_tool]
    
    def get_description(self) -> str:
        """Get agent description."""
        return (
            "Coordinates and executes multi-source data collection based on "
            "research plans, managing API calls and data aggregation across "
            "academic, industry, and government sources."
        )
    
    def get_instruction(self) -> str:
        """Get agent instruction from file."""
        prompt_path = os.path.join(os.path.dirname(__file__), '..', 'prompts', "orchestration_agent_instruction.txt")
        with open(prompt_path, 'r') as f:
            return f.read()


def coordinate_research_execution_tool(
    research_plan: dict,
    tool_context: ToolContext
) -> Dict[str, Any]:
    """Tool for coordinating research data collection."""
    
    print(f"--- Tool: coordinate_research_execution_tool called ---")
    
    research_id = research_plan.get("research_id", "unknown")
    topic = research_plan.get("topic", "")
    questions = research_plan.get("questions", [])
    
    # Simulate data collection from multiple sources
    orchestration_results = {
        "research_id": research_id,
        "topic": topic,
        "data_sources": [
            {
                "source_type": "academic_journals",
                "query_count": len(questions),
                "papers_found": 25,
                "credibility_score": 0.9
            },
            {
                "source_type": "industry_reports",
                "query_count": len(questions),
                "reports_found": 12,
                "credibility_score": 0.85
            },
            {
                "source_type": "government_data",
                "query_count": len(questions),
                "datasets_found": 8,
                "credibility_score": 0.95
            }
        ],
        "collection_status": "complete",
        "total_sources": 45,
        "data_quality_score": 0.88,
        "collection_timestamp": tool_context.state.get("timestamp")
    }
    
    # Save results to state
    tool_context.state["orchestration_results"] = orchestration_results
    tool_context.state["research_status"] = "data_collection_complete"
    tool_context.state["raw_data_available"] = True
    
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