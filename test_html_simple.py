#!/usr/bin/env python3
"""Simple test script to debug HTML generation."""

import json
from datetime import datetime

def generate_simple_html_report(research_results):
    """Generate a simple HTML report from research results."""
    topic = research_results.get("topic", "Unknown Topic")
    live_data = research_results.get("live_data_collected", {})
    analysis = research_results.get("analysis", {})
    final_report = research_results.get("final_report", {})
    
    # Format collection timestamp
    collection_time = live_data.get("collection_timestamp", "")
    if collection_time:
        try:
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

def test_html_generation():
    """Test the HTML generation function."""
    try:
        # Load the research results
        with open('research_results.json', 'r') as f:
            data = json.load(f)
        
        # Get the session data
        session_id = "research_Artificial_Intelligence_Market_Trends"
        session_data = data.get(session_id)
        
        if not session_data:
            print(f"Session {session_id} not found")
            return
        
        research_results = session_data.get("research_results", {})
        
        print("Research results keys:", list(research_results.keys()))
        print("Live data keys:", list(research_results.get("live_data_collected", {}).keys()))
        
        # Test the HTML generation
        html_content = generate_simple_html_report(research_results)
        
        print("HTML generation successful!")
        print(f"HTML length: {len(html_content)} characters")
        print("First 200 characters:")
        print(html_content[:200])
        
        # Save the HTML to a file for inspection
        with open('test_output.html', 'w') as f:
            f.write(html_content)
        
        print("HTML saved to test_output.html")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_html_generation()
