"""
Root orchestrator agent that coordinates the entire research workflow.
"""
import os
from typing import List
from google.adk.agents import Agent

from .research_plan_agent import create_research_plan_agent
from .orchestration_agent import create_orchestration_agent
# from .synthesis_agent import create_synthesis_agent # Temporarily disabled for simplified workflow
# from .swot_analysis_agent import create_swot_analysis_agent # Temporarily disabled for simplified workflow
from .report_generation_agent import create_report_generation_agent
from config.settings import get_settings


def create_research_orchestrator() -> Agent:
    """Create the root orchestrator agent."""
    
    settings = get_settings()
    
    # Create all sub-agents
    sub_agents = [
        create_research_plan_agent().agent,
        create_orchestration_agent().agent,
        # create_synthesis_agent().agent, # Temporarily disabled for simplified workflow
        # create_swot_analysis_agent().agent, # Temporarily disabled for simplified workflow
        create_report_generation_agent().agent
    ]
    
    prompt_path = os.path.join(os.path.dirname(__file__), '..', 'prompts', "root_orchestrator_instruction.txt")
    with open(prompt_path, 'r') as f:
        instruction = f.read()

    return Agent(
        name="secondary_research_orchestrator",
        model=settings.default_model,
        description=(
            "Main coordinator for multi-agent secondary research workflow, "
            "managing delegation and ensuring comprehensive research execution."
        ),
        instruction=instruction,
        
        sub_agents=sub_agents,
        output_key="research_workflow_complete"
    )