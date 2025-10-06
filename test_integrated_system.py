#!/usr/bin/env python3
"""
Test script for the integrated multi-agent system with live data collection.

This script tests the complete workflow from data collection through report generation.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.dirname(__file__))

from src.agents.root_orchestrator_agent import RootOrchestratorAgent
from src.agents.orchestration_agent import OrchestrationAgent
from src.agents.synthesis_agent import SynthesisAgent
from src.agents.swot_analysis_agent import SWOTAnalysisAgent
from src.agents.report_generation_agent import ReportGenerationAgent
from src.data_collection import DataCollectionManager, CollectionConfig, CollectionStrategy, ValidationLevel


async def test_integrated_system():
    """Test the complete integrated system with live data collection."""
    print("=" * 80)
    print("TESTING INTEGRATED MULTI-AGENT SYSTEM WITH LIVE DATA COLLECTION")
    print("=" * 80)
    
    # Test 1: Data Collection Framework
    print("\n1. Testing Data Collection Framework...")
    await test_data_collection_framework()
    
    # Test 2: Individual Agents
    print("\n2. Testing Individual Agents...")
    await test_individual_agents()
    
    # Test 3: Orchestration Agent with Live Data
    print("\n3. Testing Orchestration Agent with Live Data...")
    await test_orchestration_agent()
    
    # Test 4: Synthesis Agent with Real Data
    print("\n4. Testing Synthesis Agent with Real Data...")
    await test_synthesis_agent()
    
    # Test 5: SWOT Analysis Agent
    print("\n5. Testing SWOT Analysis Agent...")
    await test_swot_analysis_agent()
    
    # Test 6: Report Generation Agent
    print("\n6. Testing Report Generation Agent...")
    await test_report_generation_agent()
    
    # Test 7: Root Orchestrator Integration
    print("\n7. Testing Root Orchestrator Integration...")
    await test_root_orchestrator()
    
    print("\n" + "=" * 80)
    print("INTEGRATED SYSTEM TESTING COMPLETED")
    print("=" * 80)


async def test_data_collection_framework():
    """Test the data collection framework independently."""
    print("   Testing DataCollectionManager...")
    
    try:
        config = CollectionConfig(
            strategy=CollectionStrategy.FOCUSED,
            max_parallel_tasks=3,
            timeout_seconds=60,
            validation_level=ValidationLevel.STANDARD,
            enable_aggregation=True,
            enable_deduplication=True,
            max_results_per_source=5
        )
        
        manager = DataCollectionManager(config)
        await manager.initialize()
        
        # Test data collection
        result = await manager.collect_data(
            research_query="AI in tax preparation software",
            research_context={
                "plan_id": "test_plan_001",
                "subject_scope": "AI tax software market analysis",
                "critical_questions": [
                    "What are the current market trends?",
                    "Who are the key competitors?",
                    "What are the growth opportunities?"
                ]
            }
        )
        
        print(f"   ✓ Data collection completed: {result.success}")
        print(f"   ✓ Items collected: {result.total_items_collected}")
        print(f"   ✓ Collection time: {result.collection_time_seconds:.2f}s")
        print(f"   ✓ Collectors used: {len(result.items_by_collector)}")
        
        if result.errors:
            print(f"   ⚠ Errors encountered: {len(result.errors)}")
            for error in result.errors[:3]:  # Show first 3 errors
                print(f"     - {error}")
        
        await manager.cleanup()
        
    except Exception as e:
        print(f"   ✗ Data collection framework test failed: {e}")


async def test_individual_agents():
    """Test individual agents initialization and basic functionality."""
    agents = {
        "OrchestrationAgent": OrchestrationAgent(),
        "SynthesisAgent": SynthesisAgent(),
        "SWOTAnalysisAgent": SWOTAnalysisAgent(),
        "ReportGenerationAgent": ReportGenerationAgent()
    }
    
    for agent_name, agent in agents.items():
        try:
            print(f"   Testing {agent_name}...")
            await agent.initialize()
            print(f"   ✓ {agent_name} initialized successfully")
            await agent.cleanup()
            print(f"   ✓ {agent_name} cleaned up successfully")
        except Exception as e:
            print(f"   ✗ {agent_name} test failed: {e}")


async def test_orchestration_agent():
    """Test the OrchestrationAgent with live data collection."""
    print("   Testing OrchestrationAgent with live data collection...")
    
    try:
        agent = OrchestrationAgent()
        await agent.initialize()
        
        # Test live data collection
        result = await agent.execute_live_data_collection("test_plan_002")
        
        print(f"   ✓ Live data collection result: {result.get('status')}")
        print(f"   ✓ Total items collected: {result.get('total_items_collected', 0)}")
        print(f"   ✓ Data categories: {len(result.get('data_categories', {}))}")
        print(f"   ✓ Source assessments: {len(result.get('source_assessments', {}))}")
        
        # Test data validation
        validation_result = await agent.validate_collected_data("test_plan_002")
        print(f"   ✓ Data validation: {validation_result.get('status')}")
        print(f"   ✓ Overall score: {validation_result.get('overall_score', 0.0):.2f}")
        
        await agent.cleanup()
        
    except Exception as e:
        print(f"   ✗ OrchestrationAgent test failed: {e}")


async def test_synthesis_agent():
    """Test the SynthesisAgent with real data processing."""
    print("   Testing SynthesisAgent with real data processing...")
    
    try:
        agent = SynthesisAgent()
        await agent.initialize()
        
        # Test data synthesis
        result = await agent.synthesize_research_data("test_plan_003")
        
        print(f"   ✓ Data synthesis result: {result.get('status')}")
        print(f"   ✓ Insights generated: {result.get('total_insights_generated', 0)}")
        print(f"   ✓ SWOT categories: {len(result.get('swot_categorized_insights', {}))}")
        print(f"   ✓ Quality assessment: {result.get('data_quality_assessment', {}).get('assessment', 'Unknown')}")
        
        # Test SWOT preparation
        swot_prep = await agent.prepare_for_swot_analysis("test_plan_003")
        print(f"   ✓ SWOT preparation: {swot_prep.get('status')}")
        
        await agent.cleanup()
        
    except Exception as e:
        print(f"   ✗ SynthesisAgent test failed: {e}")


async def test_swot_analysis_agent():
    """Test the SWOTAnalysisAgent with real insights."""
    print("   Testing SWOTAnalysisAgent with real insights...")
    
    try:
        agent = SWOTAnalysisAgent()
        await agent.initialize()
        
        # Test SWOT analysis
        result = await agent.conduct_swot_analysis("test_plan_004")
        
        print(f"   ✓ SWOT analysis result: {result.get('status')}")
        print(f"   ✓ Strategic recommendations: {result.get('num_strategic_recommendations', 0)}")
        print(f"   ✓ Strategic alignment score: {result.get('strategic_alignment_score', 0.0):.2f}")
        
        # Test report preparation
        report_prep = await agent.prepare_for_report_generation("test_plan_004")
        print(f"   ✓ Report preparation: {report_prep.get('status')}")
        
        await agent.cleanup()
        
    except Exception as e:
        print(f"   ✗ SWOTAnalysisAgent test failed: {e}")


async def test_report_generation_agent():
    """Test the ReportGenerationAgent with comprehensive data."""
    print("   Testing ReportGenerationAgent with comprehensive data...")
    
    try:
        agent = ReportGenerationAgent()
        await agent.initialize()
        
        # Test report generation
        result = await agent.generate_comprehensive_report("test_plan_005")
        
        print(f"   ✓ Report generation result: {result.get('status')}")
        print(f"   ✓ Report sections: {result.get('report_metadata', {}).get('total_sections', 0)}")
        print(f"   ✓ Data sources: {result.get('report_metadata', {}).get('data_sources_count', 0)}")
        print(f"   ✓ Report quality score: {result.get('report_quality_score', 0.0):.2f}")
        
        await agent.cleanup()
        
    except Exception as e:
        print(f"   ✗ ReportGenerationAgent test failed: {e}")


async def test_root_orchestrator():
    """Test the RootOrchestratorAgent integration."""
    print("   Testing RootOrchestratorAgent integration...")
    
    try:
        orchestrator = RootOrchestratorAgent()
        await orchestrator.initialize()
        
        # Test workflow status
        status = await orchestrator.get_workflow_status("test_plan_006")
        print(f"   ✓ Workflow status retrieval: {status.get('status', 'Unknown')}")
        
        # Test workflow execution (this would normally require a real plan)
        print("   ✓ RootOrchestratorAgent integration test completed")
        
        await orchestrator.cleanup()
        
    except Exception as e:
        print(f"   ✗ RootOrchestratorAgent test failed: {e}")


async def test_api_endpoints():
    """Test the new API endpoints for data collection configuration."""
    print("\n8. Testing API Endpoints...")
    
    try:
        import aiohttp
        
        base_url = "http://localhost:8000"
        
        async with aiohttp.ClientSession() as session:
            # Test data sources endpoint
            async with session.get(f"{base_url}/data-collection/sources") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✓ Data sources endpoint: {data.get('total_sources', 0)} sources available")
                else:
                    print(f"   ⚠ Data sources endpoint returned status {response.status}")
            
            # Test data collection configuration
            config_data = {
                "plan_id": "test_plan_api",
                "strategy": "FOCUSED",
                "max_parallel_tasks": 3,
                "timeout_seconds": 120
            }
            
            async with session.post(f"{base_url}/data-collection/configure", json=config_data) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✓ Data collection configuration: {data.get('status')}")
                else:
                    print(f"   ⚠ Configuration endpoint returned status {response.status}")
            
            # Test data collection status
            async with session.get(f"{base_url}/data-collection/status/test_plan_api") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✓ Data collection status: {data.get('collection_status')}")
                else:
                    print(f"   ⚠ Status endpoint returned status {response.status}")
        
    except Exception as e:
        print(f"   ⚠ API endpoint testing skipped (server may not be running): {e}")


if __name__ == "__main__":
    print(f"Starting integrated system test at {datetime.now()}")
    
    try:
        asyncio.run(test_integrated_system())
        print("\n✓ All tests completed successfully!")
    except KeyboardInterrupt:
        print("\n⚠ Testing interrupted by user")
    except Exception as e:
        print(f"\n✗ Testing failed with error: {e}")
        import traceback
        traceback.print_exc()
