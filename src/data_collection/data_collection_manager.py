"""
Data Collection Manager

Orchestrates the entire data collection process using multiple collectors.
Manages collection strategies, parallel execution, and result aggregation.
"""

import asyncio
import os
import sys
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json

# Add the project root to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from .base_collector import CollectedData, DataSource
from .data_validator import DataValidator, ValidationLevel
from .data_aggregator import DataAggregator, AggregationConfig
from .financial_collector import FinancialDataCollector
from .news_collector import NewsDataCollector
from .academic_collector import AcademicDataCollector
from .government_collector import GovernmentDataCollector
from .competitive_collector import CompetitiveDataCollector


class CollectionStrategy(Enum):
    """Data collection strategies."""
    COMPREHENSIVE = "comprehensive"  # Collect from all available sources
    FOCUSED = "focused"  # Focus on most relevant sources
    QUICK = "quick"  # Fast collection with limited sources
    DEEP_DIVE = "deep_dive"  # Thorough collection with extensive sources


@dataclass
class CollectionConfig:
    """Configuration for data collection."""
    strategy: CollectionStrategy = CollectionStrategy.FOCUSED
    max_parallel_tasks: int = 5
    timeout_seconds: int = 300
    validation_level: ValidationLevel = ValidationLevel.STANDARD
    enable_aggregation: bool = True
    enable_deduplication: bool = True
    max_results_per_source: int = 10
    retry_failed_requests: bool = True
    max_retries: int = 2


@dataclass
class CollectionResult:
    """Result of a data collection operation."""
    success: bool
    total_items_collected: int
    items_by_collector: Dict[str, int]
    collection_time_seconds: float
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    aggregated_data: Optional[List[Any]] = None
    quality_report: Optional[Dict[str, Any]] = None


