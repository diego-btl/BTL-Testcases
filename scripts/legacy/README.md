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
