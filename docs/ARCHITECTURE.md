# BTL TestCases Framework - Architecture

**Version:** 1.0.0
**Last Updated:** 2026-01-30

---

## 🎯 Overview

The BTL TestCases Framework provides bidirectional synchronization between local YAML files and the Testmo platform, enabling:
- Version-controlled test case management
- AI-assisted test case creation and transformation
- Batch operations for efficiency
- Smart change detection and sync

---

## 🏗️ High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERFACE                           │
│  (Human Developer, AI Agent, CI/CD Pipeline)                │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                  CLI INTERFACE (btl_testmo.py)              │
│  Commands: export, import, update, create, sync, status     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│             CORE FRAMEWORK (testmo_sync package)            │
│                                                             │
│  ┌──────────────────┐          ┌──────────────────┐        │
│  │   READ OPS       │          │   WRITE OPS      │        │
│  │   (reader.py)    │          │   (writer.py)    │        │
│  │                  │          │                  │        │
│  │ • list_folders   │          │ • update_case    │        │
│  │ • get_all_cases  │          │ • create_case    │        │
│  │ • get_case       │          │ • batch_update   │        │
│  └────────┬─────────┘          └────────┬─────────┘        │
│           │                              │                  │
│  ┌────────┴──────────────────────────────┴─────────┐       │
│  │         SUPPORT MODULES                          │       │
│  │  • hasher.py - Change detection                  │       │
│  │  • mapper.py - Path ↔ ID mapping                 │       │
│  │  • validator.py - YAML validation                │       │
│  │  • converter.py - Format conversion              │       │
│  │  • sync_engine.py - Smart sync logic             │       │
│  └──────────────────────────────────────────────────┘       │
└────────────┬────────────────────────┬───────────────────────┘
             │                        │
             ↓                        ↓
┌────────────────────────┐  ┌────────────────────────┐
│   TESTMO MCP SERVER    │  │  TESTMO REST API       │
│  (Read Operations)     │  │  (Write Operations)    │
│                        │  │                        │
│ • Auto-pagination      │  │ • PATCH /cases         │
│ • 162 folders          │  │ • POST /cases          │
│ • Attachments          │  │ • Batch operations     │
│ • Test runs            │  │                        │
└────────────┬───────────┘  └────────────┬───────────┘
             │                           │
             └───────────┬───────────────┘
                         ↓
              ┌──────────────────────┐
              │   TESTMO PLATFORM    │
              │ bethinklabs.testmo.net│
              └──────────────────────┘
```

---

## 🔧 Component Details

### **CLI Layer (btl_testmo.py)**

**Responsibility:** Command-line interface and argument parsing

**Key Functions:**
- Parse user commands and arguments
- Validate inputs
- Route to appropriate framework functions
- Format output for users

**Design Decisions:**
- Single entry point for all operations
- Consistent command structure
- Rich error messages
- Progress indicators for long operations

---

### **Reader Module (reader.py)**

**Responsibility:** All READ operations via Testmo MCP

**Key Functions:**
```python
class TestmoReader:
    def get_all_folders(project_id: int) -> List[Folder]
        """Get ALL folders with auto-pagination (162 folders)"""

    def get_all_cases(project_id: int) -> List[Case]
        """Get ALL cases with auto-pagination (1334 cases)"""

    def get_case(project_id: int, case_id: int) -> Case
        """Get single case with full details"""

    def get_attachments(project_id: int, case_id: int) -> List[Attachment]
        """Get case attachments (MCP only)"""
