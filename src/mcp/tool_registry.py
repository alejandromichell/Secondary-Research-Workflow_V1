"""
Tool Registry System for Multi-Agent Research System.

This module provides a centralized registry for all tools available to agents
in the research system, with discovery and management capabilities.
"""

import json
import os
from typing import Dict, Any, List, Optional, Callable, Type
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
import inspect


class ToolCategory(Enum):
    """Categories of tools in the system."""
    DATA_COLLECTION = "data_collection"
    ANALYSIS = "analysis"
    PLANNING = "planning"
    REPORTING = "reporting"
    COMMUNICATION = "communication"
    VALIDATION = "validation"


class ToolStatus(Enum):
    """Status of tools in the registry."""
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    EXPERIMENTAL = "experimental"
    MAINTENANCE = "maintenance"


@dataclass
class ToolDefinition:
    """Definition of a tool in the registry."""
    id: str
    name: str
    description: str
    category: ToolCategory
    status: ToolStatus
    version: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    required_permissions: List[str]
    estimated_duration: Optional[int] = None  # in minutes
    dependencies: List[str] = None
    tags: List[str] = None
    created_at: str = ""
    updated_at: str = ""
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.created_at == "":
            self.created_at = datetime.now().isoformat()
        if self.updated_at == "":
            self.updated_at = datetime.now().isoformat()
        if self.dependencies is None:
            self.dependencies = []
        if self.tags is None:
            self.tags = []
        if self.metadata is None:
            self.metadata = {}


@dataclass
class ToolInstance:
    """Instance of a tool with its implementation."""
    definition: ToolDefinition
    implementation: Callable
    agent_id: Optional[str] = None
    last_used: Optional[str] = None
    usage_count: int = 0
    success_count: int = 0
    error_count: int = 0


