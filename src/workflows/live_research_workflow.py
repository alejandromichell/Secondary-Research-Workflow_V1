"""
Live research workflow coordination with real data collection.
"""

import asyncio
from typing import Dict, Any
from datetime import datetime

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from utils.data_validation import validate_research_request
from agents.research_plan_agent import create_research_plan_agent
from agents.orchestration_agent import create_orchestration_agent
from agents.synthesis_agent import create_synthesis_agent
from agents.swot_analysis_agent import create_swot_analysis_agent
from agents.report_generation_agent import create_report_generation_agent


class LiveSecondaryResearchWorkflow:
    """Main workflow manager for live secondary research with real data collection."""
    
    def __init__(self):
        self.research_plan_agent = create_research_plan_agent()
        self.orchestration_agent = create_orchestration_agent()
        self.synthesis_agent = create_synthesis_agent()
        self.swot_analysis_agent = create_swot_analysis_agent()
        self.report_generation_agent = create_report_generation_agent()
    
    async def execute_research(self, research_request: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the complete live secondary research workflow."""
        
        # Validate input
        if not validate_research_request(research_request):
            return {
                "status": "error",
                "error": "Invalid research request format"
            }
        
        print(">>> Starting LIVE secondary research workflow...", flush=True)
        print(f">>> Topic: {research_request.get('topic', 'Unknown')}", flush=True)
        
        try:
            # Step 1: Create Research Plan
            print("--- Phase 1: Research Planning ---", flush=True)
            research_plan = await self._create_research_plan(research_request)
            
            if research_plan.get("status") != "success":
                return {
                    "status": "error",
                    "error": "Failed to create research plan",
                    "details": research_plan
                }
            
            # Step 2: Live Data Collection (Orchestration)
            print("--- Phase 2: LIVE Data Collection ---", flush=True)
            orchestration_results = await self._orchestrate_live_data_collection(research_plan)
            
            if orchestration_results.get("status") != "success":
                return {
                    "status": "error",
                    "error": "Failed to collect live data",
                    "details": orchestration_results
                }
            
            # Step 3: Data Synthesis
            print("--- Phase 3: Data Synthesis ---", flush=True)
            synthesis_results = await self._synthesize_live_data(orchestration_results, research_request)
            
            if synthesis_results.get("status") != "success":
                return {
                    "status": "error",
                    "error": "Failed to synthesize data",
                    "details": synthesis_results
                }
            
            # Step 4: SWOT Analysis
            print("--- Phase 4: SWOT Analysis ---", flush=True)
            swot_results = await self._conduct_swot_analysis(synthesis_results, research_request)
            
            if swot_results.get("status") != "success":
                return {
                    "status": "error",
                    "error": "Failed to conduct SWOT analysis",
                    "details": swot_results
                }
            
            # Step 5: Report Generation
            print("--- Phase 5: Report Generation ---", flush=True)
            final_report = await self._generate_final_report(research_plan, synthesis_results, swot_results)
            
            if final_report.get("status") != "success":
                return {
                    "status": "error",
                    "error": "Failed to generate final report",
                    "details": final_report
                }
            
            print("<<< LIVE research workflow completed successfully.", flush=True)
            
            return {
                "status": "complete",
                "research_results": {
                    "topic": research_request.get("topic"),
                    "research_plan": research_plan.get("research_plan", {}),
                    "live_data_collection": orchestration_results.get("orchestration_results", {}),
                    "data_synthesis": synthesis_results.get("synthesis_results", {}),
                    "swot_analysis": swot_results.get("swot_analysis", {}),
                    "final_report": final_report.get("final_report", {})
                },
                "metadata": {
                    "api_used": "live_data_collection",
                    "workflow_type": "live_multi_agent_research",
                    "research_steps_completed": 5,
                    "data_collection_method": "real_apis_web_scraping_market_data",
                    "timestamp": datetime.now().isoformat()
                },
                "session_state": {
                    "research_request": research_request,
                    "workflow_stage": "completed",
                    "timestamp": asyncio.get_event_loop().time(),
                    "agent_execution_log": [
                        "research_planning", 
                        "live_data_collection", 
                        "data_synthesis", 
                        "swot_analysis", 
                        "final_report"
                    ]
                },
                "session_id": f"live_research_{research_request.get('topic', 'default').replace(' ', '_')}"
            }
            
        except Exception as e:
            print(f"!!! LIVE research workflow failed: {str(e)}", flush=True)
            return {
                "status": "error",
                "error": str(e),
                "session_id": f"live_research_{research_request.get('topic', 'default').replace(' ', '_')}"
            }
    
    async def _create_research_plan(self, research_request: Dict[str, Any]) -> Dict[str, Any]:
        """Create comprehensive research plan."""
        try:
            # Simulate research plan creation (would use actual agent in full implementation)
            research_plan = {
                "research_id": f"research_{research_request.get('topic', 'default').replace(' ', '_')}",
                "topic": research_request.get("topic"),
                "objectives": research_request.get("objectives", [f"Comduct research on {research_request.get('topic')}"]),
                "questions": research_request.get("questions", [f"What are the key aspects of {research_request.get('topic')}?"]),
                "methodology": {
                    "approach": "live_multi_source_research",
                    "frameworks": ["swot_analysis", "market_analysis", "competitive_intelligence"],
                    "sources": [
                        "academic_databases",
                        "financial_markets", 
                        "government_sources",
                        "industry_reports",
                        "news_media"
                    ],
                    "quality_criteria": [
                        "source_credibility",
                        "data_recency",
                        "relevance_to_objectives"
                    ]
                },
                "timeline": {
                    "total_duration": "2-4 hours",
                    "phases": {
                        "planning": "15 minutes",
                        "data_collection": "1-2 hours",
                        "analysis": "30-60 minutes",
                        "reporting": "30 minutes"
                    }
                }
            }
            
            return {
                "status": "success",
                "research_plan": research_plan
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to create research plan: {str(e)}"
            }
    
    async def _orchestrate_live_data_collection(self, research_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrate live data collection from real sources."""
        try:
            # Use the orchestration agent to collect live data
            orchestration_results = await self.orchestration_agent.coordinate_live_research_execution_tool(
                research_plan["research_plan"]
            )
            
            return orchestration_results
            
        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to orchestrate live data collection: {str(e)}"
            }
    
    async def _synthesize_live_data(self, orchestration_results: Dict[str, Any], research_request: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize live collected data."""
        try:
            # Use the synthesis agent to process live data
            from agents.synthesis_agent import synthesize_research_data_tool
            
            # Create a mock tool context
            class MockToolContext:
                def __init__(self):
                    self.state = {"timestamp": datetime.now().isoformat()}
            
            tool_context = MockToolContext()
            
            synthesis_results = synthesize_research_data_tool(
                orchestration_results["orchestration_results"],
                research_request.get("questions", []),
                tool_context
            )
            
            return synthesis_results
            
        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to synthesize live data: {str(e)}"
            }
    
    async def _conduct_swot_analysis(self, synthesis_results: Dict[str, Any], research_request: Dict[str, Any]) -> Dict[str, Any]:
        """Conduct SWOT analysis on synthesized data."""
        try:
            # Use the SWOT analysis agent
            from agents.swot_analysis_agent import conduct_swot_analysis_tool
            
            # Create a mock tool context
            class MockToolContext:
                def __init__(self):
                    self.state = {"timestamp": datetime.now().isoformat()}
            
            tool_context = MockToolContext()
            
            swot_results = conduct_swot_analysis_tool(
                synthesis_results["synthesis_results"],
                research_request.get("topic", "Unknown"),
                tool_context
            )
            
            return swot_results
            
        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to conduct SWOT analysis: {str(e)}"
            }
    
    async def _generate_final_report(self, research_plan: Dict[str, Any], synthesis_results: Dict[str, Any], swot_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate final comprehensive report."""
        try:
            # Use the report generation agent
            from agents.report_generation_agent import generate_comprehensive_report_tool
            
            # Create a mock tool context
            class MockToolContext:
                def __init__(self):
                    self.state = {"timestamp": datetime.now().isoformat()}
            
            tool_context = MockToolContext()
            
            final_report = generate_comprehensive_report_tool(
                research_plan["research_plan"],
                synthesis_results["synthesis_results"],
                swot_results["swot_analysis"],
                tool_context
            )
            
            return final_report
            
        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to generate final report: {str(e)}"
            }
