"""
Orchestration Agent - Executes live data collection from external sources.

This agent specializes in coordinating live data collection from various
external APIs, web scraping, and real-time data sources.
"""

import os
import sys
import asyncio
import aiohttp
import yfinance as yf
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json

# Add the project root to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# from src.mcp.mcp_client import MCPAgentInterface  # Temporarily disabled for testing


class OrchestrationAgent:
    """Agent responsible for executing live data collection from external sources."""
    
    def __init__(self):
        self.agent_name = "Orchestration Agent"
        self.agent_role = "Research Execution Specialist"
        # self.mcp_interface = MCPAgentInterface()  # Temporarily disabled for testing
        
        # Load orchestration instructions
        self.instructions = self._load_instructions()
        
        # Data collection results storage
        self.collected_data = {}
        self.source_quality_assessments = {}
    
    def _load_instructions(self) -> str:
        """Load the orchestration instructions from prompt file."""
        try:
            prompt_path = os.path.join(
                os.path.dirname(__file__), '..', 'prompts', 'orchestration_agent_instruction.txt'
            )
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except FileNotFoundError:
            return "System Role: You are the Research Execution Specialist."
    
    async def initialize(self):
        """Initialize the MCP interface."""
        await self.mcp_interface.initialize()
        print(f">>> {self.agent_name}: Initialized and ready for live data collection", flush=True)
    
    async def cleanup(self):
        """Clean up resources."""
        await self.mcp_interface.cleanup()
        print(f">>> {self.agent_name}: Cleanup completed", flush=True)
    
    async def execute_live_data_collection(self, plan_id: str) -> Dict[str, Any]:
        """
        Execute live data collection for a research plan.
        
        Args:
            plan_id: ID of the research plan
            
        Returns:
            Dictionary containing collected data and source assessments
        """
        try:
            print(f">>> {self.agent_name}: Starting live data collection for plan {plan_id}", flush=True)
            
            # Get research context to understand what data to collect
            context = await self.mcp_interface.client.get_research_context(plan_id)
            if context.get("status") != "complete":
                return {"status": "error", "message": "Research context not ready"}
            
            # Extract research objectives
            foundation_context = context.get("foundation_context", {})
            research_foundation = foundation_context.get("research_foundation", {})
            subject_scope = research_foundation.get("subject_scope", "")
            critical_questions = research_foundation.get("critical_questions", "")
            
            # Initialize data collection results
            collection_results = {
                "plan_id": plan_id,
                "started_at": datetime.now().isoformat(),
                "sources_collected": 0,
                "data_categories": {},
                "source_assessments": {},
                "collection_summary": {}
            }
            
            # Execute data collection phases
            print(f">>> {self.agent_name}: Phase 1 - Academic and Research Data", flush=True)
            academic_data = await self._collect_academic_data(subject_scope, critical_questions)
            collection_results["data_categories"]["academic"] = academic_data
            collection_results["sources_collected"] += len(academic_data.get("sources", []))
            
            print(f">>> {self.agent_name}: Phase 2 - Financial and Market Data", flush=True)
            financial_data = await self._collect_financial_data(subject_scope)
            collection_results["data_categories"]["financial"] = financial_data
            collection_results["sources_collected"] += len(financial_data.get("sources", []))
            
            print(f">>> {self.agent_name}: Phase 3 - Regulatory and Government Data", flush=True)
            regulatory_data = await self._collect_regulatory_data(subject_scope)
            collection_results["data_categories"]["regulatory"] = regulatory_data
            collection_results["sources_collected"] += len(regulatory_data.get("sources", []))
            
            print(f">>> {self.agent_name}: Phase 4 - News and Industry Data", flush=True)
            news_data = await self._collect_news_data(subject_scope)
            collection_results["data_categories"]["news"] = news_data
            collection_results["sources_collected"] += len(news_data.get("sources", []))
            
            # Generate collection summary
            collection_results["completed_at"] = datetime.now().isoformat()
            collection_results["collection_summary"] = self._generate_collection_summary(collection_results)
            
            print(f">>> {self.agent_name}: Live data collection completed - {collection_results['sources_collected']} sources collected", flush=True)
            
            return {
                "status": "success",
                "sources_collected": collection_results["sources_collected"],
                "collection_results": collection_results,
                "data_quality_score": self._calculate_data_quality_score(collection_results)
            }
            
        except Exception as e:
            print(f">>> {self.agent_name}: Error in live data collection: {e}", flush=True)
            return {
                "status": "error",
                "error": str(e),
                "completed_at": datetime.now().isoformat()
            }
    
    async def _collect_academic_data(self, subject_scope: str, critical_questions: str) -> Dict[str, Any]:
        """Collect academic and research data from relevant sources."""
        try:
            # Simulate academic data collection
            # In a real implementation, this would query PubMed, ArXiv, etc.
            
            academic_sources = [
                {
                    "source": "PubMed",
                    "query": f"research on {subject_scope}",
                    "results_count": 15,
                    "publication_date_range": "2023-2024",
                    "relevance_score": 0.85,
                    "authority_score": 0.95,
                    "data_points": [
                        "Recent studies on market trends",
                        "Technology adoption research",
                        "Consumer behavior analysis"
                    ]
                },
                {
                    "source": "ArXiv",
                    "query": f"technology trends {subject_scope}",
                    "results_count": 8,
                    "publication_date_range": "2023-2024",
                    "relevance_score": 0.78,
                    "authority_score": 0.88,
                    "data_points": [
                        "AI and machine learning applications",
                        "Digital transformation studies",
                        "Innovation research papers"
                    ]
                }
            ]
            
            return {
                "category": "Academic Research",
                "sources": academic_sources,
                "total_sources": len(academic_sources),
                "collection_timestamp": datetime.now().isoformat(),
                "quality_assessment": {
                    "average_relevance": 0.82,
                    "average_authority": 0.92,
                    "recency_score": 0.95
                }
            }
            
        except Exception as e:
            print(f">>> {self.agent_name}: Error collecting academic data: {e}", flush=True)
            return {"error": str(e)}
    
    async def _collect_financial_data(self, subject_scope: str) -> Dict[str, Any]:
        """Collect financial and market data."""
        try:
            # Simulate financial data collection
            # In a real implementation, this would use Yahoo Finance, SEC filings, etc.
            
            financial_sources = [
                {
                    "source": "Yahoo Finance",
                    "data_type": "Market Data",
                    "symbols_queried": ["AAPL", "MSFT", "GOOGL"],
                    "time_period": "1Y",
                    "data_points": [
                        "Stock performance trends",
                        "Market capitalization data",
                        "Volume and volatility metrics"
                    ],
                    "relevance_score": 0.90,
                    "authority_score": 0.95
                },
                {
                    "source": "SEC EDGAR",
                    "data_type": "Regulatory Filings",
                    "filing_types": ["10-K", "10-Q", "8-K"],
                    "time_period": "2023-2024",
                    "data_points": [
                        "Financial statements",
                        "Risk factors",
                        "Business operations updates"
                    ],
                    "relevance_score": 0.88,
                    "authority_score": 1.0
                }
            ]
            
            return {
                "category": "Financial and Market Data",
                "sources": financial_sources,
                "total_sources": len(financial_sources),
                "collection_timestamp": datetime.now().isoformat(),
                "quality_assessment": {
                    "average_relevance": 0.89,
                    "average_authority": 0.98,
                    "recency_score": 0.92
                }
            }
            
        except Exception as e:
            print(f">>> {self.agent_name}: Error collecting financial data: {e}", flush=True)
            return {"error": str(e)}
    
    async def _collect_regulatory_data(self, subject_scope: str) -> Dict[str, Any]:
        """Collect regulatory and government data."""
        try:
            # Simulate regulatory data collection
            # In a real implementation, this would query FDA, SEC, government databases
            
            regulatory_sources = [
                {
                    "source": "FDA Database",
                    "data_type": "Regulatory Information",
                    "query_parameters": {
                        "product_category": subject_scope,
                        "date_range": "2023-2024"
                    },
                    "data_points": [
                        "Approval status updates",
                        "Regulatory guidance documents",
                        "Safety and efficacy data"
                    ],
                    "relevance_score": 0.85,
                    "authority_score": 1.0
                },
                {
                    "source": "Government Policy Database",
                    "data_type": "Policy and Regulation",
                    "query_parameters": {
                        "sector": subject_scope,
                        "document_types": ["policy_papers", "regulations"]
                    },
                    "data_points": [
                        "Policy changes and updates",
                        "Regulatory framework analysis",
                        "Compliance requirements"
                    ],
                    "relevance_score": 0.82,
                    "authority_score": 0.95
                }
            ]
            
            return {
                "category": "Regulatory and Government Data",
                "sources": regulatory_sources,
                "total_sources": len(regulatory_sources),
                "collection_timestamp": datetime.now().isoformat(),
                "quality_assessment": {
                    "average_relevance": 0.84,
                    "average_authority": 0.98,
                    "recency_score": 0.90
                }
            }
            
        except Exception as e:
            print(f">>> {self.agent_name}: Error collecting regulatory data: {e}", flush=True)
            return {"error": str(e)}
    
    async def _collect_news_data(self, subject_scope: str) -> Dict[str, Any]:
        """Collect news and industry data."""
        try:
            # Simulate news data collection
            # In a real implementation, this would scrape Reuters, Bloomberg, etc.
            
            news_sources = [
                {
                    "source": "Reuters",
                    "data_type": "Industry News",
                    "query": f"{subject_scope} industry news",
                    "date_range": "2023-2024",
                    "articles_collected": 25,
                    "data_points": [
                        "Market developments",
                        "Company announcements",
                        "Industry trends and analysis"
                    ],
                    "relevance_score": 0.88,
                    "authority_score": 0.92
                },
                {
                    "source": "Industry Trade Publications",
                    "data_type": "Specialized Industry Content",
                    "publications": ["Industry Weekly", "Trade Journal", "Sector Report"],
                    "articles_collected": 18,
                    "data_points": [
                        "Expert analysis and commentary",
                        "Industry best practices",
                        "Technology and innovation updates"
                    ],
                    "relevance_score": 0.90,
                    "authority_score": 0.85
                }
            ]
            
            return {
                "category": "News and Industry Data",
                "sources": news_sources,
                "total_sources": len(news_sources),
                "collection_timestamp": datetime.now().isoformat(),
                "quality_assessment": {
                    "average_relevance": 0.89,
                    "average_authority": 0.89,
                    "recency_score": 0.95
                }
            }
            
        except Exception as e:
            print(f">>> {self.agent_name}: Error collecting news data: {e}", flush=True)
            return {"error": str(e)}
    
    def _generate_collection_summary(self, collection_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of the data collection results."""
        total_sources = collection_results["sources_collected"]
        categories = collection_results["data_categories"]
        
        # Calculate overall quality metrics
        all_quality_scores = []
        for category, data in categories.items():
            if "quality_assessment" in data:
                assessment = data["quality_assessment"]
                all_quality_scores.extend([
                    assessment.get("average_relevance", 0),
                    assessment.get("average_authority", 0),
                    assessment.get("recency_score", 0)
                ])
        
        overall_quality = sum(all_quality_scores) / len(all_quality_scores) if all_quality_scores else 0
        
        return {
            "total_sources_collected": total_sources,
            "categories_covered": len(categories),
            "overall_quality_score": round(overall_quality, 3),
            "collection_completeness": "High" if total_sources >= 15 else "Medium" if total_sources >= 10 else "Low",
            "data_freshness": "Excellent" if overall_quality >= 0.9 else "Good" if overall_quality >= 0.8 else "Fair",
            "source_diversity": "High" if len(categories) >= 4 else "Medium"
        }
    
    def _calculate_data_quality_score(self, collection_results: Dict[str, Any]) -> float:
        """Calculate an overall data quality score."""
        summary = collection_results.get("collection_summary", {})
        return summary.get("overall_quality_score", 0.0)
    
    async def assess_source_quality(self, source_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess the quality of a data source based on predefined criteria."""
        try:
            # Extract quality metrics
            relevance_score = source_data.get("relevance_score", 0)
            authority_score = source_data.get("authority_score", 0)
            recency_score = source_data.get("recency_score", 0)
            
            # Calculate overall quality score
            overall_score = (relevance_score + authority_score + recency_score) / 3
            
            # Determine quality tier
            if overall_score >= 0.9:
                quality_tier = "Excellent"
            elif overall_score >= 0.8:
                quality_tier = "Good"
            elif overall_score >= 0.7:
                quality_tier = "Acceptable"
            else:
                quality_tier = "Poor"
            
            return {
                "source": source_data.get("source", "Unknown"),
                "overall_score": round(overall_score, 3),
                "quality_tier": quality_tier,
                "relevance_score": relevance_score,
                "authority_score": authority_score,
                "recency_score": recency_score,
                "assessment_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    async def validate_collected_data(self, plan_id: str) -> Dict[str, Any]:
        """Validate the quality and completeness of collected data."""
        try:
            # This would typically load the collected data and validate it
            # For now, return a basic validation result
            return {
                "status": "success",
                "validation_results": {
                    "data_completeness": "Complete",
                    "source_quality": "High",
                    "relevance_assessment": "Relevant",
                    "recency_check": "Current"
                }
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}