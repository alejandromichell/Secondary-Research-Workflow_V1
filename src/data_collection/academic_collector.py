"""
Academic Data Collector

Collects academic and research data from various free sources including:
- Google Scholar
- PubMed
- arXiv
- SSRN
- ResearchGate
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


class AcademicDataCollector(BaseDataCollector):
    """Collects academic and research data from various free sources."""
    
    def __init__(self):
        super().__init__(
            name="Academic Data Collector",
            description="Collects academic papers and research from Google Scholar, PubMed, arXiv, and other sources"
        )
        self.sources = self._initialize_sources()
    
    def _initialize_sources(self) -> List[DataSource]:
        """Initialize supported data sources."""
        return [
            DataSource(
                name="Google Scholar",
                url="https://scholar.google.com",
                category="academic",
                reliability_score=0.95,
                description="Academic papers, research studies, and citations"
            ),
            DataSource(
                name="PubMed",
                url="https://pubmed.ncbi.nlm.nih.gov",
                category="medical",
                reliability_score=1.0,
                description="Life sciences and biomedical research"
            ),
            DataSource(
                name="arXiv",
                url="https://arxiv.org",
                category="academic",
                reliability_score=0.90,
                description="Pre-print scientific papers"
            ),
            DataSource(
                name="SSRN",
                url="https://papers.ssrn.com",
                category="academic",
                reliability_score=0.85,
                description="Social Science Research Network - working papers and research"
            ),
            DataSource(
                name="ResearchGate",
                url="https://www.researchgate.net",
                category="academic",
                reliability_score=0.80,
                description="Academic publications and researcher networks"
            )
        ]
    
    async def collect_data(self, query: str, **kwargs) -> List[CollectedData]:
        """
        Collect academic data based on the query.
        
        Args:
            query: Research topic or keywords
            **kwargs: Additional parameters like 'year_range', 'max_results', etc.
            
        Returns:
            List of collected academic data
        """
        print(f">>> {self.name}: Starting academic data collection for '{query}'", flush=True)
        
        collected_data = []
        max_results = kwargs.get('max_results', 10)
        year_range = kwargs.get('year_range', '2020-2024')
        
        # Collect from different sources
        scholar_data = await self._collect_google_scholar(query, max_results)
        if scholar_data:
            collected_data.extend(scholar_data)
        
        pubmed_data = await self._collect_pubmed_data(query, max_results)
        if pubmed_data:
            collected_data.extend(pubmed_data)
        
        arxiv_data = await self._collect_arxiv_data(query, max_results)
        if arxiv_data:
            collected_data.extend(arxiv_data)
        
        ssrn_data = await self._collect_ssrn_data(query, max_results)
        if ssrn_data:
            collected_data.extend(ssrn_data)
        
        self.collected_data.extend(collected_data)
        print(f">>> {self.name}: Collected {len(collected_data)} academic papers", flush=True)
        
        return collected_data
    
    def get_supported_sources(self) -> List[DataSource]:
        """Get list of supported academic data sources."""
        return self.sources
    
    async def _collect_google_scholar(self, query: str, max_results: int) -> List[CollectedData]:
        """Collect data from Google Scholar."""
        collected_data = []
        
        try:
            # Google Scholar search URL
            encoded_query = quote(query)
            scholar_url = f"https://scholar.google.com/scholar?q={encoded_query}&hl=en&as_sdt=0%2C5"
            
            response = await self.make_request(scholar_url, source_name="Google Scholar")
            if response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Find search results
                results = soup.find_all('div', class_='gs_ri')
                
                for result in results[:max_results]:
                    title_elem = result.find('h3', class_='gs_rt')
                    if not title_elem:
                        continue
                    
                    title_link = title_elem.find('a')
                    title = title_link.get_text(strip=True) if title_link else title_elem.get_text(strip=True)
                    url = title_link.get('href') if title_link else None
                    
                    # Extract authors and publication info
                    authors_elem = result.find('div', class_='gs_a')
                    authors = authors_elem.get_text(strip=True) if authors_elem else ""
                    
                    # Extract abstract
                    abstract_elem = result.find('div', class_='gs_rs')
                    abstract = abstract_elem.get_text(strip=True) if abstract_elem else ""
                    
                    # Extract citations
                    citations_elem = result.find('a', href=re.compile(r'cites'))
                    citations = 0
                    if citations_elem:
                        citations_text = citations_elem.get_text(strip=True)
                        citations_match = re.search(r'(\d+)', citations_text)
                        if citations_match:
                            citations = int(citations_match.group(1))
                    
                    paper_data = {
                        "title": title,
                        "authors": authors,
                        "abstract": abstract,
                        "url": url,
                        "citations": citations,
                        "source": "Google Scholar",
                        "query": query,
                        "collected_at": datetime.now().isoformat()
                    }
                    
                    data_item = CollectedData(
                        source=self.sources[0],  # Google Scholar
                        data=paper_data,
                        collected_at=datetime.now(),
                        data_type="academic_paper",
                        quality_score=self.calculate_quality_score(paper_data, self.sources[0]),
                        relevance_score=self.calculate_relevance_score(paper_data['title'] + ' ' + paper_data['abstract'], query),
                        processing_notes=["Google Scholar search results"]
                    )
                    collected_data.append(data_item)
                    
        except Exception as e:
            print(f">>> {self.name}: Error collecting Google Scholar data: {e}", flush=True)
        
        return collected_data
    
    async def _collect_pubmed_data(self, query: str, max_results: int) -> List[CollectedData]:
        """Collect data from PubMed."""
        collected_data = []
        
        try:
            # PubMed E-utilities API
            encoded_query = quote(query)
            search_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={encoded_query}&retmax={max_results}&retmode=json"
            
            response = await self.make_request(search_url, source_name="PubMed")
            if response:
                search_data = await response.json()
                
                if 'esearchresult' in search_data and 'idlist' in search_data['esearchresult']:
                    pmids = search_data['esearchresult']['idlist']
                    
                    # Get details for each PMID
                    for pmid in pmids[:max_results]:
                        detail_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={pmid}&retmode=xml"
                        
                        detail_response = await self.make_request(detail_url, source_name="PubMed")
                        if detail_response:
                            xml_content = await detail_response.text()
                            soup = BeautifulSoup(xml_content, 'xml')
                            
                            # Extract paper details
                            article = soup.find('Article')
                            if article:
                                title_elem = article.find('ArticleTitle')
                                title = title_elem.get_text(strip=True) if title_elem else ""
                                
                                abstract_elem = article.find('AbstractText')
                                abstract = abstract_elem.get_text(strip=True) if abstract_elem else ""
                                
                                # Extract authors
                                authors = []
                                author_list = article.find('AuthorList')
                                if author_list:
                                    for author in author_list.find_all('Author'):
                                        last_name = author.find('LastName')
                                        first_name = author.find('ForeName')
                                        if last_name and first_name:
                                            authors.append(f"{first_name.get_text()} {last_name.get_text()}")
                                
                                # Extract journal
                                journal_elem = article.find('Journal')
                                journal = ""
                                if journal_elem:
                                    journal_title = journal_elem.find('Title')
                                    journal = journal_title.get_text(strip=True) if journal_title else ""
                                
                                # Extract publication date
                                pub_date_elem = article.find('PubDate')
                                pub_date = ""
                                if pub_date_elem:
                                    year = pub_date_elem.find('Year')
                                    month = pub_date_elem.find('Month')
                                    if year:
                                        pub_date = year.get_text()
                                        if month:
                                            pub_date += f"-{month.get_text()}"
                                
                                paper_data = {
                                    "pmid": pmid,
                                    "title": title,
                                    "authors": authors,
                                    "abstract": abstract,
                                    "journal": journal,
                                    "publication_date": pub_date,
                                    "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                                    "source": "PubMed",
                                    "query": query
                                }
                                
                                data_item = CollectedData(
                                    source=self.sources[1],  # PubMed
                                    data=paper_data,
                                    collected_at=datetime.now(),
                                    data_type="medical_paper",
                                    quality_score=self.calculate_quality_score(paper_data, self.sources[1]),
                                    relevance_score=self.calculate_relevance_score(paper_data['title'] + ' ' + paper_data['abstract'], query),
                                    processing_notes=["PubMed E-utilities API"]
                                )
                                collected_data.append(data_item)
                        
                        # Add delay between requests
                        await asyncio.sleep(0.5)
                        
        except Exception as e:
            print(f">>> {self.name}: Error collecting PubMed data: {e}", flush=True)
        
        return collected_data
    
    async def _collect_arxiv_data(self, query: str, max_results: int) -> List[CollectedData]:
        """Collect data from arXiv."""
        collected_data = []
        
        try:
            # arXiv API
            encoded_query = quote(query)
            arxiv_url = f"http://export.arxiv.org/api/query?search_query=all:{encoded_query}&start=0&max_results={max_results}&sortBy=relevance&sortOrder=descending"
            
            response = await self.make_request(arxiv_url, source_name="arXiv")
            if response:
                xml_content = await response.text()
                soup = BeautifulSoup(xml_content, 'xml')
                
                entries = soup.find_all('entry')
                
                for entry in entries:
                    title_elem = entry.find('title')
                    title = title_elem.get_text(strip=True) if title_elem else ""
                    
                    summary_elem = entry.find('summary')
                    abstract = summary_elem.get_text(strip=True) if summary_elem else ""
                    
                    # Extract authors
                    authors = []
                    for author in entry.find_all('author'):
                        name_elem = author.find('name')
                        if name_elem:
                            authors.append(name_elem.get_text(strip=True))
                    
                    # Extract publication date
                    published_elem = entry.find('published')
                    published_date = published_elem.get_text(strip=True) if published_elem else ""
                    
                    # Extract arXiv ID and URL
                    id_elem = entry.find('id')
                    arxiv_id = id_elem.get_text(strip=True) if id_elem else ""
                    arxiv_url = f"https://arxiv.org/abs/{arxiv_id.split('/')[-1]}" if arxiv_id else ""
                    
                    # Extract categories
                    categories = []
                    for category in entry.find_all('category'):
                        categories.append(category.get('term', ''))
                    
                    paper_data = {
                        "arxiv_id": arxiv_id.split('/')[-1] if arxiv_id else "",
                        "title": title,
                        "authors": authors,
                        "abstract": abstract,
                        "published_date": published_date,
                        "categories": categories,
                        "url": arxiv_url,
                        "source": "arXiv",
                        "query": query
                    }
                    
                    data_item = CollectedData(
                        source=self.sources[2],  # arXiv
                        data=paper_data,
                        collected_at=datetime.now(),
                        data_type="preprint_paper",
                        quality_score=self.calculate_quality_score(paper_data, self.sources[2]),
                        relevance_score=self.calculate_relevance_score(paper_data['title'] + ' ' + paper_data['abstract'], query),
                        processing_notes=["arXiv API"]
                    )
                    collected_data.append(data_item)
                    
        except Exception as e:
            print(f">>> {self.name}: Error collecting arXiv data: {e}", flush=True)
        
        return collected_data
    
    async def _collect_ssrn_data(self, query: str, max_results: int) -> List[CollectedData]:
        """Collect data from SSRN."""
        collected_data = []
        
        try:
            # SSRN search (web scraping)
            encoded_query = quote(query)
            ssrn_url = f"https://papers.ssrn.com/sol3/results.cfm?RequestTimeout=50000000&q={encoded_query}"
            
            response = await self.make_request(ssrn_url, source_name="SSRN")
            if response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Find paper results
                results = soup.find_all('div', class_='search-result')
                
                for result in results[:max_results]:
                    title_elem = result.find('h3', class_='search-result-title')
                    if not title_elem:
                        continue
                    
                    title_link = title_elem.find('a')
                    title = title_link.get_text(strip=True) if title_link else title_elem.get_text(strip=True)
                    url = title_link.get('href') if title_link else None
                    
                    # Extract authors
                    authors_elem = result.find('div', class_='search-result-authors')
                    authors = authors_elem.get_text(strip=True) if authors_elem else ""
                    
                    # Extract abstract
                    abstract_elem = result.find('div', class_='search-result-abstract')
                    abstract = abstract_elem.get_text(strip=True) if abstract_elem else ""
                    
                    # Extract download count
                    downloads_elem = result.find('span', class_='download-count')
                    downloads = 0
                    if downloads_elem:
                        downloads_text = downloads_elem.get_text(strip=True)
                        downloads_match = re.search(r'(\d+)', downloads_text)
                        if downloads_match:
                            downloads = int(downloads_match.group(1))
                    
                    paper_data = {
                        "title": title,
                        "authors": authors,
                        "abstract": abstract,
                        "downloads": downloads,
                        "url": url,
                        "source": "SSRN",
                        "query": query
                    }
                    
                    data_item = CollectedData(
                        source=self.sources[3],  # SSRN
                        data=paper_data,
                        collected_at=datetime.now(),
                        data_type="working_paper",
                        quality_score=self.calculate_quality_score(paper_data, self.sources[3]),
                        relevance_score=self.calculate_relevance_score(paper_data['title'] + ' ' + paper_data['abstract'], query),
                        processing_notes=["SSRN web scraping"]
                    )
                    collected_data.append(data_item)
                    
        except Exception as e:
            print(f">>> {self.name}: Error collecting SSRN data: {e}", flush=True)
        
        return collected_data
