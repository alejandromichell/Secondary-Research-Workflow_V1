"""
Data Collection Agent implementation for live data gathering.
"""
import os
import asyncio
import aiohttp
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
from bs4 import BeautifulSoup
import yfinance as yf
import requests
from dataclasses import dataclass

from .base_agent import BaseResearchAgent


@dataclass
class DataSource:
    """Represents a data source with metadata."""
    name: str
    url: str
    data_type: str  # 'api', 'web', 'financial', 'academic'
    quality_score: float
    last_updated: datetime
    data: Any = None


class DataCollectionAgent(BaseResearchAgent):
    """Agent responsible for live data collection from multiple sources."""
    
    def __init__(self):
        super().__init__("data_collection_agent")
        self.session = None
        self.collected_sources = []
    
    def get_tools(self) -> List:
        """Get tools for data collection."""
        return []
    
    def get_instruction(self) -> str:
        """Get agent instruction."""
        return (
            "You are a data collection specialist responsible for gathering "
            "live data from external APIs, web scraping, and real-time sources."
        )
        
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def collect_academic_sources(self, topic: str, keywords: List[str]) -> List[DataSource]:
        """Collect data from academic sources using APIs."""
        sources = []
        
        # PubMed API for medical/healthcare research
        if any(kw in topic.lower() for kw in ['health', 'medical', 'clinical', 'drug', 'treatment']):
            pubmed_sources = await self._fetch_pubmed_data(topic, keywords)
            sources.extend(pubmed_sources)
        
        # ArXiv API for technology/computer science
        if any(kw in topic.lower() for kw in ['ai', 'artificial intelligence', 'machine learning', 'technology', 'algorithm']):
            arxiv_sources = await self._fetch_arxiv_data(topic, keywords)
            sources.extend(arxiv_sources)
        
        return sources
    
    async def _fetch_pubmed_data(self, topic: str, keywords: List[str]) -> List[DataSource]:
        """Fetch data from PubMed API."""
        sources = []
        base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
        
        try:
            # Search for articles
            search_query = f"{topic} {' '.join(keywords[:3])}"
            search_url = f"{base_url}esearch.fcgi?db=pubmed&term={search_query}&retmax=10&retmode=json"
            
            async with self.session.get(search_url) as response:
                if response.status == 200:
                    data = await response.json()
                    pmids = data.get('esearchresult', {}).get('idlist', [])
                    
                    # Fetch article details
                    for pmid in pmids[:5]:  # Limit to 5 articles
                        detail_url = f"{base_url}efetch.fcgi?db=pubmed&id={pmid}&retmode=json"
                        
                        async with self.session.get(detail_url) as detail_response:
                            if detail_response.status == 200:
                                article_data = await detail_response.json()
                                article = article_data.get('result', {}).get(pmid, {})
                                
                                source = DataSource(
                                    name=f"PubMed Article: {article.get('title', 'Unknown')[:50]}...",
                                    url=f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                                    data_type='academic',
                                    quality_score=0.9,
                                    last_updated=datetime.now(),
                                    data={
                                        'title': article.get('title', ''),
                                        'abstract': article.get('abstract', ''),
                                        'authors': article.get('authors', []),
                                        'journal': article.get('source', ''),
                                        'pub_date': article.get('pubdate', ''),
                                        'pmid': pmid
                                    }
                                )
                                sources.append(source)
                                
        except Exception as e:
            print(f"Error fetching PubMed data: {e}")
        
        return sources
    
    async def _fetch_arxiv_data(self, topic: str, keywords: List[str]) -> List[DataSource]:
        """Fetch data from ArXiv API."""
        sources = []
        base_url = "http://export.arxiv.org/api/query"
        
        try:
            search_query = f"all:{topic} {' '.join(keywords[:2])}"
            params = {
                'search_query': search_query,
                'start': 0,
                'max_results': 5,
                'sortBy': 'relevance',
                'sortOrder': 'descending'
            }
            
            async with self.session.get(base_url, params=params) as response:
                if response.status == 200:
                    content = await response.text()
                    # Parse XML response (simplified)
                    if 'entry' in content:
                        # Extract basic information
                        source = DataSource(
                            name=f"ArXiv Paper: {topic}",
                            url="http://arxiv.org/",
                            data_type='academic',
                            quality_score=0.85,
                            last_updated=datetime.now(),
                            data={
                                'content': content[:1000],  # First 1000 chars
                                'source': 'arxiv',
                                'topic': topic
                            }
                        )
                        sources.append(source)
                        
        except Exception as e:
            print(f"Error fetching ArXiv data: {e}")
        
        return sources
    
    async def collect_industry_reports(self, topic: str, keywords: List[str]) -> List[DataSource]:
        """Collect data from industry report sources."""
        sources = []
        
        # Financial data from Yahoo Finance
        if any(kw in topic.lower() for kw in ['market', 'industry', 'company', 'financial']):
            financial_sources = await self._fetch_financial_data(topic)
            sources.extend(financial_sources)
        
        # News and industry reports
        news_sources = await self._scrape_industry_news(topic, keywords)
        sources.extend(news_sources)
        
        return sources
    
    async def _fetch_financial_data(self, topic: str) -> List[DataSource]:
        """Fetch financial data from Yahoo Finance."""
        sources = []
        
        try:
            # Get market data for relevant tickers
            tickers = self._get_relevant_tickers(topic)
            
            for ticker in tickers[:3]:  # Limit to 3 tickers
                try:
                    stock = yf.Ticker(ticker)
                    info = stock.info
                    hist = stock.history(period="1mo")
                    
                    if not hist.empty:
                        source = DataSource(
                            name=f"Financial Data: {info.get('longName', ticker)}",
                            url=f"https://finance.yahoo.com/quote/{ticker}",
                            data_type='financial',
                            quality_score=0.95,
                            last_updated=datetime.now(),
                            data={
                                'ticker': ticker,
                                'company_name': info.get('longName', ''),
                                'sector': info.get('sector', ''),
                                'market_cap': info.get('marketCap', 0),
                                'pe_ratio': info.get('trailingPE', 0),
                                'price': info.get('currentPrice', 0),
                                'volume': hist['Volume'].iloc[-1] if len(hist) > 0 else 0,
                                'price_change': hist['Close'].iloc[-1] - hist['Close'].iloc[0] if len(hist) > 1 else 0
                            }
                        )
                        sources.append(source)
                        
                except Exception as e:
                    print(f"Error fetching data for {ticker}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error in financial data collection: {e}")
        
        return sources
    
    def _get_relevant_tickers(self, topic: str) -> List[str]:
        """Get relevant stock tickers based on topic."""
        ticker_mapping = {
            'ai': ['NVDA', 'MSFT', 'GOOGL', 'META', 'TSLA'],
            'artificial intelligence': ['NVDA', 'MSFT', 'GOOGL', 'META', 'TSLA'],
            'healthcare': ['JNJ', 'PFE', 'UNH', 'ABT', 'MRK'],
            'medical': ['JNJ', 'PFE', 'UNH', 'ABT', 'MRK'],
            'technology': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META'],
            'energy': ['XOM', 'CVX', 'COP', 'EOG', 'SLB'],
            'finance': ['JPM', 'BAC', 'WFC', 'GS', 'MS'],
            'automotive': ['TSLA', 'F', 'GM', 'TM', 'HMC']
        }
        
        topic_lower = topic.lower()
        for keyword, tickers in ticker_mapping.items():
            if keyword in topic_lower:
                return tickers
        
        return ['SPY', 'QQQ', 'IWM']  # Default market indices
    
    async def _scrape_industry_news(self, topic: str, keywords: List[str]) -> List[DataSource]:
        """Scrape industry news and reports."""
        sources = []
        
        # News sources to scrape
        news_sources = [
            {
                'name': 'Reuters Business',
                'url': 'https://www.reuters.com/business',
                'search_pattern': f'search?q={topic}'
            },
            {
                'name': 'Bloomberg',
                'url': 'https://www.bloomberg.com',
                'search_pattern': f'search?query={topic}'
            }
        ]
        
        for news_source in news_sources:
            try:
                search_url = f"{news_source['url']}/{news_source['search_pattern']}"
                
                async with self.session.get(search_url) as response:
                    if response.status == 200:
                        content = await response.text()
                        soup = BeautifulSoup(content, 'html.parser')
                        
                        # Extract headlines and links (simplified)
                        headlines = soup.find_all(['h1', 'h2', 'h3'], limit=3)
                        
                        for headline in headlines:
                            if headline.text.strip():
                                source = DataSource(
                                    name=f"{news_source['name']}: {headline.text.strip()[:50]}...",
                                    url=search_url,
                                    data_type='news',
                                    quality_score=0.8,
                                    last_updated=datetime.now(),
                                    data={
                                        'headline': headline.text.strip(),
                                        'source': news_source['name'],
                                        'url': search_url,
                                        'topic': topic
                                    }
                                )
                                sources.append(source)
                                
            except Exception as e:
                print(f"Error scraping {news_source['name']}: {e}")
                continue
        
        return sources
    
    async def collect_government_data(self, topic: str, keywords: List[str]) -> List[DataSource]:
        """Collect data from government sources."""
        sources = []
        
        # FDA data for healthcare topics
        if any(kw in topic.lower() for kw in ['health', 'medical', 'drug', 'fda']):
            fda_sources = await self._fetch_fda_data(topic)
            sources.extend(fda_sources)
        
        # SEC data for financial topics
        if any(kw in topic.lower() for kw in ['financial', 'company', 'market', 'sec']):
            sec_sources = await self._fetch_sec_data(topic)
            sources.extend(sec_sources)
        
        return sources
    
    async def _fetch_fda_data(self, topic: str) -> List[DataSource]:
        """Fetch data from FDA API."""
        sources = []
        
        try:
            # FDA Drug Approvals API
            api_url = "https://api.fda.gov/drug/label.json"
            params = {
                'search': f'openfda.brand_name:"{topic}"',
                'limit': 3
            }
            
            async with self.session.get(api_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    results = data.get('results', [])
                    
                    for result in results:
                        source = DataSource(
                            name=f"FDA Drug Data: {result.get('openfda', {}).get('brand_name', ['Unknown'])[0]}",
                            url="https://www.fda.gov/",
                            data_type='government',
                            quality_score=0.95,
                            last_updated=datetime.now(),
                            data={
                                'drug_name': result.get('openfda', {}).get('brand_name', ['Unknown'])[0],
                                'manufacturer': result.get('openfda', {}).get('manufacturer_name', ['Unknown'])[0],
                                'indications': result.get('indications_and_usage', [''])[0],
                                'source': 'FDA'
                            }
                        )
                        sources.append(source)
                        
        except Exception as e:
            print(f"Error fetching FDA data: {e}")
        
        return sources
    
    async def _fetch_sec_data(self, topic: str) -> List[DataSource]:
        """Fetch data from SEC API."""
        sources = []
        
        try:
            # SEC EDGAR API for company filings
            api_url = "https://data.sec.gov/api/xbrl/companyfacts/CIK0000789019.json"
            
            async with self.session.get(api_url, headers={'User-Agent': 'Research Agent contact@example.com'}) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    source = DataSource(
                        name=f"SEC Company Data: {data.get('entityName', 'Unknown')}",
                        url="https://www.sec.gov/",
                        data_type='government',
                        quality_score=0.95,
                        last_updated=datetime.now(),
                        data={
                            'company_name': data.get('entityName', ''),
                            'cik': data.get('cik', ''),
                            'sic': data.get('sic', ''),
                            'state': data.get('stateOfIncorporation', ''),
                            'fiscal_year_end': data.get('entityFiscalYearEnd', ''),
                            'source': 'SEC'
                        }
                    )
                    sources.append(source)
                    
        except Exception as e:
            print(f"Error fetching SEC data: {e}")
        
        return sources
    
    async def collect_all_sources(self, topic: str, keywords: List[str]) -> Dict[str, Any]:
        """Collect data from all source types."""
        print(f"--- Starting live data collection for topic: {topic} ---")
        
        all_sources = []
        
        # Collect from different source types concurrently
        tasks = [
            self.collect_academic_sources(topic, keywords),
            self.collect_industry_reports(topic, keywords),
            self.collect_government_data(topic, keywords)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, list):
                all_sources.extend(result)
            else:
                print(f"Error in data collection task: {result}")
        
        # Calculate quality metrics
        total_sources = len(all_sources)
        avg_quality = sum(source.quality_score for source in all_sources) / total_sources if total_sources > 0 else 0
        
        # Group sources by type
        sources_by_type = {}
        for source in all_sources:
            if source.data_type not in sources_by_type:
                sources_by_type[source.data_type] = []
            sources_by_type[source.data_type].append(source)
        
        collection_results = {
            'research_id': f"live_research_{topic.replace(' ', '_')}",
            'topic': topic,
            'collection_timestamp': datetime.now().isoformat(),
            'total_sources_collected': total_sources,
            'average_quality_score': avg_quality,
            'sources_by_type': {
                data_type: [
                    {
                        'name': source.name,
                        'url': source.url,
                        'quality_score': source.quality_score,
                        'data': source.data
                    }
                    for source in sources
                ]
                for data_type, sources in sources_by_type.items()
            },
            'collection_summary': {
                'academic_sources': len(sources_by_type.get('academic', [])),
                'financial_sources': len(sources_by_type.get('financial', [])),
                'news_sources': len(sources_by_type.get('news', [])),
                'government_sources': len(sources_by_type.get('government', []))
            }
        }
        
        print(f"--- Live data collection completed: {total_sources} sources collected ---")
        
        return collection_results


def create_data_collection_agent() -> DataCollectionAgent:
    """Factory function to create data collection agent."""
    return DataCollectionAgent()
