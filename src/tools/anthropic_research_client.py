"""
Anthropic client for research workflow.
"""

import asyncio
from typing import Dict, Any, List
import anthropic
from config.settings import get_settings


class AnthropicResearchClient:
    """Client for conducting research using Anthropic's Claude API."""
    
    def __init__(self):
        self.settings = get_settings()
        self.client = anthropic.Anthropic(api_key=self.settings.anthropic_api_key)
    
        async def conduct_research(self, research_plan: Dict[str, Any]) -> Dict[str, Any]:
            """Conduct targeted research based on a research plan."""
            
            topic = research_plan.get('topic', 'Unknown Topic')
            questions = research_plan.get('questions', [])
            
            print(f"--- Anthropic: Starting research on '{topic}' ---", flush=True)
            
            prompt = f"""
            You are a research analyst. Conduct research to answer the following questions about {topic}:
    
            Research Questions:
            {"
            ".join(f"- {q}" for q in questions)}
    
            Please provide a detailed research report that answers these questions. Include sources where possible.
            """
            
            research_result = await self._call_claude(prompt)
            print("--- Anthropic: Research completed ---", flush=True)
            
            return {
                "status": "success",
                "research_results": {
                    "topic": topic,
                    "report": research_result
                },
                "metadata": {
                    "api_used": "anthropic_claude",
                    "model": "claude-3-5-sonnet-20240620",
                }
            }    
    async def _call_claude(self, prompt: str) -> str:
        """Make an async call to Claude API."""
        
        # Run the synchronous API call in a thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        
        def _sync_call():
            try:
                response = self.client.messages.create(
                    model="claude-3-5-sonnet-20240620",
                    max_tokens=4000,
                    temperature=0.7,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text
            except Exception as e:
                return f"Error calling Claude API: {str(e)}"
        
        result = await loop.run_in_executor(None, _sync_call)
        return result
