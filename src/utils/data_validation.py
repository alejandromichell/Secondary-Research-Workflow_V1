"""
Data validation utilities for research workflow.
"""

from typing import Dict, Any, List


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
        if not isinstance(objective, str) or len(objective.strip()) < 12:
            print(f"❌ Validation failed: Objective {i+1} must be at least 12 characters")
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
        if len(objective.strip()) < 12:
            return False
        
        # Check for action words
        action_words = ['analyze', 'identify', 'assess', 'evaluate', 'determine', 'investigate', 'examine']
        if not any(word in objective.lower() for word in action_words):
            print(f"⚠️ Objective may lack clear action: {objective[:50]}...")
    
    return True