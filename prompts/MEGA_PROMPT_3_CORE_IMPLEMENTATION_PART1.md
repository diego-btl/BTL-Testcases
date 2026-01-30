# MEGA PROMPT 3: Core Framework Implementation

**Date:** 2026-01-30
**Phase:** Framework Implementation
**Priority:** CRITICAL
**Estimated Time:** 2-3 hours
**Prerequisites:** MEGA PROMPT 1 & 2 must be complete

---

## 🎯 OBJECTIVE

Implement the complete BTL-TestCases framework based on validated workflows from TESTING_LOG.md. This will transform the placeholder structure into a fully functional, production-ready system.

**What We're Building:**
- Fully functional CLI (`btl_testmo.py`)
- 7 core modules in `testmo_sync/` package
- All operations validated in TESTING_LOG.md
- Production-ready code with error handling
- Basic unit tests

---

## 📋 PREREQUISITES

**Verify Before Starting:**
```bash
# 1. Check MEGA PROMPT 1 & 2 complete
ls -la docs/*.md | wc -l
# Expected: 7+ documentation files

ls -la scripts/testmo_sync/*.py | wc -l
# Expected: 8 placeholder files

# 2. Verify test data exists
cat TESTING_LOG.md | grep "✅ PASS"
# Expected: 5 PASS results

# 3. Check environment
python3 --version
# Expected: Python 3.8+

# 4. Verify dependencies
cat requirements.txt
# Expected: requests, pyyaml, python-dotenv

# 5. Current branch
git branch --show-current
# Expected: feature/repository-restructure or similar
```

**Required Reading:**
- `TESTING_LOG.md` - All validation results (5 tests, 100% pass rate)
- `docs/ARCHITECTURE.md` - Technical design
- `docs/CLI_REFERENCE.md` - Command specifications

---

## 🏗️ IMPLEMENTATION ROADMAP

### **Phase 1: Core Utilities (45 min)**
1. `hasher.py` - Content hashing for change detection
2. `mapper.py` - Path ↔ ID bidirectional mapping
3. `validator.py` - YAML format validation

### **Phase 2: I/O Operations (60 min)**
4. `reader.py` - MCP wrapper for read operations
5. `writer.py` - REST API wrapper for write operations
6. `converter.py` - Testmo ↔ YAML format conversion

### **Phase 3: Sync Engine (45 min)**
7. `sync_engine.py` - Smart bidirectional sync logic

### **Phase 4: CLI Interface (30 min)**
8. `btl_testmo.py` - Complete CLI implementation

### **Phase 5: Tests & Verification (20 min)**
9. Basic unit tests
10. Integration verification

---

## 📝 IMPLEMENTATION SPECIFICATIONS

### **1. hasher.py - Content Hashing Module**

**Purpose:** Compute SHA-256 hashes of YAML editable content for change detection

**Key Requirements:**
- Hash only editable sections (metadata + test_case)
- Ignore testmo section (auto-generated)
- Deterministic serialization (sorted keys)
- Fast computation

**Implementation:**

