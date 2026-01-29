"""
BTL Test Case Agent Framework

AI-powered test case creation and management with Git-first workflow.

This framework enables Claude Code to create test cases following BTL standards
by providing rules, templates, and orchestration for the complete workflow:
ClickUp Task → YAML File → Git → Testmo

Usage:
    from agents import TestCaseCreator, WorkflowOrchestrator

    # Create a test case
    creator = TestCaseCreator()
    creator.create_test_case(
        feature="tesla-pricing",
        clickup_task_id="86b7uey05",
        name="Max Charge Limit Display"
    )

    # Orchestrate full workflow
    orchestrator = WorkflowOrchestrator()
    context = orchestrator.get_context()
"""

from .test_case_creator import TestCaseCreator
from .workflow_orchestrator import WorkflowOrchestrator

__version__ = "1.0.0"
__all__ = ['TestCaseCreator', 'WorkflowOrchestrator']
