"""
Perplexity API client for web research and data collection.
"""

import aiohttp
import asyncio
from typing import Dict, Any, List
from config.settings import get_settings


class PerplexityClient:
    """Client for interacting with Perplexity API."""
    
    def __init__(self):
        self.settings = get_settings()
        self.api_key = self.settings.perplexity_api_key
        self.base_url = "https://api.perplexity.ai"
    
    async def search_research_data(
        self, 
        query: str, 
        focus_area: str = "academic"
    ) -> Dict[str, Any]:
        """Search for research data using Perplexity API."""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "llama-3.1-sonar-large-128k-online",
            "messages": [
                {
                    "role": "system",
                    "content": f"You are a research assistant specializing in {focus_area} research. Provide comprehensive, well-sourced information with citations."
                },
                {
                    "role": "user", 
                    "content": query
                }
            ],
            "max_tokens": 2000,
            "temperature": 0.2,
            "top_p": 0.9,
            "return_citations": True,
            "search_domain_filter": ["academic"] if focus_area == "academic" else None
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "status": "success",
                            "content": result["choices"][0]["message"]["content"],
                            "citations": result.get("citations", []),
                            "usage": result.get("usage", {}),
                            "model": payload["model"]
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "status": "error",
                            "error_message": f"API request failed: {response.status} - {error_text}"
                        }
                        
        except Exception as e:
            return {
                "status": "error",
                "error_message": f"Perplexity API error: {str(e)}"
            }
    
    async def multi_query_research(
        self, 
        queries: List[str], 
        focus_areas: List[str] = None
    ) -> Dict[str, Any]:
        """Execute multiple research queries in parallel."""
        
        if focus_areas is None:
            focus_areas = ["academic"] * len(queries)
        
        if len(focus_areas) != len(queries):
            focus_areas = ["academic"] * len(queries)
        
        # Execute queries concurrently
        tasks = [
            self.search_research_data(query, focus_area)
            for query, focus_area in zip(queries, focus_areas)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        successful_results = []
        errors = []
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                errors.append({
                    "query_index": i,
                    "query": queries[i],
                    "error": str(result)
                })
            elif result.get("status") == "success":
                successful_results.append({
                    "query_index": i,
                    "query": queries[i],
                    "result": result
                })
            else:
                errors.append({
                    "query_index": i,
                    "query": queries[i], 
                    "error": result.get("error_message", "Unknown error")
                })
        
        return {
            "status": "complete",
            "successful_queries": len(successful_results),
            "failed_queries": len(errors),
            "results": successful_results,
            "errors": errors,
            "total_citations": sum(len(r["result"].get("citations", [])) for r in successful_results)
        }


def create_perplexity_client() -> PerplexityClient:
    """Factory function to create Perplexity client."""
    return PerplexityClient()