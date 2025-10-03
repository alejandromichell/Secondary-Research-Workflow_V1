"""
Safety callback implementations for workflow protection.
"""

from typing import Optional
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.genai import types


def research_quality_guardrail(
    callback_context: CallbackContext, 
    llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """Ensures research requests meet minimum quality standards."""
    
    agent_name = callback_context.agent_name
    print(f"--- Safety: Quality guardrail checking for {agent_name} ---")
    
    # Extract the latest user message
    last_user_message = ""
    if llm_request.contents:
        for content in reversed(llm_request.contents):
            if content.role == 'user' and content.parts:
                last_user_message = content.parts[0].text
                break
    
    # Quality checks
    if len(last_user_message) < 50:
        print("--- Safety: Request too brief, blocking ---")
        return LlmResponse(
            content=types.Content(
                role="model",
                parts=[types.Part(text="Research request is too brief. Please provide detailed objectives, specific questions, and context for comprehensive analysis.")]
            )
        )
    
    # Check for minimum research structure
    required_terms = ["objective", "question", "analysis", "research"]
    if not any(term in last_user_message.lower() for term in required_terms):
        print("--- Safety: Missing research structure, blocking ---")
        return LlmResponse(
            content=types.Content(
                role="model",
                parts=[types.Part(text="Please structure your request with clear research objectives, specific questions, and desired analysis outcomes.")]
            )
        )
    
    print(f"--- Safety: Quality check passed for {agent_name} ---")
    return None  # Allow request to proceed


def tool_usage_monitor(tool, args, tool_context):
    """Monitors tool usage for rate limiting and quality assurance."""
    
    tool_name = tool.name
    agent_name = tool_context.agent_name
    
    print(f"--- Monitor: Tool {tool_name} called by {agent_name} ---")
    
    # Initialize usage log if not exists
    if "tool_usage_log" not in tool_context.state:
        tool_context.state["tool_usage_log"] = []
    
    # Log tool usage
    import time
    usage_entry = {
        "tool": tool_name,
        "agent": agent_name,
        "timestamp": time.time(),
        "args_summary": {k: str(v)[:100] for k, v in args.items()}
    }
    tool_context.state["tool_usage_log"].append(usage_entry)
    
    # Rate limiting check (10 tool calls per 5 minutes per agent)
    current_time = time.time()
    recent_usage = [
        log for log in tool_context.state["tool_usage_log"]
        if current_time - log["timestamp"] < 300 and log["agent"] == agent_name
    ]
    
    if len(recent_usage) > 10:
        print(f"--- Monitor: Rate limit exceeded for {agent_name} ---")
        return {
            "status": "error",
            "error_message": f"Rate limit exceeded for {agent_name}. Please wait before making more requests."
        }
    
    # Validate tool arguments
    if tool_name == "create_research_plan_tool":
        if not args.get("topic") or not args.get("objectives"):
            return {
                "status": "error", 
                "error_message": "Research plan requires topic and objectives"
            }
    
    print(f"--- Monitor: Tool usage approved for {tool_name} ---")
    return None  # Allow tool execution