```python
"""
Content Hashing Module

Provides SHA-256 hashing of YAML test case files for change detection.
Only hashes editable content (metadata + test_case sections), ignoring
auto-generated testmo metadata.

Based on validation: TESTING_LOG.md - Hash-based change detection
"""

import hashlib
import yaml
from pathlib import Path
from typing import Dict, List, Tuple, Optional


class ContentHasher:
    """Compute and verify content hashes for test case YAML files."""
    
    @staticmethod
    def compute_hash(yaml_file: Path) -> str:
        """
        Compute SHA-256 hash of editable content in YAML file.
        
        Only includes:
        - metadata section (editable by users/AI)
        - test_case section (editable by users/AI)
        
        Excludes:
        - testmo section (auto-generated)
        
        Args:
            yaml_file: Path to YAML file
            
        Returns:
            Hash string in format "sha256:abc123..."
            
        Raises:
            FileNotFoundError: If yaml_file doesn't exist
            yaml.YAMLError: If YAML parsing fails
        """
        if not yaml_file.exists():
            raise FileNotFoundError(f"YAML file not found: {yaml_file}")
        
        with open(yaml_file, 'r') as f:
            data = yaml.safe_load(f)
        
        # Extract only editable content
        editable_content = {
            'metadata': data.get('metadata', {}),
            'test_case': data.get('test_case', {})
        }
        
        # Deterministic serialization (sorted keys)
        content_str = yaml.dump(editable_content, sort_keys=True, default_flow_style=False)
        
        # Compute SHA-256 hash
        hash_obj = hashlib.sha256(content_str.encode('utf-8'))
        hash_value = hash_obj.hexdigest()
        
        return f"sha256:{hash_value}"
    
    @staticmethod
    def needs_sync(yaml_file: Path) -> bool:
        """
        Check if file has changed since last sync by comparing hashes.
        
        Args:
            yaml_file: Path to YAML file
            
        Returns:
            True if file has changed (needs sync), False otherwise
        """
        try:
            # Compute current hash
            current_hash = ContentHasher.compute_hash(yaml_file)
            
            # Read saved hash from YAML
            with open(yaml_file, 'r') as f:
                data = yaml.safe_load(f)
            
            saved_hash = data.get('testmo', {}).get('content_hash')
            
            if not saved_hash:
                # No saved hash = new file or needs sync
                return True
            
            return current_hash != saved_hash
            
        except Exception as e:
            # On error, assume needs sync
            print(f"Warning: Error checking sync status for {yaml_file}: {e}")
            return True
    
    @staticmethod
    def batch_check(folder: Path) -> List[Path]:
        """
        Find all YAML files in folder that need sync (have changed).
        
        Args:
            folder: Path to folder containing YAML files
            
        Returns:
            List of Path objects for files that need sync
        """
        changed_files = []
        
        # Find all YAML files recursively
        for yaml_file in folder.rglob("*.yml"):
            if ContentHasher.needs_sync(yaml_file):
                changed_files.append(yaml_file)
        
        return changed_files
    
    @staticmethod
    def update_hash_in_file(yaml_file: Path) -> None:
        """
        Compute and update the content_hash in YAML file's testmo section.
        
        Args:
            yaml_file: Path to YAML file to update
        """
        # Compute new hash
        new_hash = ContentHasher.compute_hash(yaml_file)
        
        # Read file
        with open(yaml_file, 'r') as f:
            data = yaml.safe_load(f)
        
        # Update hash in testmo section
        if 'testmo' not in data:
            data['testmo'] = {}
        
        data['testmo']['content_hash'] = new_hash
        
        # Write back
        with open(yaml_file, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)


# Example usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python hasher.py <yaml_file>")
        sys.exit(1)
    
    yaml_path = Path(sys.argv[1])
    
    try:
        hash_value = ContentHasher.compute_hash(yaml_path)
        print(f"Hash: {hash_value}")
        
        needs_sync = ContentHasher.needs_sync(yaml_path)
        print(f"Needs sync: {needs_sync}")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
```

---

### **2. mapper.py - Path ↔ ID Mapping Module**

**Purpose:** Bidirectional mapping between folder paths and Testmo folder IDs

**Key Requirements:**
- Load/save mapping from .sync/folder-map.json
- Fast lookups in both directions
- Handle 162 folders efficiently
- Cache for performance

**Implementation:**

