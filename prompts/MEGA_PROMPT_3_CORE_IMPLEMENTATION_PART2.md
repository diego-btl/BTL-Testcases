# MEGA PROMPT 3: Core Framework Implementation - PART 2

**Continuation of MEGA PROMPT 3 - Part 1**

This is Part 2: Implementing reader.py, writer.py, and converter.py

---

## 📝 IMPLEMENTATION SPECIFICATIONS (Continued)

### **4. reader.py - MCP Read Operations Module**

**Purpose:** Wrapper for Testmo MCP server read operations

**Key Requirements:**
- Use MCP for all read operations
- Auto-pagination (162 folders, 1334 cases)
- Clean Python interface
- Error handling

**Implementation:**

```python
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
```

---

### **5. writer.py - REST API Write Operations Module**

**Purpose:** Wrapper for Testmo REST API write operations

**Key Requirements:**
- Use REST API for all write operations (MCP has bugs)
- Support individual and batch operations
- Handle hybrid approach for batch updates
- Proper error handling

**Implementation:**

```python
"""
Testmo Writer Module - REST API Wrapper

Provides write operations via Testmo REST API.
All operations use REST API because MCP has known bugs in update_case.

Based on validation: TESTING_LOG.md
- Individual update: ~223ms per case (PATCH)
- Batch update: Hybrid approach (common fields batch, unique fields individual)
- Individual create: ~150ms + ID sync (POST)
- Batch create: ~393ms for 5 cases (true batch, 3.3x faster)
"""

import os
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime


class TestmoWriter:
    """Write operations via Testmo REST API."""
    
    def __init__(self, project_id: int, api_key: Optional[str] = None, 
                 instance: str = "bethinklabs"):
        """
        Initialize writer for a specific project.
        
        Args:
            project_id: Testmo project ID
            api_key: Testmo API key (or None to read from env)
            instance: Testmo instance name (default: bethinklabs)
        """
        self.project_id = project_id
        self.api_key = api_key or os.getenv('TESTMO_API_KEY')
        self.instance = instance
        self.base_url = f"https://{instance}.testmo.net/api/v1"
        
        if not self.api_key:
            raise ValueError("TESTMO_API_KEY not set in environment or provided")
        
        self.headers = {
            'X-API-Key': self.api_key,
            'Content-Type': 'application/json'
        }
    
    def update_case(self, case_id: int, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a single test case.
        
        Args:
            case_id: Testmo case ID
            updates: Dictionary of fields to update
                   Example: {'name': 'New Name', 'custom_notes': 'Updated notes'}
        
        Returns:
            Updated case data from API
            
        Raises:
            requests.HTTPError: If API request fails
            
        Performance:
            Validated: ~223ms per case
        """
        url = f"{self.base_url}/projects/{self.project_id}/cases"
        
        payload = {
            'ids': [case_id],
            **updates
        }
        
        response = requests.patch(url, headers=self.headers, json=payload)
        response.raise_for_status()
        
        return response.json()
    
    def update_cases_batch(self, case_ids: List[int], 
                          common_updates: Dict[str, Any],
                          individual_updates: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """
        Update multiple test cases using hybrid approach.
        
        Hybrid approach:
        - Common fields (priority, status, tags, notes): Single batch PATCH
        - Unique fields (name, description): Individual PATCH calls
        
        Args:
            case_ids: List of case IDs to update
            common_updates: Fields with same value for all cases
                          Example: {'custom_notes': 'Sprint 5'}
            individual_updates: List of dicts with unique updates per case
                              Must match order of case_ids
                              Example: [{'name': 'Test 1'}, {'name': 'Test 2'}]
        
        Returns:
            List of update results
            
        Performance:
            Validated: ~1.5s for 5 cases with hybrid approach
            - Batch (common fields): 264ms for 5 cases (53ms per case)
            - Individual (unique fields): 1193ms for 5 cases (239ms per case)
        """
        results = []
        
        # Step 1: Batch update common fields (if any)
        if common_updates:
            url = f"{self.base_url}/projects/{self.project_id}/cases"
            payload = {
                'ids': case_ids,
                **common_updates
            }
            
            response = requests.patch(url, headers=self.headers, json=payload)
            response.raise_for_status()
            results.append(response.json())
        
        # Step 2: Individual updates for unique fields (if any)
        if individual_updates:
            if len(individual_updates) != len(case_ids):
                raise ValueError("individual_updates must match length of case_ids")
            
            for case_id, updates in zip(case_ids, individual_updates):
                if updates:  # Only update if there are changes
                    result = self.update_case(case_id, updates)
                    results.append(result)
        
        return results
    
    def create_case(self, folder_id: int, case_data: Dict[str, Any]) -> int:
        """
        Create a single test case.
        
        Args:
            folder_id: Testmo folder ID where case will be created
            case_data: Case data dictionary
                      Example: {
                          'name': 'Test Case Name',
                          'description': 'Test description',
                          'custom_steps': [...],
                          'custom_priority': 'medium',
                          'custom_tags': ['tag1', 'tag2']
                      }
        
        Returns:
            New case ID
            
        Raises:
            requests.HTTPError: If API request fails
            
        Performance:
            Validated: ~150ms per case
        """
        url = f"{self.base_url}/projects/{self.project_id}/cases"
        
        # Batch format is required even for single case
        payload = {
            'cases': [{
                'folder_id': folder_id,
                **case_data
            }]
        }
        
        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()
        
        result = response.json()
        # Extract case ID from response
        return result[0]['id']
    
    def create_cases_batch(self, cases: List[Dict[str, Any]]) -> List[int]:
        """
        Create multiple test cases in a single batch operation.
        
        Args:
            cases: List of case data dictionaries, each must include folder_id
                  Example: [
                      {
                          'folder_id': 7338,
                          'name': 'Test 1',
                          'description': 'Description 1',
                          ...
                      },
                      {
                          'folder_id': 7338,
                          'name': 'Test 2',
                          'description': 'Description 2',
                          ...
                      }
                  ]
        
        Returns:
            List of new case IDs in same order as input
            
        Performance:
            Validated: ~393ms for 5 cases (79ms per case)
            - 3.3x faster than individual creates
            - True batch operation (same timestamp proves atomic)
            
        Scaling:
            - 10 cases: ~456ms
            - 50 cases: ~2.3s
            - 100 cases: ~4.6s (likely API limit)
        """
        url = f"{self.base_url}/projects/{self.project_id}/cases"
        
        payload = {'cases': cases}
        
        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()
        
        result = response.json()
        
        # Extract case IDs in order
        case_ids = [case['id'] for case in result]
        
        return case_ids
    
    def get_case(self, case_id: int) -> Dict[str, Any]:
        """
        Get a single case via REST API (for verification).
        
        This is a read operation but included here because MCP get_case has bugs.
        
        Args:
            case_id: Testmo case ID
            
        Returns:
            Case data dictionary
        """
        url = f"{self.base_url}/projects/{self.project_id}/cases/{case_id}"
        
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        
        return response.json()


# Example usage
if __name__ == "__main__":
    import sys
    
    # Example: Update a single case
    if len(sys.argv) >= 3 and sys.argv[1] == "update":
        case_id = int(sys.argv[2])
        
        writer = TestmoWriter(project_id=2)
        
        result = writer.update_case(
            case_id=case_id,
            updates={
                'custom_notes': f'Updated via writer.py at {datetime.now().isoformat()}'
            }
        )
        
        print(f"✓ Case {case_id} updated")
        print(f"Response: {result}")
    
    # Example: Create a new case
    elif len(sys.argv) >= 2 and sys.argv[1] == "create":
        writer = TestmoWriter(project_id=2)
        
        new_id = writer.create_case(
            folder_id=7338,  # V2L folder
            case_data={
                'name': 'Test Case from writer.py',
                'description': 'Created via REST API',
                'custom_priority': 'low',
                'custom_tags': ['test', 'api']
            }
        )
        
        print(f"✓ Case created with ID: {new_id}")
    
    else:
        print("Usage:")
        print("  python writer.py update <case_id>")
        print("  python writer.py create")
```

