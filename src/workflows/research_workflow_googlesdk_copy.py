"""
Main research workflow coordination.
"""

import asyncio
from typing import Dict, Any
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types

from agents.dummy_agent import create_dummy_agent
from utils.data_validation import validate_research_request
from callbacks.safety_callbacks import research_quality_guardrail, tool_usage_monitor


class SecondaryResearchWorkflow:
    """Main workflow manager for secondary research."""
    
    def __init__(self):
        self.session_service = InMemorySessionService()
        # self.orchestrator = create_research_orchestrator() # Temporarily disabled for debugging
        self.orchestrator = create_dummy_agent() # Using a simple agent for debugging
        
        # Apply safety callbacks
        self.orchestrator.before_model_callback = research_quality_guardrail
        self.orchestrator.before_tool_callback = tool_usage_monitor
        
        self.runner = Runner(
            agent=self.orchestrator,
            app_name="secondary_research_workflow",
            session_service=self.session_service
        )
    
    async def execute_research(self, research_request: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the complete secondary research workflow."""
        
        # Validate input
        if not validate_research_request(research_request):
            return {
                "status": "error",
                "error": "Invalid research request format"
            }
        
        # Create session with initial state
        session_id = f"research_{research_request.get('topic', 'default').replace(' ', '_')}"
        session = await self.session_service.create_session(
            app_name="secondary_research_workflow",
            user_id="researcher",
            session_id=session_id,
            state={
                "research_request": research_request,
                "workflow_stage": "initiated",
                "timestamp": asyncio.get_event_loop().time(),
                "agent_execution_log": []
            }
        )
        
        # Construct research query
        query = self._build_research_query(research_request)
        
        # Execute workflow
        try:
            content = types.Content(role='user', parts=[types.Part(text=query)])
            
            final_result = None
            print(">>> Calling orchestrator agent (self.runner.run_async)... This may take a while.", flush=True)
            async for event in self.runner.run_async(
                user_id="researcher",
                session_id=session.id,
                new_message=content
            ):
                if event.is_final_response():
                    if event.content and event.content.parts:
                        final_result = event.content.parts[0].text
                    break
            print("<<< Orchestrator agent call finished.", flush=True)
            
            # Get final session state
            final_session = await self.session_service.get_session(
                app_name="secondary_research_workflow",
                user_id="researcher",
                session_id=session.id
            )
            
            return {
                "status": "complete",
                "research_results": final_result,
                "session_state": final_session.state,
                "session_id": session.id
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "session_id": session.id
            }
    
    def _build_research_query(self, research_request: Dict[str, Any]) -> str:
        """Build the research query for the orchestrator."""
        
        topic = research_request.get('topic', 'Unknown Topic')
        objectives = research_request.get('objectives', [])
        questions = research_request.get('questions', [])
        
        query = f"""Conduct comprehensive secondary research on: {topic}

Research Objectives:
{chr(10).join([f'- {obj}' for obj in objectives])}

Specific Research Questions:
{chr(10).join([f'- {q}' for q in questions])}

Please execute the complete research workflow including:
1. Research planning and methodology development
2. Multi-source data collection and orchestration
3. Data synthesis and analysis
4. SWOT framework analysis
5. Comprehensive report generation

Ensure all outputs are properly documented and saved to session state for access."""
        
        return query