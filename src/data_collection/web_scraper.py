"""
Web Scraper Utility

Provides common web scraping functionality for data collection.
Handles various content types, rate limiting, and error handling.
"""

import asyncio
import aiohttp
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import json
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time


class WebScraper:
    """Utility class for web scraping operations."""
    
    def __init__(self, session: Optional[aiohttp.ClientSession] = None):
        self.session = session
        self.rate_limits: Dict[str, float] = {}
        self.request_count = 0
        self.last_request_time = 0
    
    async def scrape_page(self, 
                         url: str, 
                         selectors: Optional[Dict[str, str]] = None,
                         wait_time: float = 1.0) -> Dict[str, Any]:
        """
        Scrape a single web page.
        
        Args:
            url: URL to scrape
            selectors: Dictionary of CSS selectors to extract specific content
            wait_time: Time to wait between requests
            
        Returns:
            Dictionary containing scraped data
        """
        if not self.session:
            raise RuntimeError("No HTTP session available")
        
        # Rate limiting
        await self._respect_rate_limit(wait_time)
        
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Extract basic page information
                    page_data = {
                        "url": url,
                        "title": self._extract_title(soup),
                        "meta_description": self._extract_meta_description(soup),
                        "headings": self._extract_headings(soup),
                        "links": self._extract_links(soup, url),
                        "images": self._extract_images(soup, url),
                        "text_content": self._extract_text_content(soup),
                        "scraped_at": datetime.now().isoformat()
                    }
                    
                    # Extract specific content using selectors
                    if selectors:
                        page_data["custom_content"] = self._extract_custom_content(soup, selectors)
                    
                    return page_data
                else:
                    return {"error": f"HTTP {response.status}", "url": url}
                    
        except Exception as e:
            return {"error": str(e), "url": url}
    
    async def scrape_multiple_pages(self, 
                                   urls: List[str], 
                                   selectors: Optional[Dict[str, str]] = None,
                                   wait_time: float = 1.0,
                                   max_concurrent: int = 5) -> List[Dict[str, Any]]:
        """
        Scrape multiple web pages with concurrency control.
        
        Args:
            urls: List of URLs to scrape
            selectors: Dictionary of CSS selectors
            wait_time: Time to wait between requests
            max_concurrent: Maximum concurrent requests
            
        Returns:
            List of scraped page data
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def scrape_with_semaphore(url):
            async with semaphore:
                return await self.scrape_page(url, selectors, wait_time)
        
        tasks = [scrape_with_semaphore(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and return valid results
        valid_results = []
        for result in results:
            if isinstance(result, dict) and "error" not in result:
                valid_results.append(result)
            elif isinstance(result, Exception):
                valid_results.append({"error": str(result)})
        
        return valid_results
    
    def extract_structured_data(self, html: str, data_type: str = "generic") -> Dict[str, Any]:
        """
        Extract structured data from HTML.
        
        Args:
            html: HTML content
            data_type: Type of data to extract (article, product, etc.)
            
        Returns:
            Dictionary containing structured data
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        if data_type == "article":
            return self._extract_article_data(soup)
        elif data_type == "product":
            return self._extract_product_data(soup)
        elif data_type == "contact":
            return self._extract_contact_data(soup)
        else:
            return self._extract_generic_data(soup)
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text content."""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)]', '', text)
        
        return text.strip()
    
    def extract_emails(self, text: str) -> List[str]:
        """Extract email addresses from text."""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return re.findall(email_pattern, text)
    
    def extract_phones(self, text: str) -> List[str]:
        """Extract phone numbers from text."""
        phone_pattern = r'(\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})'
        return re.findall(phone_pattern, text)
    
    def extract_urls(self, text: str) -> List[str]:
        """Extract URLs from text."""
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        return re.findall(url_pattern, text)
    
    async def _respect_rate_limit(self, wait_time: float):
        """Respect rate limiting between requests."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < wait_time:
            await asyncio.sleep(wait_time - time_since_last)
        
        self.last_request_time = time.time()
        self.request_count += 1
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title."""
        title_tag = soup.find('title')
        return title_tag.get_text(strip=True) if title_tag else ""
    
    def _extract_meta_description(self, soup: BeautifulSoup) -> str:
        """Extract meta description."""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        return meta_desc.get('content', '') if meta_desc else ""
    
    def _extract_headings(self, soup: BeautifulSoup) -> Dict[str, List[str]]:
        """Extract all headings from the page."""
        headings = {}
        for level in range(1, 7):
            tag = f'h{level}'
            elements = soup.find_all(tag)
            headings[tag] = [elem.get_text(strip=True) for elem in elements]
        return headings
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """Extract all links from the page."""
        links = []
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            text = link.get_text(strip=True)
            
            # Convert relative URLs to absolute
            if href:
                absolute_url = urljoin(base_url, href)
                links.append({
                    "url": absolute_url,
                    "text": text,
                    "domain": urlparse(absolute_url).netloc
                })
        
        return links
    
    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """Extract all images from the page."""
        images = []
        for img in soup.find_all('img', src=True):
            src = img.get('src')
            alt = img.get('alt', '')
            
            if src:
                absolute_url = urljoin(base_url, src)
                images.append({
                    "url": absolute_url,
                    "alt": alt,
                    "width": img.get('width'),
                    "height": img.get('height')
                })
        
        return images
    
    def _extract_text_content(self, soup: BeautifulSoup) -> str:
        """Extract main text content from the page."""
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text content
        text = soup.get_text()
        return self.clean_text(text)
    
    def _extract_custom_content(self, soup: BeautifulSoup, selectors: Dict[str, str]) -> Dict[str, Any]:
        """Extract custom content using CSS selectors."""
        custom_content = {}
        
        for key, selector in selectors.items():
            elements = soup.select(selector)
            if elements:
                if len(elements) == 1:
                    custom_content[key] = elements[0].get_text(strip=True)
                else:
                    custom_content[key] = [elem.get_text(strip=True) for elem in elements]
            else:
                custom_content[key] = None
        
        return custom_content
    
    def _extract_article_data(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract article-specific data."""
        article_data = {}
        
        # Try to find article title
        title_selectors = ['h1', '.article-title', '.post-title', '[class*="title"]']
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                article_data['title'] = title_elem.get_text(strip=True)
                break
        
        # Try to find article content
        content_selectors = ['.article-content', '.post-content', '.entry-content', 'article']
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                article_data['content'] = content_elem.get_text(strip=True)
                break
        
        # Try to find publication date
        date_selectors = ['time', '.date', '.published', '[class*="date"]']
        for selector in date_selectors:
            date_elem = soup.select_one(selector)
            if date_elem:
                article_data['date'] = date_elem.get_text(strip=True)
                break
        
        return article_data
    
    def _extract_product_data(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract product-specific data."""
        product_data = {}
        
        # Try to find product name
        name_selectors = ['h1', '.product-title', '.product-name', '[class*="product-title"]']
        for selector in name_selectors:
            name_elem = soup.select_one(selector)
            if name_elem:
                product_data['name'] = name_elem.get_text(strip=True)
                break
        
        # Try to find price
        price_selectors = ['.price', '.product-price', '[class*="price"]']
        for selector in price_selectors:
            price_elem = soup.select_one(selector)
            if price_elem:
                product_data['price'] = price_elem.get_text(strip=True)
                break
        
        # Try to find description
        desc_selectors = ['.description', '.product-description', '[class*="description"]']
        for selector in desc_selectors:
            desc_elem = soup.select_one(selector)
            if desc_elem:
                product_data['description'] = desc_elem.get_text(strip=True)
                break
        
        return product_data
    
    def _extract_contact_data(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract contact information."""
        contact_data = {}
        
        # Extract all text content
        text_content = soup.get_text()
        
        # Extract emails
        contact_data['emails'] = self.extract_emails(text_content)
        
        # Extract phone numbers
        contact_data['phones'] = self.extract_phones(text_content)
        
        # Extract URLs
        contact_data['urls'] = self.extract_urls(text_content)
        
        return contact_data
    
    def _extract_generic_data(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract generic structured data."""
        generic_data = {}
        
        # Extract JSON-LD structured data
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        if json_ld_scripts:
            generic_data['structured_data'] = []
            for script in json_ld_scripts:
                try:
                    data = json.loads(script.string)
                    generic_data['structured_data'].append(data)
                except json.JSONDecodeError:
                    continue
        
        # Extract Open Graph data
        og_data = {}
        for meta in soup.find_all('meta', property=re.compile(r'^og:')):
            property_name = meta.get('property', '').replace('og:', '')
            og_data[property_name] = meta.get('content', '')
        
        if og_data:
            generic_data['open_graph'] = og_data
        
        # Extract Twitter Card data
        twitter_data = {}
        for meta in soup.find_all('meta', attrs={'name': re.compile(r'^twitter:')}):
            name = meta.get('name', '').replace('twitter:', '')
            twitter_data[name] = meta.get('content', '')
        
        if twitter_data:
            generic_data['twitter_cards'] = twitter_data
        
        return generic_data