```

**Why MCP:**
- ✅ Auto-pagination (no manual loop needed)
- ✅ Gets ALL 162 folders (REST API only got 100)
- ✅ Attachments support
- ✅ Test runs support
- ✅ Better performance

**Performance:**
- Export 1334 cases: ~1 minute
- Get single case: ~100-200ms

---

### **Writer Module (writer.py)**

**Responsibility:** All WRITE operations via Testmo REST API

**Key Functions:**
```python
class TestmoWriter:
    def update_case(project_id: int, case_id: int, updates: dict) -> dict
        """Update single case (PATCH)"""

    def update_cases_batch(project_id: int, updates: List[dict]) -> List[dict]
        """Batch update (hybrid: common fields batch, unique fields individual)"""

    def create_case(project_id: int, folder_id: int, data: dict) -> int
        """Create single case, return new case_id"""

    def create_cases_batch(project_id: int, cases: List[dict]) -> List[int]
        """Batch create (true batch, 3.3x faster)"""
```

**Why REST API:**
- ✅ MCP update_case has bug (wrong endpoint)
- ✅ Workaround confirmed working
- ✅ Batch operations validated

**Performance:**
- Update single: ~223ms
- Update batch (5 cases): ~1.5s (hybrid approach)
- Create single: ~150ms
- Create batch (5 cases): ~393ms (pure batch)

---

### **Hasher Module (hasher.py)**

**Responsibility:** Content hashing for change detection

**Key Functions:**
```python
class ContentHasher:
    def compute_hash(yaml_file: Path) -> str
        """Generate SHA-256 hash of editable content only"""

    def needs_sync(yaml_file: Path) -> bool
        """Compare current hash with saved hash"""

    def batch_check(folder: Path) -> List[Path]
        """Return list of files that changed"""
```

**Algorithm:**
```python
# Hash only editable sections (ignore testmo metadata)
editable_content = {
    'metadata': yaml_data['metadata'],
    'test_case': yaml_data['test_case']
}

# Deterministic serialization (sorted keys)
content_str = yaml.dump(editable_content, sort_keys=True)

# SHA-256 hash
hash_value = hashlib.sha256(content_str.encode()).hexdigest()
return f"sha256:{hash_value}"
```

**Why This Approach:**
- ✅ Reliable change detection
- ✅ Ignores metadata (testmo section)
- ✅ Fast (SHA-256 is quick)
- ✅ Git-friendly (deterministic)

---

### **Mapper Module (mapper.py)**

**Responsibility:** Bidirectional path ↔ ID mapping

**Key Functions:**
```python
class FolderMapper:
    def __init__(project_id: int):
        """Load or create mapping from .sync/folder-map.json"""

    def path_to_id(path: str) -> int
        """'home/charge/v2l' → 7338"""

    def id_to_path(folder_id: int) -> str
        """7338 → 'home/charge/v2l'"""

    def id_to_ui_name(folder_id: int) -> str
        """7338 → 'Home / Charge / V2L Vehicle to Load'"""
```

**Data Structure (folder-map.json):**
```json
{
  "7338": {
    "path": "home/charge/v2l-vehicle-to-load",
    "ui_name": "Home / Charge / V2L Vehicle to Load",
    "parent_id": 7200,
    "level": 3
  }
}
```

**Why Cache:**
- ✅ Avoid API calls for every lookup
- ✅ Faster operations
- ✅ Works offline (once cached)

---

### **Validator Module (validator.py)**

**Responsibility:** YAML format validation

**Key Functions:**
```python
class YAMLValidator:
    def validate_file(yaml_file: Path) -> Tuple[bool, List[str]]
        """Validate single file, return (is_valid, errors)"""

    def validate_batch(folder: Path) -> dict
        """Validate all YAMLs in folder"""

    def auto_fix(yaml_file: Path) -> bool
        """Fix common issues (missing fields, wrong types)"""
```

**Validation Rules:**
- Required sections: `metadata`, `test_case`
- Optional section: `testmo` (auto-generated)
- Field types must match spec
- Tags must be list of strings
- Priority must be valid value
- Steps must have `step` and `expected`

---

### **Converter Module (converter.py)**

**Responsibility:** Format conversion between Testmo and YAML

**Key Functions:**
```python
class TestmoConverter:
    def testmo_to_yaml(case: dict) -> str
        """Convert Testmo API format to YAML string"""

    def yaml_to_testmo(yaml_file: Path) -> dict
        """Convert YAML file to Testmo API format"""
