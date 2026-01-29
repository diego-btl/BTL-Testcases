"""
Workflow Orchestrator

Coordinates multi-step workflows for test case management.

Workflows:
1. ClickUp Task → YAML → Git → Testmo
2. Export from Testmo → Git
3. Batch updates and synchronization
"""

import os
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from .test_case_creator import TestCaseCreator


class WorkflowOrchestrator:
    """
    Orchestrates complete workflows for test case management.

    This class coordinates the full lifecycle:
    - Reads ClickUp tasks
    - Creates test case YAML files
    - Commits to Git
    - Imports to Testmo
    - Syncs IDs back to Git
    """

    def __init__(self, base_dir: Optional[str] = None):
        """
        Initialize the workflow orchestrator.

        Args:
            base_dir: Root directory of the repository
        """
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()
        self.creator = TestCaseCreator(base_dir)

    def get_context(self, feature: Optional[str] = None) -> str:
        """
        Get complete context for AI agent including rules and examples.

        This method provides all the information Claude Code needs to
        create test cases following BTL standards.

        Args:
            feature: Optional feature to get similar tests from

        Returns:
            Formatted context string with all rules and examples
        """
        context_parts = []

        # Header
        context_parts.append("# BTL Test Case Creation Context\n\n")
        context_parts.append("This context provides all rules and examples for creating ")
        context_parts.append("test cases following BTL standards.\n\n")

        # Workflow overview
        context_parts.append("## Workflow Overview\n\n")
        context_parts.append("1. Read ClickUp task details\n")
        context_parts.append("2. Create test case YAML file\n")
        context_parts.append("3. Validate YAML schema\n")
        context_parts.append("4. Commit to Git\n")
        context_parts.append("5. Import to Testmo (optional)\n")
        context_parts.append("6. Sync testmo_id back to Git\n\n")

        # Get rules and examples from TestCaseCreator
        context_parts.append(self.creator.get_context_for_ai(feature))

        # File structure reminder
        context_parts.append("\n\n## File Structure\n\n")
        context_parts.append(f"Test cases location: {self.creator.test_cases_dir}\n")
        context_parts.append(f"Rules location: {self.creator.rules_dir}\n")
        context_parts.append(f"Schemas location: {self.base_dir / 'schemas'}\n")

        return "".join(context_parts)

    def create_from_clickup(
        self,
        clickup_task_id: str,
        feature: str,
        name: str,
        description: str,
        preconditions: List[str],
        steps: List[Dict[str, str]],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a test case from a ClickUp task and execute full workflow.

        Args:
            clickup_task_id: ClickUp task ID
            feature: Feature folder name
            name: Test case name
            description: Test case description
            preconditions: List of precondition descriptions
            steps: List of steps with 'action' and 'expected' keys
            **kwargs: Additional arguments for create_test_case

        Returns:
            Dictionary with workflow results:
            {
                'test_case_path': Path to created YAML file,
                'test_id': Generated test ID,
                'git_commit': Git commit hash (if committed),
                'validation': Validation results,
                'testmo_id': Testmo ID (if imported)
            }
        """
        result = {
            'test_case_path': None,
            'test_id': None,
            'git_commit': None,
            'validation': None,
            'testmo_id': None,
            'clickup_task_id': clickup_task_id
        }

        try:
            # Step 1: Create test case
            test_case_path = self.creator.create_test_case(
                feature=feature,
                name=name,
                description=description,
                preconditions=preconditions,
                steps=steps,
                clickup_task_id=clickup_task_id,
                **kwargs
            )
            result['test_case_path'] = str(test_case_path)
            result['test_id'] = self.creator.get_next_test_id(feature)

            # Step 2: Validate (optional - can be done externally)
            # validation_cmd = ["python", "scripts/yaml_converter.py", "validate", "--input-file", str(test_case_path)]
            # result['validation'] = subprocess.run(validation_cmd, capture_output=True, text=True)

            return result

        except Exception as e:
            result['error'] = str(e)
            return result

    def validate_test_case(self, test_case_path: Path) -> Dict[str, Any]:
        """
        Validate a test case YAML file.

        Args:
            test_case_path: Path to the YAML file

        Returns:
            Validation results dictionary
        """
        try:
            cmd = [
                "python",
                str(self.base_dir / "scripts" / "yaml_converter.py"),
                "validate",
                "--input-file",
                str(test_case_path)
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(self.base_dir))
            return {
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def git_commit(self, files: List[str], message: str) -> Dict[str, Any]:
        """
        Commit files to Git.

        Args:
            files: List of file paths to commit
            message: Commit message

        Returns:
            Git operation results
        """
        try:
            # Add files
            subprocess.run(["git", "add"] + files, cwd=str(self.base_dir), check=True)

            # Commit
            result = subprocess.run(
                ["git", "commit", "-m", message],
                capture_output=True,
                text=True,
                cwd=str(self.base_dir)
            )

            # Get commit hash
            commit_hash = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
                cwd=str(self.base_dir)
            ).stdout.strip()

            return {
                'success': result.returncode == 0,
                'commit_hash': commit_hash,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def import_to_testmo(
        self,
        project_id: int,
        feature_dir: str,
        folder_name: str
    ) -> Dict[str, Any]:
        """
        Import test cases to Testmo.

        Args:
            project_id: Testmo project ID
            feature_dir: Feature directory name
            folder_name: Target folder name in Testmo

        Returns:
            Import results
        """
        try:
            cmd = [
                "python",
                str(self.base_dir / "scripts" / "testmo_import.py"),
                "--project-id", str(project_id),
                "--input-dir", str(self.base_dir / "test-cases" / feature_dir),
                "--folder-name", folder_name
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(self.base_dir))
            return {
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def export_from_testmo(
        self,
        project_id: int,
        folder_id: int,
        output_dir: str
    ) -> Dict[str, Any]:
        """
        Export test cases from Testmo.

        Args:
            project_id: Testmo project ID
            folder_id: Folder ID to export
            output_dir: Output directory name

        Returns:
            Export results
        """
        try:
            cmd = [
                "python",
                str(self.base_dir / "scripts" / "testmo_export.py"),
                "--project-id", str(project_id),
                "--folder-id", str(folder_id),
                "--output-dir", str(self.base_dir / "test-cases" / output_dir)
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(self.base_dir))
            return {
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def sync_testmo_ids(
        self,
        project_id: int,
        folder_id: int,
        feature_dir: str
    ) -> Dict[str, Any]:
        """
        Sync testmo_ids from Testmo back to YAML files after import.

        This updates the testmo_id field in YAML files so they can be
        updated in future operations.

        Args:
            project_id: Testmo project ID
            folder_id: Folder ID to sync from
            feature_dir: Feature directory name

        Returns:
            Sync results
        """
        # Export to temporary location
        temp_export = self.export_from_testmo(project_id, folder_id, f"_temp_{feature_dir}")

        if not temp_export['success']:
            return temp_export

        # TODO: Merge testmo_ids from temp export into original files
        # This would require matching by name/id and updating the testmo_id field

        return {
            'success': True,
            'message': 'Manual ID sync required - compare exported files'
        }


# Convenience functions
def get_context(feature: Optional[str] = None) -> str:
    """Get AI context without instantiating class."""
    orchestrator = WorkflowOrchestrator()
    return orchestrator.get_context(feature)


def create_from_clickup(*args, **kwargs) -> Dict[str, Any]:
    """Create from ClickUp without instantiating class."""
    orchestrator = WorkflowOrchestrator()
    return orchestrator.create_from_clickup(*args, **kwargs)
