"""
MCP Server for Multi-Agent Research System Communication.

This module implements an MCP (Model Context Protocol) server to facilitate
communication between different agents in the research system.
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource, Tool, TextContent, ImageContent, EmbeddedResource,
    CallToolRequest, CallToolResult, ListResourcesRequest, ListResourcesResult,
    ListToolsRequest, ListToolsResult, ReadResourceRequest, ReadResourceResult
)

from ..utils.research_plan_tracker import ResearchPlanTracker, TaskStatus, PlanStatus
from ..utils.questionnaire_processor import QuestionnaireProcessor


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ResearchMCPServer:
    """MCP Server for the multi-agent research system."""
    
    def __init__(self):
        self.server = Server("research-workflow-mcp")
        self.plan_tracker = ResearchPlanTracker()
        self.questionnaire_processor = QuestionnaireProcessor()
        self.active_plans: Dict[str, Any] = {}
        
        # Register MCP handlers
        self._register_handlers()
    
    def _register_handlers(self):
        """Register MCP server handlers."""
        
        @self.server.list_tools()
        async def list_tools() -> ListToolsResult:
            """List available tools for agent communication."""
            tools = [
                Tool(
                    name="create_research_plan",
                    description="Create a new research plan based on research context",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "title": {"type": "string", "description": "Title of the research plan"},
                            "description": {"type": "string", "description": "Description of the research plan"},
                            "session_id": {"type": "string", "description": "Session ID with research context"}
                        },
                        "required": ["title", "description", "session_id"]
                    }
                ),
                Tool(
                    name="update_task_status",
                    description="Update the status of a research task",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "plan_id": {"type": "string", "description": "ID of the research plan"},
                            "task_id": {"type": "string", "description": "ID of the task to update"},
                            "status": {"type": "string", "enum": ["pending", "in_progress", "completed", "blocked", "cancelled"]},
                            "notes": {"type": "string", "description": "Optional notes about the status change"}
                        },
                        "required": ["plan_id", "task_id", "status"]
                    }
                ),
                Tool(
                    name="get_plan_progress",
                    description="Get progress information for a research plan",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "plan_id": {"type": "string", "description": "ID of the research plan"}
                        },
                        "required": ["plan_id"]
                    }
                ),
                Tool(
                    name="get_next_available_tasks",
                    description="Get tasks that are ready to be started",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "plan_id": {"type": "string", "description": "ID of the research plan"}
                        },
                        "required": ["plan_id"]
                    }
                ),
                Tool(
                    name="add_task_note",
                    description="Add a note to a specific task",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "plan_id": {"type": "string", "description": "ID of the research plan"},
                            "task_id": {"type": "string", "description": "ID of the task"},
                            "note": {"type": "string", "description": "Note to add"}
                        },
                        "required": ["plan_id", "task_id", "note"]
                    }
                ),
                Tool(
                    name="get_research_context",
                    description="Get research context from questionnaires",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "session_id": {"type": "string", "description": "Session ID"}
                        },
                        "required": ["session_id"]
                    }
                ),
                Tool(
                    name="validate_research_readiness",
                    description="Validate if a session is ready for research",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "session_id": {"type": "string", "description": "Session ID"}
                        },
                        "required": ["session_id"]
                    }
                )
            ]
            
            return ListToolsResult(tools=tools)
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
            """Handle tool calls from agents."""
            try:
                logger.info(f"MCP Tool called: {name} with arguments: {arguments}")
                
                if name == "create_research_plan":
                    return await self._handle_create_research_plan(arguments)
                elif name == "update_task_status":
                    return await self._handle_update_task_status(arguments)
                elif name == "get_plan_progress":
                    return await self._handle_get_plan_progress(arguments)
                elif name == "get_next_available_tasks":
                    return await self._handle_get_next_available_tasks(arguments)
                elif name == "add_task_note":
                    return await self._handle_add_task_note(arguments)
                elif name == "get_research_context":
                    return await self._handle_get_research_context(arguments)
                elif name == "validate_research_readiness":
                    return await self._handle_validate_research_readiness(arguments)
                else:
                    return CallToolResult(
                        content=[TextContent(type="text", text=f"Unknown tool: {name}")],
                        isError=True
                    )
                    
            except Exception as e:
                logger.error(f"Error handling tool call {name}: {e}")
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Error: {str(e)}")],
                    isError=True
                )
        
        @self.server.list_resources()
        async def list_resources() -> ListResourcesResult:
            """List available resources."""
            resources = [
                Resource(
                    uri="research-plans://active",
                    name="Active Research Plans",
                    description="List of currently active research plans",
                    mimeType="application/json"
                ),
                Resource(
                    uri="research-plans://completed",
                    name="Completed Research Plans", 
                    description="List of completed research plans",
                    mimeType="application/json"
                )
            ]
            
            return ListResourcesResult(resources=resources)
        
        @self.server.read_resource()
        async def read_resource(uri: str) -> ReadResourceResult:
            """Read a specific resource."""
            try:
                if uri == "research-plans://active":
                    active_plans = self._get_active_plans()
                    content = TextContent(
                        type="text",
                        text=json.dumps(active_plans, indent=2)
                    )
                elif uri == "research-plans://completed":
                    completed_plans = self._get_completed_plans()
                    content = TextContent(
                        type="text",
                        text=json.dumps(completed_plans, indent=2)
                    )
                else:
                    content = TextContent(
                        type="text",
                        text=f"Unknown resource: {uri}"
                    )
                
                return ReadResourceResult(contents=[content])
                
            except Exception as e:
                logger.error(f"Error reading resource {uri}: {e}")
                return ReadResourceResult(
                    contents=[TextContent(type="text", text=f"Error: {str(e)}")],
                    isError=True
                )
    
    async def _handle_create_research_plan(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Handle research plan creation."""
        try:
            title = arguments["title"]
            description = arguments["description"]
            session_id = arguments["session_id"]
            
            # Get research context
            context = self.questionnaire_processor.get_research_context(session_id)
            if context["status"] != "complete":
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text=f"Research context not ready: {context.get('message', 'Unknown error')}"
                    )],
                    isError=True
                )
            
            # Create research plan
            plan = self.plan_tracker.create_research_plan(title, description, context)
            
            # Store in active plans
            self.active_plans[plan.id] = plan
            
            result = {
                "plan_id": plan.id,
                "title": plan.title,
                "status": plan.status.value,
                "total_tasks": len(plan.tasks),
                "message": f"Research plan '{title}' created successfully with {len(plan.tasks)} tasks"
            }
            
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
            )
            
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error creating research plan: {str(e)}")],
                isError=True
            )
    
    async def _handle_update_task_status(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Handle task status updates."""
        try:
            plan_id = arguments["plan_id"]
            task_id = arguments["task_id"]
            status_str = arguments["status"]
            notes = arguments.get("notes")
            
            status = TaskStatus(status_str)
            success = self.plan_tracker.update_task_status(plan_id, task_id, status, notes)
            
            if success:
                result = {
                    "success": True,
                    "plan_id": plan_id,
                    "task_id": task_id,
                    "new_status": status.value,
                    "message": f"Task {task_id} status updated to {status.value}"
                }
            else:
                result = {
                    "success": False,
                    "message": f"Failed to update task {task_id} status"
                }
            
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
            )
            
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error updating task status: {str(e)}")],
                isError=True
            )
    
    async def _handle_get_plan_progress(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Handle plan progress requests."""
        try:
            plan_id = arguments["plan_id"]
            progress = self.plan_tracker.get_plan_progress(plan_id)
            
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=json.dumps(progress, indent=2)
                )]
            )
            
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error getting plan progress: {str(e)}")],
                isError=True
            )
    
    async def _handle_get_next_available_tasks(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Handle next available tasks requests."""
        try:
            plan_id = arguments["plan_id"]
            tasks = self.plan_tracker.get_next_available_tasks(plan_id)
            
            # Convert tasks to serializable format
            task_data = []
            for task in tasks:
                task_dict = {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "priority": task.priority,
                    "estimated_duration": task.estimated_duration,
                    "assigned_agent": task.assigned_agent,
                    "dependencies": task.dependencies
                }
                task_data.append(task_dict)
            
            result = {
                "plan_id": plan_id,
                "available_tasks": task_data,
                "count": len(task_data)
            }
            
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
            )
            
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error getting next available tasks: {str(e)}")],
                isError=True
            )
    
    async def _handle_add_task_note(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Handle adding task notes."""
        try:
            plan_id = arguments["plan_id"]
            task_id = arguments["task_id"]
            note = arguments["note"]
            
            success = self.plan_tracker.add_task_note(plan_id, task_id, note)
            
            result = {
                "success": success,
                "plan_id": plan_id,
                "task_id": task_id,
                "message": f"Note added to task {task_id}" if success else f"Failed to add note to task {task_id}"
            }
            
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
            )
            
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error adding task note: {str(e)}")],
                isError=True
            )
    
    async def _handle_get_research_context(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Handle research context requests."""
        try:
            session_id = arguments["session_id"]
            context = self.questionnaire_processor.get_research_context(session_id)
            
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=json.dumps(context, indent=2)
                )]
            )
            
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error getting research context: {str(e)}")],
                isError=True
            )
    
    async def _handle_validate_research_readiness(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Handle research readiness validation."""
        try:
            session_id = arguments["session_id"]
            validation = self.questionnaire_processor.validate_research_readiness(session_id)
            
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=json.dumps(validation, indent=2)
                )]
            )
            
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error validating research readiness: {str(e)}")],
                isError=True
            )
    
    def _get_active_plans(self) -> List[Dict[str, Any]]:
        """Get list of active research plans."""
        active_plans = []
        for plan_id, plan in self.active_plans.items():
            if plan.status in [PlanStatus.ACTIVE, PlanStatus.DRAFT]:
                progress = self.plan_tracker.get_plan_progress(plan_id)
                active_plans.append(progress)
        return active_plans
    
    def _get_completed_plans(self) -> List[Dict[str, Any]]:
        """Get list of completed research plans."""
        completed_plans = []
        for plan_id, plan in self.active_plans.items():
            if plan.status == PlanStatus.COMPLETED:
                progress = self.plan_tracker.get_plan_progress(plan_id)
                completed_plans.append(progress)
        return completed_plans
    
    async def run(self):
        """Run the MCP server."""
        logger.info("Starting Research MCP Server...")
        
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="research-workflow-mcp",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=None,
                        experimental_capabilities=None
                    )
                )
            )


async def main():
    """Main entry point for the MCP server."""
    server = ResearchMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
