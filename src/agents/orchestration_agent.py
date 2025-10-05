"""
Orchestration Agent implementation for coordinating live data collection.
"""
import os
import asyncio
from typing import Dict, Any, List

from .base_agent import BaseResearchAgent
from .data_collection_agent import DataCollectionAgent


class OrchestrationAgent(BaseResearchAgent):
    """Agent responsible for orchestrating multi-source live data collection."""
    
    def __init__(self):
        super().__init__("orchestration_agent")
        self.data_collection_agent = DataCollectionAgent()
    
    def get_tools(self) -> List:
        """Get tools for data orchestration."""
        return [self.coordinate_live_research_execution_tool]
    
    def get_instruction(self) -> str:
        """Get agent instruction from file."""
        prompt_path = os.path.join(os.path.dirname(__file__), '..', 'prompts', "orchestration_agent_instruction.txt")
        with open(prompt_path, 'r') as f:
            return f.read()

    async def coordinate_live_research_execution_tool(
        self,
        research_plan: dict,
    ) -> Dict[str, Any]:
        """Tool for coordinating live research data collection from real sources."""
        
        print(f"--- Tool: coordinate_live_research_execution_tool called ---")
        
        research_id = research_plan.get("research_id", "unknown")
        topic = research_plan.get("topic", "unknown")
        
        # Extract keywords from research plan
        objectives = research_plan.get("objectives", [])
        questions = research_plan.get("questions", [])
        
        # Generate keywords for data collection
        keywords = self._extract_keywords(topic, objectives, questions)
        
        print(f"--- Starting live data collection for topic: {topic} ---")
        print(f"--- Keywords: {keywords} ---")
        
        # Perform live data collection
        async with self.data_collection_agent as collector:
            orchestration_results = await collector.collect_all_sources(topic, keywords)
        
        print(f"--- Tool: Live data collection completed for {research_id} ---")
        
        return {
            "status": "success",
            "orchestration_results": orchestration_results,
            "data_sources": orchestration_results.get("sources_by_type", {}),
            "collection_summary": orchestration_results.get("collection_summary", {}),
            "ready_for_synthesis": True,
            "next_phase": "data_synthesis_and_analysis",
            "live_data_collected": True
        }
    
    def _extract_keywords(self, topic: str, objectives: List[str], questions: List[str]) -> List[str]:
        """Extract relevant keywords for data collection."""
        keywords = [topic]
        
        # Add words from objectives
        for objective in objectives:
            words = objective.lower().split()
            keywords.extend([word.strip('.,!?') for word in words if len(word) > 3])
        
        # Add words from questions
        for question in questions:
            words = question.lower().split()
            keywords.extend([word.strip('.,!?') for word in words if len(word) > 3])
        
        # Remove duplicates and filter
        unique_keywords = list(set(keywords))
        filtered_keywords = [kw for kw in unique_keywords if len(kw) > 2 and kw not in ['the', 'and', 'for', 'with', 'from']]
        
        return filtered_keywords[:10]  # Limit to 10 keywords


def create_orchestration_agent() -> OrchestrationAgent:
    """Factory function to create orchestration agent."""
    return OrchestrationAgent()