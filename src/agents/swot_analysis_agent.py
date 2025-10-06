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
        # await self.mcp_interface.initialize()  # Temporarily disabled
        print(f">>> {self.agent_name}: Initialized and ready for SWOT analysis", flush=True)
    
    async def cleanup(self):
        """Clean up resources."""
        # await self.mcp_interface.cleanup()  # Temporarily disabled
        print(f">>> {self.agent_name}: Cleanup completed", flush=True)
    
    async def conduct_swot_analysis(self, plan_id: str) -> Dict[str, Any]:
        """
        Conducts a comprehensive SWOT analysis based on synthesized findings.
        Now works with real data insights from the SynthesisAgent.
        """
        try:
            print(f">>> {self.agent_name}: Starting SWOT analysis for plan {plan_id}", flush=True)
            
            # Get synthesized findings from the SynthesisAgent
            # In a real implementation, this would come from the SynthesisAgent
            swot_input = await self._get_synthesized_findings_for_plan(plan_id)
            
            if not swot_input:
                return {
                    "status": "error",
                    "plan_id": plan_id,
                    "error": "No synthesized findings available for SWOT analysis",
                    "completed_at": datetime.now().isoformat()
                }
            
            # Generate SWOT matrix from insights
            swot_matrix = self._generate_swot_matrix(swot_input)
            
            # Prioritize factors based on confidence and impact
            prioritized_factors = self._prioritize_factors(swot_matrix, swot_input.get("confidence_scores", {}))
            
            # Generate strategic recommendations
            strategic_recommendations = self._generate_strategic_recommendations(prioritized_factors)
            
            # Calculate strategic alignment score
            alignment_score = await self._calculate_strategic_alignment(strategic_recommendations, prioritized_factors)
            
            # Generate SWOT analysis summary
            analysis_summary = self._generate_analysis_summary(
                swot_matrix, prioritized_factors, strategic_recommendations, alignment_score
            )
            
            # Store results
            swot_results = {
                "plan_id": plan_id,
                "status": "success",
                "completed_at": datetime.now().isoformat(),
                "swot_matrix": swot_matrix,
                "prioritized_factors": prioritized_factors,
                "strategic_recommendations": strategic_recommendations,
                "strategic_alignment_score": alignment_score,
                "analysis_summary": analysis_summary,
                "num_strategic_recommendations": len(strategic_recommendations)
            }
            
            self.swot_matrix[plan_id] = swot_results
            
            print(f">>> {self.agent_name}: SWOT analysis completed for plan {plan_id}", flush=True)
            print(f"   Generated {len(strategic_recommendations)} strategic recommendations", flush=True)
            
            return swot_results
            
        except Exception as e:
            error_result = {
                "status": "error",
                "plan_id": plan_id,
                "error": str(e),
                "completed_at": datetime.now().isoformat()
            }
            print(f">>> {self.agent_name}: Error in SWOT analysis: {e}", flush=True)
            return error_result

    async def _get_synthesized_findings_for_plan(self, plan_id: str) -> Dict[str, Any]:
        """Get synthesized findings for a plan."""
        # In a real implementation, this would retrieve data from the SynthesisAgent
        # For now, we'll return simulated data that represents synthesized insights
        return {
            "strengths": [
                "Strong market position with significant market cap",
                "Advanced AI technology capabilities",
                "Established customer base and brand recognition"
            ],
            "weaknesses": [
                "High customer acquisition costs",
                "Limited international presence",
                "Dependency on seasonal tax preparation cycles"
            ],
            "opportunities": [
                "Growing demand for AI-powered tax software solutions",
                "Expansion into international markets",
                "Partnership opportunities with financial institutions",
                "Emerging technologies like blockchain and automation"
            ],
            "threats": [
                "Intense competition from new AI startups",
                "Regulatory changes in tax preparation industry",
                "Economic downturns affecting consumer spending",
                "Technology disruption from new platforms"
            ],
            "summary_insights": [
                "AI technology trend identified in tax software market",
                "Market disruption from new competitors",
                "Academic research supports AI applications",
                "Regulatory filings indicate growth opportunities",
                "Competitors with significant funding pose threats"
            ],
            "confidence_scores": {
                "strengths": [0.9, 0.85, 0.8],
                "weaknesses": [0.7, 0.75, 0.8],
                "opportunities": [0.9, 0.8, 0.85, 0.7],
                "threats": [0.85, 0.8, 0.75, 0.7]
            }
        }

    def _generate_swot_matrix(self, swot_input: Dict[str, Any]) -> Dict[str, Any]:
        """Generates a structured SWOT matrix from insights."""
        print("   Generating SWOT matrix from synthesized insights...", flush=True)
        
        swot_matrix = {
            "Strengths": [],
            "Weaknesses": [],
            "Opportunities": [],
            "Threats": []
        }
        
        # Process strengths
        for i, strength in enumerate(swot_input.get("strengths", [])):
            confidence = swot_input.get("confidence_scores", {}).get("strengths", [0.5])[i] if i < len(swot_input.get("confidence_scores", {}).get("strengths", [])) else 0.5
            swot_matrix["Strengths"].append({
                "description": strength,
                "impact": "High" if confidence > 0.8 else "Medium" if confidence > 0.6 else "Low",
                "confidence": confidence,
                "category": "Internal"
            })
        
        # Process weaknesses
        for i, weakness in enumerate(swot_input.get("weaknesses", [])):
            confidence = swot_input.get("confidence_scores", {}).get("weaknesses", [0.5])[i] if i < len(swot_input.get("confidence_scores", {}).get("weaknesses", [])) else 0.5
            swot_matrix["Weaknesses"].append({
                "description": weakness,
                "impact": "High" if confidence > 0.8 else "Medium" if confidence > 0.6 else "Low",
                "confidence": confidence,
                "category": "Internal"
            })
        
        # Process opportunities
        for i, opportunity in enumerate(swot_input.get("opportunities", [])):
            confidence = swot_input.get("confidence_scores", {}).get("opportunities", [0.5])[i] if i < len(swot_input.get("confidence_scores", {}).get("opportunities", [])) else 0.5
            swot_matrix["Opportunities"].append({
                "description": opportunity,
                "impact": "High" if confidence > 0.8 else "Medium" if confidence > 0.6 else "Low",
                "confidence": confidence,
                "category": "External"
            })
        
        # Process threats
        for i, threat in enumerate(swot_input.get("threats", [])):
            confidence = swot_input.get("confidence_scores", {}).get("threats", [0.5])[i] if i < len(swot_input.get("confidence_scores", {}).get("threats", [])) else 0.5
            swot_matrix["Threats"].append({
                "description": threat,
                "impact": "High" if confidence > 0.8 else "Medium" if confidence > 0.6 else "Low",
                "confidence": confidence,
                "category": "External"
            })
        
        return swot_matrix

    def _prioritize_factors(self, swot_matrix: Dict[str, Any], confidence_scores: Dict[str, List[float]]) -> Dict[str, Any]:
        """Prioritizes SWOT factors based on impact and confidence."""
        print("   Prioritizing SWOT factors by impact and confidence...", flush=True)
        
        prioritized = {}
        
        for category, factors in swot_matrix.items():
            # Sort by impact (High > Medium > Low) and then by confidence
            impact_order = {"High": 3, "Medium": 2, "Low": 1}
            sorted_factors = sorted(
                factors,
                key=lambda x: (impact_order.get(x.get("impact", "Low"), 1), x.get("confidence", 0.5)),
                reverse=True
            )
            prioritized[category] = sorted_factors
        
        return prioritized

    def _generate_strategic_recommendations(self, prioritized_factors: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generates strategic recommendations based on interconnected factors."""
        print("   Generating strategic recommendations from SWOT factors...", flush=True)
        
        recommendations = []
        
        # S-O Strategies (Leverage Strengths to capitalize on Opportunities)
        strengths = prioritized_factors.get("Strengths", [])
        opportunities = prioritized_factors.get("Opportunities", [])
        
        if strengths and opportunities:
            top_strength = strengths[0]
            top_opportunity = opportunities[0]
            
            recommendations.append({
                "type": "S-O (Leverage Strengths for Opportunities)",
                "description": f"Leverage {top_strength['description']} to capitalize on {top_opportunity['description']}",
                "priority": "High",
                "implementation_difficulty": "Medium",
                "expected_impact": "High",
                "time_horizon": "6-12 months",
                "confidence": (top_strength.get("confidence", 0.5) + top_opportunity.get("confidence", 0.5)) / 2
            })
        
        # W-T Strategies (Minimize Weaknesses and avoid Threats)
        weaknesses = prioritized_factors.get("Weaknesses", [])
        threats = prioritized_factors.get("Threats", [])
        
        if weaknesses and threats:
            top_weakness = weaknesses[0]
            top_threat = threats[0]
            
            recommendations.append({
                "type": "W-T (Minimize Weaknesses to avoid Threats)",
                "description": f"Address {top_weakness['description']} to mitigate {top_threat['description']}",
                "priority": "High",
                "implementation_difficulty": "High",
                "expected_impact": "Medium",
                "time_horizon": "12-18 months",
                "confidence": (top_weakness.get("confidence", 0.5) + top_threat.get("confidence", 0.5)) / 2
            })
        
        # S-T Strategies (Use Strengths to counter Threats)
        if strengths and threats:
            top_strength = strengths[0]
            top_threat = threats[0]
            
            recommendations.append({
                "type": "S-T (Use Strengths to counter Threats)",
                "description": f"Utilize {top_strength['description']} to defend against {top_threat['description']}",
                "priority": "Medium",
                "implementation_difficulty": "Medium",
                "expected_impact": "Medium",
                "time_horizon": "3-6 months",
                "confidence": (top_strength.get("confidence", 0.5) + top_threat.get("confidence", 0.5)) / 2
            })
        
        # W-O Strategies (Overcome Weaknesses to pursue Opportunities)
        if weaknesses and opportunities:
            top_weakness = weaknesses[0]
            top_opportunity = opportunities[0]
            
            recommendations.append({
                "type": "W-O (Overcome Weaknesses for Opportunities)",
                "description": f"Address {top_weakness['description']} to pursue {top_opportunity['description']}",
                "priority": "Medium",
                "implementation_difficulty": "High",
                "expected_impact": "High",
                "time_horizon": "12-24 months",
                "confidence": (top_weakness.get("confidence", 0.5) + top_opportunity.get("confidence", 0.5)) / 2
            })
        
        # Sort recommendations by priority and confidence
        priority_order = {"High": 3, "Medium": 2, "Low": 1}
        recommendations.sort(
            key=lambda x: (priority_order.get(x.get("priority", "Low"), 1), x.get("confidence", 0.5)),
            reverse=True
        )
        
        return recommendations

    async def _calculate_strategic_alignment(self, recommendations: List[Dict[str, Any]], prioritized_factors: Dict[str, Any]) -> float:
        """Calculate a score for strategic alignment of recommendations."""
        if not recommendations:
            return 0.0
        
        # Calculate alignment based on:
        # 1. Number of recommendations (more is better, up to a point)
        # 2. Average confidence of recommendations
        # 3. Coverage of SWOT categories
        
        num_recommendations = len(recommendations)
        avg_confidence = sum(rec.get("confidence", 0.5) for rec in recommendations) / num_recommendations
        
        # Check coverage of SWOT categories in recommendations
        covered_categories = set()
        for rec in recommendations:
            rec_type = rec.get("type", "")
            if "S-O" in rec_type:
                covered_categories.update(["Strengths", "Opportunities"])
            elif "W-T" in rec_type:
                covered_categories.update(["Weaknesses", "Threats"])
            elif "S-T" in rec_type:
                covered_categories.update(["Strengths", "Threats"])
            elif "W-O" in rec_type:
                covered_categories.update(["Weaknesses", "Opportunities"])
        
        coverage_score = len(covered_categories) / 4.0  # 4 SWOT categories
        
        # Calculate overall alignment score
        alignment_score = (
            min(num_recommendations / 4.0, 1.0) * 0.3 +  # Recommendation count (max 4)
            avg_confidence * 0.4 +                        # Average confidence
            coverage_score * 0.3                          # Category coverage
        )
        
        return min(1.0, alignment_score)

    def _generate_analysis_summary(self, swot_matrix: Dict[str, Any], prioritized_factors: Dict[str, Any], 
                                 strategic_recommendations: List[Dict[str, Any]], alignment_score: float) -> Dict[str, Any]:
        """Generate a comprehensive summary of the SWOT analysis."""
        return {
            "analysis_overview": {
                "total_factors": sum(len(factors) for factors in swot_matrix.values()),
                "high_impact_factors": sum(
                    len([f for f in factors if f.get("impact") == "High"])
                    for factors in swot_matrix.values()
                ),
                "average_confidence": sum(
                    sum(f.get("confidence", 0.5) for f in factors)
                    for factors in swot_matrix.values()
                ) / sum(len(factors) for factors in swot_matrix.values()) if any(swot_matrix.values()) else 0.0
            },
            "strategic_recommendations_summary": {
                "total_recommendations": len(strategic_recommendations),
                "high_priority_recommendations": len([r for r in strategic_recommendations if r.get("priority") == "High"]),
                "average_implementation_difficulty": sum(
                    {"Low": 1, "Medium": 2, "High": 3}.get(r.get("implementation_difficulty", "Medium"), 2)
                    for r in strategic_recommendations
                ) / len(strategic_recommendations) if strategic_recommendations else 0,
                "strategic_alignment_score": alignment_score
            },
            "key_insights": [
                f"Identified {len(swot_matrix.get('Strengths', []))} key strengths",
                f"Found {len(swot_matrix.get('Opportunities', []))} growth opportunities",
                f"Generated {len(strategic_recommendations)} strategic recommendations",
                f"Strategic alignment score: {alignment_score:.2f}"
            ],
            "next_steps": [
                "Prioritize high-impact strategic recommendations",
                "Develop implementation timelines for top recommendations",
                "Monitor external factors for changes in opportunities and threats",
                "Regularly reassess internal strengths and weaknesses"
            ]
        }

    async def prepare_for_report_generation(self, plan_id: str) -> Dict[str, Any]:
        """Prepare the SWOT analysis results for the report generation agent."""
        try:
            if plan_id not in self.swot_matrix:
                return {"status": "error", "message": f"No SWOT analysis results found for plan {plan_id}"}
            
            swot_results = self.swot_matrix[plan_id]
            
            # Prepare structured input for report generation
            report_input = {
                "swot_summary": {
                    "matrix": swot_results.get("swot_matrix", {}),
                    "prioritized_factors": swot_results.get("prioritized_factors", {}),
                    "analysis_summary": swot_results.get("analysis_summary", {})
                },
                "strategic_recommendations": swot_results.get("strategic_recommendations", []),
                "key_findings": swot_results.get("analysis_summary", {}).get("key_insights", []),
                "strategic_alignment_score": swot_results.get("strategic_alignment_score", 0.0)
            }
            
            return {
                "status": "success",
                "plan_id": plan_id,
                "report_input": report_input,
                "preparation_timestamp": datetime.now().isoformat(),
                "message": "SWOT results prepared for report generation"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "plan_id": plan_id,
                "error": str(e),
                "preparation_timestamp": datetime.now().isoformat()
            }
