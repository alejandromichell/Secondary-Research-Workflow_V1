"""
Advanced monitoring and analytics callbacks.
"""

import time
import json
from typing import Dict, Any
from google.adk.agents.callback_context import CallbackContext


def workflow_performance_monitor(callback_context: CallbackContext, event_data: Dict[str, Any]):
    """Monitor workflow performance and collect metrics."""
    
    agent_name = callback_context.agent_name
    current_time = time.time()
    
    # Initialize performance tracking
    if "performance_metrics" not in callback_context.state:
        callback_context.state["performance_metrics"] = {
            "workflow_start_time": current_time,
            "agent_execution_times": {},
            "tool_execution_counts": {},
            "error_counts": {},
            "quality_scores": {}
        }
    
    metrics = callback_context.state["performance_metrics"]
    
    # Track agent execution
    if agent_name not in metrics["agent_execution_times"]:
        metrics["agent_execution_times"][agent_name] = {
            "start_time": current_time,
            "total_execution_time": 0,
            "call_count": 0
        }
    
    metrics["agent_execution_times"][agent_name]["call_count"] += 1
    
    # Log performance data
    print(f"--- Performance: {agent_name} execution #{metrics['agent_execution_times'][agent_name]['call_count']} ---")


def research_quality_tracker(callback_context: CallbackContext, quality_data: Dict[str, Any]):
    """Track research quality metrics throughout the workflow."""
    
    if "quality_tracking" not in callback_context.state:
        callback_context.state["quality_tracking"] = {
            "source_quality_scores": [],
            "analysis_confidence_levels": [],
            "recommendation_actionability": [],
            "overall_quality_trend": []
        }
    
    tracking = callback_context.state["quality_tracking"]
    
    # Update quality metrics based on the data
    if "source_quality" in quality_data:
        tracking["source_quality_scores"].append(quality_data["source_quality"])
    
    if "confidence_level" in quality_data:
        tracking["analysis_confidence_levels"].append(quality_data["confidence_level"])
    
    # Calculate overall quality score
    if tracking["source_quality_scores"] and tracking["analysis_confidence_levels"]:
        overall_quality = (
            sum(tracking["source_quality_scores"]) / len(tracking["source_quality_scores"]) * 0.6 +
            sum(tracking["analysis_confidence_levels"]) / len(tracking["analysis_confidence_levels"]) * 0.4
        )
        tracking["overall_quality_trend"].append(overall_quality)
        
        print(f"--- Quality: Current overall score: {overall_quality:.2f} ---")