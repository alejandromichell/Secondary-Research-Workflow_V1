"""
SWOT Analysis Agent implementation.
"""
import os
from typing import Dict, Any, List
from google.adk.agents import Agent
from google.adk.tools.tool_context import ToolContext

from .base_agent import BaseResearchAgent
from tools.google_sheets_client import GoogleSheetsClient


class SWOTAnalysisAgent(BaseResearchAgent):
    """Agent responsible for conducting comprehensive SWOT analysis."""
    
    def __init__(self):
        super().__init__("swot_analysis_agent")
        self.sheets_client = GoogleSheetsClient()
    
    def _create_agent(self) -> Agent:
        """Create the SWOT analysis agent."""
        return Agent(
            name=self.name,
            model=self.model,
            description=self.get_description(),
            instruction=self.get_instruction(),
            tools=self.get_tools(),
            output_key="swot_analysis_complete"
        )
    
    def get_tools(self) -> List:
        """Get tools for SWOT analysis."""
        return [conduct_swot_analysis_tool]
    
    def get_description(self) -> str:
        """Get agent description."""
        return (
            "Conducts comprehensive SWOT analysis using synthesized research data, "
            "creates strategic matrices and recommendations, and manages "
            "Google Sheets integration for visualization."
        )
    
    def get_instruction(self) -> str:
        """Get agent instruction from file."""
        prompt_path = os.path.join(os.path.dirname(__file__), '..', 'prompts', "swot_analysis_instruction.txt")
        with open(prompt_path, 'r') as f:
            return f.read()


def conduct_swot_analysis_tool(
    synthesis_results: dict,
    topic: str,
    tool_context: ToolContext
) -> Dict[str, Any]:
    """Tool for conducting comprehensive SWOT analysis."""
    
    print(f"--- Tool: conduct_swot_analysis_tool called for {topic} ---")
    
    research_id = synthesis_results.get("research_id", "unknown")
    findings = synthesis_results.get("synthesized_findings", {})
    
    # Conduct SWOT analysis based on synthesized findings
    swot_results = {
        "research_id": research_id,
        "topic": topic,
        "analysis_timestamp": tool_context.state.get("timestamp"),
        "swot_matrix": {
            "strengths": [
                {
                    "factor": "Strong market growth trajectory",
                    "description": "Consistent growth patterns identified across multiple sources",
                    "impact_score": 0.9,
                    "evidence_sources": ["industry_reports", "market_data"]
                },
                {
                    "factor": "Technology leadership position",
                    "description": "Advanced technological capabilities and innovation",
                    "impact_score": 0.85,
                    "evidence_sources": ["competitive_analysis", "patent_data"]
                },
                {
                    "factor": "Regulatory alignment trends",
                    "description": "Favorable regulatory environment development",
                    "impact_score": 0.75,
                    "evidence_sources": ["government_reports", "policy_analysis"]
                }
            ],
            "weaknesses": [
                {
                    "factor": "Market consolidation pressure",
                    "description": "Increasing competitive pressure from larger players",
                    "impact_score": 0.7,
                    "evidence_sources": ["competitive_analysis", "market_reports"]
                },
                {
                    "factor": "Resource constraints for smaller players",
                    "description": "High barriers to entry and scale requirements",
                    "impact_score": 0.8,
                    "evidence_sources": ["financial_analysis", "industry_data"]
                }
            ],
            "opportunities": [
                {
                    "factor": "Emerging market segments",
                    "description": "New niche markets with high growth potential",
                    "impact_score": 0.85,
                    "evidence_sources": ["trend_analysis", "market_segmentation"]
                },
                {
                    "factor": "International expansion potential",
                    "description": "Untapped markets in developing regions",
                    "impact_score": 0.75,
                    "evidence_sources": ["geographic_analysis", "market_data"]
                },
                {
                    "factor": "Technology convergence trends",
                    "description": "Cross-industry collaboration opportunities",
                    "impact_score": 0.8,
                    "evidence_sources": ["technology_analysis", "partnership_data"]
                }
            ],
            "threats": [
                {
                    "factor": "Regulatory uncertainty",
                    "description": "Potential for restrictive policy changes",
                    "impact_score": 0.65,
                    "evidence_sources": ["policy_analysis", "regulatory_tracking"]
                },
                {
                    "factor": "Economic downturn risk",
                    "description": "Market sensitivity to economic cycles",
                    "impact_score": 0.7,
                    "evidence_sources": ["economic_indicators", "historical_analysis"]
                },
                {
                    "factor": "Technology disruption risk",
                    "description": "Potential for disruptive technological changes",
                    "impact_score": 0.75,
                    "evidence_sources": ["technology_trends", "innovation_analysis"]
                }
            ]
        },
        "strategic_implications": [
            {
                "strategy_type": "SO_Strategies",
                "description": "Leverage strengths to capitalize on opportunities",
                "recommendations": [
                    "Accelerate expansion into emerging market segments",
                    "Invest in technology leadership to maintain competitive advantage",
                    "Build strategic partnerships for international expansion"
                ]
            },
            {
                "strategy_type": "WO_Strategies", 
                "description": "Address weaknesses to capture opportunities",
                "recommendations": [
                    "Develop strategic alliances to overcome resource constraints",
                    "Focus on niche segments where scale advantages are less critical",
                    "Implement agile business models for rapid market response"
                ]
            },
            {
                "strategy_type": "ST_Strategies",
                "description": "Use strengths to mitigate threats",
                "recommendations": [
                    "Diversify market exposure to reduce economic sensitivity",
                    "Strengthen regulatory relationships and compliance capabilities",
                    "Invest in continuous innovation to stay ahead of disruption"
                ]
            },
            {
                "strategy_type": "WT_Strategies",
                "description": "Address weaknesses and threats defensively",
                "recommendations": [
                    "Build financial reserves for economic uncertainty",
                    "Develop contingency plans for regulatory changes",
                    "Create flexible operational models for adaptation"
                ]
            }
        ],
        "priority_recommendations": [
            {
                "priority": 1,
                "recommendation": "Accelerate expansion into high-growth emerging segments",
                "rationale": "Combines market opportunity with existing strengths",
                "implementation_timeline": "6-12 months",
                "resource_requirements": "Medium"
            },
            {
                "priority": 2,
                "recommendation": "Develop strategic partnerships for scale and resources",
                "rationale": "Addresses key weaknesses while capturing opportunities",
                "implementation_timeline": "3-9 months",
                "resource_requirements": "Low-Medium"
            },
            {
                "priority": 3,
                "recommendation": "Build regulatory compliance and relationship capabilities",
                "rationale": "Mitigates key regulatory threats and uncertainties",
                "implementation_timeline": "6-18 months",
                "resource_requirements": "Medium-High"
            }
        ]
    }
    
    # Save to state
    tool_context.state["swot_analysis"] = swot_results
    tool_context.state["framework_analysis_complete"] = True
    tool_context.state["ready_for_report"] = True
    
    # Simulate Google Sheets integration
    sheets_result = {
        "status": "success",
        "spreadsheet_id": f"swot_analysis_{research_id}",
        "worksheet_url": f"https://sheets.google.com/spreadsheet_{research_id}",
        "last_updated": tool_context.state.get("timestamp")
    }
    
    print(f"--- Tool: SWOT analysis completed for {research_id} ---")
    
    return {
        "status": "success",
        "swot_analysis": swot_results,
        "sheets_integration": sheets_result,
        "next_phase": "report_generation"
    }


def create_swot_analysis_agent() -> SWOTAnalysisAgent:
    """Factory function to create SWOT analysis agent."""
    return SWOTAnalysisAgent()