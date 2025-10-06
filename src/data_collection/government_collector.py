"""
Government Data Collector

Collects government and regulatory data from various free sources including:
- Federal Reserve Economic Data (FRED)
- Bureau of Labor Statistics (BLS)
- Census Bureau
- Data.gov
- Bureau of Economic Analysis (BEA)
- World Bank Open Data
"""

import asyncio
import aiohttp
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
import re
from bs4 import BeautifulSoup
from urllib.parse import quote, urljoin

from .base_collector import BaseDataCollector, DataSource, CollectedData


class GovernmentDataCollector(BaseDataCollector):
    """Collects government and regulatory data from various free sources."""
    
    def __init__(self):
        super().__init__(
            name="Government Data Collector",
            description="Collects government and regulatory data from FRED, BLS, Census, Data.gov, and other sources"
        )
        self.sources = self._initialize_sources()
    
    def _initialize_sources(self) -> List[DataSource]:
        """Initialize supported data sources."""
        return [
            DataSource(
                name="FRED (Federal Reserve)",
                url="https://fred.stlouisfed.org",
                category="economic",
                reliability_score=1.0,
                description="Economic indicators and financial data from the Federal Reserve"
            ),
            DataSource(
                name="Bureau of Labor Statistics",
                url="https://www.bls.gov",
                category="economic",
                reliability_score=1.0,
                description="Employment, wages, and productivity data"
            ),
            DataSource(
                name="Census Bureau",
                url="https://www.census.gov",
                category="demographic",
                reliability_score=1.0,
                description="Demographic and economic census data"
            ),
            DataSource(
                name="Data.gov",
                url="https://www.data.gov",
                category="government",
                reliability_score=1.0,
                description="US government open data portal"
            ),
            DataSource(
                name="Bureau of Economic Analysis",
                url="https://www.bea.gov",
                category="economic",
                reliability_score=1.0,
                description="GDP, economic growth, and industry data"
            ),
            DataSource(
                name="World Bank Open Data",
                url="https://data.worldbank.org",
                category="international",
                reliability_score=1.0,
                description="Global development and economic indicators"
            )
        ]
    
    async def collect_data(self, query: str, **kwargs) -> List[CollectedData]:
        """
        Collect government data based on the query.
        
        Args:
            query: Economic indicator, demographic topic, or data category
            **kwargs: Additional parameters like 'timeframe', 'geography', etc.
            
        Returns:
            List of collected government data
        """
        print(f">>> {self.name}: Starting government data collection for '{query}'", flush=True)
        
        collected_data = []
        timeframe = kwargs.get('timeframe', '5y')  # Default to last 5 years
        
        # Collect from different sources
        fred_data = await self._collect_fred_data(query, timeframe)
        if fred_data:
            collected_data.extend(fred_data)
        
        bls_data = await self._collect_bls_data(query)
        if bls_data:
            collected_data.extend(bls_data)
        
        census_data = await self._collect_census_data(query)
        if census_data:
            collected_data.extend(census_data)
        
        datagov_data = await self._collect_datagov_data(query)
        if datagov_data:
            collected_data.extend(datagov_data)
        
        worldbank_data = await self._collect_worldbank_data(query)
        if worldbank_data:
            collected_data.extend(worldbank_data)
        
        self.collected_data.extend(collected_data)
        print(f">>> {self.name}: Collected {len(collected_data)} government data items", flush=True)
        
        return collected_data
    
    def get_supported_sources(self) -> List[DataSource]:
        """Get list of supported government data sources."""
        return self.sources
    
    async def _collect_fred_data(self, query: str, timeframe: str) -> List[CollectedData]:
        """Collect data from Federal Reserve Economic Data (FRED)."""
        collected_data = []
        
        try:
            # FRED API search
            api_key = "demo"  # In production, use a real API key
            encoded_query = quote(query)
            search_url = f"https://api.stlouisfed.org/fred/series/search?search_text={encoded_query}&api_key={api_key}&file_type=json"
            
            response = await self.make_request(search_url, source_name="FRED")
            if response:
                search_data = await response.json()
                
                if 'seriess' in search_data:
                    for series in search_data['seriess'][:5]:  # Limit to 5 series
                        series_id = series.get('id')
                        title = series.get('title', '')
                        units = series.get('units', '')
                        frequency = series.get('frequency', '')
                        
                        # Get actual data for the series
                        data_url = f"https://api.stlouisfed.org/fred/series/observations?series_id={series_id}&api_key={api_key}&file_type=json&limit=100"
                        
                        data_response = await self.make_request(data_url, source_name="FRED")
                        if data_response:
                            series_data = await data_response.json()
                            
                            if 'observations' in series_data:
                                observations = series_data['observations']
                                latest_value = None
                                latest_date = None
                                
                                # Get the most recent non-null value
                                for obs in reversed(observations):
                                    if obs.get('value') != '.':
                                        latest_value = float(obs.get('value', 0))
                                        latest_date = obs.get('date')
                                        break
                                
                                fred_data = {
                                    "series_id": series_id,
                                    "title": title,
                                    "units": units,
                                    "frequency": frequency,
                                    "latest_value": latest_value,
                                    "latest_date": latest_date,
                                    "total_observations": len(observations),
                                    "source": "FRED",
                                    "query": query
                                }
                                
                                data_item = CollectedData(
                                    source=self.sources[0],  # FRED
                                    data=fred_data,
                                    collected_at=datetime.now(),
                                    data_type="economic_indicator",
                                    quality_score=self.calculate_quality_score(fred_data, self.sources[0]),
                                    relevance_score=self.calculate_relevance_score(fred_data['title'], query),
                                    processing_notes=["FRED API"]
                                )
                                collected_data.append(data_item)
                        
                        # Add delay between requests
                        await asyncio.sleep(0.5)
                        
        except Exception as e:
            print(f">>> {self.name}: Error collecting FRED data: {e}", flush=True)
        
        return collected_data
    
    async def _collect_bls_data(self, query: str) -> List[CollectedData]:
        """Collect data from Bureau of Labor Statistics."""
        collected_data = []
        
        try:
            # BLS API (requires registration for production use)
            # For demo purposes, we'll use a simplified approach
            
            # Common BLS series IDs for different economic indicators
            bls_series = {
                'unemployment': 'LNS14000000',
                'employment': 'LNS12300000',
                'inflation': 'CUUR0000SA0',
                'wages': 'CES0500000003'
            }
            
            # Find relevant series based on query
            relevant_series = []
            query_lower = query.lower()
            
            for indicator, series_id in bls_series.items():
                if indicator in query_lower or any(word in query_lower for word in ['employment', 'unemployment', 'inflation', 'wage']):
                    relevant_series.append((indicator, series_id))
            
            for indicator, series_id in relevant_series[:3]:  # Limit to 3 series
                # BLS API endpoint (simplified)
                bls_url = f"https://api.bls.gov/publicAPI/v2/timeseries/data/{series_id}"
                
                # Note: BLS API requires proper headers and may need authentication
                # This is a simplified example
                bls_data = {
                    "series_id": series_id,
                    "indicator": indicator,
                    "note": "BLS API requires proper authentication and headers",
                    "suggested_approach": "Use BLS API with proper registration",
                    "source": "BLS",
                    "query": query
                }
                
                data_item = CollectedData(
                    source=self.sources[1],  # BLS
                    data=bls_data,
                    collected_at=datetime.now(),
                    data_type="labor_statistics",
                    quality_score=0.7,  # Lower score due to access limitations
                    relevance_score=self.calculate_relevance_score(indicator, query),
                    processing_notes=["BLS API requires authentication"]
                )
                collected_data.append(data_item)
                
        except Exception as e:
            print(f">>> {self.name}: Error collecting BLS data: {e}", flush=True)
        
        return collected_data
    
    async def _collect_census_data(self, query: str) -> List[CollectedData]:
        """Collect data from Census Bureau."""
        collected_data = []
        
        try:
            # Census API search
            encoded_query = quote(query)
            census_url = f"https://api.census.gov/data/2020/dec/pl?get=NAME,P1_001N&for=state:*&key=demo"
            
            response = await self.make_request(census_url, source_name="Census Bureau")
            if response:
                census_data = await response.json()
                
                if isinstance(census_data, list) and len(census_data) > 1:
                    # Process census data
                    headers = census_data[0]
                    data_rows = census_data[1:]
                    
                    census_summary = {
                        "dataset": "2020 Decennial Census",
                        "total_states": len(data_rows),
                        "sample_data": data_rows[:5],  # First 5 states
                        "headers": headers,
                        "source": "Census Bureau",
                        "query": query
                    }
                    
                    data_item = CollectedData(
                        source=self.sources[2],  # Census Bureau
                        data=census_summary,
                        collected_at=datetime.now(),
                        data_type="census_data",
                        quality_score=self.calculate_quality_score(census_summary, self.sources[2]),
                        relevance_score=self.calculate_relevance_score("census demographic", query),
                        processing_notes=["Census API"]
                    )
                    collected_data.append(data_item)
                    
        except Exception as e:
            print(f">>> {self.name}: Error collecting Census data: {e}", flush=True)
        
        return collected_data
    
    async def _collect_datagov_data(self, query: str) -> List[CollectedData]:
        """Collect data from Data.gov."""
        collected_data = []
        
        try:
            # Data.gov API search
            encoded_query = quote(query)
            datagov_url = f"https://catalog.data.gov/api/3/action/package_search?q={encoded_query}&rows=10"
            
            response = await self.make_request(datagov_url, source_name="Data.gov")
            if response:
                search_data = await response.json()
                
                if 'result' in search_data and 'results' in search_data['result']:
                    datasets = search_data['result']['results']
                    
                    for dataset in datasets[:5]:  # Limit to 5 datasets
                        dataset_info = {
                            "title": dataset.get('title', ''),
                            "description": dataset.get('notes', ''),
                            "organization": dataset.get('organization', {}).get('title', ''),
                            "tags": [tag.get('display_name', '') for tag in dataset.get('tags', [])],
                            "url": dataset.get('url', ''),
                            "source": "Data.gov",
                            "query": query
                        }
                        
                        data_item = CollectedData(
                            source=self.sources[3],  # Data.gov
                            data=dataset_info,
                            collected_at=datetime.now(),
                            data_type="government_dataset",
                            quality_score=self.calculate_quality_score(dataset_info, self.sources[3]),
                            relevance_score=self.calculate_relevance_score(dataset_info['title'] + ' ' + dataset_info['description'], query),
                            processing_notes=["Data.gov API"]
                        )
                        collected_data.append(data_item)
                        
        except Exception as e:
            print(f">>> {self.name}: Error collecting Data.gov data: {e}", flush=True)
        
        return collected_data
    
    async def _collect_worldbank_data(self, query: str) -> List[CollectedData]:
        """Collect data from World Bank Open Data."""
        collected_data = []
        
        try:
            # World Bank API search
            encoded_query = quote(query)
            worldbank_url = f"https://api.worldbank.org/v2/country/all/indicator?format=json&per_page=10&q={encoded_query}"
            
            response = await self.make_request(worldbank_url, source_name="World Bank")
            if response:
                wb_data = await response.json()
                
                if isinstance(wb_data, list) and len(wb_data) > 1:
                    indicators = wb_data[1]  # Second element contains the data
                    
                    for indicator in indicators[:5]:  # Limit to 5 indicators
                        indicator_info = {
                            "indicator_id": indicator.get('indicator', {}).get('id', ''),
                            "indicator_name": indicator.get('indicator', {}).get('value', ''),
                            "country": indicator.get('country', {}).get('value', ''),
                            "date": indicator.get('date', ''),
                            "value": indicator.get('value'),
                            "source": "World Bank",
                            "query": query
                        }
                        
                        data_item = CollectedData(
                            source=self.sources[5],  # World Bank
                            data=indicator_info,
                            collected_at=datetime.now(),
                            data_type="world_bank_indicator",
                            quality_score=self.calculate_quality_score(indicator_info, self.sources[5]),
                            relevance_score=self.calculate_relevance_score(indicator_info['indicator_name'], query),
                            processing_notes=["World Bank API"]
                        )
                        collected_data.append(data_item)
                        
        except Exception as e:
            print(f">>> {self.name}: Error collecting World Bank data: {e}", flush=True)
        
        return collected_data