```python
"""
Folder Mapping Module

Provides bidirectional mapping between local folder paths and Testmo folder IDs.
Caches mappings in .sync/folder-map.json for fast lookups.

Based on validation: TESTING_LOG.md - 162 folders with hierarchy up to 4 levels
"""

import json
from pathlib import Path
from typing import Dict, Optional, List


class FolderMapper:
    """Bidirectional mapping between folder paths and Testmo folder IDs."""
    
    def __init__(self, project_dir: Path):
        """
        Initialize mapper and load mappings from .sync/folder-map.json.
        
        Args:
            project_dir: Path to project directory (e.g., testmo/oneapp)
        """
        self.project_dir = project_dir
        self.sync_dir = project_dir / ".sync"
        self.map_file = self.sync_dir / "folder-map.json"
        
        # Load mappings
        self.id_to_folder: Dict[int, Dict] = {}  # folder_id -> folder info
        self.path_to_id: Dict[str, int] = {}     # path -> folder_id
        
        self._load_mappings()
    
    def _load_mappings(self) -> None:
        """Load mappings from folder-map.json."""
        if not self.map_file.exists():
            # No mappings yet - will be created during export
            return
        
        with open(self.map_file, 'r') as f:
            data = json.load(f)
        
        # Build both mappings
        for folder_id_str, folder_info in data.items():
            folder_id = int(folder_id_str)
            self.id_to_folder[folder_id] = folder_info
            self.path_to_id[folder_info['path']] = folder_id
    
    def save_mappings(self) -> None:
        """Save current mappings to folder-map.json."""
        # Ensure .sync directory exists
        self.sync_dir.mkdir(parents=True, exist_ok=True)
        
        # Convert to JSON-serializable format (keys must be strings)
        data = {str(folder_id): info for folder_id, info in self.id_to_folder.items()}
        
        with open(self.map_file, 'w') as f:
            json.dump(data, f, indent=2, sort_keys=True)
    
    def add_folder(self, folder_id: int, path: str, ui_name: str, 
                   parent_id: Optional[int] = None, level: int = 1) -> None:
        """
        Add a folder to the mapping.
        
        Args:
            folder_id: Testmo folder ID
            path: Local folder path (e.g., "home/charge/v2l")
            ui_name: UI display name (e.g., "Home / Charge / V2L")
            parent_id: Parent folder ID (None for root folders)
            level: Folder depth level (1-4)
        """
        folder_info = {
            'path': path,
            'ui_name': ui_name,
            'parent_id': parent_id,
            'level': level
        }
        
        self.id_to_folder[folder_id] = folder_info
        self.path_to_id[path] = folder_id
    
    def get_folder_id(self, path: str) -> Optional[int]:
        """
        Get Testmo folder ID from local path.
        
        Args:
            path: Local folder path (e.g., "home/charge/v2l")
            
        Returns:
            Folder ID or None if not found
        """
        return self.path_to_id.get(path)
    
    def get_folder_path(self, folder_id: int) -> Optional[str]:
        """
        Get local folder path from Testmo folder ID.
        
        Args:
            folder_id: Testmo folder ID
            
        Returns:
            Local path or None if not found
        """
        folder_info = self.id_to_folder.get(folder_id)
        return folder_info['path'] if folder_info else None
    
    def get_folder_ui_name(self, folder_id: int) -> Optional[str]:
        """
        Get UI display name from Testmo folder ID.
        
        Args:
            folder_id: Testmo folder ID
            
        Returns:
            UI name (e.g., "Home / Charge / V2L") or None if not found
        """
        folder_info = self.id_to_folder.get(folder_id)
        return folder_info['ui_name'] if folder_info else None
    
    def get_all_folders(self) -> Dict[int, Dict]:
        """
        Get all folder mappings.
        
        Returns:
            Dictionary of folder_id -> folder_info
        """
        return self.id_to_folder.copy()
    
    def folder_exists(self, folder_id: int) -> bool:
        """Check if folder ID exists in mappings."""
        return folder_id in self.id_to_folder
    
    def path_exists(self, path: str) -> bool:
        """Check if path exists in mappings."""
        return path in self.path_to_id


# Example usage
if __name__ == "__main__":
    project_dir = Path("testmo/oneapp")
    mapper = FolderMapper(project_dir)
    
    print(f"Loaded {len(mapper.id_to_folder)} folders")
    
    # Test lookup
    folder_id = mapper.get_folder_id("home/charge/v2l-vehicle-to-load")
    if folder_id:
        print(f"Folder ID for 'home/charge/v2l-vehicle-to-load': {folder_id}")
        ui_name = mapper.get_folder_ui_name(folder_id)
        print(f"UI Name: {ui_name}")
```

---

### **3. validator.py - YAML Validation Module**

**Purpose:** Validate YAML test case files against schema

**Key Requirements:**
- Validate required sections (metadata, test_case)
- Check field types
- Validate enum values (priority, status)
- Auto-fix common issues

**Implementation:**

