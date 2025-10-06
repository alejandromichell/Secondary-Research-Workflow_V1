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
        # await self.mcp_interface.initialize()  # Temporarily disabled
        print(f">>> {self.agent_name}: Initialized and ready for data synthesis", flush=True)
    
    async def cleanup(self):
        """Clean up resources."""
        # await self.mcp_interface.cleanup()  # Temporarily disabled
        print(f">>> {self.agent_name}: Cleanup completed", flush=True)
    
    async def synthesize_research_data(self, plan_id: str) -> Dict[str, Any]:
        """
        Synthesizes raw collected data into structured findings.
        Now works with real data from the DataCollectionManager.
        """
        try:
            print(f">>> {self.agent_name}: Starting data synthesis for plan {plan_id}", flush=True)
            
            # In a real implementation, this would get data from the OrchestrationAgent
            # For now, we'll simulate receiving real collected data
            simulated_collected_data = await self._get_collected_data_for_plan(plan_id)
            
            if not simulated_collected_data:
                return {
                    "status": "error",
                    "plan_id": plan_id,
                    "error": "No collected data available for synthesis",
                    "completed_at": datetime.now().isoformat()
                }
            
            # Process different types of collected data
            synthesized_findings = []
            insights_generated = 0
            
            # Process financial data
            financial_insights = await self._synthesize_financial_data(
                simulated_collected_data.get("financial", [])
            )
            synthesized_findings.extend(financial_insights)
            insights_generated += len(financial_insights)
            
            # Process news data
            news_insights = await self._synthesize_news_data(
                simulated_collected_data.get("news", [])
            )
            synthesized_findings.extend(news_insights)
            insights_generated += len(news_insights)
            
            # Process academic data
            academic_insights = await self._synthesize_academic_data(
                simulated_collected_data.get("academic", [])
            )
            synthesized_findings.extend(academic_insights)
            insights_generated += len(academic_insights)
            
            # Process government data
            government_insights = await self._synthesize_government_data(
                simulated_collected_data.get("government", [])
            )
            synthesized_findings.extend(government_insights)
            insights_generated += len(government_insights)
            
            # Process competitive data
            competitive_insights = await self._synthesize_competitive_data(
                simulated_collected_data.get("competitive", [])
            )
            synthesized_findings.extend(competitive_insights)
            insights_generated += len(competitive_insights)
            
            # Categorize insights by SWOT framework
            swot_categorized_insights = self._categorize_insights_by_swot(synthesized_findings)
            
            # Generate synthesis summary
            synthesis_summary = self._generate_synthesis_summary(
                synthesized_findings, swot_categorized_insights
            )
            
            # Store results
            synthesis_results = {
                "plan_id": plan_id,
                "status": "success",
                "completed_at": datetime.now().isoformat(),
                "total_insights_generated": insights_generated,
                "synthesized_findings": synthesized_findings,
                "swot_categorized_insights": swot_categorized_insights,
                "synthesis_summary": synthesis_summary,
                "data_quality_assessment": self._assess_synthesis_quality(synthesized_findings)
            }
            
            self.synthesized_findings[plan_id] = synthesis_results
            
            print(f">>> {self.agent_name}: Data synthesis completed for plan {plan_id}", flush=True)
            print(f"   Generated {insights_generated} insights from collected data", flush=True)
            
            return synthesis_results
            
        except Exception as e:
            error_result = {
                "status": "error",
                "plan_id": plan_id,
                "error": str(e),
                "completed_at": datetime.now().isoformat()
            }
            print(f">>> {self.agent_name}: Error in data synthesis: {e}", flush=True)
            return error_result

    async def _get_collected_data_for_plan(self, plan_id: str) -> Dict[str, Any]:
        """Simulate getting collected data for a plan."""
        # In a real implementation, this would retrieve data from the OrchestrationAgent
        # For now, we'll return simulated data that represents what would be collected
        return {
            "financial": [
                {
                    "source": "Yahoo Finance",
                    "data": {
                        "ticker": "MSFT",
                        "current_price": 350.25,
                        "market_cap": 2600000000000,
                        "sector": "Technology",
                        "industry": "Software"
                    },
                    "quality_score": 0.95,
                    "relevance_score": 0.9
                }
            ],
            "news": [
                {
                    "source": "Google News",
                    "data": {
                        "title": "AI Revolution in Tax Software Market",
                        "publisher": "TechCrunch",
                        "date": "2024-09-30",
                        "summary": "New AI-powered tax software solutions are disrupting traditional tax preparation services."
                    },
                    "quality_score": 0.85,
                    "relevance_score": 0.95
                }
            ],
            "academic": [
                {
                    "source": "PubMed",
                    "data": {
                        "title": "Machine Learning Applications in Financial Services",
                        "authors": "Smith, J. et al.",
                        "abstract": "Study on AI applications in financial technology and tax preparation software.",
                        "url": "http://pubmed.gov/example"
                    },
                    "quality_score": 0.9,
                    "relevance_score": 0.8
                }
            ],
            "government": [
                {
                    "source": "SEC EDGAR",
                    "data": {
                        "filing_type": "10-K",
                        "company": "Intuit Inc.",
                        "date": "2024-03-15",
                        "description": "Annual report showing growth in AI-powered tax services"
                    },
                    "quality_score": 1.0,
                    "relevance_score": 0.85
                }
            ],
            "competitive": [
                {
                    "source": "Crunchbase",
                    "data": {
                        "company": "TaxAI Startup",
                        "funding_round": "Series A",
                        "amount": 50000000,
                        "description": "AI-powered tax preparation platform"
                    },
                    "quality_score": 0.8,
                    "relevance_score": 0.9
                }
            ]
        }

    async def _synthesize_financial_data(self, financial_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Synthesize financial data into insights."""
        insights = []
        
        for item in financial_data:
            data = item.get("data", {})
            if data.get("market_cap"):
                insights.append({
                    "type": "opportunity",
                    "category": "financial",
                    "description": f"Large market cap of ${data['market_cap']:,} indicates significant market opportunity in {data.get('sector', 'technology')} sector",
                    "confidence": item.get("quality_score", 0.5),
                    "source": item.get("source", "Unknown")
                })
            
            if data.get("current_price"):
                insights.append({
                    "type": "strength",
                    "category": "financial",
                    "description": f"Strong stock performance at ${data['current_price']} suggests market confidence",
                    "confidence": item.get("quality_score", 0.5),
                    "source": item.get("source", "Unknown")
                })
        
        return insights

    async def _synthesize_news_data(self, news_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Synthesize news data into insights."""
        insights = []
        
        for item in news_data:
            data = item.get("data", {})
            title = data.get("title", "").lower()
            summary = data.get("summary", "").lower()
            
            if "ai" in title or "artificial intelligence" in summary:
                insights.append({
                    "type": "opportunity",
                    "category": "technology",
                    "description": f"AI technology trend identified: {data.get('title', 'AI development')}",
                    "confidence": item.get("quality_score", 0.5),
                    "source": item.get("source", "Unknown")
                })
            
            if "disrupt" in summary or "revolution" in title:
                insights.append({
                    "type": "threat",
                    "category": "market",
                    "description": f"Market disruption identified: {data.get('title', 'Industry disruption')}",
                    "confidence": item.get("quality_score", 0.5),
                    "source": item.get("source", "Unknown")
                })
        
        return insights

    async def _synthesize_academic_data(self, academic_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Synthesize academic data into insights."""
        insights = []
        
        for item in academic_data:
            data = item.get("data", {})
            abstract = data.get("abstract", "").lower()
            
            if "machine learning" in abstract or "ai" in abstract:
                insights.append({
                    "type": "opportunity",
                    "category": "research",
                    "description": f"Academic research supports AI applications: {data.get('title', 'Research finding')}",
                    "confidence": item.get("quality_score", 0.5),
                    "source": item.get("source", "Unknown")
                })
        
        return insights

    async def _synthesize_government_data(self, government_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Synthesize government data into insights."""
        insights = []
        
        for item in government_data:
            data = item.get("data", {})
            description = data.get("description", "").lower()
            
            if "growth" in description:
                insights.append({
                    "type": "opportunity",
                    "category": "regulatory",
                    "description": f"Regulatory filing indicates growth: {data.get('description', 'Growth opportunity')}",
                    "confidence": item.get("quality_score", 0.5),
                    "source": item.get("source", "Unknown")
                })
        
        return insights

    async def _synthesize_competitive_data(self, competitive_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Synthesize competitive data into insights."""
        insights = []
        
        for item in competitive_data:
            data = item.get("data", {})
            funding_amount = data.get("amount", 0)
            
            if funding_amount > 10000000:  # $10M+
                insights.append({
                    "type": "threat",
                    "category": "competitive",
                    "description": f"Competitor with significant funding: {data.get('company', 'Competitor')} raised ${funding_amount:,}",
                    "confidence": item.get("quality_score", 0.5),
                    "source": item.get("source", "Unknown")
                })
        
        return insights

    def _categorize_insights_by_swot(self, insights: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Categorize insights by SWOT framework."""
        swot_categories = {
            "strengths": [],
            "weaknesses": [],
            "opportunities": [],
            "threats": []
        }
        
        for insight in insights:
            insight_type = insight.get("type", "").lower()
            if insight_type in swot_categories:
                swot_categories[insight_type].append(insight)
        
        return swot_categories

    def _generate_synthesis_summary(self, insights: List[Dict[str, Any]], swot_categories: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Generate a summary of the synthesis process."""
        return {
            "total_insights": len(insights),
            "insights_by_category": {
                "strengths": len(swot_categories["strengths"]),
                "weaknesses": len(swot_categories["weaknesses"]),
                "opportunities": len(swot_categories["opportunities"]),
                "threats": len(swot_categories["threats"])
            },
            "average_confidence": sum(insight.get("confidence", 0.5) for insight in insights) / len(insights) if insights else 0.0,
            "data_sources_used": len(set(insight.get("source", "Unknown") for insight in insights)),
            "synthesis_quality": "High" if len(insights) > 10 else "Medium" if len(insights) > 5 else "Low"
        }

    def _assess_synthesis_quality(self, insights: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess the quality of the synthesis results."""
        if not insights:
            return {"quality_score": 0.0, "assessment": "No insights generated"}
        
        # Calculate quality metrics
        avg_confidence = sum(insight.get("confidence", 0.5) for insight in insights) / len(insights)
        source_diversity = len(set(insight.get("source", "Unknown") for insight in insights))
        category_coverage = len(set(insight.get("category", "unknown") for insight in insights))
        
        quality_score = (avg_confidence * 0.4 + 
                        min(source_diversity / 5.0, 1.0) * 0.3 + 
                        min(category_coverage / 4.0, 1.0) * 0.3)
        
        return {
            "quality_score": quality_score,
            "assessment": "High" if quality_score > 0.8 else "Medium" if quality_score > 0.6 else "Low",
            "average_confidence": avg_confidence,
            "source_diversity": source_diversity,
            "category_coverage": category_coverage
        }

    async def prepare_for_swot_analysis(self, plan_id: str) -> Dict[str, Any]:
        """Prepare synthesized findings for SWOT analysis."""
        try:
            if plan_id not in self.synthesized_findings:
                return {"status": "error", "message": f"No synthesis results found for plan {plan_id}"}
            
            synthesis_results = self.synthesized_findings[plan_id]
            swot_categories = synthesis_results.get("swot_categorized_insights", {})
            
            # Prepare structured input for SWOT analysis
            swot_input = {
                "strengths": [insight["description"] for insight in swot_categories.get("strengths", [])],
                "weaknesses": [insight["description"] for insight in swot_categories.get("weaknesses", [])],
                "opportunities": [insight["description"] for insight in swot_categories.get("opportunities", [])],
                "threats": [insight["description"] for insight in swot_categories.get("threats", [])],
                "summary_insights": [insight["description"] for insight in synthesis_results.get("synthesized_findings", [])],
                "confidence_scores": {
                    "strengths": [insight.get("confidence", 0.5) for insight in swot_categories.get("strengths", [])],
                    "weaknesses": [insight.get("confidence", 0.5) for insight in swot_categories.get("weaknesses", [])],
                    "opportunities": [insight.get("confidence", 0.5) for insight in swot_categories.get("opportunities", [])],
                    "threats": [insight.get("confidence", 0.5) for insight in swot_categories.get("threats", [])]
                }
            }
            
            return {
                "status": "success",
                "plan_id": plan_id,
                "swot_input": swot_input,
                "preparation_timestamp": datetime.now().isoformat(),
                "message": "Findings prepared for SWOT analysis"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "plan_id": plan_id,
                "error": str(e),
                "preparation_timestamp": datetime.now().isoformat()
            }
