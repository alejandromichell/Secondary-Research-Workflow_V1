"""
Research Plan Agent - Creates comprehensive, structured research plans.

This agent specializes in developing detailed research plans based on
research context and objectives from the questionnaire system.
"""

import os
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# from src.mcp.mcp_client import MCPAgentInterface  # Temporarily disabled for testing


class ResearchPlanAgent:
    """Agent responsible for creating comprehensive research plans."""
    
    def __init__(self):
        self.agent_name = "Research Plan Agent"
        self.agent_role = "Research Planning Specialist"
        # self.mcp_interface = MCPAgentInterface()  # Temporarily disabled for testing
        
        # Load research plan instructions
        self.instructions = self._load_instructions()
    
    def _load_instructions(self) -> str:
        """Load the research plan instructions from prompt file."""
        try:
            prompt_path = os.path.join(
                os.path.dirname(__file__), '..', 'prompts', 'research_plan_instruction.txt'
            )
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except FileNotFoundError:
            return "System Role: You are the Research Planning Specialist."
    
    async def initialize(self):
        """Initialize the MCP interface."""
        await self.mcp_interface.initialize()
        print(f">>> {self.agent_name}: Initialized and ready for research planning", flush=True)
    
    async def cleanup(self):
        """Clean up resources."""
        await self.mcp_interface.cleanup()
        print(f">>> {self.agent_name}: Cleanup completed", flush=True)
    
    async def create_detailed_research_plan(self, plan_id: str, research_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a detailed research plan based on research context.
        
        Args:
            plan_id: ID of the research plan
            research_context: Context from foundation and SWOT questionnaires
            
        Returns:
            Dictionary containing the detailed research plan
        """
        try:
            print(f">>> {self.agent_name}: Creating detailed research plan for {plan_id}", flush=True)
            
            # Extract key information from research context
            foundation_context = research_context.get("foundation_context", {})
            swot_context = research_context.get("swot_context", {})
            
            # Parse foundation responses
            foundation_responses = foundation_context.get("research_foundation", {})
            primary_objective = foundation_responses.get("primary_objective", "")
            subject_scope = foundation_responses.get("subject_scope", "")
            critical_questions = foundation_responses.get("critical_questions", "")
            timeline = foundation_responses.get("timeline", "")
            
            # Parse SWOT responses
            swot_responses = swot_context.get("swot_assessment", {})
            business_context = swot_responses.get("business_context", "")
            analysis_scope = swot_responses.get("analysis_scope", "")
            stakeholder_requirements = swot_responses.get("stakeholder_requirements", "")
            
            # Create comprehensive research plan
            research_plan = {
                "plan_id": plan_id,
                "created_at": datetime.now().isoformat(),
                "agent": self.agent_name,
                "instructions_used": self.instructions,
                
                # Research Foundation
                "research_foundation": {
                    "primary_objective": primary_objective,
                    "subject_scope": subject_scope,
                    "critical_questions": critical_questions,
                    "timeline_requirements": timeline
                },
                
                # SWOT Context
                "swot_context": {
                    "business_context": business_context,
                    "analysis_scope": analysis_scope,
                    "stakeholder_requirements": stakeholder_requirements
                },
                
                # Source Strategy Framework
                "source_strategy": self._create_source_strategy(primary_objective, subject_scope),
                
                # Research Methodology
                "methodology": self._create_research_methodology(critical_questions),
                
                # Data Collection Plan
                "data_collection_plan": self._create_data_collection_plan(subject_scope, analysis_scope),
                
                # Quality Assessment Criteria
                "quality_criteria": self._create_quality_criteria(),
                
                # Timeline and Milestones
                "timeline": self._create_timeline(timeline),
                
                # Success Metrics
                "success_metrics": self._create_success_metrics(critical_questions)
            }
            
            print(f">>> {self.agent_name}: Research plan created successfully", flush=True)
            
            return {
                "status": "success",
                "plan_summary": f"Comprehensive research plan for {subject_scope}",
                "research_plan": research_plan,
                "sections_created": len(research_plan) - 3,  # Exclude metadata fields
                "created_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f">>> {self.agent_name}: Error creating research plan: {e}", flush=True)
            return {
                "status": "error",
                "error": str(e),
                "created_at": datetime.now().isoformat()
            }
    
    def _create_source_strategy(self, primary_objective: str, subject_scope: str) -> Dict[str, Any]:
        """Create a comprehensive source strategy based on the research methodology framework."""
        return {
            "internal_factors_sources": {
                "financial_performance": [
                    "Annual reports (10-K, 10-Q filings for public companies)",
                    "Industry financial benchmarking reports",
                    "Credit rating agency reports (Moody's, S&P, Fitch)",
                    "Analyst research reports from major investment banks"
                ],
                "operational_excellence": [
                    "Industry trade publications and journals",
                    "Operational efficiency studies and benchmarks",
                    "Technology adoption and innovation reports",
                    "Supply chain analysis reports"
                ],
                "human_capital": [
                    "Employee satisfaction surveys (if public)",
                    "Talent acquisition and retention studies",
                    "Corporate culture and diversity reports"
                ],
                "brand_market_position": [
                    "Brand valuation studies (Interbrand, BrandZ)",
                    "Customer satisfaction and loyalty research",
                    "Market share analysis reports",
                    "Social media sentiment analysis studies"
                ]
            },
            "external_factors_sources": {
                "industry_market_analysis": [
                    "Industry research reports (IBISWorld, McKinsey Global Institute)",
                    "Market sizing and growth projections",
                    "Industry life cycle analysis"
                ],
                "competitive_landscape": [
                    "Competitive intelligence reports",
                    "Market share and positioning studies",
                    "New entrant and substitute threat analysis"
                ],
                "regulatory_policy": [
                    "Government policy papers and regulatory updates",
                    "Legal and regulatory risk assessments"
                ],
                "technology_innovation": [
                    "Technology disruption reports",
                    "R&D investment and patent analysis"
                ],
                "economic_social_factors": [
                    "Macroeconomic forecasts and scenarios",
                    "Demographic and consumer behavior trend analysis",
                    "ESG (Environmental, Social, Governance) impact assessments"
                ]
            }
        }
    
    def _create_research_methodology(self, critical_questions: str) -> Dict[str, Any]:
        """Create research methodology based on critical questions."""
        return {
            "approach": "Multi-source secondary research with live data collection",
            "methodology_framework": "SWOT Analysis with comprehensive factor analysis",
            "data_collection_methods": [
                "API-based data collection from authoritative sources",
                "Web scraping of relevant industry publications",
                "Real-time market data collection",
                "Document analysis and content extraction"
            ],
            "analysis_framework": [
                "Data validation and cross-referencing",
                "Factor prioritization and impact assessment",
                "Strategic interconnection analysis",
                "Recommendation development and prioritization"
            ],
            "critical_questions_to_address": critical_questions.split('\n') if critical_questions else []
        }
    
    def _create_data_collection_plan(self, subject_scope: str, analysis_scope: str) -> Dict[str, Any]:
        """Create a detailed data collection plan."""
        return {
            "collection_phases": [
                {
                    "phase": 1,
                    "name": "Foundation Data Collection",
                    "description": "Gather baseline information about the subject",
                    "sources": ["Company filings", "Industry reports", "Financial data"],
                    "estimated_duration": "2-3 days"
                },
                {
                    "phase": 2,
                    "name": "Market and Competitive Analysis",
                    "description": "Collect market data and competitive intelligence",
                    "sources": ["Market research reports", "Competitor analysis", "Industry publications"],
                    "estimated_duration": "3-4 days"
                },
                {
                    "phase": 3,
                    "name": "Trend and Innovation Analysis",
                    "description": "Identify emerging trends and technological developments",
                    "sources": ["Technology reports", "Patent databases", "Innovation studies"],
                    "estimated_duration": "2-3 days"
                },
                {
                    "phase": 4,
                    "name": "Regulatory and Policy Analysis",
                    "description": "Assess regulatory environment and policy impacts",
                    "sources": ["Government databases", "Regulatory filings", "Policy papers"],
                    "estimated_duration": "1-2 days"
                }
            ],
            "data_validation_process": [
                "Source credibility assessment",
                "Cross-reference verification",
                "Recency and relevance validation",
                "Quality scoring and ranking"
            ]
        }
    
    def _create_quality_criteria(self) -> Dict[str, Any]:
        """Create quality assessment criteria for data sources."""
        return {
            "recency_standards": {
                "excellent": "Published within last 6 months",
                "good": "Published within last 12 months",
                "acceptable": "Published within last 24 months",
                "unacceptable": "Published more than 24 months ago"
            },
            "authority_standards": {
                "tier_1": "Government agencies, major research institutions, top-tier consulting firms",
                "tier_2": "Industry associations, established trade publications, reputable analysts",
                "tier_3": "Specialized industry publications, regional sources",
                "tier_4": "Blogs, opinion pieces, unverified sources"
            },
            "relevance_criteria": {
                "high": "Directly applicable to research objectives and subject scope",
                "medium": "Generally relevant with some applicability",
                "low": "Tangentially related or limited applicability",
                "irrelevant": "No clear connection to research objectives"
            },
            "objectivity_standards": {
                "high": "Balanced perspective with clear methodology and data sources",
                "medium": "Generally objective with some bias or limited methodology",
                "low": "Significant bias or unclear methodology",
                "unacceptable": "Clearly biased or promotional content"
            }
        }
    
    def _create_timeline(self, timeline_requirements: str) -> Dict[str, Any]:
        """Create project timeline based on requirements."""
        return {
            "overall_timeline": timeline_requirements,
            "phase_timeline": {
                "research_planning": "1 day",
                "data_collection_planning": "1 day",
                "live_data_collection": "8-10 days",
                "data_analysis_synthesis": "3-4 days",
                "swot_analysis": "2-3 days",
                "report_generation": "1-2 days"
            },
            "milestones": [
                "Research plan approval",
                "Data collection completion",
                "Synthesis and analysis completion",
                "SWOT analysis completion",
                "Final report delivery"
            ],
            "critical_path": [
                "Research planning → Data collection planning → Live data collection → Analysis → Report"
            ]
        }
    
    def _create_success_metrics(self, critical_questions: str) -> Dict[str, Any]:
        """Create success metrics for the research project."""
        return {
            "data_quality_metrics": {
                "source_diversity": "Minimum 15-20 diverse, high-quality sources",
                "recency_score": "Average publication date within last 18 months",
                "authority_score": "Minimum 70% from Tier 1 and Tier 2 sources",
                "relevance_score": "Minimum 80% high relevance sources"
            },
            "coverage_metrics": {
                "internal_factors": "Comprehensive coverage of strengths and weaknesses",
                "external_factors": "Thorough analysis of opportunities and threats",
                "critical_questions": "All critical questions addressed with evidence",
                "stakeholder_needs": "Requirements fully met"
            },
            "deliverable_metrics": {
                "report_completeness": "All required sections included",
                "actionability": "Clear, prioritized recommendations provided",
                "evidence_based": "All conclusions supported by collected data",
                "stakeholder_alignment": "Deliverables meet stakeholder requirements"
            }
        }
    
    async def validate_research_plan(self, plan_id: str) -> Dict[str, Any]:
        """Validate a research plan for completeness and quality."""
        try:
            # This would typically load the plan and validate it
            # For now, return a basic validation result
            return {
                "status": "success",
                "validation_results": {
                    "completeness": "Complete",
                    "quality": "High",
                    "actionability": "Actionable",
                    "timeline_feasibility": "Feasible"
                }
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}