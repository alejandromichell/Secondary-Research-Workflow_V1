"""
HTML Report Generator for Live Research Results.
Separate utility to convert research results into beautiful HTML reports.
"""

from typing import Dict, Any
from datetime import datetime
import json


class HTMLReportGenerator:
    """Generates HTML reports from research results."""
    
    def __init__(self):
        self.template = self._get_html_template()
    
    def generate_report(self, research_results: Dict[str, Any]) -> str:
        """Generate HTML report from research results."""
        
        # Extract data from research results
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
        financial_html = self._generate_financial_section(live_data.get("sources", {}).get("financial", {}))
        
        # Generate news data section
        news_html = self._generate_news_section(live_data.get("sources", {}).get("news", {}))
        
        # Generate analysis section
        analysis_html = self._generate_analysis_section(analysis)
        
        # Generate recommendations section
        recommendations_html = self._generate_recommendations_section(final_report)
        
        # Fill in the template
        html_content = self.template.format(
            title=f"Live Research Report: {topic}",
            topic=topic,
            collection_time=formatted_time,
            financial_section=financial_html,
            news_section=news_html,
            analysis_section=analysis_html,
            recommendations_section=recommendations_html,
            generation_time=datetime.now().strftime("%B %d, %Y at %I:%M %p")
        )
        
        return html_content
    
    def _generate_financial_section(self, financial_data: Dict[str, Any]) -> str:
        """Generate HTML for financial data section."""
        if not financial_data or not financial_data.get("tickers"):
            return "<p>No financial data collected.</p>"
        
        html = '<div class="financial-section">'
        html += '<h3>📊 Live Financial Data</h3>'
        
        for ticker in financial_data["tickers"]:
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
            
            html += f'''
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
        
        html += '</div>'
        return html
    
    def _generate_news_section(self, news_data: Dict[str, Any]) -> str:
        """Generate HTML for news data section."""
        if not news_data or not news_data.get("headlines"):
            return "<p>No news data collected.</p>"
        
        html = '<div class="news-section">'
        html += '<h3>📰 Live News & Market Updates</h3>'
        
        headlines = news_data.get("headlines", [])
        sources = news_data.get("sources", [])
        
        html += '<div class="news-grid">'
        for i, headline in enumerate(headlines):
            source = sources[i] if i < len(sources) else "Industry Source"
            html += f'''
            <div class="news-item">
                <h4>{headline}</h4>
                <p class="news-source">Source: {source}</p>
            </div>
            '''
        html += '</div>'
        html += '</div>'
        
        return html
    
    def _generate_analysis_section(self, analysis: Dict[str, Any]) -> str:
        """Generate HTML for analysis section."""
        if not analysis:
            return "<p>No analysis data available.</p>"
        
        html = '<div class="analysis-section">'
        html += '<h3>🔍 Data Analysis & Insights</h3>'
        
        # Key findings
        key_findings = analysis.get("key_findings", [])
        if key_findings:
            html += '<h4>Key Findings:</h4>'
            html += '<ul class="findings-list">'
            for finding in key_findings:
                html += f'<li>{finding}</li>'
            html += '</ul>'
        
        # Market insights
        market_insights = analysis.get("market_insights", {})
        if market_insights:
            html += '<h4>Market Insights:</h4>'
            for insight_type, insight_data in market_insights.items():
                html += f'<div class="insight-item">'
                html += f'<strong>{insight_type.replace("_", " ").title()}:</strong> '
                html += f'{insight_data}</div>'
        
        html += '</div>'
        return html
    
    def _generate_recommendations_section(self, final_report: Dict[str, Any]) -> str:
        """Generate HTML for recommendations section."""
        if not final_report:
            return "<p>No recommendations available.</p>"
        
        html = '<div class="recommendations-section">'
        html += '<h3>💡 Strategic Recommendations</h3>'
        
        # Executive summary
        exec_summary = final_report.get("executive_summary", {})
        if exec_summary:
            research_method = exec_summary.get("research_method", "")
            if research_method:
                html += f'<p><strong>Research Method:</strong> {research_method}</p>'
        
        # Recommendations
        recommendations = final_report.get("recommendations", [])
        if recommendations:
            html += '<h4>Key Recommendations:</h4>'
            html += '<ul class="recommendations-list">'
            for rec in recommendations:
                html += f'<li>{rec}</li>'
            html += '</ul>'
        
        # Next steps
        next_steps = final_report.get("next_steps", [])
        if next_steps:
            html += '<h4>Next Steps:</h4>'
            html += '<ul class="next-steps-list">'
            for step in next_steps:
                html += f'<li>{step}</li>'
            html += '</ul>'
        
        html += '</div>'
        return html
    
    def _get_html_template(self) -> str:
        """Get the HTML template for the report."""
        return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
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
        
        .news-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }}
        
        .news-item {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 3px 10px rgba(0,0,0,0.1);
            border-left: 4px solid #e74c3c;
        }}
        
        .news-item h4 {{
            color: #2c3e50;
            margin-bottom: 10px;
            line-height: 1.4;
        }}
        
        .news-source {{
            color: #6c757d;
            font-size: 0.9em;
            font-style: italic;
        }}
        
        .findings-list, .recommendations-list, .next-steps-list {{
            list-style: none;
            padding: 0;
        }}
        
        .findings-list li, .recommendations-list li, .next-steps-list li {{
            background: white;
            margin-bottom: 10px;
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid #3498db;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        
        .insight-item {{
            background: white;
            margin-bottom: 10px;
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid #f39c12;
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
            <h1>{title}</h1>
            <div class="subtitle">Live Data Collection Research Report</div>
            <div class="timestamp">Data collected on {collection_time}</div>
        </div>
        
        <div class="content">
            {financial_section}
            {news_section}
            {analysis_section}
            {recommendations_section}
        </div>
        
        <div class="footer">
            <p>Report generated on {generation_time} | Live Research Workflow System</p>
        </div>
    </div>
</body>
</html>
        '''
    
    def save_report(self, research_results: Dict[str, Any], filename: str = None) -> str:
        """Generate and save HTML report to file."""
        if filename is None:
            topic = research_results.get("topic", "research_report")
            safe_topic = "".join(c for c in topic if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = f"{safe_topic.replace(' ', '_')}_report.html"
        
        html_content = self.generate_report(research_results)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return filename


def create_html_report(research_results: Dict[str, Any], output_file: str = None) -> str:
    """Convenience function to create HTML report."""
    generator = HTMLReportGenerator()
    return generator.save_report(research_results, output_file)
