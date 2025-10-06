"""
News Data Collector

Collects news and current events from various free sources including:
- Google News
- Reddit (industry subreddits)
- LinkedIn (public posts)
- Twitter/X (public tweets)
- Press release sites
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


class NewsDataCollector(BaseDataCollector):
    """Collects news and current events from various free sources."""
    
    def __init__(self):
        super().__init__(
            name="News Data Collector",
            description="Collects news and current events from Google News, Reddit, LinkedIn, and other sources"
        )
        self.sources = self._initialize_sources()
    
    def _initialize_sources(self) -> List[DataSource]:
        """Initialize supported data sources."""
        return [
            DataSource(
                name="Google News",
                url="https://news.google.com",
                category="news",
                reliability_score=0.90,
                description="Current events, company news, and industry updates"
            ),
            DataSource(
                name="Reddit",
                url="https://www.reddit.com",
                category="social",
                reliability_score=0.70,
                description="Community insights and sentiment analysis from industry subreddits"
            ),
            DataSource(
                name="LinkedIn",
                url="https://www.linkedin.com",
                category="professional",
                reliability_score=0.80,
                description="Company updates, executive movements, and thought leadership"
            ),
            DataSource(
                name="PR Newswire",
                url="https://www.prnewswire.com",
                category="press",
                reliability_score=0.95,
                description="Official company announcements and press releases"
            ),
            DataSource(
                name="Business Wire",
                url="https://www.businesswire.com",
                category="press",
                reliability_score=0.95,
                description="Business news and company announcements"
            )
        ]
    
    async def collect_data(self, query: str, **kwargs) -> List[CollectedData]:
        """
        Collect news data based on the query.
        
        Args:
            query: Search query or topic
            **kwargs: Additional parameters like 'timeframe', 'sources', etc.
            
        Returns:
            List of collected news data
        """
        print(f">>> {self.name}: Starting news data collection for '{query}'", flush=True)
        
        collected_data = []
        timeframe = kwargs.get('timeframe', '7d')  # Default to last 7 days
        
        # Collect from different sources
        news_data = await self._collect_google_news(query, timeframe)
        if news_data:
            collected_data.extend(news_data)
        
        reddit_data = await self._collect_reddit_data(query)
        if reddit_data:
            collected_data.extend(reddit_data)
        
        press_data = await self._collect_press_releases(query)
        if press_data:
            collected_data.extend(press_data)
        
        self.collected_data.extend(collected_data)
        print(f">>> {self.name}: Collected {len(collected_data)} news items", flush=True)
        
        return collected_data
    
    def get_supported_sources(self) -> List[DataSource]:
        """Get list of supported news data sources."""
        return self.sources
    
    async def _collect_google_news(self, query: str, timeframe: str) -> List[CollectedData]:
        """Collect news from Google News."""
        collected_data = []
        
        try:
            # Google News RSS feed
            encoded_query = quote(query)
            news_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
            
            response = await self.make_request(news_url, source_name="Google News")
            if response:
                xml_content = await response.text()
                
                # Parse RSS feed
                soup = BeautifulSoup(xml_content, 'xml')
                items = soup.find_all('item')
                
                for item in items[:20]:  # Limit to 20 most recent items
                    title = item.find('title')
                    link = item.find('link')
                    pub_date = item.find('pubDate')
                    description = item.find('description')
                    
                    if title and link:
                        news_item = {
                            "title": title.get_text(strip=True),
                            "link": link.get_text(strip=True),
                            "published_date": pub_date.get_text(strip=True) if pub_date else None,
                            "description": description.get_text(strip=True) if description else "",
                            "source": "Google News",
                            "query": query
                        }
                        
                        data_item = CollectedData(
                            source=self.sources[0],  # Google News
                            data=news_item,
                            collected_at=datetime.now(),
                            data_type="news_article",
                            quality_score=self.calculate_quality_score(news_item, self.sources[0]),
                            relevance_score=self.calculate_relevance_score(news_item['title'] + ' ' + news_item['description'], query),
                            processing_notes=["RSS feed parsing"]
                        )
                        collected_data.append(data_item)
                        
        except Exception as e:
            print(f">>> {self.name}: Error collecting Google News data: {e}", flush=True)
        
        return collected_data
    
    async def _collect_reddit_data(self, query: str) -> List[CollectedData]:
        """Collect data from relevant Reddit subreddits."""
        collected_data = []
        
        # Define relevant subreddits for business/finance topics
        subreddits = [
            'investing', 'stocks', 'SecurityAnalysis', 'ValueInvesting',
            'business', 'entrepreneur', 'startups', 'technology',
            'finance', 'personalfinance', 'Economics'
        ]
        
        try:
            for subreddit in subreddits[:3]:  # Limit to 3 subreddits to avoid rate limits
                # Reddit JSON API
                reddit_url = f"https://www.reddit.com/r/{subreddit}/search.json?q={quote(query)}&sort=relevance&limit=5"
                
                response = await self.make_request(
                    reddit_url,
                    source_name="Reddit",
                    headers={'User-Agent': 'Secondary Research Workflow Bot 1.0'}
                )
                
                if response:
                    data = await response.json()
                    
                    if 'data' in data and 'children' in data['data']:
                        for post in data['data']['children']:
                            post_data = post['data']
                            
                            reddit_item = {
                                "title": post_data.get('title', ''),
                                "selftext": post_data.get('selftext', ''),
                                "score": post_data.get('score', 0),
                                "num_comments": post_data.get('num_comments', 0),
                                "created_utc": post_data.get('created_utc', 0),
                                "subreddit": subreddit,
                                "url": f"https://reddit.com{post_data.get('permalink', '')}",
                                "author": post_data.get('author', ''),
                                "query": query
                            }
                            
                            data_item = CollectedData(
                                source=self.sources[1],  # Reddit
                                data=reddit_item,
                                collected_at=datetime.now(),
                                data_type="reddit_post",
                                quality_score=self.calculate_quality_score(reddit_item, self.sources[1]),
                                relevance_score=self.calculate_relevance_score(reddit_item['title'] + ' ' + reddit_item['selftext'], query),
                                processing_notes=[f"Reddit r/{subreddit} search"]
                            )
                            collected_data.append(data_item)
                
                # Add delay between subreddit requests
                await asyncio.sleep(2)
                
        except Exception as e:
            print(f">>> {self.name}: Error collecting Reddit data: {e}", flush=True)
        
        return collected_data
    
    async def _collect_press_releases(self, query: str) -> List[CollectedData]:
        """Collect press releases from PR Newswire and Business Wire."""
        collected_data = []
        
        try:
            # PR Newswire search
            pr_url = f"https://www.prnewswire.com/search/news/?keyword={quote(query)}&pageSize=10"
            
            response = await self.make_request(pr_url, source_name="PR Newswire")
            if response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Find press release links
                press_links = soup.find_all('a', href=re.compile(r'/news-releases/'))
                
                for link in press_links[:5]:  # Limit to 5 press releases
                    title = link.get_text(strip=True)
                    href = link.get('href')
                    
                    if title and href:
                        full_url = urljoin("https://www.prnewswire.com", href)
                        
                        # Get the press release content
                        pr_response = await self.make_request(full_url, source_name="PR Newswire")
                        if pr_response:
                            pr_html = await pr_response.text()
                            pr_soup = BeautifulSoup(pr_html, 'html.parser')
                            
                            # Extract content
                            content_div = pr_soup.find('div', class_='release-body')
                            content = content_div.get_text(strip=True) if content_div else ""
                            
                            # Extract date
                            date_elem = pr_soup.find('time')
                            date = date_elem.get('datetime') if date_elem else None
                            
                            press_item = {
                                "title": title,
                                "content": content[:1000],  # Limit content length
                                "url": full_url,
                                "published_date": date,
                                "source": "PR Newswire",
                                "query": query
                            }
                            
                            data_item = CollectedData(
                                source=self.sources[3],  # PR Newswire
                                data=press_item,
                                collected_at=datetime.now(),
                                data_type="press_release",
                                quality_score=self.calculate_quality_score(press_item, self.sources[3]),
                                relevance_score=self.calculate_relevance_score(press_item['title'] + ' ' + press_item['content'], query),
                                processing_notes=["PR Newswire press release"]
                            )
                            collected_data.append(data_item)
                
                # Add delay between requests
                await asyncio.sleep(1)
                
        except Exception as e:
            print(f">>> {self.name}: Error collecting press releases: {e}", flush=True)
        
        return collected_data
    
    async def _collect_linkedin_data(self, query: str) -> List[CollectedData]:
        """Collect public LinkedIn data (limited due to access restrictions)."""
        collected_data = []
        
        try:
            # Note: LinkedIn has strict access controls
            # This is a simplified example that would need proper authentication
            # For now, we'll simulate the structure
            
            linkedin_item = {
                "query": query,
                "note": "LinkedIn data collection requires authentication and API access",
                "suggested_approach": "Use LinkedIn API or web scraping with proper authentication",
                "data_type": "linkedin_placeholder"
            }
            
            data_item = CollectedData(
                source=self.sources[2],  # LinkedIn
                data=linkedin_item,
                collected_at=datetime.now(),
                data_type="linkedin_placeholder",
                quality_score=0.5,  # Low score due to access limitations
                relevance_score=0.8,
                processing_notes=["LinkedIn access requires authentication"]
            )
            collected_data.append(data_item)
            
        except Exception as e:
            print(f">>> {self.name}: Error with LinkedIn data collection: {e}", flush=True)
        
        return collected_data