class DataCollectionManager:
    """Orchestrates data collection using multiple specialized collectors."""
    
    def __init__(self, config: Optional[CollectionConfig] = None):
        self.config = config or CollectionConfig()
        self.validator = DataValidator(self.config.validation_level)
        
        # Initialize collectors
        self.collectors = {
            "financial": FinancialDataCollector(),
            "news": NewsDataCollector(),
            "academic": AcademicDataCollector(),
            "government": GovernmentDataCollector(),
            "competitive": CompetitiveDataCollector()
        }
        
        # Initialize all collectors
        self._initialized = False
        
        # Initialize aggregator if enabled
        if self.config.enable_aggregation:
            agg_config = AggregationConfig(
                enable_deduplication=self.config.enable_deduplication,
                validation_level=self.config.validation_level
            )
            self.aggregator = DataAggregator(agg_config)
        else:
            self.aggregator = None
        
        print(f">>> DataCollectionManager initialized with {len(self.collectors)} collectors")
    
    async def initialize(self):
        """Initialize all collectors."""
        if not self._initialized:
            print(">>> DataCollectionManager: Initializing all collectors...")
            for name, collector in self.collectors.items():
                try:
                    await collector.initialize()
                    print(f"   {name} collector initialized")
                except Exception as e:
                    print(f"   Error initializing {name} collector: {e}")
            self._initialized = True
            print(">>> DataCollectionManager: All collectors initialized")
    
    async def cleanup(self):
        """Cleanup all collectors."""
        if self._initialized:
            print(">>> DataCollectionManager: Cleaning up all collectors...")
            for name, collector in self.collectors.items():
                try:
                    await collector.cleanup()
                    print(f"   {name} collector cleaned up")
                except Exception as e:
                    print(f"   Error cleaning up {name} collector: {e}")
            self._initialized = False
            print(">>> DataCollectionManager: All collectors cleaned up")
    
    async def collect_data(self, 
                          research_query: str,
                          research_context: Optional[Dict[str, Any]] = None,
                          custom_sources: Optional[Dict[str, List[str]]] = None) -> CollectionResult:
        """
        Collect data using the configured strategy.
        
        Args:
            research_query: The research query or topic
            research_context: Optional research context for better collection
            custom_sources: Optional custom source configuration
            
        Returns:
            Collection result with aggregated data
        """
        start_time = datetime.now()
        print(f">>> DataCollectionManager: Starting data collection for '{research_query}'")
        print(f"   Strategy: {self.config.strategy.value}")
        print(f"   Max parallel tasks: {self.config.max_parallel_tasks}")
        
        # Ensure collectors are initialized
        if not self._initialized:
            await self.initialize()
        
        # Determine collection plan
        collection_plan = self._create_collection_plan(research_query, custom_sources)
        print(f"   Collection plan: {len(collection_plan)} tasks across {len(set(task['collector'] for task in collection_plan))} collectors")
        
        # Execute collection tasks
        try:
            collected_data = await self._execute_collection_plan(collection_plan, research_query)
            print(f"   Collected {sum(len(data) for data in collected_data.values())} total items")
            
            # Validate collected data
            all_data = []
            for collector_name, data_list in collected_data.items():
                validated_data = self.validator.filter_high_quality_data(data_list)
                all_data.extend(validated_data)
                print(f"   {collector_name}: {len(data_list)} collected, {len(validated_data)} validated")
            
            # Aggregate data if enabled
            aggregated_data = None
            if self.aggregator and all_data:
                print("   Aggregating data...")
                aggregated_data = self.aggregator.aggregate_data(
                    {"all": all_data}, 
                    research_context
                )
                print(f"   Created {len(aggregated_data)} aggregated items")
            
            # Generate quality report
            quality_report = self.validator.generate_quality_report(all_data)
            
            # Calculate collection time
            collection_time = (datetime.now() - start_time).total_seconds()
            
            # Count items by collector
            items_by_collector = {
                collector_name: len(data_list) 
                for collector_name, data_list in collected_data.items()
            }
            
            result = CollectionResult(
                success=True,
                total_items_collected=len(all_data),
                items_by_collector=items_by_collector,
                collection_time_seconds=collection_time,
                aggregated_data=aggregated_data,
                quality_report=quality_report
            )
            
            print(f">>> DataCollectionManager: Collection completed successfully in {collection_time:.2f} seconds")
            return result
            
        except Exception as e:
            collection_time = (datetime.now() - start_time).total_seconds()
            print(f">>> DataCollectionManager: Collection failed after {collection_time:.2f} seconds: {e}")
            
            return CollectionResult(
                success=False,
                total_items_collected=0,
                items_by_collector={},
                collection_time_seconds=collection_time,
                errors=[str(e)]
            )
    
    def _create_collection_plan(self, 
                               research_query: str, 
                               custom_sources: Optional[Dict[str, List[str]]] = None) -> List[Dict[str, Any]]:
        """Create a collection plan based on strategy and query."""
        plan = []
        
        # Define source configurations for each strategy
        strategy_configs = {
            CollectionStrategy.QUICK: {
                "financial": ["yahoo_finance"],
                "news": ["google_news"],
                "academic": ["pubmed"],
                "government": [],
                "competitive": []
            },
            CollectionStrategy.FOCUSED: {
                "financial": ["yahoo_finance", "google_finance"],
                "news": ["google_news", "web_scrape"],
                "academic": ["pubmed", "arxiv"],
                "government": ["fda", "sec_edgar_filings"],
                "competitive": ["builtwith"]
            },
            CollectionStrategy.COMPREHENSIVE: {
                "financial": ["yahoo_finance", "google_finance", "sec_edgar"],
                "news": ["google_news", "web_scrape"],
                "academic": ["pubmed", "arxiv"],
                "government": ["fda", "sec_edgar_filings", "data_gov"],
                "competitive": ["builtwith", "g2_capterra_reviews"]
            },
            CollectionStrategy.DEEP_DIVE: {
                "financial": ["yahoo_finance", "google_finance", "sec_edgar"],
                "news": ["google_news", "web_scrape"],
                "academic": ["pubmed", "arxiv"],
                "government": ["fda", "sec_edgar_filings", "data_gov"],
                "competitive": ["builtwith", "g2_capterra_reviews"]
            }
        }
        
        # Get source configuration
        if custom_sources:
            source_config = custom_sources
        else:
            source_config = strategy_configs.get(self.config.strategy, strategy_configs[CollectionStrategy.FOCUSED])
        
        # Create collection tasks
        for collector_name, sources in source_config.items():
            if collector_name not in self.collectors:
                continue
            
            for source in sources:
                task = {
                    "collector": collector_name,
                    "source": source,
                    "query": research_query,
                    "max_results": self.config.max_results_per_source,
                    "timeout": self.config.timeout_seconds
                }
                plan.append(task)
        
        return plan
    
    async def _execute_collection_plan(self, 
                                     collection_plan: List[Dict[str, Any]], 
                                     research_query: str) -> Dict[str, List[CollectedData]]:
        """Execute the collection plan with parallel processing."""
        collected_data = {collector_name: [] for collector_name in self.collectors.keys()}
        
        # Create semaphore to limit concurrent tasks
        semaphore = asyncio.Semaphore(self.config.max_parallel_tasks)
        
        async def collect_with_semaphore(task):
            async with semaphore:
                return await self._execute_collection_task(task)
        
        # Execute all tasks
        tasks = [collect_with_semaphore(task) for task in collection_plan]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for i, result in enumerate(results):
            task = collection_plan[i]
            collector_name = task["collector"]
            
            if isinstance(result, Exception):
                print(f"   Error in {collector_name} ({task['source']}): {result}")
                continue
            
            if result and isinstance(result, list):
                collected_data[collector_name].extend(result)
        
        return collected_data
    
    async def _execute_collection_task(self, task: Dict[str, Any]) -> List[CollectedData]:
        """Execute a single collection task."""
        collector_name = task["collector"]
        source = task["source"]
        query = task["query"]
        max_results = task.get("max_results", self.config.max_results_per_source)
        
        collector = self.collectors.get(collector_name)
        if not collector:
            print(f"   Warning: Collector '{collector_name}' not found")
            return []
        
        try:
            print(f"   Collecting from {collector_name} ({source})...")
            
            # Execute collection with timeout
            result = await asyncio.wait_for(
                collector.collect_data(query, max_results=max_results),
                timeout=task.get("timeout", self.config.timeout_seconds)
            )
            
            if result and isinstance(result, list):
                print(f"   {collector_name} ({source}): {len(result)} items collected")
                return result
            else:
                print(f"   {collector_name} ({source}): Collection failed - No data returned")
                return []
                
        except asyncio.TimeoutError:
            print(f"   {collector_name} ({source}): Collection timed out")
            return []
        except Exception as e:
            print(f"   {collector_name} ({source}): Collection error - {e}")
            return []
    
    async def collect_from_specific_sources(self, 
                                          research_query: str,
                                          source_requests: List[Dict[str, Any]]) -> CollectionResult:
        """
        Collect data from specific sources with custom parameters.
        
        Args:
            research_query: The research query
            source_requests: List of source request configurations
            
        Returns:
            Collection result
        """
        start_time = datetime.now()
        print(f">>> DataCollectionManager: Collecting from {len(source_requests)} specific sources")
        
        # Ensure collectors are initialized
        if not self._initialized:
            await self.initialize()
        
        collected_data = {}
        errors = []
        
        for request in source_requests:
            collector_name = request.get("collector")
            source = request.get("source")
            params = request.get("params", {})
            
            if collector_name not in self.collectors:
                errors.append(f"Unknown collector: {collector_name}")
                continue
            
            try:
                collector = self.collectors[collector_name]
                result = await collector.collect_data(research_query, **params)
                
                if result and isinstance(result, list):
                    if collector_name not in collected_data:
                        collected_data[collector_name] = []
                    collected_data[collector_name].extend(result)
                else:
                    errors.append(f"{collector_name} ({source}): No data returned")
                    
            except Exception as e:
                errors.append(f"{collector_name} ({source}): {str(e)}")
        
        # Process and aggregate results
        all_data = []
        for data_list in collected_data.values():
            all_data.extend(data_list)
        
        # Validate and aggregate
        validated_data = self.validator.filter_high_quality_data(all_data)
        
        aggregated_data = None
        if self.aggregator and validated_data:
            aggregated_data = self.aggregator.aggregate_data({"specific": validated_data})
        
        quality_report = self.validator.generate_quality_report(validated_data)
        
        collection_time = (datetime.now() - start_time).total_seconds()
        
        return CollectionResult(
            success=len(errors) == 0,
            total_items_collected=len(validated_data),
            items_by_collector={name: len(data) for name, data in collected_data.items()},
            collection_time_seconds=collection_time,
            errors=errors,
            aggregated_data=aggregated_data,
            quality_report=quality_report
        )
    
    def get_collector_info(self) -> Dict[str, Any]:
        """Get information about available collectors."""
        info = {}
        for name, collector in self.collectors.items():
            info[name] = {
                "name": collector.name,
                "description": collector.description,
                "available_sources": collector.get_supported_sources()
            }
        return info
    
    def update_config(self, new_config: CollectionConfig):
        """Update the collection configuration."""
        self.config = new_config
        self.validator = DataValidator(self.config.validation_level)
        
        if self.config.enable_aggregation and not self.aggregator:
            agg_config = AggregationConfig(
                enable_deduplication=self.config.enable_deduplication,
                validation_level=self.config.validation_level
            )
            self.aggregator = DataAggregator(agg_config)
        elif not self.config.enable_aggregation:
            self.aggregator = None
        
        print(f">>> DataCollectionManager: Configuration updated")
    
    async def test_collectors(self) -> Dict[str, Any]:
        """Test all collectors with a simple query."""
        test_query = "artificial intelligence"
        test_results = {}
        
        print(f">>> DataCollectionManager: Testing collectors with query '{test_query}'")
        
        # Ensure collectors are initialized
        if not self._initialized:
            await self.initialize()
        
        for name, collector in self.collectors.items():
            try:
                # Test with first available source
                sources = collector.get_supported_sources()
                if sources:
                    test_source = sources[0]
                    result = await collector.collect_data(test_query, max_results=2)
                    test_results[name] = {
                        "status": "success" if result and isinstance(result, list) else "failed",
                        "items_collected": len(result) if result and isinstance(result, list) else 0,
                        "test_source": test_source
                    }
                else:
                    test_results[name] = {
                        "status": "no_sources",
                        "items_collected": 0,
                        "test_source": None
                    }
            except Exception as e:
                test_results[name] = {
                    "status": "error",
                    "items_collected": 0,
                    "error": str(e),
                    "test_source": None
                }
        
        return test_results
