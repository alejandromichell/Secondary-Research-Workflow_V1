"""
Root Orchestrator Agent - Coordinates the entire multi-agent research workflow.

This agent serves as the central coordinator for the research system, managing
the flow between different specialized agents and ensuring proper task execution.
"""

import os
import sys
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# from src.mcp.mcp_client import MCPAgentInterface  # Temporarily disabled for testing
from src.utils.research_plan_tracker import ResearchPlanTracker, TaskStatus, PlanStatus


class RootOrchestratorAgent:
    """Root orchestrator for coordinating multi-agent research workflow."""
    
    def __init__(self):
        self.agent_name = "Root Orchestrator Agent"
        self.agent_role = "Research Workflow Coordinator"
        self.plan_tracker = ResearchPlanTracker()
        # self.mcp_interface = MCPAgentInterface()  # Temporarily disabled for testing
        
        # Load orchestrator instructions
        self.instructions = self._load_instructions()
        
        # Agent registry for delegation
        self.agent_registry = {
            "ResearchPlanAgent": None,  # Will be initialized when needed
            "OrchestrationAgent": None,
            "SynthesisAgent": None,
            "SWOTAnalysisAgent": None,
            "ReportGenerationAgent": None
        }
    
    def _load_instructions(self) -> str:
        """Load the root orchestrator instructions from prompt file."""
        try:
            prompt_path = os.path.join(
                os.path.dirname(__file__), '..', 'prompts', 'root_orchestrator_instruction.txt'
            )
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except FileNotFoundError:
            return "System Role: You are the Secondary Research Workflow Orchestrator."
    
    async def initialize(self):
        """Initialize the MCP interface."""
        await self.mcp_interface.initialize()
        print(f">>> {self.agent_name}: Initialized and ready for coordination", flush=True)
    
    async def cleanup(self):
        """Clean up resources."""
        await self.mcp_interface.cleanup()
        print(f">>> {self.agent_name}: Cleanup completed", flush=True)
    
    async def execute_research_workflow(self, plan_id: str) -> Dict[str, Any]:
        """
        Execute the complete research workflow for a given plan.
        
        Args:
            plan_id: ID of the research plan to execute
            
        Returns:
            Dictionary containing workflow execution results
        """
        try:
            print(f">>> {self.agent_name}: Starting research workflow for plan {plan_id}", flush=True)
            
            # Get the research plan
            plan = self.plan_tracker.get_plan(plan_id)
            if not plan:
                return {"error": f"Research plan {plan_id} not found"}
            
            # Update plan status to active
            plan.status = PlanStatus.ACTIVE
            if not plan.started_at:
                plan.started_at = datetime.now().isoformat()
            
            workflow_results = {
                "plan_id": plan_id,
                "started_at": datetime.now().isoformat(),
                "phases": {},
                "status": "in_progress"
            }
            
            # Phase 1: Research Planning
            print(f">>> {self.agent_name}: Executing Phase 1 - Research Planning", flush=True)
            planning_result = await self._execute_research_planning(plan_id)
            workflow_results["phases"]["research_planning"] = planning_result
            
            if planning_result.get("status") != "success":
                workflow_results["status"] = "failed"
                workflow_results["error"] = "Research planning failed"
                return workflow_results
            
            # Phase 2: Data Collection Planning
            print(f">>> {self.agent_name}: Executing Phase 2 - Data Collection Planning", flush=True)
            collection_planning_result = await self._execute_data_collection_planning(plan_id)
            workflow_results["phases"]["data_collection_planning"] = collection_planning_result
            
            if collection_planning_result.get("status") != "success":
                workflow_results["status"] = "failed"
                workflow_results["error"] = "Data collection planning failed"
                return workflow_results
            
            # Phase 3: Live Data Collection
            print(f">>> {self.agent_name}: Executing Phase 3 - Live Data Collection", flush=True)
            data_collection_result = await self._execute_live_data_collection(plan_id)
            workflow_results["phases"]["live_data_collection"] = data_collection_result
            
            if data_collection_result.get("status") != "success":
                workflow_results["status"] = "failed"
                workflow_results["error"] = "Live data collection failed"
                return workflow_results
            
            # Phase 4: Data Analysis and Synthesis
            print(f">>> {self.agent_name}: Executing Phase 4 - Data Analysis and Synthesis", flush=True)
            synthesis_result = await self._execute_data_synthesis(plan_id)
            workflow_results["phases"]["data_synthesis"] = synthesis_result
            
            if synthesis_result.get("status") != "success":
                workflow_results["status"] = "failed"
                workflow_results["error"] = "Data synthesis failed"
                return workflow_results
            
            # Phase 5: SWOT Analysis
            print(f">>> {self.agent_name}: Executing Phase 5 - SWOT Analysis", flush=True)
            swot_result = await self._execute_swot_analysis(plan_id)
            workflow_results["phases"]["swot_analysis"] = swot_result
            
            if swot_result.get("status") != "success":
                workflow_results["status"] = "failed"
                workflow_results["error"] = "SWOT analysis failed"
                return workflow_results
            
            # Phase 6: Report Generation
            print(f">>> {self.agent_name}: Executing Phase 6 - Report Generation", flush=True)
            report_result = await self._execute_report_generation(plan_id)
            workflow_results["phases"]["report_generation"] = report_result
            
            if report_result.get("status") != "success":
                workflow_results["status"] = "failed"
                workflow_results["error"] = "Report generation failed"
                return workflow_results
            
            # Mark plan as completed
            plan.status = PlanStatus.COMPLETED
            plan.completed_at = datetime.now().isoformat()
            workflow_results["status"] = "completed"
            workflow_results["completed_at"] = datetime.now().isoformat()
            
            print(f">>> {self.agent_name}: Research workflow completed successfully for plan {plan_id}", flush=True)
            
            return workflow_results
            
        except Exception as e:
            print(f">>> {self.agent_name}: Error executing research workflow: {e}", flush=True)
            return {
                "plan_id": plan_id,
                "status": "failed",
                "error": str(e),
                "failed_at": datetime.now().isoformat()
            }
    
    async def _execute_research_planning(self, plan_id: str) -> Dict[str, Any]:
        """Execute research planning phase."""
        try:
            # Get the first task (research planning)
            tasks = self.plan_tracker.get_next_available_tasks(plan_id)
            if not tasks:
                return {"status": "error", "message": "No available tasks for research planning"}
            
            planning_task = tasks[0]  # First task should be research planning
            
            # Start the task
            await self.mcp_interface.start_task(plan_id, planning_task.id, self.agent_name)
            
            # Get research context
            context = await self.mcp_interface.client.get_research_context(
                plan_id  # Using plan_id as session_id for now
            )
            
            # Delegate to Research Plan Agent
            from src.agents.research_plan_agent import ResearchPlanAgent
            research_plan_agent = ResearchPlanAgent()
            await research_plan_agent.initialize()
            
            try:
                result = await research_plan_agent.create_detailed_research_plan(
                    plan_id, context
                )
                
                # Complete the task
                await self.mcp_interface.complete_task(
                    plan_id, planning_task.id, self.agent_name,
                    f"Research plan created successfully: {result.get('plan_summary', 'N/A')}"
                )
                
                return {
                    "status": "success",
                    "task_id": planning_task.id,
                    "result": result
                }
                
            finally:
                await research_plan_agent.cleanup()
                
        except Exception as e:
            print(f">>> {self.agent_name}: Error in research planning: {e}", flush=True)
            return {"status": "error", "message": str(e)}
    
    async def _execute_data_collection_planning(self, plan_id: str) -> Dict[str, Any]:
        """Execute data collection planning phase."""
        try:
            # Get the next available task
            tasks = self.plan_tracker.get_next_available_tasks(plan_id)
            if not tasks:
                return {"status": "error", "message": "No available tasks for data collection planning"}
            
            planning_task = tasks[0]
            
            # Start the task
            await self.mcp_interface.start_task(plan_id, planning_task.id, self.agent_name)
            
            # For now, create a basic data collection strategy
            # This will be enhanced when we implement the Orchestration Agent
            strategy = {
                "data_sources": [
                    "Academic databases (PubMed, ArXiv)",
                    "Financial markets (Yahoo Finance)",
                    "Government sources (FDA, SEC)",
                    "News websites (Reuters, Bloomberg)",
                    "Industry reports and company filings"
                ],
                "collection_methods": [
                    "API queries for structured data",
                    "Web scraping for news and reports",
                    "Real-time market data collection",
                    "Document analysis and extraction"
                ],
                "quality_criteria": {
                    "recency": "Within last 2 years (preferably 12 months)",
                    "authority": "Recognized industry experts and institutions",
                    "relevance": "Directly applicable to research objectives",
                    "objectivity": "Balanced perspective with clear methodology"
                }
            }
            
            # Complete the task
            await self.mcp_interface.complete_task(
                plan_id, planning_task.id, self.agent_name,
                f"Data collection strategy created with {len(strategy['data_sources'])} source types"
            )
            
            return {
                "status": "success",
                "task_id": planning_task.id,
                "strategy": strategy
            }
            
        except Exception as e:
            print(f">>> {self.agent_name}: Error in data collection planning: {e}", flush=True)
            return {"status": "error", "message": str(e)}
    
    async def _execute_live_data_collection(self, plan_id: str) -> Dict[str, Any]:
        """Execute live data collection phase."""
        try:
            # Get the next available task
            tasks = self.plan_tracker.get_next_available_tasks(plan_id)
            if not tasks:
                return {"status": "error", "message": "No available tasks for data collection"}
            
            collection_task = tasks[0]
            
            # Start the task
            await self.mcp_interface.start_task(plan_id, collection_task.id, self.agent_name)
            
            # Delegate to Orchestration Agent
            from src.agents.orchestration_agent import OrchestrationAgent
            orchestration_agent = OrchestrationAgent()
            await orchestration_agent.initialize()
            
            try:
                result = await orchestration_agent.execute_live_data_collection(plan_id)
                
                # Complete the task
                await self.mcp_interface.complete_task(
                    plan_id, collection_task.id, self.agent_name,
                    f"Live data collection completed: {result.get('sources_collected', 0)} sources"
                )
                
                return {
                    "status": "success",
                    "task_id": collection_task.id,
                    "result": result
                }
                
            finally:
                await orchestration_agent.cleanup()
                
        except Exception as e:
            print(f">>> {self.agent_name}: Error in live data collection: {e}", flush=True)
            return {"status": "error", "message": str(e)}
    
    async def _execute_data_synthesis(self, plan_id: str) -> Dict[str, Any]:
        """Execute data synthesis phase."""
        try:
            # Get the next available task
            tasks = self.plan_tracker.get_next_available_tasks(plan_id)
            if not tasks:
                return {"status": "error", "message": "No available tasks for data synthesis"}
            
            synthesis_task = tasks[0]
            
            # Start the task
            await self.mcp_interface.start_task(plan_id, synthesis_task.id, self.agent_name)
            
            # Delegate to Synthesis Agent
            from src.agents.synthesis_agent import SynthesisAgent
            synthesis_agent = SynthesisAgent()
            await synthesis_agent.initialize()
            
            try:
                result = await synthesis_agent.synthesize_research_data(plan_id)
                
                # Complete the task
                await self.mcp_interface.complete_task(
                    plan_id, synthesis_task.id, self.agent_name,
                    f"Data synthesis completed: {result.get('insights_generated', 0)} insights"
                )
                
                return {
                    "status": "success",
                    "task_id": synthesis_task.id,
                    "result": result
                }
                
            finally:
                await synthesis_agent.cleanup()
                
        except Exception as e:
            print(f">>> {self.agent_name}: Error in data synthesis: {e}", flush=True)
            return {"status": "error", "message": str(e)}
    
    async def _execute_swot_analysis(self, plan_id: str) -> Dict[str, Any]:
        """Execute SWOT analysis phase."""
        try:
            # Get the next available task
            tasks = self.plan_tracker.get_next_available_tasks(plan_id)
            if not tasks:
                return {"status": "error", "message": "No available tasks for SWOT analysis"}
            
            swot_task = tasks[0]
            
            # Start the task
            await self.mcp_interface.start_task(plan_id, swot_task.id, self.agent_name)
            
            # Delegate to SWOT Analysis Agent
            from src.agents.swot_analysis_agent import SWOTAnalysisAgent
            swot_agent = SWOTAnalysisAgent()
            await swot_agent.initialize()
            
            try:
                result = await swot_agent.conduct_swot_analysis(plan_id)
                
                # Complete the task
                await self.mcp_interface.complete_task(
                    plan_id, swot_task.id, self.agent_name,
                    f"SWOT analysis completed: {result.get('strategic_recommendations', 0)} recommendations"
                )
                
                return {
                    "status": "success",
                    "task_id": swot_task.id,
                    "result": result
                }
                
            finally:
                await swot_agent.cleanup()
                
        except Exception as e:
            print(f">>> {self.agent_name}: Error in SWOT analysis: {e}", flush=True)
            return {"status": "error", "message": str(e)}
    
    async def _execute_report_generation(self, plan_id: str) -> Dict[str, Any]:
        """Execute report generation phase."""
        try:
            # Get the next available task
            tasks = self.plan_tracker.get_next_available_tasks(plan_id)
            if not tasks:
                return {"status": "error", "message": "No available tasks for report generation"}
            
            report_task = tasks[0]
            
            # Start the task
            await self.mcp_interface.start_task(plan_id, report_task.id, self.agent_name)
            
            # Delegate to Report Generation Agent
            from src.agents.report_generation_agent import ReportGenerationAgent
            report_agent = ReportGenerationAgent()
            await report_agent.initialize()
            
            try:
                result = await report_agent.generate_comprehensive_report(plan_id)
                
                # Complete the task
                await self.mcp_interface.complete_task(
                    plan_id, report_task.id, self.agent_name,
                    f"Report generation completed: {result.get('report_sections', 0)} sections"
                )
                
                return {
                    "status": "success",
                    "task_id": report_task.id,
                    "result": result
                }
                
            finally:
                await report_agent.cleanup()
                
        except Exception as e:
            print(f">>> {self.agent_name}: Error in report generation: {e}", flush=True)
            return {"status": "error", "message": str(e)}
    
    async def get_workflow_status(self, plan_id: str) -> Dict[str, Any]:
        """Get the current status of a research workflow."""
        try:
            progress = self.plan_tracker.get_plan_progress(plan_id)
            return {
                "plan_id": plan_id,
                "progress": progress,
                "workflow_status": "active" if progress["plan_status"] == "active" else "completed"
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def pause_workflow(self, plan_id: str) -> Dict[str, Any]:
        """Pause a research workflow."""
        try:
            plan = self.plan_tracker.get_plan(plan_id)
            if plan:
                plan.status = PlanStatus.PAUSED
                return {"status": "success", "message": f"Workflow for plan {plan_id} paused"}
            else:
                return {"status": "error", "message": "Plan not found"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def resume_workflow(self, plan_id: str) -> Dict[str, Any]:
        """Resume a paused research workflow."""
        try:
            plan = self.plan_tracker.get_plan(plan_id)
            if plan and plan.status == PlanStatus.PAUSED:
                plan.status = PlanStatus.ACTIVE
                return {"status": "success", "message": f"Workflow for plan {plan_id} resumed"}
            else:
                return {"status": "error", "message": "Plan not found or not paused"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
