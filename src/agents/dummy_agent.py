"""
A simple dummy agent for debugging the ADK runner.
"""
from google.adk.agents import Agent
from config.settings import get_settings


def dummy_tool(message: str) -> str:
    """A simple tool that prints a message."""
    print(f"--- Dummy Tool Executed with message: {message} ---")
    return f"Tool received message: {message}"


def create_dummy_agent() -> Agent:
    """Creates a simple agent with no sub-agents."""
    settings = get_settings()
    return Agent(
        name="dummy_agent",
        model=settings.default_model,
        description="A simple agent for testing the runner.",
        instruction="Your only job is to call the dummy_tool with the message 'It works!'",
        tools=[dummy_tool]
    )
