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
    
    async def conduct_research(self, research_request: Dict[str, Any]) -> Dict[str, Any]:
        """Conduct comprehensive research on a given topic."""
        
        topic = research_request.get('topic', 'Unknown Topic')
        objectives = research_request.get('objectives', [])
        questions = research_request.get('questions', [])
        
        print(f"--- Anthropic: Starting research on '{topic}' ---", flush=True)
        
        # Step 1: Research Planning
        planning_prompt = f"""
You are a research analyst. Create a comprehensive research plan for the following topic:

Topic: {topic}
Objectives: {', '.join(objectives)}
Questions: {', '.join(questions)}

Please provide:
1. Research methodology
2. Key areas to investigate
3. Data sources to consider
4. Analysis framework
5. Expected deliverables

Format your response as a structured research plan.
"""
        
        planning_result = await self._call_claude(planning_prompt)
        print("--- Anthropic: Research planning completed ---", flush=True)
        
        # Step 2: Data Collection Strategy
        collection_prompt = f"""
Based on the research plan above, create a detailed data collection strategy for: {topic}

Include:
1. Primary data sources
2. Secondary data sources
3. Data collection methods
4. Quality assessment criteria
5. Timeline for data gathering

Focus on practical, actionable data collection approaches.
"""
        
        collection_result = await self._call_claude(collection_prompt)
        print("--- Anthropic: Data collection strategy completed ---", flush=True)
        
        # Step 3: Analysis and Synthesis
        analysis_prompt = f"""
Conduct a comprehensive analysis of: {topic}

Based on the research objectives and questions provided, perform:
1. Market analysis
2. Trend identification
3. Competitive landscape
4. Key insights and findings
5. Risk assessment

Provide detailed analysis with supporting reasoning.
"""
        
        analysis_result = await self._call_claude(analysis_prompt)
        print("--- Anthropic: Analysis and synthesis completed ---", flush=True)
        
        # Step 4: SWOT Analysis
        swot_prompt = f"""
Perform a SWOT analysis for: {topic}

Provide a comprehensive SWOT matrix including:
1. Strengths - Internal positive factors
2. Weaknesses - Internal negative factors  
3. Opportunities - External positive factors
4. Threats - External negative factors

Include specific, actionable insights for each quadrant.
"""
        
        swot_result = await self._call_claude(swot_prompt)
        print("--- Anthropic: SWOT analysis completed ---", flush=True)
        
        # Step 5: Final Report Generation
        report_prompt = f"""
Create a comprehensive research report for: {topic}

Synthesize all the previous analysis into a professional research report including:

1. Executive Summary
2. Research Objectives and Methodology
3. Key Findings
4. Market Analysis
5. SWOT Analysis
6. Recommendations
7. Conclusion
8. References and Data Sources

Make the report detailed, professional, and actionable.
"""
        
        final_report = await self._call_claude(report_prompt)
        print("--- Anthropic: Final report generation completed ---", flush=True)
        
        return {
            "status": "success",
            "research_results": {
                "topic": topic,
                "research_plan": planning_result,
                "data_collection_strategy": collection_result,
                "analysis_and_synthesis": analysis_result,
                "swot_analysis": swot_result,
                "final_report": final_report
            },
            "metadata": {
                "api_used": "anthropic_claude",
                "model": "claude-3-5-sonnet-20240620",
                "research_steps_completed": 5
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