```

**Conversion Map:**
```
Testmo API          YAML
──────────────────  ────────────────────
id                  testmo.case_id
name                metadata.name
custom_priority     metadata.priority
custom_tags         metadata.tags
state               metadata.status
description         test_case.description
custom_steps        test_case.steps
custom_configs      test_case.configurations
```

---

### **Sync Engine Module (sync_engine.py)**

**Responsibility:** Smart bidirectional sync logic

**Key Functions:**
```python
class SyncEngine:
    def diff_case(local_yaml: dict, testmo_case: dict) -> dict
        """Return only changed fields"""

    def sync_local_to_testmo(yaml_path: Path) -> bool
        """Push local changes to Testmo"""

    def sync_testmo_to_local(case_id: int, output_dir: Path) -> bool
        """Pull Testmo case to local YAML"""

    def detect_conflicts() -> List[Conflict]
        """Find cases changed in both places"""
```

**Sync Strategy:**
```
1. Scan local files, compute hashes
2. Compare with saved hashes (case-map.json)
3. Changed locally? Mark for push
4. Check Testmo updated_at vs last_sync
5. Changed in Testmo? Mark for pull
6. Both changed? Mark as conflict
7. Push local changes (batch if possible)
8. Pull remote changes
9. Prompt user for conflict resolution
10. Update all hashes and timestamps
```

---

## 💾 Data Storage

### **Local YAML Files**
```
testmo/oneapp/test-cases/
└── home/
    └── charge/
        └── v2l-vehicle-to-load/
            └── TC66186-v2l-screen.yml
