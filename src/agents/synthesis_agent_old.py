"""
Synthesis Agent - Analyzes and synthesizes collected research data.

This agent specializes in transforming raw collected data into structured,
validated, and standardized findings for SWOT analysis.
"""

import os
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

# Add the project root to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# from src.mcp.mcp_client import MCPAgentInterface  # Temporarily disabled for testing


class SynthesisAgent:
    """Agent responsible for synthesizing and analyzing collected research data."""
    
    def __init__(self):
        self.agent_name = "Synthesis Agent"
        self.agent_role = "Research Synthesis Specialist"
        # self.mcp_interface = MCPAgentInterface()  # Temporarily disabled for testing
        
        # Load synthesis instructions
        self.instructions = self._load_instructions()
        
        # Synthesis results storage
        self.synthesized_findings = {}
        self.data_insights = {}
    
    def _load_instructions(self) -> str:
        """Load the synthesis instructions from prompt file."""
        try:
            prompt_path = os.path.join(
                os.path.dirname(__file__), '..', 'prompts', 'synthesis_agent_instruction.txt'
            )
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except FileNotFoundError:
            return "System Role: You are the Research Synthesis Specialist."
    
    async def initialize(self):
        """Initialize the MCP interface."""
        await self.mcp_interface.initialize()
        print(f">>> {self.agent_name}: Initialized and ready for data synthesis", flush=True)
    
    async def cleanup(self):
        """Clean up resources."""
        await self.mcp_interface.cleanup()
        print(f">>> {self.agent_name}: Cleanup completed", flush=True)
    
    async def synthesize_research_data(self, plan_id: str) -> Dict[str, Any]:
        """
        Synthesize collected research data into structured findings.
        
        Args:
            plan_id: ID of the research plan
            
        Returns:
            Dictionary containing synthesized findings and insights
        """
        try:
            print(f">>> {self.agent_name}: Starting data synthesis for plan {plan_id}", flush=True)
            
            # Get research context
            context = await self.mcp_interface.client.get_research_context(plan_id)
            if context.get("status") != "complete":
                return {"status": "error", "message": "Research context not ready"}
            
            # Simulate getting collected data (in real implementation, this would load from storage)
            collected_data = await self._simulate_collected_data(plan_id)
            
            # Initialize synthesis results
            synthesis_results = {
                "plan_id": plan_id,
                "started_at": datetime.now().isoformat(),
                "agent": self.agent_name,
                "instructions_used": self.instructions,
                "synthesis_framework": "Data Validation and Standardization Framework",
                "findings": {},
                "insights": {},
                "data_quality_assessment": {},
                "gaps_identified": []
            }
            
            # Phase 1: Data Validation
            print(f">>> {self.agent_name}: Phase 1 - Data Validation", flush=True)
            validation_results = await self._validate_collected_data(collected_data)
            synthesis_results["data_quality_assessment"] = validation_results
            
            # Phase 2: Data Standardization
            print(f">>> {self.agent_name}: Phase 2 - Data Standardization", flush=True)
            standardized_data = await self._standardize_data(collected_data)
            synthesis_results["standardized_data"] = standardized_data
            
            # Phase 3: Pattern Recognition and Analysis
            print(f">>> {self.agent_name}: Phase 3 - Pattern Recognition and Analysis", flush=True)
            pattern_analysis = await self._analyze_patterns(standardized_data, context)
            synthesis_results["pattern_analysis"] = pattern_analysis
            
            # Phase 4: Insight Generation
            print(f">>> {self.agent_name}: Phase 4 - Insight Generation", flush=True)
            insights = await self._generate_insights(pattern_analysis, context)
            synthesis_results["insights"] = insights
            
            # Phase 5: Gap Analysis
            print(f">>> {self.agent_name}: Phase 5 - Gap Analysis", flush=True)
            gaps = await self._identify_gaps(standardized_data, context)
            synthesis_results["gaps_identified"] = gaps
            
            # Phase 6: SWOT Factor Preparation
            print(f">>> {self.agent_name}: Phase 6 - SWOT Factor Preparation", flush=True)
            swot_factors = await self._prepare_swot_factors(insights, context)
            synthesis_results["swot_factors"] = swot_factors
            
            # Generate synthesis summary
            synthesis_results["completed_at"] = datetime.now().isoformat()
            synthesis_results["synthesis_summary"] = self._generate_synthesis_summary(synthesis_results)
            
            print(f">>> {self.agent_name}: Data synthesis completed - {len(insights)} insights generated", flush=True)
            
            return {
                "status": "success",
                "insights_generated": len(insights),
                "synthesis_results": synthesis_results,
                "data_quality_score": validation_results.get("overall_quality_score", 0.0)
            }
            
        except Exception as e:
            print(f">>> {self.agent_name}: Error in data synthesis: {e}", flush=True)
            return {
                "status": "error",
                "error": str(e),
                "completed_at": datetime.now().isoformat()
            }
    
    async def _simulate_collected_data(self, plan_id: str) -> Dict[str, Any]:
        """Simulate collected data for synthesis (in real implementation, load from storage)."""
        return {
            "academic": {
                "sources": [
                    {
                        "source": "PubMed",
                        "data_points": [
                            "Market growth rate: 15% annually",
                            "Technology adoption: 60% of companies",
                            "Consumer preference shift: 40% increase in digital solutions"
                        ],
                        "quality_score": 0.92
                    }
                ]
            },
            "financial": {
                "sources": [
                    {
                        "source": "Yahoo Finance",
                        "data_points": [
                            "Market cap growth: $2.3B to $3.1B",
                            "Revenue growth: 25% YoY",
                            "Profit margins: 18% average"
                        ],
                        "quality_score": 0.95
                    }
                ]
            },
            "regulatory": {
                "sources": [
                    {
                        "source": "FDA Database",
                        "data_points": [
                            "New regulations: 3 major updates in 2024",
                            "Compliance requirements: Increased by 20%",
                            "Approval timeline: Average 8 months"
                        ],
                        "quality_score": 0.98
                    }
                ]
            },
            "news": {
                "sources": [
                    {
                        "source": "Reuters",
                        "data_points": [
                            "Industry consolidation: 5 major acquisitions",
                            "New market entrants: 12 startups",
                            "Technology disruption: AI integration accelerating"
                        ],
                        "quality_score": 0.88
                    }
                ]
            }
        }
    
    async def _validate_collected_data(self, collected_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate collected data against quality criteria."""
        try:
            total_sources = 0
            quality_scores = []
            recency_scores = []
            authority_scores = []
            
            for category, data in collected_data.items():
                sources = data.get("sources", [])
                total_sources += len(sources)
                
                for source in sources:
                    quality_scores.append(source.get("quality_score", 0))
                    # Simulate other quality metrics
                    recency_scores.append(0.9)  # Simulated
                    authority_scores.append(0.85)  # Simulated
            
            overall_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
            overall_recency = sum(recency_scores) / len(recency_scores) if recency_scores else 0
            overall_authority = sum(authority_scores) / len(authority_scores) if authority_scores else 0
            
            return {
                "total_sources_validated": total_sources,
                "overall_quality_score": round(overall_quality, 3),
                "recency_score": round(overall_recency, 3),
                "authority_score": round(overall_authority, 3),
                "validation_status": "Passed" if overall_quality >= 0.8 else "Failed",
                "quality_tier": "High" if overall_quality >= 0.9 else "Medium" if overall_quality >= 0.8 else "Low"
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    async def _standardize_data(self, collected_data: Dict[str, Any]) -> Dict[str, Any]:
        """Standardize collected data into consistent formats and metrics."""
        try:
            standardized = {
                "financial_metrics": {},
                "market_metrics": {},
                "technology_metrics": {},
                "regulatory_metrics": {},
                "competitive_metrics": {}
            }
            
            # Process each category and extract standardized metrics
            for category, data in collected_data.items():
                sources = data.get("sources", [])
                
                for source in sources:
                    data_points = source.get("data_points", [])
                    
                    for point in data_points:
                        # Extract and standardize financial metrics
                        if "growth" in point.lower() and "%" in point:
                            standardized["financial_metrics"]["growth_rate"] = point
                        elif "revenue" in point.lower():
                            standardized["financial_metrics"]["revenue"] = point
                        elif "profit" in point.lower():
                            standardized["financial_metrics"]["profitability"] = point
                        
                        # Extract market metrics
                        elif "market" in point.lower():
                            standardized["market_metrics"]["market_size"] = point
                        elif "adoption" in point.lower():
                            standardized["market_metrics"]["adoption_rate"] = point
                        
                        # Extract technology metrics
                        elif "technology" in point.lower() or "ai" in point.lower():
                            standardized["technology_metrics"]["tech_trends"] = point
                        
                        # Extract regulatory metrics
                        elif "regulation" in point.lower() or "compliance" in point.lower():
                            standardized["regulatory_metrics"]["regulatory_changes"] = point
                        
                        # Extract competitive metrics
                        elif "acquisition" in point.lower() or "startup" in point.lower():
                            standardized["competitive_metrics"]["competitive_landscape"] = point
            
            return standardized
            
        except Exception as e:
            return {"error": str(e)}
    
    async def _analyze_patterns(self, standardized_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze patterns and trends in the standardized data."""
        try:
            patterns = {
                "growth_patterns": [],
                "technology_trends": [],
                "market_dynamics": [],
                "regulatory_trends": [],
                "competitive_movements": []
            }
            
            # Analyze financial patterns
            financial_metrics = standardized_data.get("financial_metrics", {})
            if financial_metrics:
                patterns["growth_patterns"].append("Strong revenue growth observed across multiple sources")
                patterns["growth_patterns"].append("Profit margins showing consistent improvement")
            
            # Analyze market patterns
            market_metrics = standardized_data.get("market_metrics", {})
            if market_metrics:
                patterns["market_dynamics"].append("Market adoption accelerating")
                patterns["market_dynamics"].append("Consumer preferences shifting toward digital solutions")
            
            # Analyze technology patterns
            tech_metrics = standardized_data.get("technology_metrics", {})
            if tech_metrics:
                patterns["technology_trends"].append("AI integration becoming mainstream")
                patterns["technology_trends"].append("Technology disruption accelerating")
            
            # Analyze regulatory patterns
            regulatory_metrics = standardized_data.get("regulatory_metrics", {})
            if regulatory_metrics:
                patterns["regulatory_trends"].append("Regulatory environment becoming more complex")
                patterns["regulatory_trends"].append("Compliance requirements increasing")
            
            # Analyze competitive patterns
            competitive_metrics = standardized_data.get("competitive_metrics", {})
            if competitive_metrics:
                patterns["competitive_movements"].append("Industry consolidation through acquisitions")
                patterns["competitive_movements"].append("New entrants disrupting traditional models")
            
            return patterns
            
        except Exception as e:
            return {"error": str(e)}
    
    async def _generate_insights(self, pattern_analysis: Dict[str, Any], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate actionable insights from pattern analysis."""
        try:
            insights = []
            
            # Extract research objectives
            foundation_context = context.get("foundation_context", {})
            research_foundation = foundation_context.get("research_foundation", {})
            critical_questions = research_foundation.get("critical_questions", "")
            
            # Generate insights based on patterns
            for pattern_type, patterns in pattern_analysis.items():
                if patterns and not isinstance(patterns, dict):  # Skip error objects
                    for pattern in patterns:
                        insight = {
                            "category": pattern_type,
                            "insight": pattern,
                            "confidence_level": "High",
                            "supporting_evidence": f"Based on analysis of {pattern_type}",
                            "strategic_implication": self._derive_strategic_implication(pattern, pattern_type),
                            "generated_at": datetime.now().isoformat()
                        }
                        insights.append(insight)
            
            return insights
            
        except Exception as e:
            return [{"error": str(e)}]
    
    def _derive_strategic_implication(self, pattern: str, pattern_type: str) -> str:
        """Derive strategic implications from patterns."""
        implications = {
            "growth_patterns": "Indicates strong market opportunity and potential for expansion",
            "technology_trends": "Suggests need for technology investment and digital transformation",
            "market_dynamics": "Points to changing customer needs and market positioning opportunities",
            "regulatory_trends": "Highlights importance of compliance and regulatory strategy",
            "competitive_movements": "Indicates need for competitive response and market positioning"
        }
        
        return implications.get(pattern_type, "Requires further strategic analysis")
    
    async def _identify_gaps(self, standardized_data: Dict[str, Any], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify gaps in the collected data."""
        try:
            gaps = []
            
            # Check for missing data categories
            required_categories = ["financial_metrics", "market_metrics", "technology_metrics", "regulatory_metrics", "competitive_metrics"]
            
            for category in required_categories:
                if not standardized_data.get(category):
                    gaps.append({
                        "gap_type": "Missing Data Category",
                        "category": category,
                        "severity": "Medium",
                        "recommendation": f"Collect additional data for {category}",
                        "impact": "May limit comprehensive analysis"
                    })
            
            # Check for data quality gaps
            if not standardized_data.get("financial_metrics", {}).get("growth_rate"):
                gaps.append({
                    "gap_type": "Missing Key Metric",
                    "metric": "Growth Rate",
                    "severity": "High",
                    "recommendation": "Obtain specific growth rate data",
                    "impact": "Critical for market analysis"
                })
            
            return gaps
            
        except Exception as e:
            return [{"error": str(e)}]
    
    async def _prepare_swot_factors(self, insights: List[Dict[str, Any]], context: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare factors for SWOT analysis."""
        try:
            swot_factors = {
                "strengths": [],
                "weaknesses": [],
                "opportunities": [],
                "threats": []
            }
            
            # Categorize insights into SWOT factors
            for insight in insights:
                if isinstance(insight, dict) and "error" not in insight:
                    category = insight.get("category", "")
                    insight_text = insight.get("insight", "")
                    
                    # Simple categorization logic (in real implementation, this would be more sophisticated)
                    if "growth" in insight_text.lower() or "strong" in insight_text.lower():
                        swot_factors["strengths"].append(insight)
                    elif "disruption" in insight_text.lower() or "threat" in insight_text.lower():
                        swot_factors["threats"].append(insight)
                    elif "opportunity" in insight_text.lower() or "potential" in insight_text.lower():
                        swot_factors["opportunities"].append(insight)
                    elif "complex" in insight_text.lower() or "challenge" in insight_text.lower():
                        swot_factors["weaknesses"].append(insight)
            
            return swot_factors
            
        except Exception as e:
            return {"error": str(e)}
    
    def _generate_synthesis_summary(self, synthesis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of the synthesis results."""
        insights = synthesis_results.get("insights", [])
        gaps = synthesis_results.get("gaps_identified", [])
        swot_factors = synthesis_results.get("swot_factors", {})
        
        return {
            "total_insights_generated": len(insights),
            "gaps_identified": len(gaps),
            "swot_factors_prepared": sum(len(factors) for factors in swot_factors.values() if isinstance(factors, list)),
            "synthesis_quality": "High" if len(insights) >= 10 else "Medium" if len(insights) >= 5 else "Low",
            "readiness_for_swot": "Ready" if len(insights) >= 5 else "Needs more data"
        }
    
    async def validate_synthesis_results(self, plan_id: str) -> Dict[str, Any]:
        """Validate the synthesis results for completeness and quality."""
        try:
            # This would typically load the synthesis results and validate them
            # For now, return a basic validation result
            return {
                "status": "success",
                "validation_results": {
                    "synthesis_completeness": "Complete",
                    "insight_quality": "High",
                    "swot_readiness": "Ready",
                    "data_coverage": "Comprehensive"
                }
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}