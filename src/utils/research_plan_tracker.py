"""
Research Plan Tracker - Manages research plans as to-do lists with progress tracking.

This module implements a research plan system that works like a to-do list,
tracking progress and updating status as tasks are completed, similar to how
AI assistants work with task management.
"""

import json
import os
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, asdict


class TaskStatus(Enum):
    """Status of individual research tasks."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


class PlanStatus(Enum):
    """Status of the overall research plan."""
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    PAUSED = "paused"
    CANCELLED = "cancelled"


@dataclass
class ResearchTask:
    """Individual research task within a plan."""
    id: str
    title: str
    description: str
    status: TaskStatus
    priority: int  # 1-5, where 5 is highest priority
    dependencies: List[str]  # List of task IDs this task depends on
    estimated_duration: Optional[int] = None  # Estimated duration in minutes
    actual_duration: Optional[int] = None  # Actual duration in minutes
    assigned_agent: Optional[str] = None
    created_at: str = ""
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    notes: List[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.created_at == "":
            self.created_at = datetime.now().isoformat()
        if self.notes is None:
            self.notes = []
        if self.metadata is None:
            self.metadata = {}


@dataclass
class ResearchPlan:
    """Complete research plan with tasks and progress tracking."""
    id: str
    title: str
    description: str
    status: PlanStatus
    created_at: str
    updated_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    tasks: List[ResearchTask] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.tasks is None:
            self.tasks = []
        if self.metadata is None:
            self.metadata = {}


class ResearchPlanTracker:
    """Manages research plans as to-do lists with progress tracking."""
    
    def __init__(self, storage_dir: str = "data/research_plans"):
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
    
    def create_research_plan(self, title: str, description: str, 
                           research_context: Dict[str, Any]) -> ResearchPlan:
        """
        Create a new research plan based on research context.
        
        Args:
            title: Title of the research plan
            description: Description of the research plan
            research_context: Context from foundation and SWOT questionnaires
            
        Returns:
            Created research plan with initial tasks
        """
        try:
            plan_id = f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Create initial tasks based on research context
            initial_tasks = self._generate_initial_tasks(plan_id, research_context)
            
            plan = ResearchPlan(
                id=plan_id,
                title=title,
                description=description,
                status=PlanStatus.DRAFT,
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
                tasks=initial_tasks,
                metadata={
                    "research_context": research_context,
                    "total_tasks": len(initial_tasks),
                    "completed_tasks": 0,
                    "progress_percentage": 0.0
                }
            )
            
            # Save the plan
            self._save_plan(plan)
            
            print(f">>> ResearchPlanTracker: Created research plan '{title}' with {len(initial_tasks)} initial tasks", flush=True)
            
            return plan
            
        except Exception as e:
            print(f">>> ResearchPlanTracker: Error creating research plan: {e}", flush=True)
            raise
    
    def _generate_initial_tasks(self, plan_id: str, research_context: Dict[str, Any]) -> List[ResearchTask]:
        """Generate initial tasks based on research context."""
        tasks = []
        
        # Extract key information from research context
        foundation_context = research_context.get("foundation_context", {})
        swot_context = research_context.get("swot_context", {})
        
        # Task 1: Research Planning
        tasks.append(ResearchTask(
            id=f"{plan_id}_task_001",
            title="Develop Comprehensive Research Plan",
            description="Create detailed research plan based on foundation context and research objectives",
            status=TaskStatus.PENDING,
            priority=5,
            dependencies=[],
            estimated_duration=30,
            assigned_agent="ResearchPlanAgent",
            metadata={
                "phase": "planning",
                "context_section": "foundation_context"
            }
        ))
        
        # Task 2: Data Collection Planning
        tasks.append(ResearchTask(
            id=f"{plan_id}_task_002",
            title="Plan Data Collection Strategy",
            description="Identify and plan data collection from various sources (academic, financial, news, regulatory)",
            status=TaskStatus.PENDING,
            priority=4,
            dependencies=[f"{plan_id}_task_001"],
            estimated_duration=45,
            assigned_agent="DataCollectionAgent",
            metadata={
                "phase": "planning",
                "context_section": "foundation_context"
            }
        ))
        
        # Task 3: Live Data Collection
        tasks.append(ResearchTask(
            id=f"{plan_id}_task_003",
            title="Execute Live Data Collection",
            description="Collect live data from external APIs, web scraping, and real-time sources",
            status=TaskStatus.PENDING,
            priority=5,
            dependencies=[f"{plan_id}_task_002"],
            estimated_duration=120,
            assigned_agent="DataCollectionAgent",
            metadata={
                "phase": "data_collection",
                "context_section": "foundation_context"
            }
        ))
        
        # Task 4: Data Analysis and Synthesis
        tasks.append(ResearchTask(
            id=f"{plan_id}_task_004",
            title="Analyze and Synthesize Collected Data",
            description="Analyze collected data, identify patterns, and synthesize insights",
            status=TaskStatus.PENDING,
            priority=4,
            dependencies=[f"{plan_id}_task_003"],
            estimated_duration=90,
            assigned_agent="SynthesisAgent",
            metadata={
                "phase": "analysis",
                "context_section": "foundation_context"
            }
        ))
        
        # Task 5: SWOT Analysis
        tasks.append(ResearchTask(
            id=f"{plan_id}_task_005",
            title="Conduct Comprehensive SWOT Analysis",
            description="Perform SWOT analysis based on collected data and organizational context",
            status=TaskStatus.PENDING,
            priority=4,
            dependencies=[f"{plan_id}_task_004"],
            estimated_duration=60,
            assigned_agent="SWOTAnalysisAgent",
            metadata={
                "phase": "analysis",
                "context_section": "swot_context"
            }
        ))
        
        # Task 6: Report Generation
        tasks.append(ResearchTask(
            id=f"{plan_id}_task_006",
            title="Generate Comprehensive Research Report",
            description="Create final research report with findings, analysis, and recommendations",
            status=TaskStatus.PENDING,
            priority=3,
            dependencies=[f"{plan_id}_task_005"],
            estimated_duration=45,
            assigned_agent="ReportGenerationAgent",
            metadata={
                "phase": "reporting",
                "context_section": "foundation_context"
            }
        ))
        
        return tasks
    
    def get_plan(self, plan_id: str) -> Optional[ResearchPlan]:
        """Get a research plan by ID."""
        try:
            file_path = os.path.join(self.storage_dir, f"{plan_id}.json")
            if not os.path.exists(file_path):
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Convert back to ResearchPlan object
            return self._dict_to_plan(data)
            
        except Exception as e:
            print(f">>> ResearchPlanTracker: Error getting plan {plan_id}: {e}", flush=True)
            return None
    
    def update_task_status(self, plan_id: str, task_id: str, 
                          status: TaskStatus, notes: Optional[str] = None) -> bool:
        """
        Update the status of a specific task.
        
        Args:
            plan_id: ID of the research plan
            task_id: ID of the task to update
            status: New status for the task
            notes: Optional notes about the status change
            
        Returns:
            True if successful, False otherwise
        """
        try:
            plan = self.get_plan(plan_id)
            if not plan:
                return False
            
            # Find the task
            task = None
            for t in plan.tasks:
                if t.id == task_id:
                    task = t
                    break
            
            if not task:
                return False
            
            # Update task status
            old_status = task.status
            task.status = status
            
            # Update timestamps
            now = datetime.now().isoformat()
            if status == TaskStatus.IN_PROGRESS and not task.started_at:
                task.started_at = now
            elif status == TaskStatus.COMPLETED and not task.completed_at:
                task.completed_at = now
            
            # Add notes if provided
            if notes:
                task.notes.append(f"[{now}] Status changed from {old_status.value} to {status.value}: {notes}")
            
            # Update plan metadata
            plan.updated_at = now
            self._update_plan_metadata(plan)
            
            # Save the updated plan
            self._save_plan(plan)
            
            print(f">>> ResearchPlanTracker: Updated task {task_id} status from {old_status.value} to {status.value}", flush=True)
            
            return True
            
        except Exception as e:
            print(f">>> ResearchPlanTracker: Error updating task status: {e}", flush=True)
            return False
    
    def add_task_note(self, plan_id: str, task_id: str, note: str) -> bool:
        """Add a note to a specific task."""
        try:
            plan = self.get_plan(plan_id)
            if not plan:
                return False
            
            # Find the task
            task = None
            for t in plan.tasks:
                if t.id == task_id:
                    task = t
                    break
            
            if not task:
                return False
            
            # Add the note
            timestamp = datetime.now().isoformat()
            task.notes.append(f"[{timestamp}] {note}")
            
            # Update plan
            plan.updated_at = timestamp
            self._save_plan(plan)
            
            return True
            
        except Exception as e:
            print(f">>> ResearchPlanTracker: Error adding task note: {e}", flush=True)
            return False
    
    def get_plan_progress(self, plan_id: str) -> Dict[str, Any]:
        """Get progress information for a research plan."""
        try:
            plan = self.get_plan(plan_id)
            if not plan:
                return {"error": "Plan not found"}
            
            total_tasks = len(plan.tasks)
            completed_tasks = len([t for t in plan.tasks if t.status == TaskStatus.COMPLETED])
            in_progress_tasks = len([t for t in plan.tasks if t.status == TaskStatus.IN_PROGRESS])
            pending_tasks = len([t for t in plan.tasks if t.status == TaskStatus.PENDING])
            blocked_tasks = len([t for t in plan.tasks if t.status == TaskStatus.BLOCKED])
            
            progress_percentage = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            
            # Calculate estimated vs actual time
            estimated_total = sum(t.estimated_duration or 0 for t in plan.tasks)
            actual_total = sum(t.actual_duration or 0 for t in plan.tasks)
            
            return {
                "plan_id": plan_id,
                "plan_title": plan.title,
                "plan_status": plan.status.value,
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "in_progress_tasks": in_progress_tasks,
                "pending_tasks": pending_tasks,
                "blocked_tasks": blocked_tasks,
                "progress_percentage": round(progress_percentage, 2),
                "estimated_duration_minutes": estimated_total,
                "actual_duration_minutes": actual_total,
                "created_at": plan.created_at,
                "updated_at": plan.updated_at,
                "started_at": plan.started_at,
                "completed_at": plan.completed_at
            }
            
        except Exception as e:
            print(f">>> ResearchPlanTracker: Error getting plan progress: {e}", flush=True)
            return {"error": str(e)}
    
    def get_next_available_tasks(self, plan_id: str) -> List[ResearchTask]:
        """Get tasks that are ready to be started (dependencies met)."""
        try:
            plan = self.get_plan(plan_id)
            if not plan:
                return []
            
            available_tasks = []
            
            for task in plan.tasks:
                if task.status == TaskStatus.PENDING:
                    # Check if all dependencies are completed
                    dependencies_met = True
                    for dep_id in task.dependencies:
                        dep_task = next((t for t in plan.tasks if t.id == dep_id), None)
                        if not dep_task or dep_task.status != TaskStatus.COMPLETED:
                            dependencies_met = False
                            break
                    
                    if dependencies_met:
                        available_tasks.append(task)
            
            # Sort by priority (highest first)
            available_tasks.sort(key=lambda t: t.priority, reverse=True)
            
            return available_tasks
            
        except Exception as e:
            print(f">>> ResearchPlanTracker: Error getting next available tasks: {e}", flush=True)
            return []
    
    def _save_plan(self, plan: ResearchPlan) -> None:
        """Save a research plan to storage."""
        try:
            file_path = os.path.join(self.storage_dir, f"{plan.id}.json")
            
            # Convert to dictionary
            plan_dict = asdict(plan)
            
            # Convert enums to strings
            plan_dict["status"] = plan.status.value
            for task in plan_dict["tasks"]:
                task["status"] = task["status"].value
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(plan_dict, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f">>> ResearchPlanTracker: Error saving plan: {e}", flush=True)
            raise
    
    def _dict_to_plan(self, data: Dict[str, Any]) -> ResearchPlan:
        """Convert dictionary back to ResearchPlan object."""
        # Convert status enums
        data["status"] = PlanStatus(data["status"])
        
        # Convert task status enums
        for task_data in data["tasks"]:
            task_data["status"] = TaskStatus(task_data["status"])
        
        # Create ResearchTask objects
        tasks = []
        for task_data in data["tasks"]:
            task = ResearchTask(**task_data)
            tasks.append(task)
        
        data["tasks"] = tasks
        
        return ResearchPlan(**data)
    
    def _update_plan_metadata(self, plan: ResearchPlan) -> None:
        """Update plan metadata with current progress."""
        total_tasks = len(plan.tasks)
        completed_tasks = len([t for t in plan.tasks if t.status == TaskStatus.COMPLETED])
        progress_percentage = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        plan.metadata.update({
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "progress_percentage": round(progress_percentage, 2)
        })
        
        # Update plan status based on progress
        if completed_tasks == total_tasks and plan.status != PlanStatus.COMPLETED:
            plan.status = PlanStatus.COMPLETED
            plan.completed_at = datetime.now().isoformat()
        elif completed_tasks > 0 and plan.status == PlanStatus.DRAFT:
            plan.status = PlanStatus.ACTIVE
            if not plan.started_at:
                plan.started_at = datetime.now().isoformat()