class ToolRegistry:
    """Centralized registry for all research system tools."""
    
    def __init__(self, storage_dir: str = "data/tool_registry"):
        self.storage_dir = storage_dir
        self.tools: Dict[str, ToolInstance] = {}
        self.categories: Dict[ToolCategory, List[str]] = {cat: [] for cat in ToolCategory}
        
        os.makedirs(storage_dir, exist_ok=True)
        self._load_registry()
    
    def register_tool(self, tool_definition: ToolDefinition, implementation: Callable, 
                     agent_id: Optional[str] = None) -> bool:
        """
        Register a new tool in the registry.
        
        Args:
            tool_definition: Definition of the tool
            implementation: Callable that implements the tool
            agent_id: ID of the agent that owns this tool
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate the implementation
            if not callable(implementation):
                raise ValueError("Implementation must be callable")
            
            # Check if tool already exists
            if tool_definition.id in self.tools:
                print(f"Warning: Tool {tool_definition.id} already exists, updating...")
            
            # Create tool instance
            tool_instance = ToolInstance(
                definition=tool_definition,
                implementation=implementation,
                agent_id=agent_id
            )
            
            # Register the tool
            self.tools[tool_definition.id] = tool_instance
            
            # Update categories
            if tool_definition.id not in self.categories[tool_definition.category]:
                self.categories[tool_definition.category].append(tool_definition.id)
            
            # Save to storage
            self._save_registry()
            
            print(f">>> ToolRegistry: Registered tool '{tool_definition.name}' (ID: {tool_definition.id})", flush=True)
            
            return True
            
        except Exception as e:
            print(f">>> ToolRegistry: Error registering tool {tool_definition.id}: {e}", flush=True)
            return False
    
    def unregister_tool(self, tool_id: str) -> bool:
        """Unregister a tool from the registry."""
        try:
            if tool_id not in self.tools:
                return False
            
            tool_instance = self.tools[tool_id]
            category = tool_instance.definition.category
            
            # Remove from categories
            if tool_id in self.categories[category]:
                self.categories[category].remove(tool_id)
            
            # Remove from tools
            del self.tools[tool_id]
            
            # Save to storage
            self._save_registry()
            
            print(f">>> ToolRegistry: Unregistered tool {tool_id}", flush=True)
            
            return True
            
        except Exception as e:
            print(f">>> ToolRegistry: Error unregistering tool {tool_id}: {e}", flush=True)
            return False
    
    def get_tool(self, tool_id: str) -> Optional[ToolInstance]:
        """Get a tool instance by ID."""
        return self.tools.get(tool_id)
    
    def get_tools_by_category(self, category: ToolCategory) -> List[ToolInstance]:
        """Get all tools in a specific category."""
        tool_ids = self.categories.get(category, [])
        return [self.tools[tool_id] for tool_id in tool_ids if tool_id in self.tools]
    
    def get_tools_by_agent(self, agent_id: str) -> List[ToolInstance]:
        """Get all tools owned by a specific agent."""
        return [
            tool for tool in self.tools.values() 
            if tool.agent_id == agent_id
        ]
    
    def get_active_tools(self) -> List[ToolInstance]:
        """Get all active tools."""
        return [
            tool for tool in self.tools.values()
            if tool.definition.status == ToolStatus.ACTIVE
        ]
    
    def search_tools(self, query: str, category: Optional[ToolCategory] = None) -> List[ToolInstance]:
        """Search for tools by name, description, or tags."""
        query_lower = query.lower()
        results = []
        
        for tool in self.tools.values():
            # Filter by category if specified
            if category and tool.definition.category != category:
                continue
            
            # Search in name, description, and tags
            if (query_lower in tool.definition.name.lower() or
                query_lower in tool.definition.description.lower() or
                any(query_lower in tag.lower() for tag in tool.definition.tags)):
                results.append(tool)
        
        return results
    
    def execute_tool(self, tool_id: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool with given arguments.
        
        Args:
            tool_id: ID of the tool to execute
            arguments: Arguments to pass to the tool
            
        Returns:
            Result of tool execution
        """
        try:
            tool_instance = self.get_tool(tool_id)
            if not tool_instance:
                return {"error": f"Tool {tool_id} not found"}
            
            if tool_instance.definition.status != ToolStatus.ACTIVE:
                return {"error": f"Tool {tool_id} is not active (status: {tool_instance.definition.status.value})"}
            
            # Update usage statistics
            tool_instance.last_used = datetime.now().isoformat()
            tool_instance.usage_count += 1
            
            # Execute the tool
            start_time = datetime.now()
            result = tool_instance.implementation(**arguments)
            end_time = datetime.now()
            
            # Calculate execution time
            execution_time = (end_time - start_time).total_seconds()
            
            # Update success count
            tool_instance.success_count += 1
            
            # Save updated statistics
            self._save_registry()
            
            return {
                "success": True,
                "result": result,
                "execution_time_seconds": execution_time,
                "tool_id": tool_id,
                "timestamp": end_time.isoformat()
            }
            
        except Exception as e:
            # Update error count
            if tool_id in self.tools:
                self.tools[tool_id].error_count += 1
                self._save_registry()
            
            return {
                "success": False,
                "error": str(e),
                "tool_id": tool_id,
                "timestamp": datetime.now().isoformat()
            }
    
    def get_tool_statistics(self, tool_id: str) -> Optional[Dict[str, Any]]:
        """Get usage statistics for a tool."""
        tool_instance = self.get_tool(tool_id)
        if not tool_instance:
            return None
        
        return {
            "tool_id": tool_id,
            "tool_name": tool_instance.definition.name,
            "usage_count": tool_instance.usage_count,
            "success_count": tool_instance.success_count,
            "error_count": tool_instance.error_count,
            "success_rate": (tool_instance.success_count / tool_instance.usage_count * 100) if tool_instance.usage_count > 0 else 0,
            "last_used": tool_instance.last_used,
            "agent_id": tool_instance.agent_id
        }
    
    def get_registry_summary(self) -> Dict[str, Any]:
        """Get a summary of the tool registry."""
        total_tools = len(self.tools)
        active_tools = len(self.get_active_tools())
        
        category_counts = {}
        for category in ToolCategory:
            category_counts[category.value] = len(self.categories[category])
        
        total_usage = sum(tool.usage_count for tool in self.tools.values())
        total_success = sum(tool.success_count for tool in self.tools.values())
        total_errors = sum(tool.error_count for tool in self.tools.values())
        
        return {
            "total_tools": total_tools,
            "active_tools": active_tools,
            "category_counts": category_counts,
            "total_usage": total_usage,
            "total_success": total_success,
            "total_errors": total_errors,
            "overall_success_rate": (total_success / total_usage * 100) if total_usage > 0 else 0,
            "last_updated": datetime.now().isoformat()
        }
    
    def _save_registry(self):
        """Save the registry to storage."""
        try:
            registry_data = {
                "tools": {},
                "categories": {cat.value: tool_ids for cat, tool_ids in self.categories.items()},
                "last_updated": datetime.now().isoformat()
            }
            
            # Convert tools to serializable format
            for tool_id, tool_instance in self.tools.items():
                tool_data = {
                    "definition": asdict(tool_instance.definition),
                    "agent_id": tool_instance.agent_id,
                    "last_used": tool_instance.last_used,
                    "usage_count": tool_instance.usage_count,
                    "success_count": tool_instance.success_count,
                    "error_count": tool_instance.error_count
                }
                
                # Convert enums to strings
                tool_data["definition"]["category"] = tool_data["definition"]["category"].value
                tool_data["definition"]["status"] = tool_data["definition"]["status"].value
                
                registry_data["tools"][tool_id] = tool_data
            
            file_path = os.path.join(self.storage_dir, "registry.json")
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(registry_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f">>> ToolRegistry: Error saving registry: {e}", flush=True)
    
    def _load_registry(self):
        """Load the registry from storage."""
        try:
            file_path = os.path.join(self.storage_dir, "registry.json")
            if not os.path.exists(file_path):
                return
            
            with open(file_path, 'r', encoding='utf-8') as f:
                registry_data = json.load(f)
            
            # Load categories
            for cat_str, tool_ids in registry_data.get("categories", {}).items():
                category = ToolCategory(cat_str)
                self.categories[category] = tool_ids
            
            # Note: We don't load tool implementations from storage as they need to be
            # registered at runtime. Only metadata is persisted.
            
        except Exception as e:
            print(f">>> ToolRegistry: Error loading registry: {e}", flush=True)


