"""
Notion API client for research documentation.
"""

import os
from typing import Dict, Any, Optional
from notion_client import Client
from google.adk.tools.tool_context import ToolContext

from config.settings import get_settings


class NotionClient:
    """Client for interacting with Notion API."""
    
    def __init__(self):
        self.settings = get_settings()
        self.client = Client(auth=self.settings.notion_api_key)
    
    async def create_research_page(
        self, 
        research_plan: Dict[str, Any], 
        database_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new research page in Notion."""
        try:
            page_data = {
                "parent": {"database_id": database_id} if database_id else {"page_id": "your-page-id"},
                "properties": {
                    "Name": {
                        "title": [
                            {
                                "text": {
                                    "content": f"Research: {research_plan.get('topic', 'Untitled')}"
                                }
                            }
                        ]
                    },
                    "Status": {
                        "select": {
                            "name": "Planning"
                        }
                    }
                },
                "children": self._build_page_content(research_plan)
            }
            
            response = self.client.pages.create(**page_data)
            return {
                "status": "success",
                "page_id": response["id"],
                "url": response["url"]
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error_message": f"Failed to create Notion page: {str(e)}"
            }
    
    def _build_page_content(self, research_plan: Dict[str, Any]) -> list:
        """Build Notion page content blocks."""
        content = [
            {
                "object": "block",
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [{"type": "text", "text": {"content": "Research Plan"}}]
                }
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": f"Topic: {research_plan.get('topic', 'N/A')}"}
                        }
                    ]
                }
            }
        ]
        
        # Add objectives
        if research_plan.get('objectives'):
            content.append({
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": "Objectives"}}]
                }
            })
            
            for objective in research_plan['objectives']:
                content.append({
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "rich_text": [{"type": "text", "text": {"content": objective}}]
                    }
                })
        
        return content


def create_research_plan_tool(
    objectives: list,
    topic: str,
    questions: list,
    tool_context: ToolContext
) -> Dict[str, Any]:
    """Tool for creating structured research plans."""
    
    print(f"--- Tool: create_research_plan_tool called for topic: {topic} ---")
    
    # Create research plan structure
    research_id = f"research_{hash(topic)}_{len(objectives)}"
    plan_structure = {
        "research_id": research_id,
        "topic": topic,
        "objectives": objectives,
        "questions": questions,
        "methodology": {
            "approach": "systematic secondary research",
            "frameworks": ["literature_review", "data_analysis", "swot_analysis"],
            "sources": [
                "academic_journals",
                "industry_reports", 
                "government_databases",
                "market_research_reports",
                "company_annual_reports"
            ],
            "quality_criteria": [
                "source_credibility",
                "data_recency",
                "relevance_to_objectives"
            ]
        },
        "timeline": {
            "total_duration": "5-7 days",
            "phases": {
                "planning": "1 day",
                "data_collection": "2-3 days",
                "analysis": "1-2 days",
                "reporting": "1 day"
            }
        },
        "deliverables": [
            "comprehensive_research_report",
            "swot_analysis_matrix",
            "executive_summary",
            "source_bibliography"
        ]
    }
    
    # Save to session state
    tool_context.state["current_research_plan"] = plan_structure
    tool_context.state["research_status"] = "plan_created"
    tool_context.state["research_id"] = research_id
    
    # Create Notion page (if configured)
    notion_result = {"status": "skipped", "message": "Notion integration not configured"}
    
    print(f"--- Tool: Research plan created with ID: {research_id} ---")
    
    return {
        "status": "success",
        "research_plan": plan_structure,
        "notion_page": notion_result,
        "next_steps": "Ready for orchestration and data collection phase"
    }