```python
"""
YAML Validation Module

Validates test case YAML files against the BTL-TestCases schema.
Checks required sections, field types, and enum values.

Based on: docs/YAML_FORMAT.md specification
"""

import yaml
from pathlib import Path
from typing import Tuple, List, Dict, Any, Optional


class ValidationError:
    """Represents a validation error."""
    
    def __init__(self, field: str, message: str, severity: str = "error"):
        self.field = field
        self.message = message
        self.severity = severity  # "error" or "warning"
    
    def __str__(self):
        return f"[{self.severity.upper()}] {self.field}: {self.message}"


class YAMLValidator:
    """Validate test case YAML files."""
    
    # Valid enum values
    VALID_PRIORITIES = ["low", "medium", "high", "critical"]
    VALID_STATUSES = ["active", "deprecated", "draft"]
    VALID_AUTOMATION = ["yes", "no", "partial"]
    
    @staticmethod
    def validate_file(yaml_file: Path) -> Tuple[bool, List[ValidationError]]:
        """
        Validate a single YAML file.
        
        Args:
            yaml_file: Path to YAML file
            
        Returns:
            Tuple of (is_valid, list of errors)
        """
        errors = []
        
        # Check file exists
        if not yaml_file.exists():
            errors.append(ValidationError("file", f"File not found: {yaml_file}"))
            return False, errors
        
        # Parse YAML
        try:
            with open(yaml_file, 'r') as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            errors.append(ValidationError("yaml", f"YAML parsing error: {e}"))
            return False, errors
        
        if not isinstance(data, dict):
            errors.append(ValidationError("root", "Root must be a dictionary"))
            return False, errors
        
        # Validate sections
        errors.extend(YAMLValidator._validate_metadata(data.get('metadata')))
        errors.extend(YAMLValidator._validate_test_case(data.get('test_case')))
        errors.extend(YAMLValidator._validate_testmo(data.get('testmo')))
        
        # Check for errors (not warnings)
        has_errors = any(e.severity == "error" for e in errors)
        
        return not has_errors, errors
    
    @staticmethod
    def _validate_metadata(metadata: Any) -> List[ValidationError]:
        """Validate metadata section."""
        errors = []
        
        if metadata is None:
            errors.append(ValidationError("metadata", "Missing required section"))
            return errors
        
        if not isinstance(metadata, dict):
            errors.append(ValidationError("metadata", "Must be a dictionary"))
            return errors
        
        # Validate name (required)
        if 'name' not in metadata:
            errors.append(ValidationError("metadata.name", "Required field missing"))
        elif not isinstance(metadata['name'], str) or not metadata['name'].strip():
            errors.append(ValidationError("metadata.name", "Must be a non-empty string"))
        
        # Validate priority (optional)
        if 'priority' in metadata:
            if metadata['priority'] not in YAMLValidator.VALID_PRIORITIES:
                errors.append(ValidationError(
                    "metadata.priority",
                    f"Invalid value '{metadata['priority']}'. Must be one of: {YAMLValidator.VALID_PRIORITIES}"
                ))
        
        # Validate status (optional)
        if 'status' in metadata:
            if metadata['status'] not in YAMLValidator.VALID_STATUSES:
                errors.append(ValidationError(
                    "metadata.status",
                    f"Invalid value '{metadata['status']}'. Must be one of: {YAMLValidator.VALID_STATUSES}"
                ))
        
        # Validate automation (optional)
        if 'automation' in metadata:
            if metadata['automation'] not in YAMLValidator.VALID_AUTOMATION:
                errors.append(ValidationError(
                    "metadata.automation",
                    f"Invalid value '{metadata['automation']}'. Must be one of: {YAMLValidator.VALID_AUTOMATION}"
                ))
        
        # Validate tags (optional)
        if 'tags' in metadata:
            if not isinstance(metadata['tags'], list):
                errors.append(ValidationError("metadata.tags", "Must be a list"))
            else:
                for i, tag in enumerate(metadata['tags']):
                    if not isinstance(tag, str):
                        errors.append(ValidationError(f"metadata.tags[{i}]", "Must be a string"))
        
        # Validate estimate (optional)
        if 'estimate' in metadata:
            if not isinstance(metadata['estimate'], (int, float)) or metadata['estimate'] < 0:
                errors.append(ValidationError("metadata.estimate", "Must be a non-negative number"))
        
        return errors
    
    @staticmethod
    def _validate_test_case(test_case: Any) -> List[ValidationError]:
        """Validate test_case section."""
        errors = []
        
        if test_case is None:
            errors.append(ValidationError("test_case", "Missing required section"))
            return errors
        
        if not isinstance(test_case, dict):
            errors.append(ValidationError("test_case", "Must be a dictionary"))
            return errors
        
        # Validate description (optional but recommended)
        if 'description' in test_case:
            if not isinstance(test_case['description'], str):
                errors.append(ValidationError("test_case.description", "Must be a string"))
        
        # Validate steps (optional but recommended)
        if 'steps' in test_case:
            if not isinstance(test_case['steps'], list):
                errors.append(ValidationError("test_case.steps", "Must be a list"))
            else:
                for i, step in enumerate(test_case['steps']):
                    if not isinstance(step, dict):
                        errors.append(ValidationError(f"test_case.steps[{i}]", "Must be a dictionary"))
                    else:
                        if 'step' not in step:
                            errors.append(ValidationError(f"test_case.steps[{i}].step", "Required field missing"))
                        if 'expected' not in step:
                            errors.append(ValidationError(f"test_case.steps[{i}].expected", "Required field missing"))
        
        # Validate configurations (optional)
        if 'configurations' in test_case:
            if not isinstance(test_case['configurations'], list):
                errors.append(ValidationError("test_case.configurations", "Must be a list"))
            else:
                for i, config in enumerate(test_case['configurations']):
                    if not isinstance(config, str):
                        errors.append(ValidationError(f"test_case.configurations[{i}]", "Must be a string"))
        
        return errors
    
    @staticmethod
    def _validate_testmo(testmo: Any) -> List[ValidationError]:
        """Validate testmo section (warnings only - this is auto-generated)."""
        errors = []
        
        if testmo is None:
            # testmo section is optional (for new cases)
            return errors
        
        if not isinstance(testmo, dict):
            errors.append(ValidationError("testmo", "Must be a dictionary", severity="warning"))
            return errors
        
        # Check for expected fields (warnings only)
        expected_fields = ['case_id', 'folder_id', 'project_id', 'content_hash']
        for field in expected_fields:
            if field not in testmo:
                errors.append(ValidationError(
                    f"testmo.{field}",
                    f"Auto-generated field missing",
                    severity="warning"
                ))
        
        return errors
    
    @staticmethod
    def validate_batch(folder: Path) -> Dict[str, Tuple[bool, List[ValidationError]]]:
        """
        Validate all YAML files in a folder.
        
        Args:
            folder: Path to folder containing YAML files
            
        Returns:
            Dictionary mapping file paths to (is_valid, errors) tuples
        """
        results = {}
        
        for yaml_file in folder.rglob("*.yml"):
            is_valid, errors = YAMLValidator.validate_file(yaml_file)
            results[str(yaml_file)] = (is_valid, errors)
        
        return results
    
    @staticmethod
    def auto_fix(yaml_file: Path) -> bool:
        """
        Attempt to auto-fix common issues in YAML file.
        
        Returns:
            True if fixes were applied, False otherwise
        """
        try:
            with open(yaml_file, 'r') as f:
                data = yaml.safe_load(f)
            
            fixed = False
            
            # Ensure metadata section exists
            if 'metadata' not in data:
                data['metadata'] = {}
                fixed = True
            
            # Ensure test_case section exists
            if 'test_case' not in data:
                data['test_case'] = {}
                fixed = True
            
            # Fix invalid priority
            if 'priority' in data.get('metadata', {}):
                if data['metadata']['priority'] not in YAMLValidator.VALID_PRIORITIES:
                    data['metadata']['priority'] = 'medium'
                    fixed = True
            
            # Fix tags (ensure it's a list)
            if 'tags' in data.get('metadata', {}):
                if not isinstance(data['metadata']['tags'], list):
                    data['metadata']['tags'] = []
                    fixed = True
            
            if fixed:
                with open(yaml_file, 'w') as f:
                    yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            return fixed
            
        except Exception:
            return False


# Example usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python validator.py <yaml_file>")
        sys.exit(1)
    
    yaml_path = Path(sys.argv[1])
    
    is_valid, errors = YAMLValidator.validate_file(yaml_path)
    
    if is_valid:
        print(f"✓ {yaml_path} is valid")
    else:
        print(f"✗ {yaml_path} has errors:")
        for error in errors:
            print(f"  {error}")
    
    sys.exit(0 if is_valid else 1)
```

---

### **CONTINUE TO PART 2...**

This is Part 1 of MEGA PROMPT 3. Due to length, I'll split into multiple parts.

**Continue with:**
- Part 2: reader.py, writer.py, converter.py
- Part 3: sync_engine.py, btl_testmo.py
- Part 4: Tests and verification

Would you like me to continue with Part 2 now?
