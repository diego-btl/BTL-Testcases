# CLI Reference - btl_testmo

**Version:** 1.0.0
**Last Updated:** 2026-01-30

---

## 🎯 Overview

The `btl_testmo` CLI provides a unified interface for all test case management operations. All commands follow consistent patterns and provide rich feedback.

**Current Status:** ⚠️ CLI is a placeholder. Use legacy scripts in `scripts/legacy/` for now.

---

## 📋 Command Index

- [`export`](#export) - Export test cases from Testmo to local YAML
- [`import`](#import) - Import test cases from local YAML to Testmo
- [`update`](#update) - Update existing test cases in Testmo
- [`create`](#create) - Create new test cases in Testmo
- [`sync`](#sync) - Bidirectional smart sync
- [`status`](#status) - Show sync status and changes
- [`validate`](#validate) - Validate YAML file format
- [`--help`](#help) - Show help information
- [`--version`](#version) - Show version information

---

## 📚 Global Options

All commands support these global options:

```bash
--verbose, -v       # Increase output verbosity
--quiet, -q         # Suppress non-error output
--no-color          # Disable colored output
--config FILE       # Use custom config file (default: .env)
```

---

## 🔧 Commands

### `export`

Export test cases from Testmo to local YAML files.

#### Syntax

```bash
btl_testmo export --project-id ID --output DIR [OPTIONS]
```

#### Required Parameters

- `--project-id ID` - Testmo project ID to export from
- `--output DIR` - Output directory for YAML files

#### Optional Parameters

- `--folder-id ID` - Export specific folder only (default: all folders)
- `--include-attachments` - Download attachments (default: false)
- `--force` - Overwrite existing files without prompting

#### Examples

```bash
# Export complete project
btl_testmo export --project-id 2 --output testmo/oneapp

# Export specific folder
btl_testmo export --project-id 2 --folder-id 7338 --output testmo/oneapp

# Export with attachments
btl_testmo export --project-id 2 --output testmo/oneapp --include-attachments

# Force overwrite existing files
btl_testmo export --project-id 2 --output testmo/oneapp --force
```

#### Output

```
✓ Connected to Testmo (bethinklabs.testmo.net)
✓ Found 162 folders
✓ Found 1334 test cases
✓ Exported 1334 test cases
✓ Created folder structure
✓ Generated metadata (.sync/)
✓ Export complete (duration: 62.4s)

Summary:
  Project: OneApp (ID: 2)
  Folders: 162
  Cases: 1334
  Output: testmo/oneapp/test-cases/
```

#### Exit Codes

- `0` - Success
- `1` - API error (connection, authentication)
- `2` - File system error
- `3` - Invalid parameters

---

### `import`

Import test cases from local YAML files to Testmo.

#### Syntax

```bash
btl_testmo import --project-id ID --source DIR [OPTIONS]
```

#### Required Parameters

- `--project-id ID` - Target Testmo project ID
- `--source DIR` - Source directory with YAML files

#### Optional Parameters

- `--folder-name NAME` - Create cases under this folder (default: create hierarchy)
- `--dry-run` - Show what would be imported without making changes
- `--skip-validation` - Skip YAML validation (not recommended)

#### Examples

```bash
# Import complete directory
btl_testmo import --project-id 9 --source testmo/oneapp

# Import into specific folder
btl_testmo import --project-id 9 --source testmo/oneapp --folder-name "Imported Tests"

# Dry run to preview changes
btl_testmo import --project-id 9 --source testmo/oneapp --dry-run
```

#### Output

```
✓ Validating YAML files (1334 files)
✓ Creating folder structure
✓ Importing test cases (batch mode)
  [============================] 1334/1334 (100%)
✓ Syncing case IDs back to YAML files
✓ Import complete (duration: 58.2s)

Summary:
  Source: testmo/oneapp/test-cases/
  Cases imported: 1334
  Folders created: 162
  Failures: 0
```

#### Exit Codes

- `0` - Success
- `1` - API error
- `2` - Validation error (invalid YAML)
- `3` - Invalid parameters

---

### `update`

Update existing test cases in Testmo from local YAML files.

#### Syntax

```bash
btl_testmo update FILE [FILE...] [OPTIONS]

# OR

btl_testmo update --folder DIR [OPTIONS]
```

#### Required Parameters

One of:
- `FILE [FILE...]` - One or more YAML files to update
- `--folder DIR` - Update all files in directory

#### Optional Parameters

- `--batch` - Use batch mode for multiple files (faster)
- `--dry-run` - Show changes without applying them
- `--force` - Update even if no changes detected

#### Examples

```bash
# Update single file
btl_testmo update testmo/oneapp/test-cases/installation/TC00535-fresh-install.yml

# Update multiple files
btl_testmo update TC00535*.yml TC00536*.yml

# Update entire folder (batch mode)
btl_testmo update --folder testmo/oneapp/test-cases/installation --batch

# Dry run to preview changes
btl_testmo update TC00535*.yml --dry-run
```

#### Output (Single File)

```
✓ Reading TC00535-fresh-install.yml
✓ Detected changes:
  - metadata.name
  - test_case.description (2 lines changed)
✓ Updating case 535 in Testmo
✓ Syncing local metadata
✓ Update complete (duration: 0.2s)
```

#### Output (Batch Mode)

```
✓ Scanning folder for changes
✓ Found 5 modified files
✓ Batch updating (hybrid mode)
  - Common fields (batch): 3 cases (0.3s)
  - Unique fields (individual): 5 cases (1.1s)
✓ Syncing local metadata
✓ Update complete (duration: 1.5s)

Summary:
  Files updated: 5
  API calls: 2 (batch) + 5 (individual)
  Performance: 3.3x faster than individual
```

#### Exit Codes

- `0` - Success
- `1` - API error
- `2` - File not found or not a valid YAML
- `3` - No changes detected (unless --force)

---

### `create`

Create new test cases in Testmo from local YAML files.

#### Syntax

```bash
btl_testmo create FILE [FILE...] [OPTIONS]

# OR

btl_testmo create --folder DIR [OPTIONS]
```

#### Required Parameters

One of:
- `FILE [FILE...]` - One or more TC-NEW-*.yml files
- `--folder DIR` - Create all TC-NEW-*.yml files in directory

#### Optional Parameters

- `--batch` - Use batch mode (recommended for multiple files)
- `--folder-id ID` - Create in specific folder (overrides path detection)
- `--no-rename` - Don't rename TC-NEW-* after creation

#### Examples

```bash
# Create single file
btl_testmo create testmo/oneapp/test-cases/installation/TC-NEW-my-test.yml

# Create multiple files (batch mode)
btl_testmo create TC-NEW-*.yml --batch

# Create in specific folder
btl_testmo create TC-NEW-test.yml --folder-id 7338

# Create without auto-rename
btl_testmo create TC-NEW-test.yml --no-rename
```

#### Output (Single File)

```
✓ Reading TC-NEW-my-test.yml
✓ Validating YAML format
✓ Detecting folder from path: installation (ID: 123)
✓ Creating case in Testmo
✓ Case created (ID: 66500)
✓ Renaming file: TC-NEW-my-test.yml → TC66500-my-test.yml
✓ Syncing metadata to YAML
✓ Create complete (duration: 0.3s)

New case URL: https://bethinklabs.testmo.net/repositories/2/cases/66500
```

#### Output (Batch Mode)

```
✓ Scanning folder for TC-NEW-*.yml files
✓ Found 5 new test cases
✓ Validating YAML files
✓ Batch creating (true batch mode)
✓ Created 5 cases (IDs: 66306-66310)
✓ Renaming files
✓ Syncing metadata
✓ Create complete (duration: 0.4s)

Summary:
  Files created: 5
  Performance: 3.3x faster than individual
  Case IDs: 66306, 66307, 66308, 66309, 66310
```

#### Exit Codes

- `0` - Success
- `1` - API error
- `2` - Validation error
- `3` - File already has case_id (not TC-NEW-*)

---

### `sync`

Bidirectional smart sync between local YAML files and Testmo.

#### Syntax

```bash
btl_testmo sync --project DIR [OPTIONS]
```

#### Required Parameters

- `--project DIR` - Project directory (e.g., testmo/oneapp)

#### Optional Parameters

- `--direction DIRECTION` - Sync direction: `both`, `push`, `pull` (default: both)
- `--resolve STRATEGY` - Conflict resolution: `ask`, `local`, `remote` (default: ask)
- `--dry-run` - Show what would be synced without making changes

#### Examples

```bash
# Bidirectional sync with conflict prompts
btl_testmo sync --project testmo/oneapp

# Push local changes only
btl_testmo sync --project testmo/oneapp --direction push

# Pull remote changes only
btl_testmo sync --project testmo/oneapp --direction pull

# Auto-resolve conflicts (prefer local)
btl_testmo sync --project testmo/oneapp --resolve local

# Dry run to preview changes
btl_testmo sync --project testmo/oneapp --dry-run
```

#### Output

```
✓ Scanning local files (1334 files)
✓ Computing content hashes
✓ Comparing with Testmo
✓ Detected changes:
  - Local changes: 3 files
  - Remote changes: 1 file
  - Conflicts: 0 files

✓ Pushing local changes (batch mode)
  [============================] 3/3 (100%)
✓ Pulling remote changes
  [============================] 1/1 (100%)
✓ Updating hashes and timestamps
✓ Sync complete (duration: 2.1s)

Summary:
  Pushed: 3 cases
  Pulled: 1 case
  Conflicts: 0
```

#### Conflict Resolution

When conflicts are detected (same case changed locally and remotely):

```
⚠ Conflict detected: TC00535-fresh-install.yml

Local changes:
  - metadata.name: "Fresh Install" → "Fresh Install Test"

Remote changes:
  - test_case.description: Updated in Testmo

Resolution options:
  1. Keep local (overwrite Testmo)
  2. Keep remote (overwrite local)
  3. Skip this case
  4. Show full diff

Choice [1-4]:
```

#### Exit Codes

- `0` - Success (no conflicts or all resolved)
- `1` - API error
- `2` - Unresolved conflicts (when --resolve not specified)
- `3` - Invalid parameters

---

### `status`

Show sync status and detect local/remote changes.

#### Syntax

```bash
btl_testmo status --project DIR [OPTIONS]
```

#### Required Parameters

- `--project DIR` - Project directory

#### Optional Parameters

- `--detailed` - Show detailed diff for each change
- `--remote` - Check remote changes (requires API call)

#### Examples

```bash
# Quick local status
btl_testmo status --project testmo/oneapp

# Detailed status with diffs
btl_testmo status --project testmo/oneapp --detailed

# Include remote changes
btl_testmo status --project testmo/oneapp --remote
```

#### Output

```
Project: OneApp (testmo/oneapp)
Total files: 1334

Local changes (not pushed):
  modified: TC00535-fresh-install.yml
  modified: TC00536-upgrade.yml
  modified: TC00537-reinstall.yml

Remote changes (not pulled):
  modified: TC00600-login.yml

Clean files: 1330

Sync recommendation: Run 'btl_testmo sync --project testmo/oneapp'
```

#### Exit Codes

- `0` - Clean (no changes)
- `1` - Changes detected
- `2` - API error (when --remote used)

---

### `validate`

Validate YAML file format and structure.

#### Syntax

```bash
btl_testmo validate FILE [FILE...] [OPTIONS]

# OR

btl_testmo validate --folder DIR [OPTIONS]
```

#### Required Parameters

One of:
- `FILE [FILE...]` - One or more YAML files
- `--folder DIR` - Validate all YAML files in directory

#### Optional Parameters

- `--fix` - Auto-fix common issues
- `--strict` - Enable strict validation (all optional fields required)

#### Examples

```bash
# Validate single file
btl_testmo validate TC00535-fresh-install.yml

# Validate multiple files
btl_testmo validate TC00535*.yml

# Validate entire folder
btl_testmo validate --folder testmo/oneapp/test-cases

# Auto-fix issues
btl_testmo validate TC00535*.yml --fix
```

#### Output (Valid File)

```
✓ TC00535-fresh-install.yml
  - All required fields present
  - Field types correct
  - Steps format valid
  - No issues found
```

#### Output (Invalid File)

```
✗ TC00536-upgrade.yml
  Errors:
    - Missing required field: metadata.name
    - Invalid type for metadata.priority (expected string, got int)
    - Steps[2].expected is empty
  Warnings:
    - testmo.case_id is null (not synced yet?)

Summary: 1 file validated, 1 error, 1 warning
```

#### Exit Codes

- `0` - All files valid
- `1` - Validation errors found
- `2` - File not found or not YAML

---

### `--help`

Show help information for btl_testmo or specific commands.

#### Syntax

```bash
btl_testmo --help
btl_testmo COMMAND --help
```

#### Examples

```bash
# General help
btl_testmo --help

# Command-specific help
btl_testmo export --help
btl_testmo update --help
```

---

### `--version`

Show version information.

#### Syntax

```bash
btl_testmo --version
```

#### Output

```
BTL Testmo CLI v1.0.0
Python: 3.11.5
Platform: darwin (macOS 14.2)
```

---

## 🔥 Common Workflows

### Daily Developer Workflow

```bash
# 1. Pull latest changes
btl_testmo sync --project testmo/oneapp --direction pull

# 2. Edit test cases locally
vim testmo/oneapp/test-cases/**/*.yml

# 3. Validate changes
btl_testmo validate --folder testmo/oneapp/test-cases

# 4. Push changes
btl_testmo sync --project testmo/oneapp --direction push
```

### Batch Creation Workflow

```bash
# 1. Create multiple TC-NEW-*.yml files

# 2. Validate all new files
btl_testmo validate TC-NEW-*.yml

# 3. Batch create (fast)
btl_testmo create TC-NEW-*.yml --batch

# 4. Verify files renamed
ls TC*.yml
```

### Migration Workflow

```bash
# 1. Export from old project
btl_testmo export --project-id 2 --output backup/

# 2. Validate export
btl_testmo validate --folder backup/test-cases

# 3. Import to new project
btl_testmo import --project-id 9 --source backup/

# 4. Verify import
btl_testmo status --project backup/ --remote
```

---

## 🐛 Error Messages

### Common Errors

**Error:** `TESTMO_API_KEY not set`
**Solution:** Create `.env` file with API key

**Error:** `Project ID X not found`
**Solution:** Verify project ID in Testmo UI

**Error:** `Permission denied for project X`
**Solution:** Check API key has correct access level

**Error:** `File TC00535-*.yml not found`
**Solution:** Verify file path is correct (use absolute path or cd to directory)

**Error:** `Case ID 535 not found in Testmo`
**Solution:** Case may have been deleted, run sync to detect orphaned files

---

## 📊 Performance Tips

1. **Use batch mode** for multiple operations (3-5x faster)
2. **Validate locally** before pushing to catch errors early
3. **Use --dry-run** to preview operations
4. **Sync regularly** to avoid large merges
5. **Filter with --folder-id** to work with subsets

---

## 📚 See Also

- [YAML Format Specification](YAML_FORMAT.md)
- [Workflows Guide](WORKFLOWS.md)
- [Architecture Documentation](ARCHITECTURE.md)
- [Troubleshooting Guide](TROUBLESHOOTING.md)

---

**CLI Reference complete** ✅
