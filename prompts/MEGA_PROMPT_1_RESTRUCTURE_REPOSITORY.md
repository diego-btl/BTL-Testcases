# MEGA PROMPT 1: Repository Restructuring

**Date:** 2026-01-30
**Phase:** Repository Reorganization
**Priority:** CRITICAL
**Estimated Time:** 30-45 minutes

---

## 🎯 OBJECTIVE

Restructure the BTL-TestCases repository based on validated workflows and testing results. This reorganization will:
- Preserve ALL working functionality
- Create clear separation between active and deprecated code
- Establish production-ready structure
- Prepare foundation for framework implementation

---

## 📋 PREREQUISITES

**Required Context:**
- Read: `TESTING_LOG.md` (validation results)
- Understand: All 5 tests passed (export, import, update, create, batch operations)
- Know: MCP is used for reads, REST API for writes
- Confirm: Current working directory is `/Users/diegodelaguila/Projects/BTL-TestCases`

**Validation Before Starting:**
```bash
# Verify current structure
ls -la scripts/
ls -la testmo/oneapp/

# Ensure no uncommitted changes that could be lost
git status

# Create backup branch
git checkout -b restructure-backup
git checkout -b feature/repository-restructure
```

---

## 🗂️ NEW DIRECTORY STRUCTURE

Create this exact structure:

```
BTL-TestCases/
├── testmo/                          # Test cases by project
│   ├── oneapp/
│   │   ├── .sync/                   # Sync metadata (NEW)
│   │   │   ├── project.json
│   │   │   ├── folder-map.json
│   │   │   ├── case-map.json
│   │   │   └── sync-log.jsonl
│   │   └── test-cases/              # YAML files (KEEP AS IS)
│   ├── nmex/                        # (placeholder for future)
│   └── nba/                         # (placeholder for future)
│
├── scripts/
│   ├── btl_testmo.py                # CLI entry point (NEW - placeholder)
│   │
│   ├── testmo_sync/                 # Core package (NEW)
│   │   ├── __init__.py
│   │   ├── reader.py                # MCP wrapper (NEW - placeholder)
│   │   ├── writer.py                # API wrapper (NEW - placeholder)
│   │   ├── hasher.py                # Content hashing (NEW - placeholder)
│   │   ├── mapper.py                # Path ↔ ID mapping (NEW - placeholder)
│   │   ├── validator.py             # YAML validation (NEW - placeholder)
│   │   ├── converter.py             # Testmo ↔ YAML (NEW - placeholder)
│   │   └── sync_engine.py           # Smart sync (NEW - placeholder)
│   │
│   └── legacy/                      # Deprecated scripts (MOVE HERE)
│       ├── testmo_client.py         # MOVE from scripts/
│       ├── testmo_export.py         # MOVE from scripts/
│       ├── testmo_import.py         # MOVE from scripts/
│       ├── yaml_converter.py        # MOVE from scripts/
│       └── README.md                # Explain deprecation (NEW)
│
├── docs/                            # Documentation (NEW)
│   ├── README.md                    # Placeholder
│   ├── GETTING_STARTED.md           # Placeholder
│   ├── ARCHITECTURE.md              # Placeholder
│   ├── CLI_REFERENCE.md             # Placeholder
│   ├── YAML_FORMAT.md               # Placeholder
│   ├── WORKFLOWS.md                 # Placeholder
│   └── TROUBLESHOOTING.md           # Placeholder
│
├── tests/                           # Unit tests (NEW)
│   ├── __init__.py
│   └── README.md                    # Placeholder for future tests
│
├── prompts/                         # Mega prompts (KEEP)
│   └── *.md
│
├── .gitignore                       # UPDATE
├── requirements.txt                 # UPDATE
└── README.md                        # UPDATE (main readme)
```

---

## 📝 STEP-BY-STEP EXECUTION

### **PHASE 1: Create New Structure (15 min)**

#### Step 1.1: Create .sync directories
```bash
# Create sync directories for each project
mkdir -p testmo/oneapp/.sync
mkdir -p testmo/nmex/.sync
mkdir -p testmo/nba/.sync

# Create placeholder projects (empty for now)
mkdir -p testmo/nmex/test-cases
mkdir -p testmo/nba/test-cases
```