# Decorator for easy tool registration
def register_tool(tool_definition: ToolDefinition, agent_id: Optional[str] = None):
    """Decorator to register a tool function."""
    def decorator(func):
        registry = ToolRegistry()
        registry.register_tool(tool_definition, func, agent_id)
        return func
    return decorator


# Example tool definitions
def create_example_tool_definitions() -> List[ToolDefinition]:
    """Create example tool definitions for the research system."""
    tools = []
    
    # Data Collection Tools
    tools.append(ToolDefinition(
        id="fetch_financial_data",
        name="Fetch Financial Data",
        description="Fetch real-time financial data from external APIs",
        category=ToolCategory.DATA_COLLECTION,
        status=ToolStatus.ACTIVE,
        version="1.0.0",
        input_schema={
            "type": "object",
            "properties": {
                "symbols": {"type": "array", "items": {"type": "string"}},
                "data_types": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["symbols"]
        },
        output_schema={
            "type": "object",
            "properties": {
                "data": {"type": "object"},
                "timestamp": {"type": "string"}
            }
        },
        required_permissions=["api_access"],
        estimated_duration=5,
        tags=["financial", "api", "real-time"]
    ))
    
    # Analysis Tools
    tools.append(ToolDefinition(
        id="analyze_market_trends",
        name="Analyze Market Trends",
        description="Analyze market trends from collected data",
        category=ToolCategory.ANALYSIS,
        status=ToolStatus.ACTIVE,
        version="1.0.0",
        input_schema={
            "type": "object",
            "properties": {
                "data": {"type": "object"},
                "timeframe": {"type": "string"}
            },
            "required": ["data"]
        },
        output_schema={
            "type": "object",
            "properties": {
                "trends": {"type": "array"},
                "insights": {"type": "array"}
            }
        },
        required_permissions=["analysis"],
        estimated_duration=15,
        tags=["analysis", "trends", "market"]
    ))
    
    return tools