---

### **6. converter.py - Format Conversion Module**

**Purpose:** Convert between Testmo API format and YAML format

**Key Requirements:**
- Bidirectional conversion
- Handle all field mappings
- Preserve data integrity
- Support partial updates

**Implementation:**

```python
"""
Format Conversion Module

Converts between Testmo API format and YAML file format.
Handles all field mappings and data transformations.

Based on: docs/YAML_FORMAT.md specification
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import re


class TestmoConverter:
    """Convert between Testmo API format and YAML format."""
    
    # Field mapping: YAML path -> Testmo API field
    FIELD_MAP = {
        'metadata.name': 'name',
        'metadata.priority': 'custom_priority',
        'metadata.type': 'custom_type',
        'metadata.status': 'state',
        'metadata.estimate': 'estimate',
        'metadata.automation': 'custom_automation',
        'metadata.tags': 'custom_tags',
        'test_case.description': 'description',
        'test_case.preconditions': 'custom_preconditions',
        'test_case.steps': 'custom_steps',
        'test_case.configurations': 'custom_configurations',
        'test_case.notes': 'custom_notes'
    }
    
    @staticmethod
    def testmo_to_yaml(case: Dict[str, Any], folder_path: str = "", 
                      folder_name_ui: str = "") -> Dict[str, Any]:
        """
        Convert Testmo API case format to YAML dictionary.
        
        Args:
            case: Case data from Testmo API
            folder_path: Local folder path (e.g., "home/charge/v2l")
            folder_name_ui: UI folder name (e.g., "Home / Charge / V2L")
            
        Returns:
            Dictionary ready to be written as YAML
        """
        yaml_data = {
            'testmo': {
                'case_id': case['id'],
                'folder_id': case.get('folder_id'),
                'project_id': case.get('project_id'),
                'folder_path': folder_path,
                'folder_name_ui': folder_name_ui,
                'created_at': case.get('created_at'),
                'updated_at': case.get('updated_at'),
                'last_sync': datetime.now().isoformat() + 'Z',
                'url': f"https://bethinklabs.testmo.net/repositories/{case.get('project_id')}/cases/{case['id']}"
                # content_hash will be added by hasher
            },
            'metadata': {
                'name': case.get('name', ''),
                'priority': case.get('custom_priority', 'medium'),
                'type': case.get('custom_type', 'functional'),
                'status': case.get('state', 'active'),
                'estimate': case.get('estimate'),
                'automation': case.get('custom_automation', 'no'),
                'tags': case.get('custom_tags', [])
            },
            'test_case': {
                'description': case.get('description', ''),
                'preconditions': case.get('custom_preconditions', ''),
                'steps': case.get('custom_steps', []),
                'configurations': case.get('custom_configurations', []),
                'notes': case.get('custom_notes', '')
            }
        }
        
        # Remove None values from metadata
        yaml_data['metadata'] = {k: v for k, v in yaml_data['metadata'].items() if v is not None}
        
        # Remove empty strings from test_case
        yaml_data['test_case'] = {k: v for k, v in yaml_data['test_case'].items() 
                                  if v is not None and v != '' and v != []}
        
        return yaml_data
    
    @staticmethod
    def yaml_to_testmo(yaml_file: Path) -> Dict[str, Any]:
        """
        Convert YAML file to Testmo API format.
        
        Args:
            yaml_file: Path to YAML file
            
        Returns:
            Dictionary ready for Testmo API
        """
        with open(yaml_file, 'r') as f:
            data = yaml.safe_load(f)
        
        # Extract editable sections
        metadata = data.get('metadata', {})
        test_case = data.get('test_case', {})
        
        # Convert to Testmo format
        testmo_data = {
            'name': metadata.get('name', ''),
            'custom_priority': metadata.get('priority'),
            'custom_type': metadata.get('type'),
            'state': metadata.get('status'),
            'estimate': metadata.get('estimate'),
            'custom_automation': metadata.get('automation'),
            'custom_tags': metadata.get('tags', []),
            'description': test_case.get('description', ''),
            'custom_preconditions': test_case.get('preconditions', ''),
            'custom_steps': test_case.get('steps', []),
            'custom_configurations': test_case.get('configurations', []),
            'custom_notes': test_case.get('notes', '')
        }
        
        # Remove None values (don't update fields that weren't set)
        testmo_data = {k: v for k, v in testmo_data.items() if v is not None}
        
        return testmo_data
    
    @staticmethod
    def yaml_to_testmo_dict(yaml_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert YAML dictionary to Testmo API format.
        
        Similar to yaml_to_testmo but works with dictionary instead of file.
        
        Args:
            yaml_data: YAML data as dictionary
            
        Returns:
            Dictionary ready for Testmo API
        """
        metadata = yaml_data.get('metadata', {})
        test_case = yaml_data.get('test_case', {})
        
        testmo_data = {
            'name': metadata.get('name', ''),
            'custom_priority': metadata.get('priority'),
            'custom_type': metadata.get('type'),
            'state': metadata.get('status'),
            'estimate': metadata.get('estimate'),
            'custom_automation': metadata.get('automation'),
            'custom_tags': metadata.get('tags', []),
            'description': test_case.get('description', ''),
            'custom_preconditions': test_case.get('preconditions', ''),
            'custom_steps': test_case.get('steps', []),
            'custom_configurations': test_case.get('configurations', []),
            'custom_notes': test_case.get('notes', '')
        }
        
        testmo_data = {k: v for k, v in testmo_data.items() if v is not None}
        
        return testmo_data
    
    @staticmethod
    def slugify(text: str, max_length: int = 50) -> str:
        """
        Convert text to filename-safe slug.
        
        Args:
            text: Text to slugify (e.g., "V2L Screen - Set Minimum SoC")
            max_length: Maximum length of slug
            
        Returns:
            Slug (e.g., "v2l-screen-set-minimum-soc")
        """
        # Convert to lowercase
        slug = text.lower()
        
        # Replace spaces and special chars with hyphens
        slug = re.sub(r'[^a-z0-9]+', '-', slug)
        
        # Remove leading/trailing hyphens
        slug = slug.strip('-')
        
        # Truncate to max length
        if len(slug) > max_length:
            slug = slug[:max_length].rsplit('-', 1)[0]
        
        return slug
    
    @staticmethod
    def generate_filename(case_id: int, name: str) -> str:
        """
        Generate filename for a test case.
        
        Args:
            case_id: Testmo case ID
            name: Case name
            
        Returns:
            Filename (e.g., "TC66186-v2l-screen-set-minimum-soc.yml")
        """
        slug = TestmoConverter.slugify(name)
        return f"TC{case_id}-{slug}.yml"
    
    @staticmethod
    def extract_case_id_from_filename(filename: str) -> Optional[int]:
        """
        Extract case ID from filename.
        
        Args:
            filename: Filename (e.g., "TC66186-v2l-screen.yml")
            
        Returns:
            Case ID or None if not found
        """
        match = re.match(r'TC(\d+)-', filename)
        if match:
            return int(match.group(1))
        return None


# Example usage
if __name__ == "__main__":
    # Example: Convert Testmo case to YAML
    testmo_case = {
        'id': 66186,
        'name': 'V2L Screen - Set Minimum SoC',
        'folder_id': 7338,
        'project_id': 2,
        'custom_priority': 'medium',
        'custom_tags': ['v2l', 'charge'],
        'description': 'Test V2L screen functionality',
        'custom_steps': [
            {'step': 'Navigate to V2L screen', 'expected': 'Screen loads'}
        ],
        'created_at': '2023-08-01T23:08:19Z',
        'updated_at': '2025-02-06T18:11:36Z'
    }
    
    yaml_data = TestmoConverter.testmo_to_yaml(
        testmo_case,
        folder_path="home/charge/v2l-vehicle-to-load",
        folder_name_ui="Home / Charge / V2L Vehicle to Load"
    )
    
    print("YAML Data:")
    print(yaml.dump(yaml_data, default_flow_style=False, sort_keys=False))
    
    print("\nFilename:")
    print(TestmoConverter.generate_filename(66186, "V2L Screen - Set Minimum SoC"))
```

---

## 📊 PART 2 COMPLETE

**Modules Implemented:**
- ✅ reader.py - MCP wrapper with usage guide
- ✅ writer.py - REST API wrapper (update, create, batch)
- ✅ converter.py - Bidirectional format conversion

**Next: PART 3**
- sync_engine.py - Smart bidirectional sync
- btl_testmo.py - Complete CLI implementation
- Tests and verification

**Status:** 3/8 modules complete (37%)

Would you like me to create PART 3 now?