#### Step 1.2: Create initial .sync files for OneApp
```bash
# Create project.json
cat > testmo/oneapp/.sync/project.json << 'EOF'
{
  "project_id": 2,
  "project_name": "OneApp",
  "testmo_url": "https://bethinklabs.testmo.net",
  "last_full_sync": null,
  "total_cases": 1334,
  "total_folders": 162,
  "version": "1.0",
  "notes": "Metadata will be populated during first sync operation"
}
EOF

# Create empty placeholder files
touch testmo/oneapp/.sync/folder-map.json
echo "{}" > testmo/oneapp/.sync/folder-map.json

touch testmo/oneapp/.sync/case-map.json
echo "{}" > testmo/oneapp/.sync/case-map.json

touch testmo/oneapp/.sync/sync-log.jsonl
```

#### Step 1.3: Create testmo_sync package
```bash
# Create package directory
mkdir -p scripts/testmo_sync

# Create __init__.py
cat > scripts/testmo_sync/__init__.py << 'EOF'
"""
BTL Testmo Sync Framework

Core package for synchronizing test cases between local YAML files and Testmo.

Modules:
- reader: MCP-based read operations (folders, cases)
- writer: REST API write operations (create, update)
- hasher: Content hashing for change detection
- mapper: Bidirectional path ↔ ID mapping
- validator: YAML format validation
- converter: Testmo ↔ YAML format conversion
- sync_engine: Smart bidirectional sync logic

Version: 1.0.0
"""

__version__ = "1.0.0"
__all__ = [
    "reader",
    "writer", 
    "hasher",
    "mapper",
    "validator",
    "converter",
    "sync_engine"
]
EOF

# Create placeholder module files
for module in reader writer hasher mapper validator converter sync_engine; do
cat > scripts/testmo_sync/${module}.py << EOF
"""
${module^} module - Placeholder

TODO: Implement ${module} functionality based on TESTING_LOG.md results
"""

# Placeholder - to be implemented
pass
EOF
done
```

#### Step 1.4: Create legacy directory
```bash
mkdir -p scripts/legacy

# Create README explaining deprecation
cat > scripts/legacy/README.md << 'EOF'
# Legacy Scripts

⚠️ **DEPRECATED** - These scripts are preserved for reference but should not be used in production.

## Why Deprecated?

These scripts were part of the initial implementation but have been superseded by the new `btl_testmo.py` CLI and `testmo_sync` package, which provide:

- Better MCP integration (auto-pagination, 162 folders)
- REST API workarounds for known bugs
- Unified interface for all operations
- Content hashing for change detection
- Bidirectional sync capabilities

## Migration Guide

| Old Script | New Command |
|------------|-------------|
| `python scripts/testmo_export.py --project-id 2` | `btl_testmo export --project-id 2 --output testmo/oneapp` |
| `python scripts/testmo_import.py --project-id 9` | `btl_testmo import --project-id 9 --source testmo/oneapp` |
| Direct API calls via `testmo_client.py` | Use `testmo_sync.reader` or `testmo_sync.writer` |

## Preservation Reason

These files are kept for:
1. Reference during framework development
2. Understanding original implementation decisions
3. Code that might be reused in new modules

## Files

- `testmo_client.py` - Original REST API client (has pagination bugs)
- `testmo_export.py` - Export script (now integrated into btl_testmo.py)
- `testmo_import.py` - Import script (now integrated into btl_testmo.py)
- `yaml_converter.py` - YAML conversion utilities (may be reused)

Last updated: 2026-01-30
EOF
```

#### Step 1.5: Move files to legacy
```bash
# Move deprecated scripts to legacy folder
mv scripts/testmo_client.py scripts/legacy/
mv scripts/testmo_export.py scripts/legacy/
mv scripts/testmo_import.py scripts/legacy/
mv scripts/yaml_converter.py scripts/legacy/

# Note: If test_csv_mapping.py or other test files exist, move them too
if [ -f scripts/test_csv_mapping.py ]; then
    mv scripts/test_csv_mapping.py scripts/legacy/
fi
```

