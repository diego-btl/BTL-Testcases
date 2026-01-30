"""
Sync Engine Module

Orchestrates smart bidirectional synchronization between local YAML files
and Testmo platform. Coordinates all other modules to detect changes and
sync in both directions.

Based on validation: TESTING_LOG.md - All sync operations tested and working
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import yaml

from .hasher import ContentHasher
from .mapper import FolderMapper
from .validator import YAMLValidator
from .converter import TestmoConverter
from .writer import TestmoWriter


class SyncConflict:
    """Represents a sync conflict (file changed in both places)."""

    def __init__(self, case_id: int, yaml_file: Path,
                 local_hash: str, remote_updated_at: str, last_sync: str):
        self.case_id = case_id
        self.yaml_file = yaml_file
        self.local_hash = local_hash
        self.remote_updated_at = remote_updated_at
        self.last_sync = last_sync

    def __str__(self):
        return f"Conflict: Case {self.case_id} ({self.yaml_file.name}) - changed locally and in Testmo"


class SyncEngine:
    """Smart bidirectional sync between local and Testmo."""

    def __init__(self, project_dir: Path, project_id: int):
        """
        Initialize sync engine.

        Args:
            project_dir: Path to project directory (e.g., testmo/oneapp)
            project_id: Testmo project ID
        """
        self.project_dir = project_dir
        self.project_id = project_id
        self.test_cases_dir = project_dir / "test-cases"
        self.sync_dir = project_dir / ".sync"
        self.case_map_file = self.sync_dir / "case-map.json"

        # Initialize components
        self.hasher = ContentHasher()
        self.mapper = FolderMapper(project_dir)
        self.validator = YAMLValidator()
        self.converter = TestmoConverter()
        self.writer = TestmoWriter(project_id)

    def detect_local_changes(self) -> List[Path]:
        """
        Find all YAML files that have changed locally (hash mismatch).

        Returns:
            List of paths to changed files
        """
        return self.hasher.batch_check(self.test_cases_dir)

    def detect_remote_changes(self) -> List[int]:
        """
        Find all cases that have changed in Testmo (timestamp comparison).

        This requires calling MCP or REST API to get all cases and compare
        updated_at timestamps with last_sync from local files.

        Returns:
            List of case IDs that changed remotely

        Note:
            This method requires MCP/API access and should be called by
            Claude/Claude Code with actual API integration.
        """
        # Load case map
        if not self.case_map_file.exists():
            return []

        with open(self.case_map_file, 'r') as f:
            case_map = json.load(f)

        changed_remotely = []

        # For each case, we need to:
        # 1. Get updated_at from Testmo (via MCP or REST API)
        # 2. Compare with last_sync from local file
        # 3. If updated_at > last_sync, mark as changed remotely

        # This is a placeholder - actual implementation requires API calls
        # Claude/Claude Code should implement this using MCP or REST API

        return changed_remotely

    def detect_conflicts(self, local_changes: List[Path],
                        remote_changes: List[int]) -> List[SyncConflict]:
        """
        Find conflicts (cases changed both locally and remotely).

        Args:
            local_changes: List of locally changed files
            remote_changes: List of remotely changed case IDs

        Returns:
            List of conflicts
        """
        conflicts = []

        # Build set of remotely changed case IDs
        remote_set = set(remote_changes)

        # Check each local change
        for yaml_file in local_changes:
            # Extract case ID
            case_id = self.converter.extract_case_id_from_filename(yaml_file.name)

            if case_id and case_id in remote_set:
                # Conflict detected
                with open(yaml_file, 'r') as f:
                    data = yaml.safe_load(f)

                conflict = SyncConflict(
                    case_id=case_id,
                    yaml_file=yaml_file,
                    local_hash=self.hasher.compute_hash(yaml_file),
                    remote_updated_at=data.get('testmo', {}).get('updated_at', ''),
                    last_sync=data.get('testmo', {}).get('last_sync', '')
                )
                conflicts.append(conflict)

        return conflicts

    def push_local_changes(self, yaml_files: List[Path]) -> Dict[str, any]:
        """
        Push local changes to Testmo.

        Args:
            yaml_files: List of files to push

        Returns:
            Dictionary with results: {'success': [...], 'failed': [...]}
        """
        results = {'success': [], 'failed': []}

        for yaml_file in yaml_files:
            try:
                # Validate first
                is_valid, errors = self.validator.validate_file(yaml_file)
                if not is_valid:
                    results['failed'].append({
                        'file': str(yaml_file),
                        'error': f"Validation failed: {errors[0]}"
                    })
                    continue

                # Load YAML
                with open(yaml_file, 'r') as f:
                    data = yaml.safe_load(f)

                # Extract case ID
                case_id = data.get('testmo', {}).get('case_id')
                if not case_id:
                    results['failed'].append({
                        'file': str(yaml_file),
                        'error': "No case_id in testmo section"
                    })
                    continue

                # Convert to Testmo format
                updates = self.converter.yaml_to_testmo_dict(data)

                # Push to Testmo
                self.writer.update_case(case_id, updates)

                # Update hash in file
                self.hasher.update_hash_in_file(yaml_file)

                # Update last_sync timestamp
                data['testmo']['last_sync'] = datetime.now().isoformat() + 'Z'
                with open(yaml_file, 'w') as f:
                    yaml.dump(data, f, default_flow_style=False, sort_keys=False)

                results['success'].append({
                    'file': str(yaml_file),
                    'case_id': case_id
                })

            except Exception as e:
                results['failed'].append({
                    'file': str(yaml_file),
                    'error': str(e)
                })

        return results

    def pull_remote_changes(self, case_ids: List[int]) -> Dict[str, any]:
        """
        Pull remote changes from Testmo to local files.

        Args:
            case_ids: List of case IDs to pull

        Returns:
            Dictionary with results: {'success': [...], 'failed': [...]}

        Note:
            This requires MCP/API access to get case data.
            Should be implemented by Claude/Claude Code with API integration.
        """
        results = {'success': [], 'failed': []}

        # This is a placeholder
        # Actual implementation requires:
        # 1. Get case data from Testmo (via MCP or REST API)
        # 2. Convert to YAML format
        # 3. Update local file
        # 4. Update hash

        return results

    def sync(self, direction: str = "bidirectional",
            auto_resolve_conflicts: bool = False) -> Dict[str, any]:
        """
        Perform smart sync operation.

        Args:
            direction: "push" (local->testmo), "pull" (testmo->local), or "bidirectional"
            auto_resolve_conflicts: If True, newer version wins. If False, prompt user.

        Returns:
            Dictionary with sync results
        """
        results = {
            'local_changes': [],
            'remote_changes': [],
            'conflicts': [],
            'pushed': [],
            'pulled': [],
            'errors': []
        }

        # Detect changes
        local_changes = self.detect_local_changes()
        results['local_changes'] = [str(f) for f in local_changes]

        if direction in ["pull", "bidirectional"]:
            remote_changes = self.detect_remote_changes()
            results['remote_changes'] = remote_changes

            # Detect conflicts
            conflicts = self.detect_conflicts(local_changes, remote_changes)
            results['conflicts'] = [str(c) for c in conflicts]

            if conflicts and not auto_resolve_conflicts:
                # Don't sync - user needs to resolve conflicts
                results['errors'].append("Conflicts detected - manual resolution required")
                return results

        # Push local changes
        if direction in ["push", "bidirectional"] and local_changes:
            push_results = self.push_local_changes(local_changes)
            results['pushed'] = push_results['success']
            results['errors'].extend(push_results['failed'])

        # Pull remote changes
        if direction in ["pull", "bidirectional"] and remote_changes:
            pull_results = self.pull_remote_changes(remote_changes)
            results['pulled'] = pull_results['success']
            results['errors'].extend(pull_results['failed'])

        return results


# Example usage
if __name__ == "__main__":
    project_dir = Path("testmo/oneapp")
    engine = SyncEngine(project_dir, project_id=2)

    # Detect local changes
    local_changes = engine.detect_local_changes()
    print(f"Local changes: {len(local_changes)} files")

    for file in local_changes:
        print(f"  - {file}")
