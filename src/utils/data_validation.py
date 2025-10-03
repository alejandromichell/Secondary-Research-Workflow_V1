"""
Data validation utilities for research workflow.
"""

from typing import Dict, Any, List
import re


def validate_research_request(request: Dict[str, Any]) -> bool:
    """Validate research request structure and content."""
    
    # Check required fields
    required_fields = ["topic", "objectives"]
    for field in required_fields:
        if field not in request:
            print(f"❌ Validation failed: Missing required field '{field}'")
            return False
    
    # Validate topic
    topic = request.get("topic", "")
    if not topic or len(topic.strip()) < 10:
        print("❌ Validation failed: Topic must be at least 10 characters")
        return False
    
    # Validate objectives
    objectives = request.get("objectives", [])
    if not isinstance(objectives, list) or len(objectives) == 0:
        print("❌ Validation failed: At least one objective required")
        return False
    
    for i, objective in enumerate(objectives):
        if not isinstance(objective, str) or len(objective.strip()) < 15:
            print(f"❌ Validation failed: Objective {i+1} must be at least 15 characters")
            return False
    
    # Validate questions (if provided)
    questions = request.get("questions", [])
    if questions:
        if not isinstance(questions, list):
            print("❌ Validation failed: Questions must be a list")
            return False
        
        for i, question in enumerate(questions):
            if not isinstance(question, str) or len(question.strip()) < 10:
                print(f"❌ Validation failed: Question {i+1} must be at least 10 characters")
                return False
    
    print("✅ Research request validation passed")
    return True


def validate_research_objectives(objectives: List[str]) -> bool:
    """Validate research objectives for quality and structure."""
    
    if not objectives or len(objectives) == 0:
        return False
    
    for objective in objectives:
        # Check length
        if len(objective.strip()) < 15:
            return False
        
        # Check for action words
        action_words = ['analyze', 'identify', 'assess', 'evaluate', 'determine', 'investigate', 'examine']
        if not any(word in objective.lower() for word in action_words):
            print(f"⚠️ Objective may lack clear action: {objective[:50]}...")
    
    return True


def validate_agent_output(output: Dict[str, Any], agent_name: str) -> bool:
    """Validate agent output structure and content."""
    
    # Check status
    if "status" not in output:
        print(f"❌ {agent_name} output missing status field")
        return False
    
    if output["status"] not in ["success", "error"]:
        print(f"❌ {agent_name} invalid status: {output['status']}")
        return False
    
    # If error, check error message
    if output["status"] == "error":
        if "error_message" not in output:
            print(f"❌ {agent_name} error output missing error_message")
            return False
        return True
    
    # Agent-specific validation
    if agent_name == "research_plan_agent":
        return _validate_research_plan_output(output)
    elif agent_name == "orchestration_agent":
        return _validate_orchestration_output(output)
    elif agent_name == "synthesis_agent":
        return _validate_synthesis_output(output)
    elif agent_name == "swot_analysis_agent":
        return _validate_swot_output(output)
    elif agent_name == "report_generation_agent":
        return _validate_report_output(output)
    
    return True


def _validate_research_plan_output(output: Dict[str, Any]) -> bool:
    """Validate research plan agent output."""
    required_fields = ["research_plan"]
    for field in required_fields:
        if field not in output:
            print(f"❌ Research plan output missing {field}")
            return False
    
    plan = output["research_plan"]
    plan_required = ["research_id", "topic", "objectives", "methodology"]
    for field in plan_required:
        if field not in plan:
            print(f"❌ Research plan missing {field}")
            return False
    
    return True


def _validate_orchestration_output(output: Dict[str, Any]) -> bool:
    """Validate orchestration agent output."""
    required_fields = ["orchestration_results"]
    for field in required_fields:
        if field not in output:
            print(f"❌ Orchestration output missing {field}")
            return False
    
    return True


def _validate_synthesis_output(output: Dict[str, Any]) -> bool:
    """Validate synthesis agent output."""
    required_fields = ["synthesis_results"]
    for field in required_fields:
        if field not in output:
            print(f"❌ Synthesis output missing {field}")
            return False
    
    return True


def _validate_swot_output(output: Dict[str, Any]) -> bool:
    """Validate SWOT analysis agent output."""
    required_fields = ["swot_analysis"]
    for field in required_fields:
        if field not in output:
            print(f"❌ SWOT output missing {field}")
            return False
    
    swot = output["swot_analysis"]
    if "swot_matrix" not in swot:
        print("❌ SWOT analysis missing swot_matrix")
        return False
    
    matrix = swot["swot_matrix"]
    swot_quadrants = ["strengths", "weaknesses", "opportunities", "threats"]
    for quadrant in swot_quadrants:
        if quadrant not in matrix:
            print(f"❌ SWOT matrix missing {quadrant}")
            return False
    
    return True


def _validate_report_output(output: Dict[str, Any]) -> bool:
    """Validate report generation agent output."""
    required_fields = ["final_report"]
    for field in required_fields:
        if field not in output:
            print(f"❌ Report output missing {field}")
            return False
    
    return True


def sanitize_text_input(text: str) -> str:
    """Sanitize text input for safety."""
    if not isinstance(text, str):
        return ""
    
    # Remove potentially harmful patterns
    text = re.sub(r'<script.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'javascript:', '', text, flags=re.IGNORECASE)
    text = re.sub(r'on\w+\s*=', '', text, flags=re.IGNORECASE)
    
    # Limit length
    if len(text) > 10000:
        text = text[:10000] + "..."
    
    return text.strip()