"""
Questionnaire Processing System - Manages research foundation and SWOT assessment questionnaires.

This module handles the collection, validation, and processing of questionnaire responses
for both the Core Research Foundation and SWOT Analysis Assessment phases.
"""

import json
import os
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from enum import Enum

from src.agents.research_foundation_agent import ResearchFoundationAgent
from src.agents.swot_assessment_agent import SWOTAssessmentAgent


class QuestionnaireType(Enum):
    """Types of questionnaires in the system."""
    FOUNDATION = "foundation"
    SWOT_ASSESSMENT = "swot_assessment"


class QuestionnaireProcessor:
    """Manages questionnaire processing for research foundation and SWOT assessment."""
    
    def __init__(self, storage_dir: str = "data/questionnaires"):
        self.storage_dir = storage_dir
        self.foundation_agent = ResearchFoundationAgent()
        self.swot_agent = SWOTAssessmentAgent()
        
        # Ensure storage directory exists
        os.makedirs(storage_dir, exist_ok=True)
    
    def get_foundation_questions(self) -> Dict[str, Any]:
        """Get the foundation questions for display to user."""
        return self.foundation_agent.get_foundation_questions()
    
    def get_swot_questions(self) -> Dict[str, Any]:
        """Get the SWOT assessment questions for display to user."""
        return self.swot_agent.get_swot_questions()
    
    def format_foundation_questions_for_user(self) -> str:
        """Format foundation questions in user-friendly format."""
        return self.foundation_agent.format_questions_for_user()
    
    def format_swot_questions_for_user(self) -> str:
        """Format SWOT questions in user-friendly format."""
        return self.swot_agent.format_questions_for_user()
    
    def process_foundation_responses(self, session_id: str, responses: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process foundation questionnaire responses.
        
        Args:
            session_id: Unique session identifier
            responses: User responses to foundation questions
            
        Returns:
            Processing result with validation and structured data
        """
        try:
            print(f">>> QuestionnaireProcessor: Processing foundation responses for session {session_id}", flush=True)
            
            # Conduct foundation assessment
            assessment_result = self.foundation_agent.conduct_foundation_assessment(responses)
            
            # Save responses to storage
            self._save_questionnaire_responses(
                session_id, 
                QuestionnaireType.FOUNDATION, 
                responses, 
                assessment_result
            )
            
            return assessment_result
            
        except Exception as e:
            print(f">>> QuestionnaireProcessor: Error processing foundation responses: {e}", flush=True)
            return {
                "status": "error",
                "error": str(e),
                "session_id": session_id,
                "questionnaire_type": QuestionnaireType.FOUNDATION.value
            }
    
    def process_swot_responses(self, session_id: str, responses: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process SWOT assessment questionnaire responses.
        
        Args:
            session_id: Unique session identifier
            responses: User responses to SWOT assessment questions
            
        Returns:
            Processing result with validation and structured data
        """
        try:
            print(f">>> QuestionnaireProcessor: Processing SWOT responses for session {session_id}", flush=True)
            
            # Conduct SWOT assessment
            assessment_result = self.swot_agent.conduct_swot_assessment(responses)
            
            # Save responses to storage
            self._save_questionnaire_responses(
                session_id, 
                QuestionnaireType.SWOT_ASSESSMENT, 
                responses, 
                assessment_result
            )
            
            return assessment_result
            
        except Exception as e:
            print(f">>> QuestionnaireProcessor: Error processing SWOT responses: {e}", flush=True)
            return {
                "status": "error",
                "error": str(e),
                "session_id": session_id,
                "questionnaire_type": QuestionnaireType.SWOT_ASSESSMENT.value
            }
    
    def get_questionnaire_status(self, session_id: str) -> Dict[str, Any]:
        """
        Get the status of questionnaires for a session.
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            Status of both foundation and SWOT questionnaires
        """
        try:
            foundation_file = self._get_questionnaire_file_path(session_id, QuestionnaireType.FOUNDATION)
            swot_file = self._get_questionnaire_file_path(session_id, QuestionnaireType.SWOT_ASSESSMENT)
            
            foundation_complete = os.path.exists(foundation_file)
            swot_complete = os.path.exists(swot_file)
            
            status = {
                "session_id": session_id,
                "foundation_questionnaire": {
                    "completed": foundation_complete,
                    "file_path": foundation_file if foundation_complete else None
                },
                "swot_questionnaire": {
                    "completed": swot_complete,
                    "file_path": swot_file if swot_complete else None
                },
                "overall_status": "complete" if (foundation_complete and swot_complete) else "incomplete",
                "ready_for_research": foundation_complete and swot_complete
            }
            
            return status
            
        except Exception as e:
            print(f">>> QuestionnaireProcessor: Error getting questionnaire status: {e}", flush=True)
            return {
                "session_id": session_id,
                "error": str(e),
                "overall_status": "error"
            }
    
    def get_research_context(self, session_id: str) -> Dict[str, Any]:
        """
        Get the complete research context from both questionnaires.
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            Combined research context from foundation and SWOT assessments
        """
        try:
            foundation_context = self._load_questionnaire_data(session_id, QuestionnaireType.FOUNDATION)
            swot_context = self._load_questionnaire_data(session_id, QuestionnaireType.SWOT_ASSESSMENT)
            
            if not foundation_context or not swot_context:
                return {
                    "status": "incomplete",
                    "message": "Missing questionnaire data",
                    "foundation_available": foundation_context is not None,
                    "swot_available": swot_context is not None
                }
            
            # Combine contexts
            combined_context = {
                "session_id": session_id,
                "foundation_context": foundation_context.get("foundation_context", {}),
                "swot_context": swot_context.get("swot_context", {}),
                "foundation_summary": foundation_context.get("assessment_summary", {}),
                "swot_summary": swot_context.get("assessment_summary", {}),
                "collection_timestamp": datetime.now().isoformat(),
                "status": "complete"
            }
            
            return combined_context
            
        except Exception as e:
            print(f">>> QuestionnaireProcessor: Error getting research context: {e}", flush=True)
            return {
                "status": "error",
                "error": str(e),
                "session_id": session_id
            }
    
    def _save_questionnaire_responses(self, session_id: str, questionnaire_type: QuestionnaireType, 
                                    responses: Dict[str, Any], assessment_result: Dict[str, Any]) -> None:
        """Save questionnaire responses and assessment results to storage."""
        try:
            file_path = self._get_questionnaire_file_path(session_id, questionnaire_type)
            
            data = {
                "session_id": session_id,
                "questionnaire_type": questionnaire_type.value,
                "responses": responses,
                "assessment_result": assessment_result,
                "timestamp": datetime.now().isoformat()
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            print(f">>> QuestionnaireProcessor: Saved {questionnaire_type.value} responses to {file_path}", flush=True)
            
        except Exception as e:
            print(f">>> QuestionnaireProcessor: Error saving questionnaire responses: {e}", flush=True)
            raise
    
    def _load_questionnaire_data(self, session_id: str, questionnaire_type: QuestionnaireType) -> Optional[Dict[str, Any]]:
        """Load questionnaire data from storage."""
        try:
            file_path = self._get_questionnaire_file_path(session_id, questionnaire_type)
            
            if not os.path.exists(file_path):
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return data.get("assessment_result", {})
            
        except Exception as e:
            print(f">>> QuestionnaireProcessor: Error loading questionnaire data: {e}", flush=True)
            return None
    
    def _get_questionnaire_file_path(self, session_id: str, questionnaire_type: QuestionnaireType) -> str:
        """Get the file path for storing questionnaire data."""
        filename = f"{session_id}_{questionnaire_type.value}_responses.json"
        return os.path.join(self.storage_dir, filename)
    
    def validate_research_readiness(self, session_id: str) -> Dict[str, Any]:
        """
        Validate if a session is ready to proceed with research planning.
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            Validation result indicating readiness for research
        """
        try:
            status = self.get_questionnaire_status(session_id)
            
            if status["overall_status"] != "complete":
                return {
                    "ready": False,
                    "reason": "Incomplete questionnaires",
                    "details": status,
                    "next_steps": self._get_next_steps(status)
                }
            
            # Get research context to validate quality
            context = self.get_research_context(session_id)
            
            if context["status"] != "complete":
                return {
                    "ready": False,
                    "reason": "Invalid research context",
                    "details": context
                }
            
            return {
                "ready": True,
                "reason": "All questionnaires completed successfully",
                "context": context,
                "status": status
            }
            
        except Exception as e:
            print(f">>> QuestionnaireProcessor: Error validating research readiness: {e}", flush=True)
            return {
                "ready": False,
                "reason": f"Validation error: {str(e)}",
                "error": str(e)
            }
    
    def _get_next_steps(self, status: Dict[str, Any]) -> List[str]:
        """Get next steps based on questionnaire status."""
        next_steps = []
        
        if not status["foundation_questionnaire"]["completed"]:
            next_steps.append("Complete Foundation Questionnaire")
        
        if not status["swot_questionnaire"]["completed"]:
            next_steps.append("Complete SWOT Assessment Questionnaire")
        
        return next_steps
