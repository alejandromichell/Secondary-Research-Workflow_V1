"""
Main research workflow coordination.
"""

import asyncio
from typing import Dict, Any

from utils.data_validation import validate_research_request
from tools.anthropic_research_client import AnthropicResearchClient


class SecondaryResearchWorkflow:
    """Main workflow manager for secondary research."""
    
    def __init__(self):
        self.anthropic_client = AnthropicResearchClient()
    
    async def execute_research(self, research_request: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the complete secondary research workflow using Anthropic."""
        
        # Validate input
        if not validate_research_request(research_request):
            return {
                "status": "error",
                "error": "Invalid research request format"
            }
        
        print(">>> Starting Anthropic-powered research workflow...", flush=True)
        
        try:
            # Use Anthropic client to conduct real research
            research_results = await self.anthropic_client.conduct_research(research_request)
            
            if research_results["status"] == "success":
                print("<<< Anthropic research workflow completed successfully.", flush=True)
                
                return {
                    "status": "complete",
                    "research_results": research_results["research_results"],
                    "metadata": research_results["metadata"],
                    "session_state": {
                        "research_request": research_request,
                        "workflow_stage": "completed",
                        "timestamp": asyncio.get_event_loop().time(),
                        "agent_execution_log": ["research_planning", "data_collection_strategy", "analysis_synthesis", "swot_analysis", "final_report"]
                    },
                    "session_id": f"research_{research_request.get('topic', 'default').replace(' ', '_')}"
                }
            else:
                print(f"!!! Anthropic research failed: {research_results.get('error', 'Unknown error')}", flush=True)
                return {
                    "status": "error",
                    "error": research_results.get('error', 'Research failed'),
                    "session_id": f"research_{research_request.get('topic', 'default').replace(' ', '_')}"
                }
            
        except Exception as e:
            print(f"!!! Research workflow failed: {str(e)}", flush=True)
            return {
                "status": "error",
                "error": str(e),
                "session_id": f"research_{research_request.get('topic', 'default').replace(' ', '_')}"
            }