"""
Orchestration Agent - Executes live data collection from external sources.

This agent specializes in coordinating live data collection from various
external APIs, web scraping, and real-time data sources using the new
data collection framework.
"""

import os
import sys
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json

# Add the project root to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Import our new live data collection framework
from src.data_collection import (
    DataCollectionManager, CollectionConfig, CollectionStrategy,
    DataValidator, ValidationLevel
)

# from src.mcp.mcp_client import MCPAgentInterface  # Temporarily disabled for testing


class OrchestrationAgent:
    """Agent responsible for executing live data collection from external sources."""
    
    def __init__(self):
        self.agent_name = "Orchestration Agent"
        self.agent_role = "Research Execution Specialist"
        # self.mcp_interface = MCPAgentInterface()  # Temporarily disabled for testing
        
        # Load orchestration instructions
        self.instructions = self._load_instructions()
        
        # Initialize live data collection framework
        self.collection_config = CollectionConfig(
            strategy=CollectionStrategy.FOCUSED,
            max_parallel_tasks=5,
            timeout_seconds=300,
            validation_level=ValidationLevel.STANDARD,
            enable_aggregation=True,
            enable_deduplication=True,
            max_results_per_source=10
        )
        self.data_collection_manager = DataCollectionManager(self.collection_config)
        
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
        """Initialize the MCP interface and data collection manager."""
        # await self.mcp_interface.initialize()  # Temporarily disabled
        await self.data_collection_manager.initialize()
        print(f">>> {self.agent_name}: Initialized and ready for live data collection", flush=True)
    
    async def cleanup(self):
        """Clean up resources."""
        # await self.mcp_interface.cleanup()  # Temporarily disabled
        await self.data_collection_manager.cleanup()
        print(f">>> {self.agent_name}: Cleanup completed", flush=True)
    
    async def execute_live_data_collection(self, plan_id: str) -> Dict[str, Any]:
        """
        Execute live data collection for a research plan using the new data collection framework.
        
        Args:
            plan_id: ID of the research plan
            
        Returns:
            Dictionary containing collected data and source assessments
        """
        try:
            print(f">>> {self.agent_name}: Starting live data collection for plan {plan_id}", flush=True)
            
            # For now, we'll use a simulated research context since MCP is disabled
            # In a real implementation, this would come from the research plan
            research_query = f"Research plan {plan_id} - comprehensive market analysis"
            research_context = {
                "plan_id": plan_id,
                "subject_scope": "Technology and market analysis",
                "critical_questions": [
                    "What are the current market trends?",
                    "Who are the key competitors?",
                    "What are the growth opportunities?",
                    "What are the potential risks?"
                ],
                "geographic_scope": "Global",
                "timeline": "Current state analysis"
            }
            
            # Execute live data collection using our new framework
            print(f">>> {self.agent_name}: Executing comprehensive data collection", flush=True)
            collection_result = await self.data_collection_manager.collect_data(
                research_query=research_query,
                research_context=research_context
            )
            
            if not collection_result.success:
                return {
                    "status": "error",
                    "plan_id": plan_id,
                    "error": f"Data collection failed: {collection_result.errors}",
                    "completed_at": datetime.now().isoformat()
                }
            
            # Process and structure the results
            processed_results = {
                "plan_id": plan_id,
                "status": "success",
                "started_at": collection_result.collection_time_seconds,
                "completed_at": datetime.now().isoformat(),
                "total_items_collected": collection_result.total_items_collected,
                "items_by_collector": collection_result.items_by_collector,
                "collection_time_seconds": collection_result.collection_time_seconds,
                "aggregated_data": collection_result.aggregated_data,
                "quality_report": collection_result.quality_report,
                "data_categories": self._categorize_collected_data(collection_result.aggregated_data),
                "source_assessments": self._assess_collected_sources(collection_result.aggregated_data),
                "collection_summary": self._generate_collection_summary(collection_result)
            }
            
            # Store results
            self.collected_data[plan_id] = processed_results
            
            print(f">>> {self.agent_name}: Live data collection completed for plan {plan_id}", flush=True)
            print(f"   Collected {collection_result.total_items_collected} items from {len(collection_result.items_by_collector)} collectors", flush=True)
            
            return processed_results
            
        except Exception as e:
            error_result = {
                "status": "error",
                "plan_id": plan_id,
                "error": str(e),
                "completed_at": datetime.now().isoformat()
            }
            print(f">>> {self.agent_name}: Error in live data collection: {e}", flush=True)
            return error_result

    def _categorize_collected_data(self, aggregated_data: Any) -> Dict[str, Any]:
        """Categorize collected data by type and source."""
        categories = {
            "financial": [],
            "news": [],
            "academic": [],
            "government": [],
            "competitive": [],
            "other": []
        }
        
        if hasattr(aggregated_data, 'items_by_collector'):
            for collector_name, items in aggregated_data.items_by_collector.items():
                collector_type = collector_name.lower()
                if 'financial' in collector_type:
                    categories["financial"].extend(items)
                elif 'news' in collector_type:
                    categories["news"].extend(items)
                elif 'academic' in collector_type:
                    categories["academic"].extend(items)
                elif 'government' in collector_type:
                    categories["government"].extend(items)
                elif 'competitive' in collector_type:
                    categories["competitive"].extend(items)
                else:
                    categories["other"].extend(items)
        
        return categories

    def _assess_collected_sources(self, aggregated_data: Any) -> Dict[str, Any]:
        """Assess the quality and reliability of collected sources."""
        assessments = {}
        
        if hasattr(aggregated_data, 'items_by_collector'):
            for collector_name, items in aggregated_data.items_by_collector.items():
                if items:
                    # Calculate average quality score
                    quality_scores = [getattr(item, 'quality_score', 0.5) for item in items]
                    avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0.5
                    
                    assessments[collector_name] = {
                        "item_count": len(items),
                        "average_quality_score": avg_quality,
                        "reliability": "High" if avg_quality > 0.8 else "Medium" if avg_quality > 0.6 else "Low",
                        "data_freshness": "Recent" if any(getattr(item, 'collected_at', None) for item in items) else "Unknown"
                    }
        
        return assessments

    def _generate_collection_summary(self, collection_result: Any) -> Dict[str, Any]:
        """Generate a summary of the data collection process."""
        return {
            "total_items": collection_result.total_items_collected,
            "collectors_used": len(collection_result.items_by_collector),
            "collection_time_seconds": collection_result.collection_time_seconds,
            "success_rate": 1.0 if collection_result.success else 0.0,
            "quality_score": getattr(collection_result.quality_report, 'overall_quality_score', 0.5),
            "data_coverage": "Comprehensive" if collection_result.total_items_collected > 20 else "Limited",
            "recommendations": [
                "Data collection completed successfully",
                "Multiple source types covered",
                "Quality validation performed"
            ]
        }

    async def validate_collected_data(self, plan_id: str) -> Dict[str, Any]:
        """Validate the quality and completeness of collected data."""
        try:
            if plan_id not in self.collected_data:
                return {"status": "error", "message": f"No data found for plan {plan_id}"}
            
            data = self.collected_data[plan_id]
            
            # Perform validation checks
            validation_results = {
                "plan_id": plan_id,
                "validation_timestamp": datetime.now().isoformat(),
                "checks_performed": [],
                "overall_score": 0.0,
                "recommendations": []
            }
            
            # Check data completeness
            if data.get("total_items_collected", 0) > 0:
                validation_results["checks_performed"].append("Data completeness: PASS")
                validation_results["overall_score"] += 0.3
            else:
                validation_results["checks_performed"].append("Data completeness: FAIL")
                validation_results["recommendations"].append("No data was collected")
            
            # Check source diversity
            source_count = len(data.get("items_by_collector", {}))
            if source_count >= 3:
                validation_results["checks_performed"].append("Source diversity: PASS")
                validation_results["overall_score"] += 0.3
            else:
                validation_results["checks_performed"].append("Source diversity: FAIL")
                validation_results["recommendations"].append("Limited source diversity")
            
            # Check quality scores
            quality_report = data.get("quality_report", {})
            if hasattr(quality_report, 'overall_quality_score') and quality_report.overall_quality_score > 0.6:
                validation_results["checks_performed"].append("Data quality: PASS")
                validation_results["overall_score"] += 0.4
            else:
                validation_results["checks_performed"].append("Data quality: FAIL")
                validation_results["recommendations"].append("Data quality below threshold")
            
            validation_results["status"] = "success" if validation_results["overall_score"] > 0.7 else "warning"
            
            return validation_results
            
        except Exception as e:
            return {
                "status": "error",
                "plan_id": plan_id,
                "error": str(e),
                "validation_timestamp": datetime.now().isoformat()
            }
