"""
Competitive Data Collector

Collects competitive analysis data from various free sources including:
- Google Trends
- Builtwith
- Product Hunt
- G2/Capterra
- Wayback Machine
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


class CompetitiveDataCollector(BaseDataCollector):
    """Collects competitive analysis data from various free sources."""
    
    def __init__(self):
        super().__init__(
            name="Competitive Data Collector",
            description="Collects competitive analysis data from Google Trends, Builtwith, Product Hunt, and other sources"
        )
        self.sources = self._initialize_sources()
    
    def _initialize_sources(self) -> List[DataSource]:
        """Initialize supported data sources."""
        return [
            DataSource(
                name="Google Trends",
                url="https://trends.google.com",
                category="trends",
                reliability_score=0.90,
                description="Search trends, geographic interest, and related queries"
            ),
            DataSource(
                name="Builtwith",
                url="https://builtwith.com",
                category="technology",
                reliability_score=0.85,
                description="Technology stack analysis for competitors"
            ),
            DataSource(
                name="Product Hunt",
                url="https://www.producthunt.com",
                category="products",
                reliability_score=0.80,
                description="New product launches and innovations"
            ),
            DataSource(
                name="G2",
                url="https://www.g2.com",
                category="reviews",
                reliability_score=0.85,
                description="Software reviews and competitive comparisons"
            ),
            DataSource(
                name="Wayback Machine",
                url="https://web.archive.org",
                category="historical",
                reliability_score=0.95,
                description="Historical website data and changes"
            )
        ]
    
    async def collect_data(self, query: str, **kwargs) -> List[CollectedData]:
        """
        Collect competitive data based on the query.
        
        Args:
            query: Company name, product, or competitive topic
            **kwargs: Additional parameters like 'competitors', 'timeframe', etc.
            
        Returns:
            List of collected competitive data
        """
        print(f">>> {self.name}: Starting competitive data collection for '{query}'", flush=True)
        
        collected_data = []
        competitors = kwargs.get('competitors', [])
        timeframe = kwargs.get('timeframe', '12m')  # Default to last 12 months
        
        # Collect from different sources
        trends_data = await self._collect_google_trends(query, competitors, timeframe)
        if trends_data:
            collected_data.extend(trends_data)
        
        builtwith_data = await self._collect_builtwith_data(query, competitors)
        if builtwith_data:
            collected_data.extend(builtwith_data)
        
        producthunt_data = await self._collect_producthunt_data(query)
        if producthunt_data:
            collected_data.extend(producthunt_data)
        
        g2_data = await self._collect_g2_data(query)
        if g2_data:
            collected_data.extend(g2_data)
        
        wayback_data = await self._collect_wayback_data(query, competitors)
        if wayback_data:
            collected_data.extend(wayback_data)
        
        self.collected_data.extend(collected_data)
        print(f">>> {self.name}: Collected {len(collected_data)} competitive data items", flush=True)
        
        return collected_data
    
    def get_supported_sources(self) -> List[DataSource]:
        """Get list of supported competitive data sources."""
        return self.sources
    
    async def _collect_google_trends(self, query: str, competitors: List[str], timeframe: str) -> List[CollectedData]:
        """Collect data from Google Trends."""
        collected_data = []
        
        try:
            # Google Trends API (unofficial)
            # Note: This is a simplified approach - Google Trends has rate limiting
            
            # Create a comparison query with competitors
            comparison_terms = [query] + competitors[:4]  # Limit to 5 terms total
            terms_str = ','.join(comparison_terms)
            encoded_terms = quote(terms_str)
            
            # Google Trends URL
            trends_url = f"https://trends.google.com/trends/api/explore?hl=en-US&tz=-480&req={{\"comparisonItem\":[{{\"keyword\":\"{encoded_terms}\",\"geo\":\"US\",\"time\":\"today 12-m\"}}],\"category\":0,\"property\":\"\"}}&tz=-480"
            
            # Note: Google Trends requires proper headers and may block automated requests
            # This is a simplified example
            trends_data = {
                "query": query,
                "competitors": competitors,
                "timeframe": timeframe,
                "note": "Google Trends requires proper headers and may have rate limits",
                "suggested_approach": "Use Google Trends API with proper authentication or manual data collection",
                "source": "Google Trends",
                "collected_at": datetime.now().isoformat()
            }
            
            data_item = CollectedData(
                source=self.sources[0],  # Google Trends
                data=trends_data,
                collected_at=datetime.now(),
                data_type="trends_analysis",
                quality_score=0.7,  # Lower score due to access limitations
                relevance_score=self.calculate_relevance_score(query, query),
                processing_notes=["Google Trends requires proper access"]
            )
            collected_data.append(data_item)
            
        except Exception as e:
            print(f">>> {self.name}: Error collecting Google Trends data: {e}", flush=True)
        
        return collected_data
    
    async def _collect_builtwith_data(self, query: str, competitors: List[str]) -> List[CollectedData]:
        """Collect technology stack data from Builtwith."""
        collected_data = []
        
        try:
            # Builtwith technology lookup
            # Note: Builtwith has rate limiting and may require authentication
            
            for competitor in [query] + competitors[:2]:  # Limit to 3 sites
                # Builtwith URL
                builtwith_url = f"https://builtwith.com/{quote(competitor)}"
                
                response = await self.make_request(builtwith_url, source_name="Builtwith")
                if response:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Extract technology information
                    technologies = []
                    tech_sections = soup.find_all('div', class_='techItem')
                    
                    for tech in tech_sections[:10]:  # Limit to 10 technologies
                        tech_name = tech.get_text(strip=True)
                        if tech_name:
                            technologies.append(tech_name)
                    
                    # Extract hosting information
                    hosting_info = ""
                    hosting_section = soup.find('div', class_='hosting')
                    if hosting_section:
                        hosting_info = hosting_section.get_text(strip=True)
                    
                    builtwith_data = {
                        "domain": competitor,
                        "technologies": technologies,
                        "hosting": hosting_info,
                        "total_technologies": len(technologies),
                        "source": "Builtwith",
                        "query": query
                    }
                    
                    data_item = CollectedData(
                        source=self.sources[1],  # Builtwith
                        data=builtwith_data,
                        collected_at=datetime.now(),
                        data_type="technology_stack",
                        quality_score=self.calculate_quality_score(builtwith_data, self.sources[1]),
                        relevance_score=self.calculate_relevance_score(competitor, query),
                        processing_notes=["Builtwith web scraping"]
                    )
                    collected_data.append(data_item)
                
                # Add delay between requests
                await asyncio.sleep(2)
                
        except Exception as e:
            print(f">>> {self.name}: Error collecting Builtwith data: {e}", flush=True)
        
        return collected_data
    
    async def _collect_producthunt_data(self, query: str) -> List[CollectedData]:
        """Collect data from Product Hunt."""
        collected_data = []
        
        try:
            # Product Hunt search
            encoded_query = quote(query)
            ph_url = f"https://www.producthunt.com/search?q={encoded_query}"
            
            response = await self.make_request(ph_url, source_name="Product Hunt")
            if response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Find product results
                products = soup.find_all('div', class_='styles_item')
                
                for product in products[:5]:  # Limit to 5 products
                    title_elem = product.find('h3')
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    
                    # Extract product description
                    desc_elem = product.find('p')
                    description = desc_elem.get_text(strip=True) if desc_elem else ""
                    
                    # Extract votes/upvotes
                    votes_elem = product.find('span', class_='styles_voteCount')
                    votes = 0
                    if votes_elem:
                        votes_text = votes_elem.get_text(strip=True)
                        votes_match = re.search(r'(\d+)', votes_text)
                        if votes_match:
                            votes = int(votes_match.group(1))
                    
                    # Extract product URL
                    link_elem = product.find('a')
                    product_url = link_elem.get('href') if link_elem else ""
                    if product_url and not product_url.startswith('http'):
                        product_url = urljoin("https://www.producthunt.com", product_url)
                    
                    ph_data = {
                        "title": title,
                        "description": description,
                        "votes": votes,
                        "url": product_url,
                        "source": "Product Hunt",
                        "query": query
                    }
                    
                    data_item = CollectedData(
                        source=self.sources[2],  # Product Hunt
                        data=ph_data,
                        collected_at=datetime.now(),
                        data_type="product_launch",
                        quality_score=self.calculate_quality_score(ph_data, self.sources[2]),
                        relevance_score=self.calculate_relevance_score(ph_data['title'] + ' ' + ph_data['description'], query),
                        processing_notes=["Product Hunt search results"]
                    )
                    collected_data.append(data_item)
                    
        except Exception as e:
            print(f">>> {self.name}: Error collecting Product Hunt data: {e}", flush=True)
        
        return collected_data
    
    async def _collect_g2_data(self, query: str) -> List[CollectedData]:
        """Collect data from G2."""
        collected_data = []
        
        try:
            # G2 search
            encoded_query = quote(query)
            g2_url = f"https://www.g2.com/search?utf8=%E2%9C%93&query={encoded_query}"
            
            response = await self.make_request(g2_url, source_name="G2")
            if response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Find product results
                products = soup.find_all('div', class_='product-listing')
                
                for product in products[:5]:  # Limit to 5 products
                    title_elem = product.find('h3')
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    
                    # Extract rating
                    rating_elem = product.find('div', class_='rating')
                    rating = 0
                    if rating_elem:
                        rating_text = rating_elem.get_text(strip=True)
                        rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                        if rating_match:
                            rating = float(rating_match.group(1))
                    
                    # Extract review count
                    reviews_elem = product.find('span', class_='review-count')
                    review_count = 0
                    if reviews_elem:
                        reviews_text = reviews_elem.get_text(strip=True)
                        reviews_match = re.search(r'(\d+)', reviews_text)
                        if reviews_match:
                            review_count = int(reviews_match.group(1))
                    
                    # Extract product URL
                    link_elem = product.find('a')
                    product_url = link_elem.get('href') if link_elem else ""
                    if product_url and not product_url.startswith('http'):
                        product_url = urljoin("https://www.g2.com", product_url)
                    
                    g2_data = {
                        "title": title,
                        "rating": rating,
                        "review_count": review_count,
                        "url": product_url,
                        "source": "G2",
                        "query": query
                    }
                    
                    data_item = CollectedData(
                        source=self.sources[3],  # G2
                        data=g2_data,
                        collected_at=datetime.now(),
                        data_type="product_review",
                        quality_score=self.calculate_quality_score(g2_data, self.sources[3]),
                        relevance_score=self.calculate_relevance_score(g2_data['title'], query),
                        processing_notes=["G2 search results"]
                    )
                    collected_data.append(data_item)
                    
        except Exception as e:
            print(f">>> {self.name}: Error collecting G2 data: {e}", flush=True)
        
        return collected_data
    
    async def _collect_wayback_data(self, query: str, competitors: List[str]) -> List[CollectedData]:
        """Collect historical data from Wayback Machine."""
        collected_data = []
        
        try:
            # Wayback Machine API
            for competitor in [query] + competitors[:2]:  # Limit to 3 sites
                wayback_url = f"https://web.archive.org/cdx/search/cdx?url={quote(competitor)}&output=json&limit=10"
                
                response = await self.make_request(wayback_url, source_name="Wayback Machine")
                if response:
                    wayback_data = await response.json()
                    
                    if isinstance(wayback_data, list) and len(wayback_data) > 1:
                        headers = wayback_data[0]
                        snapshots = wayback_data[1:]
                        
                        # Process snapshots
                        snapshot_info = []
                        for snapshot in snapshots[:5]:  # Limit to 5 snapshots
                            if len(snapshot) >= 3:
                                snapshot_info.append({
                                    "timestamp": snapshot[1],
                                    "url": snapshot[2],
                                    "status": snapshot[4] if len(snapshot) > 4 else "unknown"
                                })
                        
                        wayback_summary = {
                            "domain": competitor,
                            "total_snapshots": len(snapshots),
                            "recent_snapshots": snapshot_info,
                            "oldest_snapshot": snapshots[-1][1] if snapshots else None,
                            "newest_snapshot": snapshots[0][1] if snapshots else None,
                            "source": "Wayback Machine",
                            "query": query
                        }
                        
                        data_item = CollectedData(
                            source=self.sources[4],  # Wayback Machine
                            data=wayback_summary,
                            collected_at=datetime.now(),
                            data_type="historical_data",
                            quality_score=self.calculate_quality_score(wayback_summary, self.sources[4]),
                            relevance_score=self.calculate_relevance_score(competitor, query),
                            processing_notes=["Wayback Machine API"]
                        )
                        collected_data.append(data_item)
                
                # Add delay between requests
                await asyncio.sleep(1)
                
        except Exception as e:
            print(f">>> {self.name}: Error collecting Wayback Machine data: {e}", flush=True)
        
        return collected_data