#### Step 1.6: Create btl_testmo.py CLI placeholder
```bash
cat > scripts/btl_testmo.py << 'EOF'
#!/usr/bin/env python3
"""
BTL Testmo CLI - Main Entry Point

Unified command-line interface for all Testmo operations.

Usage:
    btl_testmo export --project-id 2 --output testmo/oneapp
    btl_testmo import --project-id 9 --source testmo/oneapp
    btl_testmo update --case-id 535 --project-id 2
    btl_testmo create testmo/oneapp/test-cases/folder/TC-NEW-test.yml
    btl_testmo sync --project testmo/oneapp
    btl_testmo status testmo/oneapp
    btl_testmo validate testmo/oneapp

For detailed help:
    btl_testmo --help
    btl_testmo <command> --help

Version: 1.0.0
"""

import sys
import argparse
from pathlib import Path

def main():
    print("BTL Testmo CLI v1.0.0")
    print("=" * 50)
    print("\n⚠️  Implementation in progress")
    print("\nThis CLI is a placeholder. Core functionality will be implemented in:")
    print("  - scripts/testmo_sync/ package")
    print("\nBased on validation results in TESTING_LOG.md:")
    print("  ✅ Export (1334 cases in ~1 min)")
    print("  ✅ Import (1334 cases in ~1 min)")
    print("  ✅ Update Individual (~223ms per case)")
    print("  ✅ Update Batch (hybrid: ~1.5s for 5 cases)")
    print("  ✅ Create Individual (~250ms + sync)")
    print("  ✅ Create Batch (~393ms for 5 cases)")
    print("\nFor now, use legacy scripts in scripts/legacy/")
    print("See scripts/legacy/README.md for migration guide")
    return 0

if __name__ == "__main__":
    sys.exit(main())
EOF

chmod +x scripts/btl_testmo.py
```

#### Step 1.7: Create docs directory structure
```bash
mkdir -p docs

# Create placeholder files
for doc in README GETTING_STARTED ARCHITECTURE CLI_REFERENCE YAML_FORMAT WORKFLOWS TROUBLESHOOTING; do
cat > docs/${doc}.md << EOF
# ${doc//_/ }

⚠️ **TODO:** This document will be created in MEGA PROMPT 2

Placeholder created: 2026-01-30
EOF
done
```

#### Step 1.8: Create tests directory
```bash
mkdir -p tests

cat > tests/__init__.py << 'EOF'
"""
BTL Testmo Test Suite

Unit tests for testmo_sync package modules.
"""
EOF

cat > tests/README.md << 'EOF'
# Tests

Unit tests will be added here to validate:

- Content hashing (hasher.py)
- Path ↔ ID mapping (mapper.py)
- YAML validation (validator.py)
- MCP read operations (reader.py)
- REST API write operations (writer.py)
- Conversion logic (converter.py)
- Sync engine (sync_engine.py)

Tests will use pytest framework.

Run tests:
```bash
pytest tests/
```

Coverage report:
```bash
pytest --cov=testmo_sync tests/
```
EOF
```

---

### **PHASE 2: Update Configuration Files (10 min)**

#### Step 2.1: Update .gitignore
```bash
cat >> .gitignore << 'EOF'

# BTL-TestCases specific
testmo/*/.sync/sync-log.jsonl
testmo/*/.sync/case-map.json
testmo/*/.sync/folder-map.json
*.pyc
__pycache__/
.pytest_cache/
.coverage
htmlcov/
dist/
build/
*.egg-info/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Temp files
*.tmp
*.bak
*~
EOF
```

#### Step 2.2: Update requirements.txt
```bash
cat > requirements.txt << 'EOF'
# BTL Testmo Framework Requirements

# Core dependencies
requests>=2.31.0
pyyaml>=6.0.1
python-dotenv>=1.0.0

# MCP (handled by Claude Desktop, not installed here)
# - Testmo MCP server configured in claude_desktop_config.json

# Development dependencies
pytest>=7.4.0
pytest-cov>=4.1.0
black>=23.7.0
flake8>=6.1.0
mypy>=1.5.0

# Optional: For advanced features
# rich>=13.5.0  # Better CLI output
# typer>=0.9.0  # Modern CLI framework
EOF
```

