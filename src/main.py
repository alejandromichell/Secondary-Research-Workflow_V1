"""
Main entry point for the secondary research workflow application.
This file sets up a FastAPI server to handle research requests.
"""

from typing import List, Optional

from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from .workflows.simple_live_workflow import SimpleLiveResearchWorkflow
from .utils.questionnaire_processor import QuestionnaireProcessor
from .utils.research_plan_tracker import ResearchPlanTracker, TaskStatus, PlanStatus
import asyncio
import json
import os
from typing import Dict, Any

# --- Pydantic Models ---
class ResearchRequest(BaseModel):
    topic: str

class FoundationQuestionnaireRequest(BaseModel):
    session_id: str
    responses: Dict[str, Any]

class SWOTQuestionnaireRequest(BaseModel):
    session_id: str
    responses: Dict[str, Any]

class ResearchContextRequest(BaseModel):
    session_id: str

class CreateResearchPlanRequest(BaseModel):
    title: str
    description: str
    session_id: str

class UpdateTaskStatusRequest(BaseModel):
    plan_id: str
    task_id: str
    status: str
    notes: Optional[str] = None

class AddTaskNoteRequest(BaseModel):
    plan_id: str
    task_id: str
    note: str


# --- FastAPI Application ---
app = FastAPI(
    title="Secondary Research Workflow API (Live Data Mode)",
    description="An API to initiate and manage live data collection research workflows.",
    version="2.0.0"
)

workflow = SimpleLiveResearchWorkflow()
questionnaire_processor = QuestionnaireProcessor()
plan_tracker = ResearchPlanTracker()

# Persistent storage for research results
STORAGE_FILE = "research_results.json"

def load_research_results() -> Dict[str, Any]:
    """Load research results from file."""
    if os.path.exists(STORAGE_FILE):
        try:
            with open(STORAGE_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}

