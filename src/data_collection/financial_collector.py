"""
Financial Data Collector

Collects financial data from various free sources including:
- Yahoo Finance API
- Google Finance (web scraping)
- SEC EDGAR Database
- Finviz
- Macrotrends
"""

import asyncio
import aiohttp
import yfinance as yf
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
import re
from bs4 import BeautifulSoup

from .base_collector import BaseDataCollector, DataSource, CollectedData


class FinancialDataCollector(BaseDataCollector):
    """Collects financial data from various free sources."""
    
    def __init__(self):
        super().__init__(
            name="Financial Data Collector",
            description="Collects financial data from Yahoo Finance, SEC EDGAR, and other free sources"
        )
        self.sources = self._initialize_sources()
    
    def _initialize_sources(self) -> List[DataSource]:
        """Initialize supported data sources."""
        return [
            DataSource(
                name="Yahoo Finance",
                url="https://finance.yahoo.com",
                category="financial",
                reliability_score=0.95,
                description="Real-time stock data, financial metrics, and company information"
            ),
            DataSource(
                name="SEC EDGAR",
                url="https://www.sec.gov/edgar",
                category="regulatory",
                reliability_score=1.0,
                description="Official SEC filings including 10-K, 10-Q, and proxy statements"
            ),
            DataSource(
                name="Finviz",
                url="https://finviz.com",
                category="financial",
                reliability_score=0.85,
                description="Stock screener and financial visualizations"
            ),
            DataSource(
                name="Macrotrends",
                url="https://www.macrotrends.net",
                category="financial",
                reliability_score=0.90,
                description="Long-term financial trends and ratios"
            ),
            DataSource(
                name="MarketWatch",
                url="https://www.marketwatch.com",
                category="financial",
                reliability_score=0.80,
                description="Market data and financial news"
            )
        ]
    
    async def collect_data(self, query: str, **kwargs) -> List[CollectedData]:
        """
        Collect financial data based on the query.
        
        Args:
            query: Company name, ticker symbol, or financial topic
            **kwargs: Additional parameters like 'ticker', 'timeframe', etc.
            
        Returns:
            List of collected financial data
        """
        print(f">>> {self.name}: Starting financial data collection for '{query}'", flush=True)
        
        collected_data = []
        
        # Extract ticker if provided or try to infer from query
        ticker = kwargs.get('ticker')
        if not ticker and self._looks_like_ticker(query):
            ticker = query.upper()
        elif not ticker:
            ticker = await self._find_ticker_for_company(query)
        
        # Collect from different sources
        if ticker:
            # Yahoo Finance data
            yahoo_data = await self._collect_yahoo_finance_data(ticker)
            if yahoo_data:
                collected_data.extend(yahoo_data)
            
            # SEC EDGAR data
            sec_data = await self._collect_sec_data(ticker, query)
            if sec_data:
                collected_data.extend(sec_data)
            
            # Finviz data
            finviz_data = await self._collect_finviz_data(ticker)
            if finviz_data:
                collected_data.extend(finviz_data)
        
        # Market and industry data
        market_data = await self._collect_market_data(query)
        if market_data:
            collected_data.extend(market_data)
        
        self.collected_data.extend(collected_data)
        print(f">>> {self.name}: Collected {len(collected_data)} financial data items", flush=True)
        
        return collected_data
    
    def get_supported_sources(self) -> List[DataSource]:
        """Get list of supported financial data sources."""
        return self.sources
    
    def _looks_like_ticker(self, query: str) -> bool:
        """Check if the query looks like a stock ticker symbol."""
        # Simple heuristic: 1-5 uppercase letters
        return bool(re.match(r'^[A-Z]{1,5}$', query.strip().upper()))
    
    async def _find_ticker_for_company(self, company_name: str) -> Optional[str]:
        """Try to find ticker symbol for a company name."""
        try:
            # Use yfinance to search for ticker
            # This is a simplified approach - in practice, you might use a more robust search
            search_url = f"https://query1.finance.yahoo.com/v1/finance/search?q={company_name}"
            
            response = await self.make_request(search_url, source_name="Yahoo Finance")
            if response:
                data = await response.json()
                if data.get('quotes'):
                    return data['quotes'][0].get('symbol')
        except Exception as e:
            print(f">>> {self.name}: Error finding ticker for {company_name}: {e}", flush=True)
        
        return None
    
    async def _collect_yahoo_finance_data(self, ticker: str) -> List[CollectedData]:
        """Collect data from Yahoo Finance using yfinance library."""
        collected_data = []
        
        try:
            # Get stock information
            stock = yf.Ticker(ticker)
            
            # Basic info
            info = stock.info
            if info:
                data_item = CollectedData(
                    source=self.sources[0],  # Yahoo Finance
                    data={
                        "ticker": ticker,
                        "company_name": info.get('longName', ''),
                        "sector": info.get('sector', ''),
                        "industry": info.get('industry', ''),
                        "market_cap": info.get('marketCap', 0),
                        "revenue": info.get('totalRevenue', 0),
                        "profit_margin": info.get('profitMargins', 0),
                        "pe_ratio": info.get('trailingPE', 0),
                        "current_price": info.get('currentPrice', 0),
                        "52_week_high": info.get('fiftyTwoWeekHigh', 0),
                        "52_week_low": info.get('fiftyTwoWeekLow', 0)
                    },
                    collected_at=datetime.now(),
                    data_type="company_financials",
                    quality_score=self.calculate_quality_score(info, self.sources[0]),
                    relevance_score=1.0,  # Direct ticker match
                    processing_notes=["Collected via yfinance library"]
                )
                collected_data.append(data_item)
            
            # Historical data (last 1 year)
            hist = stock.history(period="1y")
            if not hist.empty:
                hist_data = {
                    "ticker": ticker,
                    "period": "1y",
                    "data_points": len(hist),
                    "latest_price": float(hist['Close'].iloc[-1]),
                    "price_change_1y": float((hist['Close'].iloc[-1] - hist['Close'].iloc[0]) / hist['Close'].iloc[0] * 100),
                    "volatility": float(hist['Close'].pct_change().std() * 100),
                    "average_volume": float(hist['Volume'].mean())
                }
                
                data_item = CollectedData(
                    source=self.sources[0],
                    data=hist_data,
                    collected_at=datetime.now(),
                    data_type="historical_prices",
                    quality_score=self.calculate_quality_score(hist_data, self.sources[0]),
                    relevance_score=1.0,
                    processing_notes=["Historical price data via yfinance"]
                )
                collected_data.append(data_item)
            
            # Financial statements
            financials = stock.financials
            if not financials.empty:
                latest_financials = financials.iloc[0].to_dict()
                data_item = CollectedData(
                    source=self.sources[0],
                    data={
                        "ticker": ticker,
                        "period": str(financials.index[0]),
                        "financial_metrics": latest_financials
                    },
                    collected_at=datetime.now(),
                    data_type="financial_statements",
                    quality_score=self.calculate_quality_score(latest_financials, self.sources[0]),
                    relevance_score=1.0,
                    processing_notes=["Financial statements via yfinance"]
                )
                collected_data.append(data_item)
                
        except Exception as e:
            print(f">>> {self.name}: Error collecting Yahoo Finance data for {ticker}: {e}", flush=True)
        
        return collected_data
    
    async def _collect_sec_data(self, ticker: str, company_name: str) -> List[CollectedData]:
        """Collect data from SEC EDGAR database."""
        collected_data = []
        
        try:
            # SEC EDGAR API endpoint for company filings
            cik = await self._get_cik_for_ticker(ticker)
            if not cik:
                return collected_data
            
            # Get recent filings
            filings_url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik.zfill(10)}.json"
            
            response = await self.make_request(
                filings_url, 
                source_name="SEC EDGAR",
                headers={'User-Agent': 'Secondary Research Workflow Bot (educational@example.com)'}
            )
            
            if response:
                data = await response.json()
                
                # Extract key financial metrics
                company_facts = data.get('facts', {}).get('us-gaap', {})
                if company_facts:
                    key_metrics = {}
                    for metric in ['Revenues', 'Assets', 'Liabilities', 'StockholdersEquity']:
                        if metric in company_facts:
                            latest_data = company_facts[metric]['units']['USD'][-1]
                            key_metrics[metric] = {
                                'value': latest_data['val'],
                                'period': latest_data['end'],
                                'form': latest_data.get('form', '')
                            }
                    
                    data_item = CollectedData(
                        source=self.sources[1],  # SEC EDGAR
                        data={
                            "ticker": ticker,
                            "company_name": data.get('entityName', company_name),
                            "cik": cik,
                            "key_metrics": key_metrics,
                            "filing_date": datetime.now().isoformat()
                        },
                        collected_at=datetime.now(),
                        data_type="sec_filings",
                        quality_score=self.calculate_quality_score(key_metrics, self.sources[1]),
                        relevance_score=1.0,
                        processing_notes=["SEC EDGAR company facts data"]
                    )
                    collected_data.append(data_item)
                    
        except Exception as e:
            print(f">>> {self.name}: Error collecting SEC data for {ticker}: {e}", flush=True)
        
        return collected_data
    
    async def _get_cik_for_ticker(self, ticker: str) -> Optional[str]:
        """Get CIK (Central Index Key) for a ticker symbol."""
        try:
            # SEC ticker to CIK mapping
            tickers_url = "https://www.sec.gov/files/company_tickers.json"
            
            response = await self.make_request(
                tickers_url,
                source_name="SEC EDGAR",
                headers={'User-Agent': 'Secondary Research Workflow Bot (educational@example.com)'}
            )
            
            if response:
                data = await response.json()
                for entry in data.values():
                    if entry.get('ticker', '').upper() == ticker.upper():
                        return str(entry.get('cik_str', ''))
                        
        except Exception as e:
            print(f">>> {self.name}: Error getting CIK for {ticker}: {e}", flush=True)
        
        return None
    
    async def _collect_finviz_data(self, ticker: str) -> List[CollectedData]:
        """Collect data from Finviz (web scraping)."""
        collected_data = []
        
        try:
            # Finviz quote page
            url = f"https://finviz.com/quote.ashx?t={ticker}"
            
            response = await self.make_request(url, source_name="Finviz")
            if response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Extract key metrics from the quote table
                metrics = {}
                quote_table = soup.find('table', class_='snapshot-table2')
                if quote_table:
                    rows = quote_table.find_all('tr')
                    for row in rows:
                        cells = row.find_all('td')
                        if len(cells) >= 2:
                            key = cells[0].get_text(strip=True)
                            value = cells[1].get_text(strip=True)
                            metrics[key] = value
                
                if metrics:
                    data_item = CollectedData(
                        source=self.sources[2],  # Finviz
                        data={
                            "ticker": ticker,
                            "metrics": metrics,
                            "scraped_at": datetime.now().isoformat()
                        },
                        collected_at=datetime.now(),
                        data_type="finviz_metrics",
                        quality_score=self.calculate_quality_score(metrics, self.sources[2]),
                        relevance_score=1.0,
                        processing_notes=["Web scraped from Finviz quote page"]
                    )
                    collected_data.append(data_item)
                    
        except Exception as e:
            print(f">>> {self.name}: Error collecting Finviz data for {ticker}: {e}", flush=True)
        
        return collected_data
    
    async def _collect_market_data(self, query: str) -> List[CollectedData]:
        """Collect general market and industry data."""
        collected_data = []
        
        try:
            # Market overview from Yahoo Finance
            market_url = "https://query1.finance.yahoo.com/v8/finance/chart/%5EGSPC"  # S&P 500
            
            response = await self.make_request(market_url, source_name="Yahoo Finance")
            if response:
                data = await response.json()
                
                if 'chart' in data and 'result' in data['chart']:
                    result = data['chart']['result'][0]
                    meta = result.get('meta', {})
                    
                    market_data = {
                        "index": "S&P 500",
                        "current_price": meta.get('regularMarketPrice', 0),
                        "change": meta.get('regularMarketChange', 0),
                        "change_percent": meta.get('regularMarketChangePercent', 0),
                        "volume": meta.get('regularMarketVolume', 0),
                        "market_state": meta.get('marketState', ''),
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    data_item = CollectedData(
                        source=self.sources[0],  # Yahoo Finance
                        data=market_data,
                        collected_at=datetime.now(),
                        data_type="market_overview",
                        quality_score=self.calculate_quality_score(market_data, self.sources[0]),
                        relevance_score=0.7,  # General market data
                        processing_notes=["S&P 500 market data"]
                    )
                    collected_data.append(data_item)
                    
        except Exception as e:
            print(f">>> {self.name}: Error collecting market data: {e}", flush=True)
        
        return collected_data