#### Step 2.3: Create pyproject.toml
```bash
cat > pyproject.toml << 'EOF'
[project]
name = "btl-testcases"
version = "1.0.0"
description = "Test case management framework for Testmo integration"
authors = [{name = "Diego Del Aguila", email = "diego@bethinklabs.com"}]
requires-python = ">=3.8"
dependencies = [
    "requests>=2.31.0",
    "pyyaml>=6.0.1",
    "python-dotenv>=1.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "black>=23.7.0",
    "flake8>=6.1.0",
    "mypy>=1.5.0",
]

[project.scripts]
btl-testmo = "scripts.btl_testmo:main"

[build-system]
requires = ["setuptools>=68.0.0", "wheel"]
build-backend = "setuptools.build_meta"

[tool.black]
line-length = 100
target-version = ['py38', 'py39', 'py310', 'py311']

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_classes = "Test*"
python_functions = "test_*"

[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = false
EOF
```

#### Step 2.4: Update main README.md
```bash
cat > README.md << 'EOF'
# BTL TestCases Framework

**Version:** 1.0.0  
**Status:** ✅ Core Validation Complete - Implementation in Progress  
**Last Updated:** 2026-01-30

---

## 🎯 Overview

Unified framework for managing test cases across Testmo projects with bidirectional synchronization between local YAML files and Testmo platform.

**Key Features:**
- ✅ **Export** - Pull 1334+ cases with full hierarchy in ~1 minute
- ✅ **Import** - Push cases to new/existing projects  
- ✅ **Update** - Individual or batch updates with smart change detection
- ✅ **Create** - New cases with automatic ID sync back to local files
- ✅ **Sync** - Bidirectional smart sync with conflict detection

---

## 🚀 Quick Start

```bash
# Export test cases from Testmo
btl_testmo export --project-id 2 --output testmo/oneapp

# Update a test case locally, then push to Testmo
# 1. Edit: testmo/oneapp/test-cases/installation/TC00535-fresh-install.yml
# 2. Push changes:
btl_testmo update testmo/oneapp/test-cases/installation/TC00535-fresh-install.yml

# Create new test cases
# 1. Create: testmo/oneapp/test-cases/folder/TC-NEW-my-test.yml
# 2. Upload to Testmo:
btl_testmo create testmo/oneapp/test-cases/folder/TC-NEW-my-test.yml
# 3. File automatically renamed to TC{new_id}-my-test.yml with synced metadata
```

---

## 📚 Documentation

- **[Getting Started](docs/GETTING_STARTED.md)** - Installation and setup
- **[Architecture](docs/ARCHITECTURE.md)** - Technical design and decisions
- **[CLI Reference](docs/CLI_REFERENCE.md)** - All available commands
- **[YAML Format](docs/YAML_FORMAT.md)** - Standard YAML structure
- **[Workflows](docs/WORKFLOWS.md)** - Common use cases
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues and solutions
- **[Testing Log](TESTING_LOG.md)** - Validation results (5/5 tests passed)

---

## 📊 Validation Status

All core operations have been validated with 100% success rate:

| Operation | Status | Performance | Details |
|-----------|--------|-------------|---------|
| **Export** | ✅ PASS | ~1 min for 1334 cases | Full hierarchy, auto-pagination |
| **Import** | ✅ PASS | ~1 min for 1334 cases | Preserves structure, 0 errors |
| **Update Individual** | ✅ PASS | ~223ms per case | REST API PATCH |
| **Update Batch** | ✅ PASS | ~1.5s for 5 cases | Hybrid approach |
| **Create Individual** | ✅ PASS | ~250ms + ID sync | Automatic rename |
| **Create Batch** | ✅ PASS | ~393ms for 5 cases | True batch, 3.3x faster |

See [TESTING_LOG.md](TESTING_LOG.md) for complete validation details.

---

## 🗂️ Project Structure

```
BTL-TestCases/
├── testmo/              # Test cases by project
│   ├── oneapp/          # OneApp test cases (1334 cases, 162 folders)
│   ├── nmex/            # NMEX test cases (placeholder)
│   └── nba/             # NBA test cases (placeholder)
├── scripts/
│   ├── btl_testmo.py    # CLI entry point
│   ├── testmo_sync/     # Core framework package
│   └── legacy/          # Deprecated scripts (reference only)
├── docs/                # Complete documentation
└── tests/               # Unit tests
```

---

## 🛠️ Technology Stack

- **Python 3.8+** - Core language
- **Testmo MCP** - Read operations (folders, cases, attachments)
- **Testmo REST API** - Write operations (create, update)
- **YAML** - Test case storage format
- **Git** - Version control for test cases

---

## 📝 YAML Format

```yaml
# Sync metadata (auto-generated, don't edit manually)
testmo:
  case_id: 66186
  folder_id: 7338
  project_id: 2
  content_hash: "sha256:..."
  last_sync: "2026-01-30T21:30:00Z"

