"""
Test the main research workflow functionality.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from workflows.research_workflow import SecondaryResearchWorkflow
from utils.data_validation import validate_research_request


class TestSecondaryResearchWorkflow:
    """Test class for SecondaryResearchWorkflow."""
    
    @pytest.fixture
    def workflow(self):
        """Create workflow instance for testing."""
        return SecondaryResearchWorkflow()
    
    @pytest.fixture
    def valid_research_request(self):
        """Valid research request for testing."""
        return {
            "topic": "Test AI Tools Market Analysis",
            "objectives": [
                "Analyze market size and growth patterns",
                "Identify key competitive players and positioning",
                "Assess regulatory environment and compliance requirements"
            ],
            "questions": [
                "What is the current total addressable market size?",
                "Who are the top 5 competitors in this space?",
                "What regulatory challenges exist for new market entrants?"
            ]
        }
    
    def test_workflow_initialization(self, workflow):
        """Test workflow initializes correctly."""
        assert workflow.session_service is not None
        assert workflow.orchestrator is not None
        assert workflow.runner is not None
        assert workflow.orchestrator.name == "secondary_research_orchestrator"
    
    @pytest.mark.asyncio
    async def test_execute_research_valid_request(self, workflow, valid_research_request):
        """Test workflow execution with valid request."""
        # Mock the runner's run_async method
        mock_event = MagicMock()
        mock_event.is_final_response.return_value = True
        mock_event.content.parts = [MagicMock()]
        mock_event.content.parts[0].text = "Research completed successfully"
        
        with patch.object(workflow.runner, 'run_async') as mock_run:
            mock_run.return_value = [mock_event].__aiter__()
            
            with patch.object(workflow.session_service, 'create_session') as mock_create:
                mock_session = MagicMock()
                mock_session.session_id = "test_session_123"
                mock_create.return_value = mock_session
                
                with patch.object(workflow.session_service, 'get_session') as mock_get:
                    mock_final_session = MagicMock()
                    mock_final_session.state = {
                        "research_status": "complete",
                        "research_id": "research_test_123"
                    }
                    mock_get.return_value = mock_final_session
                    
                    result = await workflow.execute_research(valid_research_request)
                    
                    assert result["status"] == "complete"
                    assert "research_results" in result
                    assert "session_state" in result
                    assert result["session_state"]["research_status"] == "complete"
    
    @pytest.mark.asyncio
    async def test_execute_research_invalid_request(self, workflow):
        """Test workflow execution with invalid request."""
        invalid_request = {
            "topic": "Too short",  # Too short topic
            "objectives": []  # Empty objectives
        }
        
        result = await workflow.execute_research(invalid_request)
        
        assert result["status"] == "error"
        assert "Invalid research request format" in result["error"]
    
    @pytest.mark.asyncio
    async def test_execute_research_exception_handling(self, workflow, valid_research_request):
        """Test workflow handles exceptions gracefully."""
        with patch.object(workflow.runner, 'run_async') as mock_run:
            mock_run.side_effect = Exception("Test exception")
            
            with patch.object(workflow.session_service, 'create_session') as mock_create:
                mock_session = MagicMock()
                mock_session.session_id = "test_session_123"
                mock_create.return_value = mock_session
                
                result = await workflow.execute_research(valid_research_request)
                
                assert result["status"] == "error"
                assert "Test exception" in result["error"]
                assert "session_id" in result
    
    def test_build_research_query(self, workflow, valid_research_request):
        """Test research query building."""
        query = workflow._build_research_query(valid_research_request)
        
        assert valid_research_request["topic"] in query
        assert "comprehensive secondary research" in query
        assert "Research Objectives:" in query
        assert "Specific Research Questions:" in query
        
        for objective in valid_research_request["objectives"]:
            assert objective in query
        
        for question in valid_research_request["questions"]:
            assert question in query


class TestDataValidation:
    """Test data validation functions."""
    
    def test_validate_valid_request(self, sample_research_request):
        """Test validation of valid research request."""
        assert validate_research_request(sample_research_request) == True
    
    def test_validate_missing_topic(self):
        """Test validation fails for missing topic."""
        request = {
            "objectives": ["Test objective one", "Test objective two"]
        }
        assert validate_research_request(request) == False
    
    def test_validate_missing_objectives(self):
        """Test validation fails for missing objectives."""
        request = {
            "topic": "Test Topic for Research Analysis"
        }
        assert validate_research_request(request) == False
    
    def test_validate_short_topic(self):
        """Test validation fails for too short topic."""
        request = {
            "topic": "Short",
            "objectives": ["Test objective that is long enough"]
        }
        assert validate_research_request(request) == False
    
    def test_validate_empty_objectives(self):
        """Test validation fails for empty objectives list."""
        request = {
            "topic": "Valid Test Topic for Research",
            "objectives": []
        }
        assert validate_research_request(request) == False
    
    def test_validate_short_objectives(self):
        """Test validation fails for too short objectives."""
        request = {
            "topic": "Valid Test Topic for Research",
            "objectives": ["Short", "Another short one"]
        }
        assert validate_research_request(request) == False
    
    def test_validate_invalid_questions_type(self):
        """Test validation fails for invalid questions type."""
        request = {
            "topic": "Valid Test Topic for Research",
            "objectives": ["Valid objective that is long enough"],
            "questions": "Should be a list, not a string"
        }
        assert validate_research_request(request) == False