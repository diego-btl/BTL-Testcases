"""
Testmo Reader Module - MCP Wrapper

Provides read operations via Testmo MCP server.
All operations use MCP for reliable auto-pagination and complete data retrieval.

Based on validation: TESTING_LOG.md - MCP gets all 162 folders (REST API only got 100)
Performance: Export 1334 cases in ~1 minute
"""

import os
from typing import List, Dict, Optional, Any
from pathlib import Path


class TestmoReader:
    """Read operations via Testmo MCP server."""

    def __init__(self, project_id: int):
        """
        Initialize reader for a specific project.

        Args:
            project_id: Testmo project ID
        """
        self.project_id = project_id

        # NOTE: MCP operations are called through Claude Desktop
        # This class provides the Python interface but actual MCP calls
        # are executed by Claude/Claude Code when they use these methods

    def get_all_folders(self) -> List[Dict[str, Any]]:
        """
        Get ALL folders in the project with auto-pagination.

        Returns:
            List of folder dictionaries with structure:
            {
                'id': int,
                'name': str,
                'parent_id': Optional[int],
                'level': int,
                'path': str  # Computed from hierarchy
            }

        Note:
            This must be called via MCP by Claude/Claude Code.
            Direct Python execution will not work without MCP integration.

        Validated:
            - Gets all 162 folders (REST API only got 100)
            - Auto-pagination works correctly
            - Hierarchy up to 4 levels deep
        """
        # This is a placeholder that documents the MCP interface
        # Actual implementation requires MCP server call
        raise NotImplementedError(
            "This method requires MCP execution via Claude/Claude Code. "
            "Use the testmo MCP tool: list_folders with project_id."
        )

    def get_all_cases(self) -> List[Dict[str, Any]]:
        """
        Get ALL test cases in the project with auto-pagination.

        Returns:
            List of case dictionaries with complete Testmo data

        Note:
            This must be called via MCP by Claude/Claude Code.

        Validated:
            - Gets all 1334 cases successfully
            - Auto-pagination handles large datasets
            - Performance: ~1 minute for 1334 cases
        """
        raise NotImplementedError(
            "This method requires MCP execution via Claude/Claude Code. "
            "Use the testmo MCP tool: get_all_cases with project_id."
        )

    def get_case(self, case_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a single test case by ID.

        Args:
            case_id: Testmo case ID

        Returns:
            Case dictionary or None if not found

        Note:
            MCP has a known bug with get_case (404 errors).
            Use get_all_cases and filter instead, or use REST API.

        Known Issue:
            testmo_get_case has 404 bug (documented in TESTING_LOG.md)
            Workaround: Use REST API GET /cases/{id} instead
        """
        raise NotImplementedError(
            "MCP get_case has known 404 bug. "
            "Use REST API: GET /api/v1/projects/{project_id}/cases/{case_id}"
        )

    @staticmethod
    def mcp_interface_guide() -> str:
        """
        Return guide for Claude/Claude Code on how to use MCP for reads.

        Returns:
            String with MCP usage instructions
        """
        return """
# Testmo MCP Read Operations Guide

When implementing read operations, Claude/Claude Code should:

1. **List ALL Folders:**
   - Use MCP tool: testmo.list_folders
   - Parameters: project_id={project_id}
   - Returns: All folders with auto-pagination
   - Validated: Gets all 162 folders correctly

2. **Get ALL Cases:**
   - Use MCP tool: testmo.get_all_cases
   - Parameters: project_id={project_id}
   - Returns: All cases with auto-pagination
   - Performance: 1334 cases in ~1 minute

3. **Get Single Case:**
   - ⚠️ MCP has bug - use REST API instead
   - REST: GET /api/v1/projects/{project_id}/cases/{case_id}
   - Include headers: X-API-Key, Content-Type

4. **Build Folder Hierarchy:**
   - After getting folders, compute paths from parent_id relationships
   - Create folder path like: "home/charge/v2l-vehicle-to-load"
   - Store in FolderMapper for fast lookups

Example MCP Usage (pseudocode):
```
folders = mcp.call("testmo.list_folders", project_id=2)
cases = mcp.call("testmo.get_all_cases", project_id=2)
```

See TESTING_LOG.md for validation details.
"""


# Example usage notes for Claude/Claude Code
class MCPUsageExample:
    """
    Example of how Claude/Claude Code should use MCP for export.

    This is NOT executable Python - it's a guide for AI agents.
    """

    @staticmethod
    def export_workflow_example():
        """
        Example workflow for exporting test cases using MCP.

        Claude/Claude Code should follow this pattern:

        1. Call MCP to get folders
        2. Build folder hierarchy and mappings
        3. Call MCP to get all cases
        4. Convert each case to YAML
        5. Compute hashes
        6. Write files to disk
        7. Save metadata (.sync/ files)
        """
        return """
# Export Workflow Using MCP

Step 1: Get Folders (MCP)
--------------------------
folders = testmo.list_folders(project_id=2)
# Returns: 162 folders with id, name, parent_id

Step 2: Build Hierarchy
-----------------------
mapper = FolderMapper(project_dir)
for folder in folders:
    path = compute_path_from_parents(folder, folders)
    ui_name = compute_ui_name(folder, folders)
    mapper.add_folder(
        folder_id=folder['id'],
        path=path,
        ui_name=ui_name,
        parent_id=folder.get('parent_id'),
        level=compute_level(folder, folders)
    )
mapper.save_mappings()

Step 3: Get All Cases (MCP)
---------------------------
cases = testmo.get_all_cases(project_id=2)
# Returns: 1334 cases with complete data

Step 4: Convert and Write
-------------------------
converter = TestmoConverter()
hasher = ContentHasher()

for case in cases:
    # Get folder path
    folder_path = mapper.get_folder_path(case['folder_id'])

    # Convert to YAML
    yaml_content = converter.testmo_to_yaml(case)

    # Compute hash
    hash_value = hasher.compute_hash_from_dict(yaml_content)

    # Add hash to YAML
    yaml_content['testmo']['content_hash'] = hash_value

    # Write file
    filename = f"TC{case['id']}-{slugify(case['name'])}.yml"
    filepath = project_dir / "test-cases" / folder_path / filename
    filepath.parent.mkdir(parents=True, exist_ok=True)

    with open(filepath, 'w') as f:
        yaml.dump(yaml_content, f, default_flow_style=False, sort_keys=False)

Step 5: Save Case Map
---------------------
case_map = {}
for case in cases:
    case_map[str(case['id'])] = {
        'file': str(filepath.relative_to(project_dir)),
        'folder_id': case['folder_id'],
        'content_hash': hash_value,
        'last_modified': datetime.now().isoformat()
    }

with open(project_dir / '.sync' / 'case-map.json', 'w') as f:
    json.dump(case_map, f, indent=2)

Step 6: Update Project Metadata
-------------------------------
project_metadata = {
    'project_id': 2,
    'project_name': 'OneApp',
    'testmo_url': 'https://bethinklabs.testmo.net',
    'last_full_sync': datetime.now().isoformat(),
    'total_cases': len(cases),
    'total_folders': len(folders),
    'version': '1.0'
}

with open(project_dir / '.sync' / 'project.json', 'w') as f:
    json.dump(project_metadata, f, indent=2)

Done! All 1334 cases exported with full hierarchy.
"""


if __name__ == "__main__":
    print(TestmoReader.mcp_interface_guide())
    print("\n" + "="*80 + "\n")
    print(MCPUsageExample.export_workflow_example())