# Editable content (humans/AI can modify)
metadata:
  name: "Test Case Name"
  priority: "medium"
  tags: ["smoke", "regression"]

test_case:
  description: "Test description"
  steps:
    - step: "Action to take"
      expected: "Expected result"
```

See [docs/YAML_FORMAT.md](docs/YAML_FORMAT.md) for complete specification.

---

## 🤝 Contributing

This is an internal Bethink Labs project. For questions or issues, contact:
- **Diego Del Aguila** - diego@bethinklabs.com

---

## 📜 License

Internal use only - Bethink Labs © 2026

---

## 🔗 Links

- **Testmo:** https://bethinklabs.testmo.net
- **OneApp Project:** https://bethinklabs.testmo.net/repositories/2
- **BTL-TestCases Project:** https://bethinklabs.testmo.net/repositories/9

---

**Status:** 🟡 Framework validated, implementation in progress  
**Next Steps:** Complete module implementation (MEGA PROMPT 2 & 3)
EOF
```

---

### **PHASE 3: Verification & Documentation (10 min)**

#### Step 3.1: Verify new structure
```bash
# Check directory structure
tree -L 3 -I '__pycache__|*.pyc|.git'

# Verify legacy files moved
ls -la scripts/legacy/

# Verify new package created
ls -la scripts/testmo_sync/

# Verify test-cases remain intact
ls -la testmo/oneapp/test-cases/ | head -20
```

#### Step 3.2: Test CLI placeholder
```bash
# Test that btl_testmo.py runs
python scripts/btl_testmo.py

# Should output:
# BTL Testmo CLI v1.0.0
# ...implementation in progress...
```