```

**Format:** See [YAML_FORMAT.md](YAML_FORMAT.md)

### **Sync Metadata (.sync/)**

**project.json** - Project configuration
**folder-map.json** - Folder ID ↔ path mapping (162 entries)
**case-map.json** - Case ID ↔ file + hash mapping (1334 entries)
**sync-log.jsonl** - Append-only operation log

---

## 🔄 Data Flow

### **Export Flow**
```
1. User: btl_testmo export --project-id 2
2. CLI: Parse arguments, call reader
3. Reader: MCP get_all_folders(2) → 162 folders
4. Reader: MCP get_all_cases(2) → 1334 cases
5. Mapper: Build folder-map.json (id ↔ path)
6. Converter: For each case, convert to YAML
7. Hasher: Compute hash for each case
8. FileSystem: Write 1334 YAML files
9. FileSystem: Write case-map.json
10. CLI: Report success
```

### **Update Flow**
```
1. User: Edit TC66186-v2l-screen.yml locally
2. User: btl_testmo update TC66186-v2l-screen.yml
3. CLI: Parse argument, call sync_engine
4. Hasher: Compute current hash
5. Hasher: Compare with saved hash → DIFFERENT
6. Converter: YAML → Testmo format
7. Writer: PATCH /cases (case_id: 66186)
8. Hasher: Update hash in case-map.json
9. FileSystem: Update testmo.last_sync in YAML
10. CLI: Report success
```

### **Create Flow**
```
1. User: Create TC-NEW-test.yml locally
2. User: btl_testmo create TC-NEW-test.yml
3. CLI: Parse argument, call sync_engine
4. Converter: YAML → Testmo format
5. Mapper: Get folder_id from file path
6. Writer: POST /cases (folder_id: 7338)
7. Response: New case_id: 66310
8. FileSystem: Rename TC-NEW-* → TC66310-*
9. FileSystem: Add testmo metadata to YAML
10. Hasher: Compute and save hash
11. case-map.json: Add entry
12. CLI: Report success with new ID
```

---

## ⚡ Performance Characteristics

### **Validated Performance (from TESTING_LOG.md)**

| Operation | Metric | Details |
|-----------|--------|---------|
| **Export** | ~1 min | 1334 cases, full hierarchy |
| **Import** | ~1 min | 1334 cases to new project |
| **Update Single** | ~223ms | Individual PATCH |
| **Update Batch (5)** | ~1.5s | Hybrid approach |
| **Create Single** | ~250ms | POST + ID sync |
| **Create Batch (5)** | ~393ms | True batch (3.3x faster) |

### **Scalability Projections**

**Export/Import:**
- 5,000 cases: ~3-4 minutes
- 10,000 cases: ~7-8 minutes
- Bottleneck: Network I/O

**Batch Updates:**
- 100 cases (common field): ~5 seconds (batch)
- 100 cases (unique fields): ~24 seconds (individual)
- Hybrid approach optimal

**Batch Creates:**
- 10 cases: ~456ms
- 50 cases: ~2.3s
- 100 cases: ~4.6s
- Likely API limit around 100/request

---

## 🎯 Design Decisions

### **Why Hybrid MCP + REST API?**

**Decision:** Use MCP for reads, REST API for writes

**Rationale:**
- MCP has bug in update_case (uses wrong endpoint)
- MCP pagination works perfectly for reads
- REST API update/create confirmed working
- Best of both worlds

**Alternative Considered:** Pure REST API
- ❌ Manual pagination required
- ❌ Only gets 100/162 folders
- ❌ More complex code

### **Why Content Hashing?**

**Decision:** Use SHA-256 hash of editable content

**Rationale:**
- More reliable than timestamps
- Works with Git operations
- Detects actual changes, not just "touches"
- Fast computation

**Alternative Considered:** Timestamps (modified date)
- ❌ Can be misleading (file touched but not changed)
- ❌ Breaks with Git operations
- ❌ Less reliable

### **Why YAML for Storage?**

**Decision:** Store test cases as YAML files

**Rationale:**
- Human-readable and editable
- Git-friendly (good diffs)
- Supports comments
- Easy to parse
- AI-friendly

**Alternative Considered:** JSON
- ❌ No comments
- ❌ Harder to read/edit manually
- ❌ Less friendly for AI transformation

### **Why Separate .sync/ Directory?**

**Decision:** Store metadata in `.sync/` separate from test cases

**Rationale:**
- Keeps test case YAMLs clean
- Easy to .gitignore metadata
- Central location for mappings
- Performance (cache lookups)

**Alternative Considered:** Metadata in each YAML
- ❌ Duplicates folder info
- ❌ Harder to query all mappings
- ❌ More storage

---

## 🔐 Security Considerations

### **API Key Storage**
- ✅ Stored in `.env` file
- ✅ `.env` in `.gitignore`
- ✅ File permissions: 600
- ❌ Never commit API keys to git

### **Data Privacy**
- Test case data stored locally
- Full control over what's committed to git
- No telemetry or external tracking

### **Access Control**
- Testmo API key determines access level
- Framework respects Testmo permissions
- No privilege escalation

---

## 🧪 Testing Strategy

### **Unit Tests**
- Each module tested independently
- Mock MCP and API responses
- Test error handling
- Test edge cases

### **Integration Tests**
- End-to-end workflows
- Real Testmo sandbox project
- Verify data integrity
- Performance benchmarks

### **Validation Tests**
- All 5 core operations validated
- 100% success rate in testing
- Performance metrics documented
- See: `TESTING_LOG.md`

---

## 🔄 Future Enhancements

### **Planned Features**
- Watch mode (auto-sync on file changes)
- Web UI for browsing test cases
- Advanced search/filter
- Test case templates
- Bulk transformations with AI
- CI/CD pipeline integration

### **Performance Optimizations**
- Parallel operations
- Delta sync (only changed files)
- Compression for large exports
- Caching strategies

---

## 📚 References

- [TESTING_LOG.md](../TESTING_LOG.md) - Validation results
- [Testmo API Docs](https://docs.testmo.com/api)
- [Testmo MCP Server](https://github.com/testmoapp/testmo-mcp)

---

**Architecture documented and validated** ✅