def save_research_results(data: Dict[str, Any]):
    """Save research results to file."""
    try:
        with open(STORAGE_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    except IOError as e:
        print(f"Warning: Could not save research results: {e}")


def generate_simple_html_report(research_results: Dict[str, Any]) -> str:
    """Generate a simple HTML report from research results."""
    topic = research_results.get("topic", "Unknown Topic")
    live_data = research_results.get("live_data_collected", {})
    analysis = research_results.get("analysis", {})
    final_report = research_results.get("final_report", {})
    
    # Format collection timestamp
    collection_time = live_data.get("collection_timestamp", "")
    if collection_time:
        try:
            from datetime import datetime
            dt = datetime.fromisoformat(collection_time.replace('Z', '+00:00'))
            formatted_time = dt.strftime("%B %d, %Y at %I:%M %p")
        except:
            formatted_time = collection_time
    else:
        formatted_time = "Unknown"
    
    # Generate financial data section
    financial_html = ""
    if "sources" in live_data and "financial" in live_data["sources"]:
        financial_data = live_data["sources"]["financial"]
        # Handle both dict with tickers key and direct list formats
        if isinstance(financial_data, dict) and "tickers" in financial_data:
            tickers = financial_data["tickers"]
        elif isinstance(financial_data, list):
            tickers = financial_data
        else:
            tickers = []
        
        if tickers and len(tickers) > 0:
            financial_html = '<div class="financial-section">'
            financial_html += '<h3>📊 Live Financial Data</h3>'
            
            for ticker in tickers:
                if isinstance(ticker, dict):
                    symbol = ticker.get("symbol", "Unknown")
                    company = ticker.get("company_name", "Unknown Company")
                    market_cap = ticker.get("market_cap", 0)
                    price = ticker.get("current_price", 0)
                    pe_ratio = ticker.get("pe_ratio", 0)
                    price_change = ticker.get("price_change_5d", 0)
                    
                    # Format market cap
                    if market_cap >= 1e12:
                        market_cap_str = f"${market_cap/1e12:.2f}T"
                    elif market_cap >= 1e9:
                        market_cap_str = f"${market_cap/1e9:.2f}B"
                    elif market_cap >= 1e6:
                        market_cap_str = f"${market_cap/1e6:.2f}M"
                    else:
                        market_cap_str = f"${market_cap:,.0f}"
                    
                    # Determine price change color
                    change_color = "green" if price_change >= 0 else "red"
                    change_symbol = "+" if price_change >= 0 else ""
                    
                    financial_html += f'''
                    <div class="ticker-card">
                        <h4>{symbol} - {company}</h4>
                        <div class="ticker-metrics">
                            <div class="metric">
                                <span class="metric-label">Market Cap:</span>
                                <span class="metric-value">{market_cap_str}</span>
                            </div>
                            <div class="metric">
                                <span class="metric-label">Current Price:</span>
                                <span class="metric-value">${price:.2f}</span>
                            </div>
                            <div class="metric">
                                <span class="metric-label">PE Ratio:</span>
                                <span class="metric-value">{pe_ratio:.2f}</span>
                            </div>
                            <div class="metric">
                                <span class="metric-label">5-Day Change:</span>
                                <span class="metric-value" style="color: {change_color}">{change_symbol}${price_change:.2f}</span>
                            </div>
                        </div>
                    </div>
                    '''
            
            financial_html += '</div>'
    
    # Generate analysis section
    analysis_html = ""
    if analysis:
        analysis_html = '<div class="analysis-section">'
        analysis_html += '<h3>🔍 Data Analysis & Insights</h3>'
        
        key_findings = analysis.get("key_findings", [])
        if key_findings:
            analysis_html += '<h4>Key Findings:</h4>'
            analysis_html += '<ul class="findings-list">'
            for finding in key_findings:
                analysis_html += f'<li>{finding}</li>'
            analysis_html += '</ul>'
        
        analysis_html += '</div>'
    
    # Generate recommendations section
    recommendations_html = ""
    if final_report:
        recommendations_html = '<div class="recommendations-section">'
        recommendations_html += '<h3>💡 Strategic Recommendations</h3>'
        
        recommendations = final_report.get("recommendations", [])
        if recommendations:
            recommendations_html += '<h4>Key Recommendations:</h4>'
            recommendations_html += '<ul class="recommendations-list">'
            for rec in recommendations:
                recommendations_html += f'<li>{rec}</li>'
            recommendations_html += '</ul>'
        
        recommendations_html += '</div>'
    
    # Generate complete HTML
    html_template = f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Live Research Report: {topic}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        .header .subtitle {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        
        .header .timestamp {{
            margin-top: 15px;
            font-size: 0.9em;
            opacity: 0.8;
        }}
        
        .content {{
            padding: 40px;
        }}
        
        .section {{
            margin-bottom: 40px;
            padding: 30px;
            background: #f8f9fa;
            border-radius: 10px;
            border-left: 5px solid #3498db;
        }}
        
        .section h3 {{
            color: #2c3e50;
            margin-bottom: 20px;
            font-size: 1.5em;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .ticker-card {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            border: 1px solid #e9ecef;
        }}
        
        .ticker-card h4 {{
            color: #2c3e50;
            margin-bottom: 15px;
            font-size: 1.3em;
        }}
        
        .ticker-metrics {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }}
        
        .metric {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 5px;
        }}
        
        .metric-label {{
            font-weight: 600;
            color: #6c757d;
        }}
        
        .metric-value {{
            font-weight: 700;
            color: #2c3e50;
            font-size: 1.1em;
        }}
        
        .findings-list, .recommendations-list {{
            list-style: none;
            padding: 0;
        }}
        
        .findings-list li, .recommendations-list li {{
            background: white;
            margin-bottom: 10px;
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid #3498db;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        
        .footer {{
            background: #2c3e50;
            color: white;
            text-align: center;
            padding: 20px;
            font-size: 0.9em;
        }}
        
        @media (max-width: 768px) {{
            .container {{
                margin: 10px;
                border-radius: 10px;
            }}
            
            .header {{
                padding: 30px 20px;
            }}
            
            .header h1 {{
                font-size: 2em;
            }}
            
            .content {{
                padding: 20px;
            }}
            
            .section {{
                padding: 20px;
            }}
            
            .ticker-metrics {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Live Research Report: {topic}</h1>
            <div class="subtitle">Live Data Collection Research Report</div>
            <div class="timestamp">Data collected on {formatted_time}</div>
        </div>
        
        <div class="content">
            {financial_html}
            {analysis_html}
            {recommendations_html}
        </div>
        
        <div class="footer">
            <p>Report generated on {formatted_time} | Live Research Workflow System</p>
        </div>
    </div>
</body>
</html>
    '''
    
    return html_template

# Load existing research results
research_results_storage = load_research_results()

def generate_html_report(topic: str, research_results: dict, metadata: dict) -> str:
    """Generate a formatted HTML report from research results."""
    
    # Extract sections
    research_plan = research_results.get("research_plan", "")
    data_collection = research_results.get("data_collection_strategy", "")
    analysis = research_results.get("analysis_and_synthesis", "")
    swot = research_results.get("swot_analysis", "")
    final_report = research_results.get("final_report", "")
    
    # Get metadata
    model_used = metadata.get("model", "Unknown")
    api_used = metadata.get("api_used", "Unknown")
    
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Research Report: {topic}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background-color: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            margin-bottom: 30px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 40px;
            margin-bottom: 20px;
            border-left: 4px solid #3498db;
            padding-left: 15px;
        }}
        h3 {{
            color: #7f8c8d;
            margin-top: 25px;
            margin-bottom: 15px;
        }}
        p {{
            margin-bottom: 15px;
            text-align: justify;
        }}
        .metadata {{
            background-color: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 30px;
            font-size: 0.9em;
        }}
        .section {{
            margin-bottom: 30px;
        }}
        ul, ol {{
            margin-left: 20px;
            margin-bottom: 15px;
        }}
        li {{
            margin-bottom: 8px;
        }}
        .highlight {{
            background-color: #fff3cd;
            padding: 15px;
            border-left: 4px solid #ffc107;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Research Report: {topic}</h1>
        
        <div class="metadata">
            <strong>Generated by:</strong> {api_used} ({model_used})<br>
            <strong>Report Date:</strong> {metadata.get('timestamp', 'Unknown')}<br>
            <strong>Research Steps Completed:</strong> {metadata.get('research_steps_completed', 'Unknown')}
        </div>

        <div class="section">
            <h2>Executive Summary</h2>
            <p>This comprehensive research report provides an in-depth analysis of {topic}, covering research methodology, data collection strategies, market analysis, SWOT assessment, and strategic recommendations. The research was conducted using advanced AI-powered analysis to deliver actionable insights and professional-grade findings.</p>
        </div>

        <div class="section">
            <h2>Research Plan & Methodology</h2>
            <div class="highlight">
                {format_text_as_html(research_plan)}
            </div>
        </div>

        <div class="section">
            <h2>Data Collection Strategy</h2>
            <div class="highlight">
                {format_text_as_html(data_collection)}
            </div>
        </div>

        <div class="section">
            <h2>Analysis & Synthesis</h2>
            <div class="highlight">
                {format_text_as_html(analysis)}
            </div>
        </div>

        <div class="section">
            <h2>SWOT Analysis</h2>
            <div class="highlight">
                {format_text_as_html(swot)}
            </div>
        </div>

        <div class="section">
            <h2>Final Research Report</h2>
            <div class="highlight">
                {format_text_as_html(final_report)}
            </div>
        </div>

        <div class="section">
            <h2>Conclusion</h2>
            <p>This research provides a comprehensive analysis of {topic}, offering valuable insights for decision-makers, researchers, and stakeholders. The findings presented in this report are based on thorough analysis and can serve as a foundation for strategic planning and informed decision-making.</p>
        </div>
    </div>
</body>
</html>
"""
    return html

def format_text_as_html(text: str) -> str:
    """Convert plain text to HTML with proper formatting."""
    if not text:
        return "<p>No content available.</p>"
    
    # Split into paragraphs
    paragraphs = text.split('\n\n')
    html_paragraphs = []
    
    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue
            
        # Check if it's a heading (starts with number or is short and ends with colon)
        if (paragraph.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.')) or 
            (len(paragraph) < 100 and paragraph.endswith(':'))):
            # Convert to h3
            clean_text = paragraph.replace(':', '').strip()
            if clean_text.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.')):
                clean_text = clean_text[3:].strip()
            html_paragraphs.append(f"<h3>{clean_text}</h3>")
        else:
            # Regular paragraph
            html_paragraphs.append(f"<p>{paragraph}</p>")
    
    return '\n'.join(html_paragraphs)

@app.on_event("startup")
async def startup_event():
    print("🚀 Secondary Research Workflow API has started in SIMPLIFIED MODE.")
    print("Listening for research requests on http://127.0.0.1:8000")

@app.post("/start-research")
async def start_research_endpoint(request: ResearchRequest, background_tasks: BackgroundTasks):
    """
    This endpoint accepts a simple research topic and starts the workflow.
    """
    print("--- New Simplified Research Request Received ---")
    
    # Adapt the simple request to the format expected by the workflow
    research_data = {
        "topic": request.topic,
        "objectives": [f"Conduct a general research inquiry into {request.topic}"],
        "questions": [f"What are the key aspects of {request.topic}?"],
        "user_context": request.dict()
    }
    
    print(f"Formatted research topic: {research_data['topic']}")
    print("Starting simplified research process in the background...")

    # Create a unique session ID for this research
    session_id = f"research_{request.topic.replace(' ', '_').replace('/', '_')}"
    
    # Store initial status
    research_results_storage[session_id] = {
        "status": "processing",
        "topic": request.topic,
        "message": "Research in progress..."
    }
    save_research_results(research_results_storage)

    # Run the long-running research task in the background
    async def run_research_and_store():
        result = await workflow.execute_research(research_data)
        research_results_storage[session_id] = result
        save_research_results(research_results_storage)
    
    background_tasks.add_task(run_research_and_store)
    
    return {
        "status": "success",
        "message": "Simplified research process initiated in the background.",
        "topic": request.topic,
        "session_id": session_id,
        "check_status_url": f"/research-status/{session_id}",
        "get_report_url": f"/research-report/{session_id}"
    }

@app.get("/research-status/{session_id}")
async def get_research_status(session_id: str):
    """
    Check the status of a research request.
    """
    # Reload from file to get latest data
    current_storage = load_research_results()
    
    if session_id not in current_storage:
        return {
            "status": "error",
            "error": "Research session not found"
        }
    
    result = current_storage[session_id]
    return {
        "session_id": session_id,
        "status": result.get("status", "unknown"),
        "topic": result.get("topic", "Unknown"),
        "message": result.get("message", "No message available")
    }

@app.get("/research-report/{session_id}")
async def get_research_report(session_id: str):
    """
    Get the complete research report for a completed research request.
    """
    # Reload from file to get latest data
    current_storage = load_research_results()
    
    if session_id not in current_storage:
        return {
            "status": "error",
            "error": "Research session not found"
        }
    
    result = current_storage[session_id]
    
    if result.get("status") == "processing":
        return {
            "status": "processing",
            "message": "Research is still in progress. Please check back later.",
            "check_status_url": f"/research-status/{session_id}"
        }
    
    if result.get("status") == "error":
        return {
            "status": "error",
            "error": result.get("error", "Unknown error occurred")
        }
    
    if result.get("status") == "complete":
        return {
            "status": "complete",
            "session_id": session_id,
            "topic": result.get("topic", "Unknown"),
            "research_results": result.get("research_results", {}),
            "metadata": result.get("metadata", {}),
            "session_state": result.get("session_state", {})
        }
    
    return {
        "status": "unknown",
        "message": "Research status is unclear"
    }

@app.get("/research-report-html/{session_id}", response_class=HTMLResponse)
async def get_research_report_html(session_id: str):
    """
    Get the research report formatted as HTML for better readability.
    """
    # Reload from file to get latest data
    current_storage = load_research_results()
    
    if session_id not in current_storage:
        return {
            "status": "error",
            "error": "Research session not found"
        }
    
    result = current_storage[session_id]
    
    if result.get("status") == "processing":
        return {
            "status": "processing",
            "message": "Research is still in progress. Please check back later.",
            "check_status_url": f"/research-status/{session_id}"
        }
    
    if result.get("status") == "error":
        return {
            "status": "error",
            "error": result.get("error", "Unknown error occurred")
        }
    
    if result.get("status") == "complete":
        try:
            research_results = result.get("research_results", {})
            topic = research_results.get("topic", "Unknown Topic")
            
            # Generate formatted HTML report using inline HTML generation
            html_content = generate_simple_html_report(research_results)
            return HTMLResponse(html_content)
        except Exception as e:
            print(f"Error generating HTML report: {e}")
            import traceback
            traceback.print_exc()
            return HTMLResponse(f"""
            <html><body>
                <h1>Error</h1>
                <p>Failed to generate HTML report: {str(e)}</p>
            </body></html>
            """, status_code=500)
    
    return HTMLResponse("""
    <html><body>
        <h1>Unknown Status</h1>
        <p>Research status is unclear.</p>
    </body></html>
    """)

@app.get("/research-report-view/{session_id}", response_class=HTMLResponse)
async def get_research_report_view(session_id: str):
    """
    Get the research report as a viewable HTML page.
    """
    # Reload from file to get latest data
    current_storage = load_research_results()
    
    if session_id not in current_storage:
        return HTMLResponse("""
        <html><body>
            <h1>Error</h1>
            <p>Research session not found.</p>
        </body></html>
        """, status_code=404)
    
    result = current_storage[session_id]
    
    if result.get("status") == "processing":
        return HTMLResponse("""
        <html><body>
            <h1>Research in Progress</h1>
            <p>Your research is still being processed. Please check back later.</p>
        </body></html>
        """)
    
    if result.get("status") == "error":
        return HTMLResponse(f"""
        <html><body>
            <h1>Error</h1>
            <p>Research failed: {result.get('error', 'Unknown error occurred')}</p>
        </body></html>
        """, status_code=500)
    
    if result.get("status") == "complete":
        try:
            research_results = result.get("research_results", {})
            topic = research_results.get("topic", "Unknown Topic")
            
            # Generate formatted HTML report using inline HTML generation
            html_content = generate_simple_html_report(research_results)
            return HTMLResponse(html_content)
        except Exception as e:
            print(f"Error generating HTML report: {e}")
            import traceback
            traceback.print_exc()
            return HTMLResponse(f"""
            <html><body>
                <h1>Error</h1>
                <p>Failed to generate HTML report: {str(e)}</p>
            </body></html>
            """, status_code=500)
    
    return HTMLResponse("""
    <html><body>
        <h1>Unknown Status</h1>
        <p>Research status is unclear.</p>
    </body></html>
    """)

# --- Questionnaire Management Endpoints ---

@app.get("/questionnaire/foundation-questions")
async def get_foundation_questions():
    """
    Get the Core Research Foundation questions that must be answered before research planning.
    """
    try:
        questions = questionnaire_processor.get_foundation_questions()
        formatted_questions = questionnaire_processor.format_foundation_questions_for_user()
        
        return {
            "status": "success",
            "questions": questions,
            "formatted_questions": formatted_questions,
            "message": "Foundation questions retrieved successfully"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "Failed to retrieve foundation questions"
        }

@app.get("/questionnaire/swot-questions")
async def get_swot_questions():
    """
    Get the SWOT Analysis Assessment questions that must be answered before SWOT analysis.
    """
    try:
        questions = questionnaire_processor.get_swot_questions()
        formatted_questions = questionnaire_processor.format_swot_questions_for_user()
        
        return {
            "status": "success",
            "questions": questions,
            "formatted_questions": formatted_questions,
            "message": "SWOT assessment questions retrieved successfully"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "Failed to retrieve SWOT assessment questions"
        }

@app.post("/questionnaire/foundation-responses")
async def submit_foundation_responses(request: FoundationQuestionnaireRequest):
    """
    Submit responses to the Core Research Foundation questionnaire.
    """
    try:
        result = questionnaire_processor.process_foundation_responses(
            request.session_id, 
            request.responses
        )
        
        return {
            "status": "success" if result.get("status") == "complete" else "incomplete",
            "result": result,
            "message": "Foundation responses processed successfully" if result.get("status") == "complete" else "Foundation responses incomplete"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "Failed to process foundation responses"
        }

@app.post("/questionnaire/swot-responses")
async def submit_swot_responses(request: SWOTQuestionnaireRequest):
    """
    Submit responses to the SWOT Analysis Assessment questionnaire.
    """
    try:
        result = questionnaire_processor.process_swot_responses(
            request.session_id, 
            request.responses
        )
        
        return {
            "status": "success" if result.get("status") == "complete" else "incomplete",
            "result": result,
            "message": "SWOT responses processed successfully" if result.get("status") == "complete" else "SWOT responses incomplete"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "Failed to process SWOT responses"
        }

@app.get("/questionnaire/status/{session_id}")
async def get_questionnaire_status(session_id: str):
    """
    Get the status of questionnaires for a specific session.
    """
    try:
        status = questionnaire_processor.get_questionnaire_status(session_id)
        
        return {
            "status": "success",
            "questionnaire_status": status,
            "message": "Questionnaire status retrieved successfully"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "Failed to retrieve questionnaire status"
        }

@app.get("/questionnaire/research-context/{session_id}")
async def get_research_context(session_id: str):
    """
    Get the complete research context from both questionnaires for a session.
    """
    try:
        context = questionnaire_processor.get_research_context(session_id)
        
        return {
            "status": "success" if context.get("status") == "complete" else "incomplete",
            "research_context": context,
            "message": "Research context retrieved successfully" if context.get("status") == "complete" else "Research context incomplete"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "Failed to retrieve research context"
        }

@app.get("/questionnaire/validate-readiness/{session_id}")
async def validate_research_readiness(session_id: str):
    """
    Validate if a session is ready to proceed with research planning.
    """
    try:
        validation = questionnaire_processor.validate_research_readiness(session_id)
        
        return {
            "status": "success",
            "validation": validation,
            "message": "Research readiness validation completed"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "Failed to validate research readiness"
        }

# --- Research Plan Management Endpoints ---

@app.post("/research-plan/create")
async def create_research_plan(request: CreateResearchPlanRequest):
    """
    Create a new research plan based on research context from questionnaires.
    """
    try:
        # Validate research readiness first
        validation = questionnaire_processor.validate_research_readiness(request.session_id)
        if not validation["ready"]:
            return {
                "status": "error",
                "message": "Research context not ready",
                "details": validation
            }
        
        # Get research context
        context = questionnaire_processor.get_research_context(request.session_id)
        
        # Create research plan
        plan = plan_tracker.create_research_plan(
            request.title,
            request.description,
            context
        )
        
        return {
            "status": "success",
            "plan": {
                "id": plan.id,
                "title": plan.title,
                "description": plan.description,
                "status": plan.status.value,
                "total_tasks": len(plan.tasks),
                "created_at": plan.created_at
            },
            "message": f"Research plan '{request.title}' created successfully with {len(plan.tasks)} tasks"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "Failed to create research plan"
        }

@app.get("/research-plan/{plan_id}")
async def get_research_plan(plan_id: str):
    """
    Get a research plan by ID.
    """
    try:
        plan = plan_tracker.get_plan(plan_id)
        if not plan:
            return {
                "status": "error",
                "message": "Research plan not found"
            }
        
        return {
            "status": "success",
            "plan": {
                "id": plan.id,
                "title": plan.title,
                "description": plan.description,
                "status": plan.status.value,
                "created_at": plan.created_at,
                "updated_at": plan.updated_at,
                "started_at": plan.started_at,
                "completed_at": plan.completed_at,
                "tasks": [
                    {
                        "id": task.id,
                        "title": task.title,
                        "description": task.description,
                        "status": task.status.value,
                        "priority": task.priority,
                        "assigned_agent": task.assigned_agent,
                        "estimated_duration": task.estimated_duration,
                        "dependencies": task.dependencies,
                        "created_at": task.created_at,
                        "started_at": task.started_at,
                        "completed_at": task.completed_at,
                        "notes": task.notes
                    }
                    for task in plan.tasks
                ],
                "metadata": plan.metadata
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "Failed to get research plan"
        }

@app.get("/research-plan/{plan_id}/progress")
async def get_plan_progress(plan_id: str):
    """
    Get progress information for a research plan.
    """
    try:
        progress = plan_tracker.get_plan_progress(plan_id)
        
        if "error" in progress:
            return {
                "status": "error",
                "message": progress["error"]
            }
        
        return {
            "status": "success",
            "progress": progress
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "Failed to get plan progress"
        }

@app.get("/research-plan/{plan_id}/next-tasks")
async def get_next_available_tasks(plan_id: str):
    """
    Get tasks that are ready to be started (dependencies met).
    """
    try:
        tasks = plan_tracker.get_next_available_tasks(plan_id)
        
        task_data = []
        for task in tasks:
            task_data.append({
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "priority": task.priority,
                "estimated_duration": task.estimated_duration,
                "assigned_agent": task.assigned_agent,
                "dependencies": task.dependencies,
                "created_at": task.created_at
            })
        
        return {
            "status": "success",
            "available_tasks": task_data,
            "count": len(task_data)
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "Failed to get next available tasks"
        }

@app.post("/research-plan/update-task-status")
async def update_task_status(request: UpdateTaskStatusRequest):
    """
    Update the status of a research task.
    """
    try:
        # Validate status
        try:
            status = TaskStatus(request.status)
        except ValueError:
            return {
                "status": "error",
                "message": f"Invalid status: {request.status}. Valid values: {[s.value for s in TaskStatus]}"
            }
        
        success = plan_tracker.update_task_status(
            request.plan_id,
            request.task_id,
            status,
            request.notes
        )
        
        if success:
            return {
                "status": "success",
                "message": f"Task {request.task_id} status updated to {request.status}"
            }
        else:
            return {
                "status": "error",
                "message": f"Failed to update task {request.task_id} status"
            }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "Failed to update task status"
        }

@app.post("/research-plan/add-task-note")
async def add_task_note(request: AddTaskNoteRequest):
    """
    Add a note to a specific task.
    """
    try:
        success = plan_tracker.add_task_note(
            request.plan_id,
            request.task_id,
            request.note
        )
        
        if success:
            return {
                "status": "success",
                "message": f"Note added to task {request.task_id}"
            }
        else:
            return {
                "status": "error",
                "message": f"Failed to add note to task {request.task_id}"
            }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "Failed to add task note"
        }

@app.get("/")
async def root():
    return {"message": "Secondary Research Workflow API is running in Simplified Mode."}
