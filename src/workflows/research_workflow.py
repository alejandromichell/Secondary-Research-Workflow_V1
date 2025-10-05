"""
Main research workflow coordination.
"""

import asyncio
from typing import Dict, Any
from google.adk.tools.tool_context import ToolContext

from utils.data_validation import validate_research_request
from agents.orchestration_agent import OrchestrationAgent


class SecondaryResearchWorkflow:
    """Main workflow manager for secondary research."""
    
    def __init__(self):
        self.orchestration_agent = OrchestrationAgent()
    
    async def execute_research(self, research_request: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the complete secondary research workflow using an agent-based approach."""
        
        # Validate input
        if not validate_research_request(research_request):
            return {
                "status": "error",
                "error": "Invalid research request format"
            }
        
        print(">>> Starting agent-based research workflow...", flush=True)
        
        try:
            # Create a query from the research request
            topic = research_request.get("topic")
            questions = research_request.get("questions")
            query = f"Please conduct a research on the topic: {topic}. Here are some specific questions: {', '.join(questions)}"

            # Run the orchestration agent
            agent_result_str = await self.orchestration_agent.run(query)
            
            # Parse the result
            try:
                agent_result = json.loads(agent_result_str)
            except json.JSONDecodeError:
                # If the result is not a valid JSON, treat it as a raw string result
                agent_result = {
                    "status": "success",
                    "orchestration_results": {
                        "report": agent_result_str
                    }
                }

            if agent_result["status"] == "success":
                print("<<< Agent-based research workflow completed successfully.", flush=True)
                
                return {
                    "status": "complete",
                    "research_results": agent_result["orchestration_results"],
                    "metadata": agent_result.get("metadata", {}),
                    "session_state": {
                        "research_request": research_request,
                        "workflow_stage": "completed",
                        "timestamp": asyncio.get_event_loop().time(),
                        "agent_execution_log": ["orchestration_agent"]
                    },
                    "session_id": f"research_{topic.replace(' ', '_')}"
                }
            else:
                print(f"!!! Agent-based research failed: {agent_result.get('error', 'Unknown error')}", flush=True)
                return {
                    "status": "error",
                    "error": agent_result.get('error', 'Research failed'),
                    "session_id": f"research_{topic.replace(' ', '_')}"
                }
            
        except Exception as e:
            print(f"!!! Research workflow failed: {str(e)}", flush=True)
            return {
                "status": "error",
                "error": str(e),
                "session_id": f"research_{research_request.get('topic', 'default').replace(' ', '_')}"
            }