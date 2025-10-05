"""
SWOT Assessment Agent - Handles SWOT Analysis Assessment questions.

This agent is responsible for gathering critical information before beginning
the SWOT analysis phase. It ensures all necessary context is collected for
comprehensive SWOT analysis.
"""

import sys
import os
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

class SWOTAssessmentAgent:
    """Agent responsible for gathering SWOT analysis assessment information."""
    
    def __init__(self):
        self.agent_name = "SWOT Assessment Agent"
        self.agent_role = "SWOT Analysis Context Specialist"
        
        # Load SWOT assessment questions
        self.swot_questions = self._load_swot_questions()
        
    def _load_swot_questions(self) -> Dict[str, Any]:
        """Load the SWOT analysis assessment questions from the context file."""
        try:
            questions_path = os.path.join(
                os.path.dirname(__file__), '..', '..', 'context', 'swot_analysis_assessment_questions.txt'
            )
            
            with open(questions_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse the questions into structured format
            return self._parse_swot_questions(content)
            
        except Exception as e:
            print(f"Error loading SWOT assessment questions: {e}")
            return self._get_default_swot_questions()
    
    def _parse_swot_questions(self, content: str) -> Dict[str, Any]:
        """Parse the SWOT assessment questions text into structured format."""
        questions = {
            "business_organization_context": {
                "title": "Business/Organization Context",
                "questions": [
                    "What is the name and primary industry of the organization being analyzed?",
                    "What is the organization's size (employees, revenue, market cap if public)?",
                    "What are the organization's core products/services and primary markets?",
                    "What is the time frame for this analysis (current state, 1-year outlook, 3-year strategic)?"
                ],
                "required": True
            },
            "analysis_scope": {
                "title": "Analysis Scope",
                "questions": [
                    "Is this a comprehensive organizational SWOT or focused on specific business units/products?",
                    "What are the primary strategic decisions this analysis will inform?",
                    "Are there specific competitors or market segments that should be prioritized?",
                    "What geographical markets should be included?"
                ],
                "required": True
            },
            "stakeholder_requirements": {
                "title": "Stakeholder Requirements",
                "questions": [
                    "Who is the primary audience for this analysis (executives, investors, board members)?",
                    "What level of detail is required (high-level strategic vs. operational detail)?",
                    "Are there specific areas of concern or opportunity to emphasize?",
                    "What format is preferred for final deliverables?"
                ],
                "required": True
            }
        }
        
        return {
            "sections": questions,
            "purpose": "Before beginning the SWOT analysis, gather the following critical information:",
            "total_sections": len(questions)
        }
    
    def _get_default_swot_questions(self) -> Dict[str, Any]:
        """Fallback questions if file loading fails."""
        return {
            "sections": {
                "business_organization_context": {
                    "title": "Business/Organization Context",
                    "questions": ["What is the name and primary industry of the organization being analyzed?"],
                    "required": True
                }
            },
            "purpose": "Gather critical information for SWOT analysis",
            "total_sections": 1
        }
    
    def get_instruction(self) -> str:
        """Get the agent's instruction prompt."""
        return f"""
You are the {self.agent_role}, a specialized agent in the multi-agent research team.

PRIMARY FUNCTION: Gather comprehensive SWOT analysis assessment information before beginning SWOT analysis.

CORE RESPONSIBILITY: Collect all necessary context to ensure comprehensive and targeted SWOT analysis.

SWOT ASSESSMENT QUESTION SECTIONS:
{self._format_questions_for_instruction()}

CRITICAL REQUIREMENTS:
1. COMPREHENSIVE CONTEXT: Gather all necessary organizational and strategic context
2. SCOPE DEFINITION: Clearly define the scope and boundaries of the SWOT analysis
3. STAKEHOLDER ALIGNMENT: Understand audience needs and deliverable requirements
4. STRATEGIC FOCUS: Identify key strategic decisions the analysis will inform

OUTPUT FORMAT: Provide responses in structured JSON format with clear section organization.
"""
    
    def _format_questions_for_instruction(self) -> str:
        """Format questions for inclusion in the instruction prompt."""
        formatted = ""
        for section_id, section_data in self.swot_questions["sections"].items():
            formatted += f"\n{section_data['title']}:\n"
            for i, question in enumerate(section_data['questions'], 1):
                formatted += f"  {i}. {question}\n"
        return formatted
    
    def conduct_swot_assessment(self, user_responses: Dict[str, Any]) -> Dict[str, Any]:
        """
        Conduct the SWOT assessment based on user responses.
        
        Args:
            user_responses: Dictionary containing user responses to SWOT assessment questions
            
        Returns:
            Dictionary containing assessment results and validation status
        """
        try:
            print(f">>> {self.agent_name}: Conducting SWOT assessment...", flush=True)
            
            # Validate completeness
            validation_result = self._validate_responses(user_responses)
            
            if not validation_result["is_complete"]:
                return {
                    "status": "incomplete",
                    "message": "SWOT assessment incomplete - missing required sections",
                    "missing_sections": validation_result["missing_sections"],
                    "validation_details": validation_result
                }
            
            # Process and structure the responses
            structured_responses = self._structure_responses(user_responses)
            
            # Generate assessment summary
            assessment_summary = self._generate_assessment_summary(structured_responses)
            
            print(f">>> {self.agent_name}: SWOT assessment completed successfully", flush=True)
            
            return {
                "status": "complete",
                "swot_context": structured_responses,
                "assessment_summary": assessment_summary,
                "validation_result": validation_result,
                "timestamp": datetime.now().isoformat(),
                "agent": self.agent_name
            }
            
        except Exception as e:
            print(f">>> {self.agent_name}: Error in SWOT assessment: {e}", flush=True)
            return {
                "status": "error",
                "error": str(e),
                "agent": self.agent_name
            }
    
    def _validate_responses(self, responses: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that all required sections have adequate responses."""
        missing_sections = []
        validation_details = {}
        
        for section_id, section_data in self.swot_questions["sections"].items():
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
            "total_required": len([s for s in self.swot_questions["sections"].values() if s["required"]]),
            "completed": len(self.swot_questions["sections"]) - len(missing_sections)
        }
    
    def _structure_responses(self, responses: Dict[str, Any]) -> Dict[str, Any]:
        """Structure the user responses into a standardized format."""
        structured = {
            "swot_assessment": {
                "business_context": responses.get("business_organization_context", ""),
                "analysis_scope": responses.get("analysis_scope", ""),
                "stakeholder_requirements": responses.get("stakeholder_requirements", "")
            },
            "metadata": {
                "collection_timestamp": datetime.now().isoformat(),
                "agent": self.agent_name,
                "version": "1.0"
            }
        }
        
        return structured
    
    def _generate_assessment_summary(self, structured_responses: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of the SWOT assessment."""
        swot_context = structured_responses["swot_assessment"]
        
        return {
            "organization_defined": "Yes" if swot_context["business_context"] else "No",
            "scope_clarity": "High" if swot_context["analysis_scope"] else "Low",
            "stakeholder_alignment": "Complete" if swot_context["stakeholder_requirements"] else "Incomplete",
            "analysis_readiness": "Ready" if all([
                swot_context["business_context"],
                swot_context["analysis_scope"],
                swot_context["stakeholder_requirements"]
            ]) else "Not Ready"
        }
    
    def get_swot_questions(self) -> Dict[str, Any]:
        """Get the complete set of SWOT assessment questions."""
        return self.swot_questions
    
    def format_questions_for_user(self) -> str:
        """Format questions in a user-friendly format for display."""
        formatted = f"{self.swot_questions['purpose']}\n\n"
        formatted += "SWOT ANALYSIS ASSESSMENT QUESTIONS\n"
        formatted += "=" * 50 + "\n\n"
        
        for section_id, section_data in self.swot_questions["sections"].items():
            formatted += f"{section_data['title']}\n"
            formatted += "-" * len(section_data['title']) + "\n"
            
            for i, question in enumerate(section_data['questions'], 1):
                formatted += f"{i}. {question}\n"
            
            formatted += "\n"
        
        return formatted
