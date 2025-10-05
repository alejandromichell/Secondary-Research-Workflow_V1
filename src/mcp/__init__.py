"""
MCP (Model Context Protocol) Module for Multi-Agent Research System.

This module provides MCP-based communication infrastructure for the multi-agent
research system, including server, client, and tool registry components.
"""

from .mcp_server import ResearchMCPServer
from .mcp_client import ResearchMCPClient, MCPAgentInterface, MCPContext
from .tool_registry import (
    ToolRegistry, ToolDefinition, ToolInstance, ToolCategory, ToolStatus,
    register_tool, create_example_tool_definitions
)

__all__ = [
    "ResearchMCPServer",
    "ResearchMCPClient", 
    "MCPAgentInterface",
    "MCPContext",
    "ToolRegistry",
    "ToolDefinition",
    "ToolInstance", 
    "ToolCategory",
    "ToolStatus",
    "register_tool",
    "create_example_tool_definitions"
]
