"""
Research Foundation Agent - Handles Core Research Foundation questions.

This agent is responsible for gathering essential research context before
beginning the research planning phase. It ensures all mandatory foundation
questions are answered before proceeding.
"""

import sys
import os
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

class ResearchFoundationAgent:
    """Agent responsible for gathering core research foundation information."""
    
    def __init__(self):
        self.agent_name = "Research Foundation Agent"
        self.agent_role = "Research Context Specialist"
        
        # Load foundation questions
        self.foundation_questions = self._load_foundation_questions()
        
    def _load_foundation_questions(self) -> Dict[str, Any]:
        """Load the core research foundation questions from the context file."""
        try:
            questions_path = os.path.join(
                os.path.dirname(__file__), '..', '..', 'context', 'core_research_foundation.txt'
            )
            
            with open(questions_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse the questions into structured format
            return self._parse_foundation_questions(content)
            
        except Exception as e:
            print(f"Error loading foundation questions: {e}")
            return self._get_default_questions()
    
    def _parse_foundation_questions(self, content: str) -> Dict[str, Any]:
        """Parse the foundation questions text into structured format."""
        questions = {
            "primary_research_objective": {
                "title": "Primary Research Objective",
                "questions": [
                    "What is the primary objective of your research? What specific strategic goal are you trying to achieve?",
                    "What key business decision will this research inform? (e.g., market entry, product launch, strategic planning, investment decision)"
                ],
                "required": True
            },
            "research_subject_scope": {
                "title": "Research Subject & Scope", 
                "questions": [
                    "What is the main subject of analysis? (company name, industry, market, or product/service)",
                    "If analyzing a specific organization, please provide: company name, primary industry, approximate size (revenue/employees), and main products/services",
                    "What is the geographic scope? (local, regional, national, global, or specific countries/regions)"
                ],
                "required": True
            },
            "critical_research_questions": {
                "title": "Critical Research Questions",
                "questions": [
                    "What are the 3-5 most important questions this research must answer?",
                    "Are there specific areas of concern or opportunity you want emphasized?"
                ],
                "required": True
            },
            "timeline_requirements": {
                "title": "Timeline Requirements",
                "questions": [
                    "What are the starting and finishing dates?",
                    "What are important milestone dates in between the starting and finishing dates?"
                ],
                "required": True
            }
        }
        
        return {
            "sections": questions,
            "mandatory_note": "MANDATORY: Do NOT proceed until you have collected adequate responses to ALL sections below.",
            "total_sections": len(questions)
        }
    
    def _get_default_questions(self) -> Dict[str, Any]:
        """Fallback questions if file loading fails."""
        return {
            "sections": {
                "primary_research_objective": {
                    "title": "Primary Research Objective",
                    "questions": ["What is the primary objective of your research?"],
                    "required": True
                }
            },
            "mandatory_note": "MANDATORY: Foundation questions must be answered before proceeding.",
            "total_sections": 1
        }
    
    def get_instruction(self) -> str:
        """Get the agent's instruction prompt."""
        return f"""
You are the {self.agent_role}, a specialized agent in the multi-agent research team.

PRIMARY FUNCTION: Gather comprehensive research foundation information before any research planning begins.

CORE RESPONSIBILITY: You MUST collect adequate responses to ALL foundation question sections before allowing the research process to proceed.

FOUNDATION QUESTION SECTIONS:
{self._format_questions_for_instruction()}

CRITICAL REQUIREMENTS:
1. MANDATORY COMPLETION: Do NOT proceed until ALL sections have adequate responses
2. COMPREHENSIVE COVERAGE: Ensure each question receives a detailed, actionable response
3. QUALITY VALIDATION: Verify responses provide sufficient context for research planning
4. STRUCTURED OUTPUT: Format responses in a structured format for downstream agents

OUTPUT FORMAT: Provide responses in structured JSON format with clear section organization.
"""
    
    def _format_questions_for_instruction(self) -> str:
        """Format questions for inclusion in the instruction prompt."""
        formatted = ""
        for section_id, section_data in self.foundation_questions["sections"].items():
            formatted += f"\n{section_data['title']}:\n"
            for i, question in enumerate(section_data['questions'], 1):
                formatted += f"  {i}. {question}\n"
        return formatted
    
    def conduct_foundation_assessment(self, user_responses: Dict[str, Any]) -> Dict[str, Any]:
        """
        Conduct the foundation assessment based on user responses.
        
        Args:
            user_responses: Dictionary containing user responses to foundation questions
            
        Returns:
            Dictionary containing assessment results and validation status
        """
        try:
            print(f">>> {self.agent_name}: Conducting foundation assessment...", flush=True)
            
            # Validate completeness
            validation_result = self._validate_responses(user_responses)
            
            if not validation_result["is_complete"]:
                return {
                    "status": "incomplete",
                    "message": "Foundation assessment incomplete - missing required sections",
                    "missing_sections": validation_result["missing_sections"],
                    "validation_details": validation_result
                }
            
            # Process and structure the responses
            structured_responses = self._structure_responses(user_responses)
            
            # Generate assessment summary
            assessment_summary = self._generate_assessment_summary(structured_responses)
            
            print(f">>> {self.agent_name}: Foundation assessment completed successfully", flush=True)
            
            return {
                "status": "complete",
                "foundation_context": structured_responses,
                "assessment_summary": assessment_summary,
                "validation_result": validation_result,
                "timestamp": datetime.now().isoformat(),
                "agent": self.agent_name
            }
            
        except Exception as e:
            print(f">>> {self.agent_name}: Error in foundation assessment: {e}", flush=True)
            return {
                "status": "error",
                "error": str(e),
                "agent": self.agent_name
            }
    
    def _validate_responses(self, responses: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that all required sections have adequate responses."""
        missing_sections = []
        validation_details = {}
        
        for section_id, section_data in self.foundation_questions["sections"].items():
            if section_data["required"]:
                if section_id not in responses or not responses[section_id]:
                    missing_sections.append(section_id)
                    validation_details[section_id] = "Missing required response"
                else:
                    # Check if response has adequate content
                    response_content = responses[section_id]
                    if isinstance(response_content, str) and len(response_content.strip()) < 10:
                        missing_sections.append(section_id)
                        validation_details[section_id] = "Response too brief"
                    elif isinstance(response_content, dict) and not any(response_content.values()):
                        missing_sections.append(section_id)
                        validation_details[section_id] = "Empty response structure"
                    else:
                        validation_details[section_id] = "Valid response"
        
        return {
            "is_complete": len(missing_sections) == 0,
            "missing_sections": missing_sections,
            "validation_details": validation_details,
            "total_required": len([s for s in self.foundation_questions["sections"].values() if s["required"]]),
            "completed": len(self.foundation_questions["sections"]) - len(missing_sections)
        }
    
    def _structure_responses(self, responses: Dict[str, Any]) -> Dict[str, Any]:
        """Structure the user responses into a standardized format."""
        structured = {
            "research_foundation": {
                "primary_objective": responses.get("primary_research_objective", ""),
                "subject_scope": responses.get("research_subject_scope", ""),
                "critical_questions": responses.get("critical_research_questions", ""),
                "timeline": responses.get("timeline_requirements", "")
            },
            "metadata": {
                "collection_timestamp": datetime.now().isoformat(),
                "agent": self.agent_name,
                "version": "1.0"
            }
        }
        
        return structured
    
    def _generate_assessment_summary(self, structured_responses: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of the foundation assessment."""
        foundation = structured_responses["research_foundation"]
        
        return {
            "objective_clarity": "High" if len(str(foundation["primary_objective"])) > 50 else "Medium",
            "scope_definition": "Complete" if foundation["subject_scope"] else "Incomplete", 
            "research_focus": "Defined" if foundation["critical_questions"] else "Undefined",
            "timeline_set": "Established" if foundation["timeline"] else "Not Set",
            "readiness_for_planning": "Ready" if all([
                foundation["primary_objective"],
                foundation["subject_scope"], 
                foundation["critical_questions"],
                foundation["timeline"]
            ]) else "Not Ready"
        }
    
    def get_foundation_questions(self) -> Dict[str, Any]:
        """Get the complete set of foundation questions."""
        return self.foundation_questions
    
    def format_questions_for_user(self) -> str:
        """Format questions in a user-friendly format for display."""
        formatted = f"{self.foundation_questions['mandatory_note']}\n\n"
        formatted += "CORE RESEARCH FOUNDATION QUESTIONS\n"
        formatted += "=" * 50 + "\n\n"
        
        for section_id, section_data in self.foundation_questions["sections"].items():
            formatted += f"{section_data['title']}\n"
            formatted += "-" * len(section_data['title']) + "\n"
            
            for i, question in enumerate(section_data['questions'], 1):
                formatted += f"{i}. {question}\n"
            
            formatted += "\n"
        
        return formatted
