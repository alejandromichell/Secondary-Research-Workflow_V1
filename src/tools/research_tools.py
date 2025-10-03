"""
Collection of tools for the research agents.
"""

from typing import Dict, Any, List

def create_research_plan_tool(
    topic: str,
    objectives: List[str],
    methodology: str,
    source_strategy: str,
    frameworks: List[str]
) -> Dict[str, Any]:
    """
    Tool for creating a structured research plan. It takes the components
    of a research plan and formats them into a structured dictionary.
    """
    print(f"--- Tool: create_research_plan_tool called for {topic} ---")
    
    research_plan = {
        "topic": topic,
        "objectives": objectives,
        "methodology": {
            "approach": methodology,
            "source_strategy": source_strategy,
            "frameworks": frameworks
        },
        "status": "plan_created"
    }
    
    print("--- Tool: Research plan created successfully ---")
    
    return research_plan
