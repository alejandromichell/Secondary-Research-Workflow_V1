"""
Base Data Collector

Abstract base class for all data collectors in the system.
Provides common functionality and interface for data collection operations.
"""

import asyncio
import aiohttp
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
import json
import os
from dataclasses import dataclass


@dataclass
class DataSource:
    """Represents a data source with metadata."""
    name: str
    url: str
    category: str
    reliability_score: float  # 0.0 to 1.0
    last_accessed: Optional[datetime] = None
    rate_limit: Optional[int] = None  # requests per minute
    requires_auth: bool = False
    description: str = ""


@dataclass
class CollectedData:
    """Represents collected data with metadata."""
    source: DataSource
    data: Any
    collected_at: datetime
    data_type: str
    quality_score: float  # 0.0 to 1.0
    relevance_score: float  # 0.0 to 1.0
    raw_response: Optional[str] = None
    processing_notes: List[str] = None
    
    def __post_init__(self):
        if self.processing_notes is None:
            self.processing_notes = []


class BaseDataCollector(ABC):
    """Abstract base class for data collectors."""
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.session: Optional[aiohttp.ClientSession] = None
        self.sources: List[DataSource] = []
        self.collected_data: List[CollectedData] = []
        self.rate_limits: Dict[str, datetime] = {}
        
    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.cleanup()
    
    async def initialize(self):
        """Initialize the data collector."""
        connector = aiohttp.TCPConnector(limit=100, limit_per_host=30)
        timeout = aiohttp.ClientTimeout(total=30, connect=10)
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={
                'User-Agent': 'Secondary Research Workflow Bot 1.0 (Educational Use)'
            }
        )
        print(f">>> {self.name}: Initialized data collector", flush=True)
    
    async def cleanup(self):
        """Clean up resources."""
        if self.session:
            await self.session.close()
        print(f">>> {self.name}: Cleaned up data collector", flush=True)
    
    @abstractmethod
    async def collect_data(self, query: str, **kwargs) -> List[CollectedData]:
        """
        Collect data based on the query.
        
        Args:
            query: Search query or topic
            **kwargs: Additional parameters specific to the collector
            
        Returns:
            List of collected data items
        """
        pass
    
    @abstractmethod
    def get_supported_sources(self) -> List[DataSource]:
        """Get list of supported data sources."""
        pass
    
    async def make_request(self, 
                          url: str, 
                          method: str = "GET",
                          params: Optional[Dict] = None,
                          headers: Optional[Dict] = None,
                          data: Optional[Any] = None,
                          source_name: str = "unknown") -> Optional[aiohttp.ClientResponse]:
        """
        Make an HTTP request with rate limiting and error handling.
        
        Args:
            url: Request URL
            method: HTTP method
            params: Query parameters
            headers: Request headers
            data: Request body
            source_name: Name of the data source for rate limiting
            
        Returns:
            HTTP response or None if failed
        """
        if not self.session:
            raise RuntimeError("Data collector not initialized")
        
        # Check rate limits
        if self._is_rate_limited(source_name):
            print(f">>> {self.name}: Rate limited for {source_name}, waiting...", flush=True)
            await asyncio.sleep(60)  # Wait 1 minute
        
        try:
            # Make the request
            async with self.session.request(
                method=method,
                url=url,
                params=params,
                headers=headers,
                data=data
            ) as response:
                # Update rate limit tracking
                self._update_rate_limit(source_name)
                
                if response.status == 200:
                    return response
                else:
                    print(f">>> {self.name}: Request failed with status {response.status} for {url}", flush=True)
                    return None
                    
        except asyncio.TimeoutError:
            print(f">>> {self.name}: Request timeout for {url}", flush=True)
            return None
        except Exception as e:
            print(f">>> {self.name}: Request error for {url}: {e}", flush=True)
            return None
    
    def _is_rate_limited(self, source_name: str) -> bool:
        """Check if a source is currently rate limited."""
        if source_name not in self.rate_limits:
            return False
        
        last_request = self.rate_limits[source_name]
        # Check if less than 1 minute has passed
        return datetime.now() - last_request < timedelta(minutes=1)
    
    def _update_rate_limit(self, source_name: str):
        """Update the rate limit timestamp for a source."""
        self.rate_limits[source_name] = datetime.now()
    
    def calculate_quality_score(self, data: Any, source: DataSource) -> float:
        """
        Calculate a quality score for collected data.
        
        Args:
            data: The collected data
            source: The data source
            
        Returns:
            Quality score between 0.0 and 1.0
        """
        score = source.reliability_score
        
        # Adjust based on data characteristics
        if isinstance(data, dict):
            if len(data) > 0:
                score += 0.1
            if any(key in data for key in ['date', 'timestamp', 'published']):
                score += 0.1
        elif isinstance(data, list):
            if len(data) > 0:
                score += 0.1
        elif isinstance(data, str):
            if len(data) > 100:  # Substantial content
                score += 0.1
        
        return min(score, 1.0)
    
    def calculate_relevance_score(self, data: Any, query: str) -> float:
        """
        Calculate a relevance score for collected data.
        
        Args:
            data: The collected data
            query: The original search query
            
        Returns:
            Relevance score between 0.0 and 1.0
        """
        query_lower = query.lower()
        relevance_score = 0.5  # Base score
        
        # Simple keyword matching
        if isinstance(data, dict):
            text_content = ' '.join(str(v) for v in data.values()).lower()
        elif isinstance(data, str):
            text_content = data.lower()
        else:
            text_content = str(data).lower()
        
        # Count query word matches
        query_words = query_lower.split()
        matches = sum(1 for word in query_words if word in text_content)
        
        if matches > 0:
            relevance_score += (matches / len(query_words)) * 0.5
        
        return min(relevance_score, 1.0)
    
    def save_collected_data(self, data: List[CollectedData], filename: str):
        """
        Save collected data to a file.
        
        Args:
            data: List of collected data items
            filename: Output filename
        """
        os.makedirs("data/collected", exist_ok=True)
        
        # Convert to serializable format
        serializable_data = []
        for item in data:
            serializable_item = {
                "source": {
                    "name": item.source.name,
                    "url": item.source.url,
                    "category": item.source.category,
                    "reliability_score": item.source.reliability_score
                },
                "data": item.data,
                "collected_at": item.collected_at.isoformat(),
                "data_type": item.data_type,
                "quality_score": item.quality_score,
                "relevance_score": item.relevance_score,
                "processing_notes": item.processing_notes
            }
            serializable_data.append(serializable_item)
        
        filepath = os.path.join("data/collected", filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(serializable_data, f, indent=2, ensure_ascii=False)
        
        print(f">>> {self.name}: Saved {len(data)} data items to {filepath}", flush=True)
    
    def get_collection_summary(self) -> Dict[str, Any]:
        """Get a summary of collected data."""
        if not self.collected_data:
            return {"total_items": 0, "sources_used": 0}
        
        sources_used = set(item.source.name for item in self.collected_data)
        avg_quality = sum(item.quality_score for item in self.collected_data) / len(self.collected_data)
        avg_relevance = sum(item.relevance_score for item in self.collected_data) / len(self.collected_data)
        
        return {
            "total_items": len(self.collected_data),
            "sources_used": len(sources_used),
            "average_quality_score": round(avg_quality, 3),
            "average_relevance_score": round(avg_relevance, 3),
            "collection_timestamp": datetime.now().isoformat()
        }
