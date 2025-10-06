#!/usr/bin/env python3
"""
Test Script for Data Collection System

Tests the comprehensive data collection system including:
- Individual collectors
- Data validation
- Data aggregation
- Collection manager orchestration
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from src.data_collection import (
    DataCollectionManager, CollectionConfig, CollectionStrategy,
    DataValidator, ValidationLevel,
    DataAggregator, AggregationConfig,
    FinancialDataCollector, NewsDataCollector, AcademicDataCollector,
    GovernmentDataCollector, CompetitiveDataCollector
)


async def test_individual_collectors():
    """Test individual data collectors."""
    print("=" * 60)
    print("TESTING INDIVIDUAL COLLECTORS")
    print("=" * 60)
    
    test_query = "artificial intelligence in healthcare"
    
    # Test Financial Collector
    print("\n1. Testing Financial Collector...")
    financial_collector = FinancialDataCollector()
    try:
        await financial_collector.initialize()
        result = await financial_collector.collect_data(test_query, max_results=3)
        print(f"   Items collected: {len(result)}")
        if result:
            print(f"   Sample data: {list(result[0].data.keys()) if isinstance(result[0].data, dict) else 'Non-dict data'}")
        await financial_collector.cleanup()
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test News Collector
    print("\n2. Testing News Collector...")
    news_collector = NewsDataCollector()
    try:
        await news_collector.initialize()
        result = await news_collector.collect_data(test_query, max_results=3)
        print(f"   Items collected: {len(result)}")
        if result:
            print(f"   Sample data: {list(result[0].data.keys()) if isinstance(result[0].data, dict) else 'Non-dict data'}")
        await news_collector.cleanup()
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test Academic Collector
    print("\n3. Testing Academic Collector...")
    academic_collector = AcademicDataCollector()
    try:
        await academic_collector.initialize()
        result = await academic_collector.collect_data(test_query, max_results=3)
        print(f"   Items collected: {len(result)}")
        if result:
            print(f"   Sample data: {list(result[0].data.keys()) if isinstance(result[0].data, dict) else 'Non-dict data'}")
        await academic_collector.cleanup()
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test Government Collector
    print("\n4. Testing Government Collector...")
    government_collector = GovernmentDataCollector()
    try:
        await government_collector.initialize()
        result = await government_collector.collect_data(test_query, max_results=3)
        print(f"   Items collected: {len(result)}")
        if result:
            print(f"   Sample data: {list(result[0].data.keys()) if isinstance(result[0].data, dict) else 'Non-dict data'}")
        await government_collector.cleanup()
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test Competitive Collector
    print("\n5. Testing Competitive Collector...")
    competitive_collector = CompetitiveDataCollector()
    try:
        await competitive_collector.initialize()
        result = await competitive_collector.collect_data("microsoft.com", max_results=3)
        print(f"   Items collected: {len(result)}")
        if result:
            print(f"   Sample data: {list(result[0].data.keys()) if isinstance(result[0].data, dict) else 'Non-dict data'}")
        await competitive_collector.cleanup()
    except Exception as e:
        print(f"   Error: {e}")


async def test_data_validation():
    """Test data validation system."""
    print("\n" + "=" * 60)
    print("TESTING DATA VALIDATION")
    print("=" * 60)
    
    # Create some sample data for testing
    from src.data_collection.base_collector import CollectedData, DataSource
    
    sample_data = [
        CollectedData(
            source=DataSource("PubMed", "https://pubmed.ncbi.nlm.nih.gov/", "academic", 0.9),
            data={"title": "AI in Healthcare", "description": "Comprehensive study on AI applications in healthcare", "date": "2024-01-15"},
            collected_at=datetime.now(),
            data_type="academic_paper",
            quality_score=0.9,
            relevance_score=0.8
        ),
        CollectedData(
            source=DataSource("Reuters", "https://reuters.com/", "news", 0.8),
            data={"title": "Healthcare AI News", "content": "Recent developments in healthcare AI"},
            collected_at=datetime.now(),
            data_type="news_article",
            quality_score=0.8,
            relevance_score=0.7
        ),
        CollectedData(
            source=DataSource("Yahoo Finance", "https://finance.yahoo.com/", "financial", 0.9),
            data={"ticker": "MSFT", "current_price": 350.0, "company_name": "Microsoft"},
            collected_at=datetime.now(),
            data_type="financial_data",
            quality_score=0.9,
            relevance_score=0.6
        )
    ]
    
    # Test with different validation levels
    for level in [ValidationLevel.BASIC, ValidationLevel.STANDARD, ValidationLevel.STRICT]:
        print(f"\nTesting validation level: {level.value}")
        validator = DataValidator(level)
        
        for i, data_item in enumerate(sample_data):
            result = validator.validate_data(data_item)
            print(f"   Item {i+1}: Valid={result.is_valid}, Quality={result.quality_score:.2f}, Issues={len(result.issues)}")
        
        # Test dataset validation
        dataset_result = validator.validate_dataset(sample_data)
        print(f"   Dataset: {dataset_result['valid_items']}/{dataset_result['total_items']} valid, Avg quality: {dataset_result['average_quality']:.2f}")


async def test_data_aggregation():
    """Test data aggregation system."""
    print("\n" + "=" * 60)
    print("TESTING DATA AGGREGATION")
    print("=" * 60)
    
    # Create sample data for aggregation
    from src.data_collection.base_collector import CollectedData, DataSource
    
    sample_data = [
        CollectedData(
            source=DataSource("PubMed", "https://pubmed.ncbi.nlm.nih.gov/", "academic", 0.9),
            data={"title": "AI in Healthcare", "description": "Study on AI applications", "authors": "Dr. Smith"},
            collected_at=datetime.now(),
            data_type="academic_paper",
            quality_score=0.9,
            relevance_score=0.8
        ),
        CollectedData(
            source=DataSource("ArXiv", "https://arxiv.org/", "academic", 0.8),
            data={"title": "AI in Healthcare", "description": "Research on AI applications in medical field", "authors": "Dr. Johnson"},
            collected_at=datetime.now(),
            data_type="academic_paper",
            quality_score=0.8,
            relevance_score=0.7
        ),
        CollectedData(
            source=DataSource("Reuters", "https://reuters.com/", "news", 0.8),
            data={"title": "Healthcare Market Analysis", "content": "Market trends in healthcare"},
            collected_at=datetime.now(),
            data_type="news_article",
            quality_score=0.8,
            relevance_score=0.6
        )
    ]
    
    # Test aggregation
    config = AggregationConfig(
        enable_deduplication=True,
        enable_merging=True,
        similarity_threshold=0.7
    )
    
    aggregator = DataAggregator(config)
    aggregated_results = aggregator.aggregate_data({"test": sample_data})
    
    print(f"Original items: {len(sample_data)}")
    print(f"Aggregated items: {len(aggregated_results)}")
    
    for item in aggregated_results:
        print(f"   {item.id}: {item.title} (confidence: {item.confidence_score:.2f}, sources: {len(item.source_data)})")
    
    # Test search functionality
    search_results = aggregator.search_aggregated_data("healthcare", min_confidence=0.5)
    print(f"\nSearch results for 'healthcare': {len(search_results)} items")
    
    # Test summary
    summary = aggregator.get_aggregation_summary()
    print(f"\nAggregation summary: {summary}")


async def test_collection_manager():
    """Test the data collection manager."""
    print("\n" + "=" * 60)
    print("TESTING DATA COLLECTION MANAGER")
    print("=" * 60)
    
    # Test with different strategies
    strategies = [CollectionStrategy.QUICK, CollectionStrategy.FOCUSED]
    
    for strategy in strategies:
        print(f"\nTesting strategy: {strategy.value}")
        
        config = CollectionConfig(
            strategy=strategy,
            max_parallel_tasks=3,
            timeout_seconds=60,
            validation_level=ValidationLevel.STANDARD,
            enable_aggregation=True,
            max_results_per_source=2
        )
        
        manager = DataCollectionManager(config)
        
        # Test collector info
        collector_info = manager.get_collector_info()
        print(f"   Available collectors: {list(collector_info.keys())}")
        
        # Test data collection
        try:
            await manager.initialize()
            result = await manager.collect_data("artificial intelligence in healthcare")
            await manager.cleanup()
            print(f"   Collection success: {result.success}")
            print(f"   Total items: {result.total_items_collected}")
            print(f"   Items by collector: {result.items_by_collector}")
            print(f"   Collection time: {result.collection_time_seconds:.2f}s")
            print(f"   Aggregated items: {len(result.aggregated_data) if result.aggregated_data else 0}")
            
            if result.quality_report:
                print(f"   Quality report: {result.quality_report['overall_summary']['validation_rate']:.2f} validation rate")
            
        except Exception as e:
            print(f"   Collection error: {e}")
    
    # Test specific source collection
    print(f"\nTesting specific source collection...")
    config = CollectionConfig(strategy=CollectionStrategy.FOCUSED)
    manager = DataCollectionManager(config)
    
    source_requests = [
        {"collector": "financial", "source": "yahoo_finance", "params": {"max_results": 2}},
        {"collector": "news", "source": "google_news", "params": {"max_results": 2}},
        {"collector": "academic", "source": "pubmed", "params": {"max_results": 2}}
    ]
    
    try:
        await manager.initialize()
        result = await manager.collect_from_specific_sources("AI healthcare", source_requests)
        await manager.cleanup()
        print(f"   Specific collection success: {result.success}")
        print(f"   Total items: {result.total_items_collected}")
        print(f"   Items by collector: {result.items_by_collector}")
        print(f"   Errors: {len(result.errors)}")
        
    except Exception as e:
        print(f"   Specific collection error: {e}")


async def test_collector_testing():
    """Test the collector testing functionality."""
    print("\n" + "=" * 60)
    print("TESTING COLLECTOR TESTING FUNCTIONALITY")
    print("=" * 60)
    
    config = CollectionConfig(strategy=CollectionStrategy.QUICK)
    manager = DataCollectionManager(config)
    
    try:
        await manager.initialize()
        test_results = await manager.test_collectors()
        await manager.cleanup()
        print("Collector test results:")
        for collector_name, result in test_results.items():
            print(f"   {collector_name}: {result['status']} - {result['items_collected']} items")
            if result.get('error'):
                print(f"      Error: {result['error']}")
    except Exception as e:
        print(f"   Testing error: {e}")


async def main():
    """Run all tests."""
    print("COMPREHENSIVE DATA COLLECTION SYSTEM TEST")
    print("=" * 60)
    print(f"Test started at: {datetime.now()}")
    
    try:
        # Test individual collectors
        await test_individual_collectors()
        
        # Test data validation
        await test_data_validation()
        
        # Test data aggregation
        await test_data_aggregation()
        
        # Test collection manager
        await test_collection_manager()
        
        # Test collector testing
        await test_collector_testing()
        
        print("\n" + "=" * 60)
        print("ALL TESTS COMPLETED SUCCESSFULLY")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
