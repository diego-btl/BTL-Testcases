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