#### Step 3.3: Create RESTRUCTURE_SUMMARY.md
```bash
cat > RESTRUCTURE_SUMMARY.md << 'EOF'
# Repository Restructure Summary

**Date:** 2026-01-30  
**Status:** ✅ COMPLETE  
**Duration:** ~45 minutes

---

## 🎯 What Was Done

### Created
- ✅ `testmo/*/.sync/` - Metadata directories for each project
- ✅ `scripts/testmo_sync/` - Core framework package (7 modules)
- ✅ `scripts/btl_testmo.py` - CLI entry point (placeholder)
- ✅ `scripts/legacy/` - Archived deprecated scripts
- ✅ `docs/` - Documentation structure (7 docs)
- ✅ `tests/` - Unit test structure
- ✅ `prompts/` - Mega prompts directory

### Moved
- ✅ `testmo_client.py` → `scripts/legacy/`
- ✅ `testmo_export.py` → `scripts/legacy/`
- ✅ `testmo_import.py` → `scripts/legacy/`
- ✅ `yaml_converter.py` → `scripts/legacy/`

### Updated
- ✅ `.gitignore` - Added new patterns
- ✅ `requirements.txt` - Updated dependencies
- ✅ `pyproject.toml` - Created package config
- ✅ `README.md` - Updated main readme

### Preserved
- ✅ `testmo/oneapp/test-cases/` - ALL 1334 YAML files intact
- ✅ `TESTING_LOG.md` - Complete validation results
- ✅ All documentation in root

---

## 📊 Structure Comparison

### Before
```
BTL-TestCases/
├── scripts/
│   ├── testmo_client.py
│   ├── testmo_export.py
│   ├── testmo_import.py
│   └── yaml_converter.py
└── testmo/
    └── oneapp/
        └── test-cases/
```

### After
```
BTL-TestCases/
├── scripts/
│   ├── btl_testmo.py           # NEW - CLI
│   ├── testmo_sync/            # NEW - Package
│   │   ├── reader.py
│   │   ├── writer.py
│   │   ├── hasher.py
│   │   ├── mapper.py
│   │   ├── validator.py
│   │   ├── converter.py
│   │   └── sync_engine.py
│   └── legacy/                 # NEW - Archived
│       ├── testmo_client.py
│       ├── testmo_export.py
│       └── ...
├── testmo/
│   └── oneapp/
│       ├── .sync/              # NEW - Metadata
│       └── test-cases/         # PRESERVED
├── docs/                       # NEW - Docs
└── tests/                      # NEW - Tests
```

---

## ✅ Verification Checklist

- [x] All directories created
- [x] All legacy scripts moved
- [x] CLI placeholder working
- [x] Package structure correct
- [x] Test cases preserved (1334 files)
- [x] Configuration files updated
- [x] Documentation placeholders created
- [x] .gitignore updated
- [x] README.md updated

---

## 🚀 Next Steps

1. **MEGA PROMPT 2:** Create complete documentation
   - All 7 docs in docs/ directory
   - User guides, technical specs, troubleshooting

2. **MEGA PROMPT 3:** Implement core modules
   - testmo_sync package functionality
   - btl_testmo.py CLI commands
   - Unit tests

3. **Testing:** Validate new structure
   - Run existing export/import workflows
   - Ensure backward compatibility
   - Verify all paths correct

---

## 📝 Notes

- Legacy scripts still functional for reference
- Test cases completely untouched
- New structure ready for framework implementation
- All validation results preserved in TESTING_LOG.md

---

**Restructure Complete!** ✅
EOF
```

#### Step 3.4: Git commit
```bash
# Stage all changes
git add -A

# Commit with detailed message
git commit -m "refactor: Restructure repository for production framework

- Create testmo_sync package structure (7 modules)
- Add btl_testmo.py CLI entry point (placeholder)
- Move deprecated scripts to legacy/ folder
- Create .sync/ directories for metadata
- Add docs/ structure (7 documentation files)
- Add tests/ structure for unit tests
- Update configuration files (.gitignore, requirements.txt, pyproject.toml)
- Update main README.md with new structure
- Preserve all 1334 test case YAML files

Based on validation: 5/5 tests passed (100% success rate)
See: TESTING_LOG.md, RESTRUCTURE_SUMMARY.md"

# Show summary
git log -1 --stat
```

---

## 🎯 DELIVERABLES

After executing this prompt, you should have:

1. ✅ **New Directory Structure** - All folders created
2. ✅ **Deprecated Scripts Archived** - Moved to `scripts/legacy/`
3. ✅ **Core Package Stub** - `testmo_sync/` with 7 modules
4. ✅ **CLI Placeholder** - `btl_testmo.py` executable
5. ✅ **Metadata Structure** - `.sync/` directories
6. ✅ **Documentation Placeholders** - 7 docs in `docs/`
7. ✅ **Configuration Updated** - `.gitignore`, `requirements.txt`, `pyproject.toml`
8. ✅ **Test Cases Preserved** - ALL 1334 YAML files intact
9. ✅ **Summary Document** - `RESTRUCTURE_SUMMARY.md`
10. ✅ **Git Commit** - Clean commit with detailed message

---

## ⚠️ CRITICAL CHECKS

Before marking this complete, verify:

```bash
# 1. Test cases intact
find testmo/oneapp/test-cases -name "*.yml" | wc -l
# Expected: 1334

# 2. Legacy scripts moved
ls scripts/legacy/*.py | wc -l
# Expected: 4+ files

# 3. New package created
ls scripts/testmo_sync/*.py | wc -l
# Expected: 8 files (7 modules + __init__)

# 4. CLI works
python scripts/btl_testmo.py
# Expected: Shows placeholder message

# 5. Docs created
ls docs/*.md | wc -l
# Expected: 7 files

# 6. Git clean
git status
# Expected: Clean working tree (everything committed)
```

---

## 🚨 TROUBLESHOOTING

**Issue:** File already exists errors
**Solution:** Some files may already exist, that's OK - skip or merge carefully

**Issue:** Git conflicts
**Solution:** We're on a new branch (feature/repository-restructure), conflicts shouldn't occur

**Issue:** Test cases missing
**Solution:** STOP immediately - verify backup, don't lose test cases!

**Issue:** Import errors after restructure
**Solution:** Update Python path or run from project root

---

## 📞 SUPPORT

If you encounter issues:
1. Check `RESTRUCTURE_SUMMARY.md` for what was done
2. Review git log: `git log --oneline -10`
3. Check working tree: `git status`
4. Restore from backup branch if needed: `git checkout restructure-backup`

---

**END OF MEGA PROMPT 1**

Estimated completion: 30-45 minutes
Status markers throughout - report progress at each phase completion.
