"""
Data Collection Module

This module provides comprehensive live data collection capabilities
for the multi-agent research system, utilizing free resources and APIs.
"""

from .base_collector import BaseDataCollector, CollectedData, DataSource
from .data_validator import DataValidator, ValidationLevel, ValidationResult
from .data_aggregator import DataAggregator, AggregationConfig, AggregatedData
from .data_collection_manager import DataCollectionManager, CollectionConfig, CollectionResult, CollectionStrategy
from .financial_collector import FinancialDataCollector
from .news_collector import NewsDataCollector
from .academic_collector import AcademicDataCollector
from .government_collector import GovernmentDataCollector
from .competitive_collector import CompetitiveDataCollector
from .web_scraper import WebScraper

__all__ = [
    # Base classes
    'BaseDataCollector',
    'CollectedData', 
    'DataSource',
    
    # Validation
    'DataValidator',
    'ValidationLevel',
    'ValidationResult',
    
    # Aggregation
    'DataAggregator',
    'AggregationConfig',
    'AggregatedData',
    
    # Management
    'DataCollectionManager',
    'CollectionConfig',
    'CollectionResult',
    'CollectionStrategy',
    
    # Collectors
    'FinancialDataCollector',
    'NewsDataCollector', 
    'AcademicDataCollector',
    'GovernmentDataCollector',
    'CompetitiveDataCollector',
    
    # Utilities
    'WebScraper'
]
