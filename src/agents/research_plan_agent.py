"""
Research Plan Agent implementation.
"""
import os
from typing import Dict, Any, List

from .base_agent import BaseResearchAgent
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from utils.data_validation import validate_research_objectives


class ResearchPlanAgent(BaseResearchAgent):
    """Agent responsible for creating comprehensive research plans."""
    
    def __init__(self):
        super().__init__("research_plan_agent")
    
    def get_tools(self) -> List:
        """Get tools for research planning."""
        return []
    
    def get_description(self) -> str:
        """Get agent description."""
        return (
            "Creates comprehensive research plans with methodology, "
            "source identification, and structured frameworks for "
            "secondary research projects."
        )
    
    def get_instruction(self) -> str:
        """Get agent instruction from file."""
        prompt_path = os.path.join(os.path.dirname(__file__), '..', 'prompts', "research_plan_instruction.txt")
        with open(prompt_path, 'r') as f:
            return f.read()

    def validate_input(self, data: Dict[str, Any]) -> bool:
        """Validate research plan input."""
        required_fields = ["topic", "objectives"]
        return all(field in data for field in required_fields)


def create_research_plan_agent() -> ResearchPlanAgent:
    """Factory function to create research plan agent."""
    return ResearchPlanAgent()