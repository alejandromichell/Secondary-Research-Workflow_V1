#!/usr/bin/env python3
"""Test script to debug HTML generation."""

import json
import sys
import os

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import the function we want to test
from main import generate_simple_html_report

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
