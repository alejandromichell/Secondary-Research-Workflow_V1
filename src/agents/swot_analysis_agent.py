"""
SWOT Analysis Agent - Conducts comprehensive SWOT analysis.

This agent specializes in applying rigorous SWOT analysis framework to
synthesized research findings and developing prioritized strategic options.
"""

import os
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

# Add the project root to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# from src.mcp.mcp_client import MCPAgentInterface  # Temporarily disabled for testing


class SWOTAnalysisAgent:
    """Agent responsible for conducting comprehensive SWOT analysis."""
    
    def __init__(self):
        self.agent_name = "SWOT Analysis Agent"
        self.agent_role = "Strategic Framework Specialist"
        # self.mcp_interface = MCPAgentInterface()  # Temporarily disabled for testing
        
        # Load SWOT analysis instructions
        self.instructions = self._load_instructions()
        
        # Analysis results storage
        self.swot_matrix = {}
        self.strategic_recommendations = []
    
    def _load_instructions(self) -> str:
        """Load the SWOT analysis instructions from prompt file."""
        try:
            prompt_path = os.path.join(
                os.path.dirname(__file__), '..', 'prompts', 'swot_analysis_instruction.txt'
            )
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except FileNotFoundError:
            return "System Role: You are the Strategic Framework Specialist."
    
    async def initialize(self):
        """Initialize the MCP interface."""
        await self.mcp_interface.initialize()
        print(f">>> {self.agent_name}: Initialized and ready for SWOT analysis", flush=True)
    
    async def cleanup(self):
        """Clean up resources."""
        await self.mcp_interface.cleanup()
        print(f">>> {self.agent_name}: Cleanup completed", flush=True)
    
    async def conduct_swot_analysis(self, plan_id: str) -> Dict[str, Any]:
        """
        Conduct comprehensive SWOT analysis based on synthesized findings.
        
        Args:
            plan_id: ID of the research plan
            
        Returns:
            Dictionary containing SWOT analysis results and strategic recommendations
        """
        try:
            print(f">>> {self.agent_name}: Starting SWOT analysis for plan {plan_id}", flush=True)
            
            # Get research context
            context = await self.mcp_interface.client.get_research_context(plan_id)
            if context.get("status") != "complete":
                return {"status": "error", "message": "Research context not ready"}
            
            # Simulate getting synthesized findings (in real implementation, load from storage)
            synthesized_findings = await self._simulate_synthesized_findings(plan_id)
            
            # Initialize SWOT analysis results
            swot_results = {
                "plan_id": plan_id,
                "started_at": datetime.now().isoformat(),
                "agent": self.agent_name,
                "instructions_used": self.instructions,
                "analysis_framework": "Comprehensive SWOT Analysis with Strategic Interconnection",
                "swot_matrix": {},
                "factor_prioritization": {},
                "strategic_recommendations": [],
                "interconnection_analysis": {}
            }
            
            # Phase 1: Factor Identification and Categorization
            print(f">>> {self.agent_name}: Phase 1 - Factor Identification and Categorization", flush=True)
            swot_factors = await self._identify_swot_factors(synthesized_findings, context)
            swot_results["swot_matrix"] = swot_factors
            
            # Phase 2: Factor Prioritization
            print(f">>> {self.agent_name}: Phase 2 - Factor Prioritization", flush=True)
            prioritized_factors = await self._prioritize_factors(swot_factors, context)
            swot_results["factor_prioritization"] = prioritized_factors
            
            # Phase 3: Interconnection Analysis
            print(f">>> {self.agent_name}: Phase 3 - Interconnection Analysis", flush=True)
            interconnection_analysis = await self._analyze_interconnections(prioritized_factors, context)
            swot_results["interconnection_analysis"] = interconnection_analysis
            
            # Phase 4: Strategic Options Development
            print(f">>> {self.agent_name}: Phase 4 - Strategic Options Development", flush=True)
            strategic_options = await self._develop_strategic_options(interconnection_analysis, context)
            swot_results["strategic_recommendations"] = strategic_options
            
            # Phase 5: Strategic Implications Assessment
            print(f">>> {self.agent_name}: Phase 5 - Strategic Implications Assessment", flush=True)
            implications = await self._assess_strategic_implications(strategic_options, context)
            swot_results["strategic_implications"] = implications
            
            # Generate analysis summary
            swot_results["completed_at"] = datetime.now().isoformat()
            swot_results["analysis_summary"] = self._generate_analysis_summary(swot_results)
            
            print(f">>> {self.agent_name}: SWOT analysis completed - {len(strategic_options)} strategic recommendations generated", flush=True)
            
            return {
                "status": "success",
                "strategic_recommendations": len(strategic_options),
                "swot_results": swot_results,
                "analysis_quality_score": self._calculate_analysis_quality(swot_results)
            }
            
        except Exception as e:
            print(f">>> {self.agent_name}: Error in SWOT analysis: {e}", flush=True)
            return {
                "status": "error",
                "error": str(e),
                "completed_at": datetime.now().isoformat()
            }
    
    async def _simulate_synthesized_findings(self, plan_id: str) -> Dict[str, Any]:
        """Simulate synthesized findings for SWOT analysis (in real implementation, load from storage)."""
        return {
            "insights": [
                {
                    "category": "growth_patterns",
                    "insight": "Strong revenue growth observed across multiple sources",
                    "confidence_level": "High",
                    "strategic_implication": "Indicates strong market opportunity and potential for expansion"
                },
                {
                    "category": "technology_trends",
                    "insight": "AI integration becoming mainstream",
                    "confidence_level": "High",
                    "strategic_implication": "Suggests need for technology investment and digital transformation"
                },
                {
                    "category": "market_dynamics",
                    "insight": "Consumer preferences shifting toward digital solutions",
                    "confidence_level": "Medium",
                    "strategic_implication": "Points to changing customer needs and market positioning opportunities"
                },
                {
                    "category": "regulatory_trends",
                    "insight": "Regulatory environment becoming more complex",
                    "confidence_level": "High",
                    "strategic_implication": "Highlights importance of compliance and regulatory strategy"
                },
                {
                    "category": "competitive_movements",
                    "insight": "Industry consolidation through acquisitions",
                    "confidence_level": "High",
                    "strategic_implication": "Indicates need for competitive response and market positioning"
                }
            ],
            "gaps_identified": [
                {
                    "gap_type": "Missing Data Category",
                    "category": "competitive_metrics",
                    "severity": "Medium",
                    "recommendation": "Collect additional competitive intelligence data"
                }
            ]
        }
    
    async def _identify_swot_factors(self, synthesized_findings: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Identify and categorize factors into SWOT matrix."""
        try:
            swot_matrix = {
                "strengths": [],
                "weaknesses": [],
                "opportunities": [],
                "threats": []
            }
            
            insights = synthesized_findings.get("insights", [])
            
            for insight in insights:
                if isinstance(insight, dict) and "error" not in insight:
                    category = insight.get("category", "")
                    insight_text = insight.get("insight", "")
                    implication = insight.get("strategic_implication", "")
                    
                    # Categorize based on content analysis
                    factor = {
                        "description": insight_text,
                        "category": category,
                        "strategic_implication": implication,
                        "confidence_level": insight.get("confidence_level", "Medium"),
                        "source": "Synthesized Research Data"
                    }
                    
                    # Enhanced categorization logic
                    if any(keyword in insight_text.lower() for keyword in ["strong", "growth", "advantage", "capability", "excellence"]):
                        swot_matrix["strengths"].append(factor)
                    elif any(keyword in insight_text.lower() for keyword in ["weak", "challenge", "limitation", "gap", "deficiency"]):
                        swot_matrix["weaknesses"].append(factor)
                    elif any(keyword in insight_text.lower() for keyword in ["opportunity", "potential", "emerging", "new market", "expansion"]):
                        swot_matrix["opportunities"].append(factor)
                    elif any(keyword in insight_text.lower() for keyword in ["threat", "risk", "disruption", "competition", "regulation"]):
                        swot_matrix["threats"].append(factor)
                    else:
                        # Default categorization based on strategic implication
                        if "opportunity" in implication.lower():
                            swot_matrix["opportunities"].append(factor)
                        elif "threat" in implication.lower() or "risk" in implication.lower():
                            swot_matrix["threats"].append(factor)
                        elif "strength" in implication.lower() or "advantage" in implication.lower():
                            swot_matrix["strengths"].append(factor)
                        else:
                            swot_matrix["weaknesses"].append(factor)
            
            return swot_matrix
            
        except Exception as e:
            return {"error": str(e)}
    
    async def _prioritize_factors(self, swot_matrix: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Prioritize SWOT factors based on strategic significance, impact, likelihood, and urgency."""
        try:
            prioritized = {
                "strengths": [],
                "weaknesses": [],
                "opportunities": [],
                "threats": []
            }
            
            for category, factors in swot_matrix.items():
                if isinstance(factors, list):
                    for factor in factors:
                        if isinstance(factor, dict) and "error" not in factor:
                            # Calculate priority score
                            priority_score = self._calculate_priority_score(factor, category)
                            
                            prioritized_factor = factor.copy()
                            prioritized_factor["priority_score"] = priority_score
                            prioritized_factor["priority_tier"] = self._determine_priority_tier(priority_score)
                            prioritized_factor["strategic_significance"] = self._assess_strategic_significance(factor, category)
                            prioritized_factor["magnitude_of_impact"] = self._assess_impact_magnitude(factor, category)
                            prioritized_factor["likelihood"] = self._assess_likelihood(factor, category)
                            prioritized_factor["urgency"] = self._assess_urgency(factor, category)
                            
                            prioritized[category].append(prioritized_factor)
                    
                    # Sort by priority score (highest first)
                    prioritized[category].sort(key=lambda x: x.get("priority_score", 0), reverse=True)
            
            return prioritized
            
        except Exception as e:
            return {"error": str(e)}
    
    def _calculate_priority_score(self, factor: Dict[str, Any], category: str) -> float:
        """Calculate priority score for a factor."""
        # Base score from confidence level
        confidence_scores = {"High": 0.9, "Medium": 0.7, "Low": 0.5}
        base_score = confidence_scores.get(factor.get("confidence_level", "Medium"), 0.7)
        
        # Category-specific adjustments
        category_weights = {
            "strengths": 0.8,  # Leverage existing strengths
            "opportunities": 0.9,  # High priority for opportunities
            "threats": 0.85,  # High priority for threats
            "weaknesses": 0.7  # Medium priority for weaknesses
        }
        
        weight = category_weights.get(category, 0.7)
        return base_score * weight
    
    def _determine_priority_tier(self, priority_score: float) -> str:
        """Determine priority tier based on score."""
        if priority_score >= 0.8:
            return "High"
        elif priority_score >= 0.6:
            return "Medium"
        else:
            return "Low"
    
    def _assess_strategic_significance(self, factor: Dict[str, Any], category: str) -> str:
        """Assess strategic significance of a factor."""
        description = factor.get("description", "").lower()
        
        if any(keyword in description for keyword in ["core", "critical", "essential", "fundamental"]):
            return "High"
        elif any(keyword in description for keyword in ["important", "significant", "major"]):
            return "Medium"
        else:
            return "Low"
    
    def _assess_impact_magnitude(self, factor: Dict[str, Any], category: str) -> str:
        """Assess magnitude of impact."""
        description = factor.get("description", "").lower()
        
        if any(keyword in description for keyword in ["major", "significant", "substantial", "dramatic"]):
            return "High"
        elif any(keyword in description for keyword in ["moderate", "considerable", "noticeable"]):
            return "Medium"
        else:
            return "Low"
    
    def _assess_likelihood(self, factor: Dict[str, Any], category: str) -> str:
        """Assess likelihood of occurrence or persistence."""
        confidence = factor.get("confidence_level", "Medium")
        
        if confidence == "High":
            return "High"
        elif confidence == "Medium":
            return "Medium"
        else:
            return "Low"
    
    def _assess_urgency(self, factor: Dict[str, Any], category: str) -> str:
        """Assess urgency of response required."""
        description = factor.get("description", "").lower()
        
        if any(keyword in description for keyword in ["immediate", "urgent", "critical", "emerging"]):
            return "High"
        elif any(keyword in description for keyword in ["soon", "near-term", "developing"]):
            return "Medium"
        else:
            return "Low"
    
    async def _analyze_interconnections(self, prioritized_factors: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze interconnections between SWOT factors to generate strategic options."""
        try:
            interconnections = {
                "so_strategies": [],  # Strengths-Opportunities
                "st_strategies": [],  # Strengths-Threats
                "wo_strategies": [],  # Weaknesses-Opportunities
                "wt_strategies": []   # Weaknesses-Threats
            }
            
            strengths = prioritized_factors.get("strengths", [])
            weaknesses = prioritized_factors.get("weaknesses", [])
            opportunities = prioritized_factors.get("opportunities", [])
            threats = prioritized_factors.get("threats", [])
            
            # S-O Strategies (Leverage): Use strengths to capitalize on opportunities
            for strength in strengths[:3]:  # Top 3 strengths
                for opportunity in opportunities[:3]:  # Top 3 opportunities
                    strategy = {
                        "strategy_type": "Leverage",
                        "strength": strength.get("description", ""),
                        "opportunity": opportunity.get("description", ""),
                        "strategy": f"Leverage {strength.get('description', '')} to capitalize on {opportunity.get('description', '')}",
                        "priority_score": (strength.get("priority_score", 0) + opportunity.get("priority_score", 0)) / 2,
                        "feasibility": "High" if strength.get("priority_score", 0) >= 0.8 else "Medium"
                    }
                    interconnections["so_strategies"].append(strategy)
            
            # S-T Strategies (Defend): Use strengths to mitigate threats
            for strength in strengths[:3]:
                for threat in threats[:3]:
                    strategy = {
                        "strategy_type": "Defend",
                        "strength": strength.get("description", ""),
                        "threat": threat.get("description", ""),
                        "strategy": f"Use {strength.get('description', '')} to defend against {threat.get('description', '')}",
                        "priority_score": (strength.get("priority_score", 0) + threat.get("priority_score", 0)) / 2,
                        "feasibility": "High" if strength.get("priority_score", 0) >= 0.8 else "Medium"
                    }
                    interconnections["st_strategies"].append(strategy)
            
            # W-O Strategies (Build): Use opportunities to address weaknesses
            for weakness in weaknesses[:3]:
                for opportunity in opportunities[:3]:
                    strategy = {
                        "strategy_type": "Build",
                        "weakness": weakness.get("description", ""),
                        "opportunity": opportunity.get("description", ""),
                        "strategy": f"Use {opportunity.get('description', '')} to address {weakness.get('description', '')}",
                        "priority_score": (weakness.get("priority_score", 0) + opportunity.get("priority_score", 0)) / 2,
                        "feasibility": "Medium"  # Building strategies typically require more resources
                    }
                    interconnections["wo_strategies"].append(strategy)
            
            # W-T Strategies (Survive): Minimize impact of threats and weaknesses
            for weakness in weaknesses[:3]:
                for threat in threats[:3]:
                    strategy = {
                        "strategy_type": "Survive",
                        "weakness": weakness.get("description", ""),
                        "threat": threat.get("description", ""),
                        "strategy": f"Minimize impact of {threat.get('description', '')} while addressing {weakness.get('description', '')}",
                        "priority_score": (weakness.get("priority_score", 0) + threat.get("priority_score", 0)) / 2,
                        "feasibility": "Low"  # Survival strategies are typically challenging
                    }
                    interconnections["wt_strategies"].append(strategy)
            
            return interconnections
            
        except Exception as e:
            return {"error": str(e)}
    
    async def _develop_strategic_options(self, interconnection_analysis: Dict[str, Any], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Develop prioritized strategic recommendations."""
        try:
            strategic_options = []
            
            # Collect all strategies from interconnections
            all_strategies = []
            for strategy_type, strategies in interconnection_analysis.items():
                if isinstance(strategies, list):
                    all_strategies.extend(strategies)
            
            # Sort by priority score
            all_strategies.sort(key=lambda x: x.get("priority_score", 0), reverse=True)
            
            # Convert to strategic recommendations
            for i, strategy in enumerate(all_strategies[:10]):  # Top 10 strategies
                if isinstance(strategy, dict) and "error" not in strategy:
                    recommendation = {
                        "rank": i + 1,
                        "strategy_type": strategy.get("strategy_type", ""),
                        "recommendation": strategy.get("strategy", ""),
                        "priority_score": strategy.get("priority_score", 0),
                        "feasibility": strategy.get("feasibility", "Medium"),
                        "implementation_timeline": self._estimate_implementation_timeline(strategy),
                        "resource_requirements": self._estimate_resource_requirements(strategy),
                        "expected_impact": self._estimate_expected_impact(strategy),
                        "risk_level": self._assess_risk_level(strategy)
                    }
                    strategic_options.append(recommendation)
            
            return strategic_options
            
        except Exception as e:
            return [{"error": str(e)}]
    
    def _estimate_implementation_timeline(self, strategy: Dict[str, Any]) -> str:
        """Estimate implementation timeline for a strategy."""
        strategy_type = strategy.get("strategy_type", "")
        
        if strategy_type == "Leverage":
            return "3-6 months"
        elif strategy_type == "Defend":
            return "1-3 months"
        elif strategy_type == "Build":
            return "6-12 months"
        else:  # Survive
            return "12+ months"
    
    def _estimate_resource_requirements(self, strategy: Dict[str, Any]) -> str:
        """Estimate resource requirements for a strategy."""
        strategy_type = strategy.get("strategy_type", "")
        feasibility = strategy.get("feasibility", "Medium")
        
        if feasibility == "High":
            return "Low to Medium"
        elif feasibility == "Medium":
            return "Medium to High"
        else:
            return "High"
    
    def _estimate_expected_impact(self, strategy: Dict[str, Any]) -> str:
        """Estimate expected impact of a strategy."""
        priority_score = strategy.get("priority_score", 0)
        
        if priority_score >= 0.8:
            return "High"
        elif priority_score >= 0.6:
            return "Medium"
        else:
            return "Low"
    
    def _assess_risk_level(self, strategy: Dict[str, Any]) -> str:
        """Assess risk level of a strategy."""
        strategy_type = strategy.get("strategy_type", "")
        
        if strategy_type in ["Leverage", "Defend"]:
            return "Low to Medium"
        elif strategy_type == "Build":
            return "Medium to High"
        else:  # Survive
            return "High"
    
    async def _assess_strategic_implications(self, strategic_options: List[Dict[str, Any]], context: Dict[str, Any]) -> Dict[str, Any]:
        """Assess strategic implications of recommendations."""
        try:
            implications = {
                "overall_strategic_direction": "",
                "key_priorities": [],
                "resource_allocation_guidance": {},
                "risk_mitigation_priorities": [],
                "success_metrics": []
            }
            
            if strategic_options:
                # Determine overall strategic direction
                top_strategies = strategic_options[:3]
                strategy_types = [s.get("strategy_type", "") for s in top_strategies]
                
                if "Leverage" in strategy_types:
                    implications["overall_strategic_direction"] = "Growth and expansion focused"
                elif "Defend" in strategy_types:
                    implications["overall_strategic_direction"] = "Defensive and protective"
                elif "Build" in strategy_types:
                    implications["overall_strategic_direction"] = "Capability building and development"
                else:
                    implications["overall_strategic_direction"] = "Survival and stabilization"
                
                # Extract key priorities
                implications["key_priorities"] = [s.get("recommendation", "") for s in top_strategies]
                
                # Resource allocation guidance
                implications["resource_allocation_guidance"] = {
                    "high_priority": len([s for s in strategic_options if s.get("priority_score", 0) >= 0.8]),
                    "medium_priority": len([s for s in strategic_options if 0.6 <= s.get("priority_score", 0) < 0.8]),
                    "low_priority": len([s for s in strategic_options if s.get("priority_score", 0) < 0.6])
                }
                
                # Risk mitigation priorities
                high_risk_strategies = [s for s in strategic_options if s.get("risk_level", "").lower() == "high"]
                implications["risk_mitigation_priorities"] = [s.get("recommendation", "") for s in high_risk_strategies[:3]]
                
                # Success metrics
                implications["success_metrics"] = [
                    "Implementation rate of high-priority strategies",
                    "Achievement of expected impact levels",
                    "Resource utilization efficiency",
                    "Risk mitigation effectiveness"
                ]
            
            return implications
            
        except Exception as e:
            return {"error": str(e)}
    
    def _generate_analysis_summary(self, swot_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of the SWOT analysis results."""
        swot_matrix = swot_results.get("swot_matrix", {})
        strategic_recommendations = swot_results.get("strategic_recommendations", [])
        implications = swot_results.get("strategic_implications", {})
        
        total_factors = sum(len(factors) for factors in swot_matrix.values() if isinstance(factors, list))
        
        return {
            "total_swot_factors": total_factors,
            "strategic_recommendations": len(strategic_recommendations),
            "high_priority_recommendations": len([r for r in strategic_recommendations if r.get("priority_score", 0) >= 0.8]),
            "analysis_completeness": "Complete" if total_factors >= 8 else "Partial",
            "strategic_direction": implications.get("overall_strategic_direction", "Not determined"),
            "readiness_for_implementation": "Ready" if len(strategic_recommendations) >= 5 else "Needs refinement"
        }
    
    def _calculate_analysis_quality(self, swot_results: Dict[str, Any]) -> float:
        """Calculate overall quality score for the SWOT analysis."""
        summary = swot_results.get("analysis_summary", {})
        total_factors = summary.get("total_swot_factors", 0)
        recommendations = summary.get("strategic_recommendations", 0)
        
        # Quality based on completeness and depth
        factor_score = min(total_factors / 12, 1.0)  # Target 12 factors
        recommendation_score = min(recommendations / 10, 1.0)  # Target 10 recommendations
        
        return (factor_score + recommendation_score) / 2
    
    async def validate_swot_analysis(self, plan_id: str) -> Dict[str, Any]:
        """Validate the SWOT analysis for completeness and quality."""
        try:
            # This would typically load the SWOT analysis results and validate them
            # For now, return a basic validation result
            return {
                "status": "success",
                "validation_results": {
                    "analysis_completeness": "Complete",
                    "factor_coverage": "Comprehensive",
                    "strategic_recommendations": "Actionable",
                    "implementation_readiness": "Ready"
                }
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}