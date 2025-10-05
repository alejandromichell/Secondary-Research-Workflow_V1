"""
MCP Client for Multi-Agent Research System Communication.

This module provides a client interface for agents to communicate with the
MCP server and manage research plans and tasks.
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from mcp.client import ClientSession
from mcp.client.stdio import stdio_client


logger = logging.getLogger(__name__)


class ResearchMCPClient:
    """MCP Client for agent communication with the research system."""
    
    def __init__(self, server_command: List[str] = None):
        self.server_command = server_command or ["python", "-m", "src.mcp.mcp_server"]
        self.session: Optional[ClientSession] = None
        self.connected = False
    
    async def connect(self):
        """Connect to the MCP server."""
        try:
            logger.info("Connecting to Research MCP Server...")
            
            # Create stdio client
            self.session = await stdio_client(self.server_command)
            
            # Initialize the session
            await self.session.initialize()
            
            self.connected = True
            logger.info("Connected to Research MCP Server successfully")
            
        except Exception as e:
            logger.error(f"Failed to connect to MCP server: {e}")
            self.connected = False
            raise
    
    async def disconnect(self):
        """Disconnect from the MCP server."""
        if self.session:
            await self.session.close()
            self.connected = False
            logger.info("Disconnected from Research MCP Server")
    
    async def create_research_plan(self, title: str, description: str, session_id: str) -> Dict[str, Any]:
        """Create a new research plan."""
        if not self.connected:
            raise RuntimeError("Not connected to MCP server")
        
        try:
            result = await self.session.call_tool(
                "create_research_plan",
                {
                    "title": title,
                    "description": description,
                    "session_id": session_id
                }
            )
            
            if result.isError:
                raise RuntimeError(f"Tool call failed: {result.content[0].text}")
            
            return json.loads(result.content[0].text)
            
        except Exception as e:
            logger.error(f"Error creating research plan: {e}")
            raise
    
    async def update_task_status(self, plan_id: str, task_id: str, 
                               status: str, notes: Optional[str] = None) -> Dict[str, Any]:
        """Update the status of a research task."""
        if not self.connected:
            raise RuntimeError("Not connected to MCP server")
        
        try:
            arguments = {
                "plan_id": plan_id,
                "task_id": task_id,
                "status": status
            }
            
            if notes:
                arguments["notes"] = notes
            
            result = await self.session.call_tool("update_task_status", arguments)
            
            if result.isError:
                raise RuntimeError(f"Tool call failed: {result.content[0].text}")
            
            return json.loads(result.content[0].text)
            
        except Exception as e:
            logger.error(f"Error updating task status: {e}")
            raise
    
    async def get_plan_progress(self, plan_id: str) -> Dict[str, Any]:
        """Get progress information for a research plan."""
        if not self.connected:
            raise RuntimeError("Not connected to MCP server")
        
        try:
            result = await self.session.call_tool(
                "get_plan_progress",
                {"plan_id": plan_id}
            )
            
            if result.isError:
                raise RuntimeError(f"Tool call failed: {result.content[0].text}")
            
            return json.loads(result.content[0].text)
            
        except Exception as e:
            logger.error(f"Error getting plan progress: {e}")
            raise
    
    async def get_next_available_tasks(self, plan_id: str) -> Dict[str, Any]:
        """Get tasks that are ready to be started."""
        if not self.connected:
            raise RuntimeError("Not connected to MCP server")
        
        try:
            result = await self.session.call_tool(
                "get_next_available_tasks",
                {"plan_id": plan_id}
            )
            
            if result.isError:
                raise RuntimeError(f"Tool call failed: {result.content[0].text}")
            
            return json.loads(result.content[0].text)
            
        except Exception as e:
            logger.error(f"Error getting next available tasks: {e}")
            raise
    
    async def add_task_note(self, plan_id: str, task_id: str, note: str) -> Dict[str, Any]:
        """Add a note to a specific task."""
        if not self.connected:
            raise RuntimeError("Not connected to MCP server")
        
        try:
            result = await self.session.call_tool(
                "add_task_note",
                {
                    "plan_id": plan_id,
                    "task_id": task_id,
                    "note": note
                }
            )
            
            if result.isError:
                raise RuntimeError(f"Tool call failed: {result.content[0].text}")
            
            return json.loads(result.content[0].text)
            
        except Exception as e:
            logger.error(f"Error adding task note: {e}")
            raise
    
    async def get_research_context(self, session_id: str) -> Dict[str, Any]:
        """Get research context from questionnaires."""
        if not self.connected:
            raise RuntimeError("Not connected to MCP server")
        
        try:
            result = await self.session.call_tool(
                "get_research_context",
                {"session_id": session_id}
            )
            
            if result.isError:
                raise RuntimeError(f"Tool call failed: {result.content[0].text}")
            
            return json.loads(result.content[0].text)
            
        except Exception as e:
            logger.error(f"Error getting research context: {e}")
            raise
    
    async def validate_research_readiness(self, session_id: str) -> Dict[str, Any]:
        """Validate if a session is ready for research."""
        if not self.connected:
            raise RuntimeError("Not connected to MCP server")
        
        try:
            result = await self.session.call_tool(
                "validate_research_readiness",
                {"session_id": session_id}
            )
            
            if result.isError:
                raise RuntimeError(f"Tool call failed: {result.content[0].text}")
            
            return json.loads(result.content[0].text)
            
        except Exception as e:
            logger.error(f"Error validating research readiness: {e}")
            raise
    
    async def list_available_tools(self) -> List[str]:
        """List available tools from the MCP server."""
        if not self.connected:
            raise RuntimeError("Not connected to MCP server")
        
        try:
            result = await self.session.list_tools()
            return [tool.name for tool in result.tools]
            
        except Exception as e:
            logger.error(f"Error listing tools: {e}")
            raise
    
    async def list_resources(self) -> List[str]:
        """List available resources from the MCP server."""
        if not self.connected:
            raise RuntimeError("Not connected to MCP server")
        
        try:
            result = await self.session.list_resources()
            return [resource.uri for resource in result.resources]
            
        except Exception as e:
            logger.error(f"Error listing resources: {e}")
            raise


class MCPAgentInterface:
    """Interface for agents to interact with the MCP system."""
    
    def __init__(self):
        self.client = ResearchMCPClient()
        self.connected = False
    
    async def initialize(self):
        """Initialize the MCP connection."""
        await self.client.connect()
        self.connected = True
    
    async def cleanup(self):
        """Clean up the MCP connection."""
        if self.connected:
            await self.client.disconnect()
            self.connected = False
    
    async def start_task(self, plan_id: str, task_id: str, agent_name: str) -> bool:
        """Start working on a task."""
        try:
            result = await self.client.update_task_status(
                plan_id, task_id, "in_progress", 
                f"Started by {agent_name} at {datetime.now().isoformat()}"
            )
            return result.get("success", False)
        except Exception as e:
            logger.error(f"Error starting task: {e}")
            return False
    
    async def complete_task(self, plan_id: str, task_id: str, agent_name: str, 
                          completion_notes: str = "") -> bool:
        """Complete a task."""
        try:
            notes = f"Completed by {agent_name} at {datetime.now().isoformat()}"
            if completion_notes:
                notes += f": {completion_notes}"
            
            result = await self.client.update_task_status(
                plan_id, task_id, "completed", notes
            )
            return result.get("success", False)
        except Exception as e:
            logger.error(f"Error completing task: {e}")
            return False
    
    async def add_task_progress_note(self, plan_id: str, task_id: str, note: str) -> bool:
        """Add a progress note to a task."""
        try:
            result = await self.client.add_task_note(plan_id, task_id, note)
            return result.get("success", False)
        except Exception as e:
            logger.error(f"Error adding task note: {e}")
            return False
    
    async def get_my_next_tasks(self, plan_id: str, agent_name: str) -> List[Dict[str, Any]]:
        """Get next available tasks for a specific agent."""
        try:
            result = await self.client.get_next_available_tasks(plan_id)
            available_tasks = result.get("available_tasks", [])
            
            # Filter tasks assigned to this agent
            my_tasks = [
                task for task in available_tasks 
                if task.get("assigned_agent") == agent_name
            ]
            
            return my_tasks
        except Exception as e:
            logger.error(f"Error getting next tasks: {e}")
            return []
    
    async def get_plan_status(self, plan_id: str) -> Dict[str, Any]:
        """Get the current status of a research plan."""
        try:
            return await self.client.get_plan_progress(plan_id)
        except Exception as e:
            logger.error(f"Error getting plan status: {e}")
            return {"error": str(e)}


# Context manager for easy MCP client usage
class MCPContext:
    """Context manager for MCP client connections."""
    
    def __init__(self):
        self.client = ResearchMCPClient()
    
    async def __aenter__(self):
        await self.client.connect()
        return self.client
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.disconnect()


# Example usage
async def example_usage():
    """Example of how to use the MCP client."""
    async with MCPContext() as client:
        # Create a research plan
        plan_result = await client.create_research_plan(
            "AI Tax Software Market Analysis",
            "Comprehensive analysis of the AI-powered tax preparation software market",
            "test_session_001"
        )
        
        print(f"Created plan: {plan_result}")
        
        # Get next available tasks
        tasks_result = await client.get_next_available_tasks(plan_result["plan_id"])
        print(f"Available tasks: {tasks_result}")
        
        # Update a task status
        if tasks_result["available_tasks"]:
            task = tasks_result["available_tasks"][0]
            update_result = await client.update_task_status(
                plan_result["plan_id"],
                task["id"],
                "in_progress",
                "Starting work on this task"
            )
            print(f"Updated task: {update_result}")


if __name__ == "__main__":
    asyncio.run(example_usage())
