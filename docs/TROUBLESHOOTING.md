# Troubleshooting Guide

**Version:** 1.0.0
**Last Updated:** 2026-01-30

---

## 🎯 Overview

This guide covers common issues, error messages, and solutions for the BTL TestCases Framework. Issues are organized by category with step-by-step resolution instructions.

---

## 📋 Table of Contents

1. [Installation Issues](#installation-issues)
2. [Authentication & API Issues](#authentication--api-issues)
3. [Sync & Export Issues](#sync--export-issues)
4. [File & YAML Issues](#file--yaml-issues)
5. [Performance Issues](#performance-issues)
6. [Git Integration Issues](#git-integration-issues)
7. [MCP Server Issues](#mcp-server-issues)

---

## 🔧 Installation Issues

### Issue: `ModuleNotFoundError: No module named 'yaml'`

**Cause:** Dependencies not installed

**Solution:**
```bash
# Install all dependencies
pip install -r requirements.txt

# Or install just the missing module
pip install pyyaml

# Verify installation
python3 -c "import yaml; print('✓ PyYAML installed')"
```

---

### Issue: `python: command not found`

**Cause:** Python not installed or not in PATH

**Solution:**
```bash
# Check if python3 is available
python3 --version

# If not installed, install Python 3.8+
# macOS
brew install python3

# Ubuntu/Debian
sudo apt-get install python3 python3-pip

# Verify
python3 --version
# Expected: Python 3.8+ or higher
```

---

### Issue: `Permission denied: scripts/btl_testmo.py`

**Cause:** Script not executable

**Solution:**
```bash
# Make script executable
chmod +x scripts/btl_testmo.py

# Verify
ls -l scripts/btl_testmo.py
# Should show: -rwxr-xr-x
```

---

## 🔐 Authentication & API Issues

### Issue: `TESTMO_API_KEY not set`

**Cause:** Missing API key in environment

**Solution:**
```bash
# 1. Check if .env file exists
ls -la .env
# If not, create it

# 2. Add API key to .env
cat > .env << 'EOF'
TESTMO_API_KEY=your_api_key_here
TESTMO_INSTANCE=bethinklabs
TESTMO_URL=https://bethinklabs.testmo.net
EOF

# 3. Secure the file
chmod 600 .env

# 4. Test
python3 -c "
from dotenv import load_dotenv
import os
load_dotenv()
print('API Key:', os.getenv('TESTMO_API_KEY')[:10] + '...')
"
```

**Get API Key:**
1. Log in to Testmo
2. Go to Profile → API Keys
3. Create new key or copy existing
4. Paste into .env file

---

### Issue: `401 Unauthorized`

**Cause:** Invalid or expired API key

**Solution:**
```bash
# 1. Verify API key is correct
cat .env | grep TESTMO_API_KEY

# 2. Test API key directly
curl -H "Authorization: Bearer YOUR_API_KEY" \
  https://bethinklabs.testmo.net/api/v1/projects

# 3. If 401 error, regenerate API key in Testmo:
# - Log in to Testmo
# - Profile → API Keys → Regenerate
# - Update .env with new key
```

---

### Issue: `403 Forbidden - Project ID X`

**Cause:** API key lacks permission for project

**Solution:**
```bash
# 1. Check your access in Testmo UI
# Can you see the project? If not, request access

# 2. Verify project ID is correct
# Projects → Your Project → URL shows project ID

# 3. Check API key permissions
# Some keys may have read-only access

# 4. Use correct project ID
btl_testmo export --project-id 2  # OneApp
# NOT: --project-id 9 (BTL-TestCases, testing only)
```

---

## 🔄 Sync & Export Issues

### Issue: `No test cases found in project`

**Cause:** Wrong project ID or empty project

**Solution:**
```bash
# 1. Verify project ID in Testmo UI
# URL format: /repositories/{project_id}

# 2. Check project has test cases
# Open project in Testmo, verify cases exist

# 3. Try exporting specific folder
btl_testmo export \
  --project-id 2 \
  --folder-id 7338 \
  --output testmo/test

# 4. Check MCP connection
# Ensure Claude Desktop is running with Testmo MCP
```

---

### Issue: `MCP server connection failed`

**Cause:** MCP server not configured or not running

**Solution:**
```bash
# 1. Verify Claude Desktop is running
ps aux | grep Claude

# 2. Check MCP configuration
# Claude Desktop → Settings → Developer → MCP Servers
# Should show: testmo MCP server

# 3. Restart Claude Desktop

# 4. Test MCP connection (in Claude Desktop)
"List Testmo projects"
# Claude should be able to list projects

# 5. If still failing, reconfigure MCP
# See: https://docs.testmo.com/mcp-server
```

---

### Issue: `Export only got 100/162 folders`

**Cause:** Using REST API instead of MCP

**Solution:**
```bash
# MCP has auto-pagination and gets ALL folders
# REST API has pagination limit

# Ensure using MCP for reads:
btl_testmo export --project-id 2 --output testmo/oneapp
# (Framework uses MCP automatically for export)

# If export incomplete:
# 1. Check MCP connection
# 2. Try export again
# 3. Verify folder count in Testmo UI matches export
```

---

### Issue: `Hash mismatch detected`

**Cause:** File was modified outside of framework

**Solution:**
```bash
# 1. View what changed
btl_testmo status --project testmo/oneapp --detailed

# 2. If changes are intentional, update Testmo
btl_testmo update TC00535-*.yml

# 3. If changes were accidental, revert
git checkout TC00535-*.yml

# 4. Resync to update hashes
btl_testmo sync --project testmo/oneapp

# To force update without hash check:
btl_testmo update TC00535-*.yml --force
```

---

## 📄 File & YAML Issues

### Issue: `YAML validation failed: Missing required field`

**Cause:** YAML file missing required fields

**Solution:**
```bash
# 1. Run validator to see all errors
btl_testmo validate TC00535-fresh-install.yml

# Example output:
# ✗ TC00535-fresh-install.yml
#   Errors:
#     - Missing required field: metadata.name
#     - Missing required field: test_case.steps

# 2. Add missing fields
vim TC00535-fresh-install.yml

# 3. Validate again
btl_testmo validate TC00535-fresh-install.yml

# 4. Or use auto-fix (careful!)
btl_testmo validate TC00535-fresh-install.yml --fix
```

**Required Fields:**
- `metadata.name`
- `metadata.priority`
- `test_case.description`
- `test_case.steps` (at least one step)
- `testmo.case_id` (can be null for new cases)
- `testmo.folder_id`
- `testmo.project_id`

---

### Issue: `Invalid YAML syntax`

**Cause:** Malformed YAML (indentation, quotes, etc.)

**Solution:**
```bash
# 1. Check YAML syntax
python3 -c "import yaml; yaml.safe_load(open('TC00535.yml'))"

# 2. Common issues:

# Wrong indentation
metadata:
 name: "Test"  # Should be 2 spaces
  priority: "high"  # Inconsistent (3 spaces)

# Missing colon
metadata
  name: "Test"  # Missing colon after metadata

# Wrong multiline format
description:
  This is wrong  # Missing |

# Correct:
description: |
  This is correct

# 3. Use YAML linter
pip install yamllint
yamllint TC00535.yml

# 4. Fix and validate
btl_testmo validate TC00535.yml
```

---

### Issue: `File TC-NEW-*.yml still has TC-NEW- prefix after create`

**Cause:** File rename failed or --no-rename flag used

**Solution:**
```bash
# 1. Check if case was created in Testmo
# (Look for case_id in testmo section of YAML)

# 2. If case_id exists, manually rename
case_id=$(grep 'case_id:' TC-NEW-test.yml | awk '{print $2}')
mv TC-NEW-test.yml TC${case_id}-test.yml

# 3. If case_id is null, case wasn't created
# Try creating again:
btl_testmo create TC-NEW-test.yml

# 4. Check for errors in output
```

---

## ⚡ Performance Issues

### Issue: `Export taking longer than 2 minutes`

**Cause:** Large project or slow network

**Solution:**
```bash
# 1. Check network speed
ping bethinklabs.testmo.net

# 2. Export specific folder first
btl_testmo export \
  --project-id 2 \
  --folder-id 7338 \
  --output testmo/oneapp/test

# 3. Use verbose mode to see progress
btl_testmo export --project-id 2 --output testmo/oneapp --verbose

# 4. If network is slow, consider:
# - Export during off-peak hours
# - Export in chunks (folder by folder)
# - Increase timeout if framework supports it

# Expected performance:
# - 1334 cases: ~60 seconds
# - 5000 cases: ~3-4 minutes
```

---

### Issue: `Update is slow (>1 second per case)`

**Cause:** Not using batch mode

**Solution:**
```bash
# Slow: Individual updates
for file in TC*.yml; do
  btl_testmo update "$file"  # ~223ms each
done
# Total for 10 files: ~2.3 seconds

# Fast: Batch update
btl_testmo update --folder testmo/oneapp/test-cases/folder --batch
# Total for 10 files: ~500ms (4.6x faster)

# Use batch mode whenever updating multiple files:
btl_testmo update TC*.yml --batch
```

---

### Issue: `Sync is hanging`

**Cause:** Large number of conflicts or network timeout

**Solution:**
```bash
# 1. Kill hanging process
pkill -f btl_testmo

# 2. Check what's changed
btl_testmo status --project testmo/oneapp

# 3. Sync in one direction first
# Pull only:
btl_testmo sync --project testmo/oneapp --direction pull

# Push only:
btl_testmo sync --project testmo/oneapp --direction push

# 4. Use dry-run to preview
btl_testmo sync --project testmo/oneapp --dry-run

# 5. If many conflicts, resolve manually
# Export fresh copy, manually merge, then force push
```

---

## 🔀 Git Integration Issues

### Issue: `Git merge conflict in YAML file`

**Cause:** Same file edited in different branches

**Solution:**
```bash
# 1. View conflict
git status
# Shows: both modified: TC00535-fresh-install.yml

# 2. Open file and look for markers
vim TC00535-fresh-install.yml

# 3. Conflict markers look like:
<<<<<<< HEAD
metadata:
  name: "Your Version"
=======
metadata:
  name: "Their Version"
>>>>>>> feature/branch

# 4. Choose version or merge manually
# Remove markers, keep desired content

# 5. Validate merged file
btl_testmo validate TC00535-fresh-install.yml

# 6. Mark as resolved
git add TC00535-fresh-install.yml
git commit -m "Merge: Resolve conflict in TC00535"
```

---

### Issue: `.sync/ files committed to git`

**Cause:** .sync/ not in .gitignore

**Solution:**
```bash
# 1. Check .gitignore
grep ".sync" .gitignore

# 2. If not present, add:
cat >> .gitignore << 'EOF'
# Sync metadata (auto-generated)
testmo/*/.sync/sync-log.jsonl
testmo/*/.sync/case-map.json
testmo/*/.sync/folder-map.json
EOF

# 3. Remove from git (keep local)
git rm --cached testmo/oneapp/.sync/*.json
git rm --cached testmo/oneapp/.sync/*.jsonl

# 4. Commit
git commit -m "Remove .sync files from git tracking"

# Keep project.json in git (has static config)
```

---

## 🖥️ MCP Server Issues

### Issue: `MCP tool call failed`

**Cause:** MCP server error or timeout

**Solution:**
```bash
# 1. Check Claude Desktop logs
# macOS: ~/Library/Logs/Claude/
# Look for MCP-related errors

# 2. Restart MCP server
# Claude Desktop → Settings → Developer → MCP Servers
# Click refresh or restart Claude Desktop

# 3. Test MCP connection
# In Claude Desktop, try:
"List all Testmo projects"

# 4. If persistent, check MCP server version
# Ensure using latest Testmo MCP server

# 5. Fall back to REST API (temporary)
# Export using legacy script:
python scripts/legacy/testmo_export.py --project-id 2 --output temp/
```

---

### Issue: `MCP returns wrong data`

**Cause:** MCP server bug or stale cache

**Solution:**
```bash
# 1. Clear MCP cache (if applicable)
# Restart Claude Desktop

# 2. Verify data in Testmo UI
# Check if case exists and data matches

# 3. Use REST API to verify
curl -H "Authorization: Bearer YOUR_KEY" \
  https://bethinklabs.testmo.net/api/v1/projects/2/cases/535

# 4. Report bug if data is incorrect
# Include: case_id, expected vs actual data

# 5. Workaround: use legacy scripts
python scripts/legacy/testmo_export.py ...
```

---

## 🐛 Common Error Messages

### `Error: Case ID X not found`

**Cause:** Case deleted in Testmo or wrong project_id

**Solution:**
```bash
# Check if case exists in Testmo UI
# If deleted, remove YAML file or update metadata

# If case exists, verify project_id in YAML matches:
grep "project_id:" TC00535-*.yml
# Should be: project_id: 2 (for OneApp)
```

---

### `Error: Folder ID X not found`

**Cause:** Folder deleted or invalid folder_id in YAML

**Solution:**
```bash
# 1. List all folders
btl_testmo export --project-id 2 --output temp-folders/

# 2. Check folder-map.json
cat testmo/oneapp/.sync/folder-map.json | jq .

# 3. Update folder_id in YAML
vim TC00535-*.yml
# Change folder_id to valid folder

# 4. Update in Testmo
btl_testmo update TC00535-*.yml
```

---

### `Error: Batch create failed with 422`

**Cause:** Invalid data or missing required fields

**Solution:**
```bash
# 1. Validate all files first
btl_testmo validate TC-NEW-*.yml

# 2. Fix validation errors

# 3. Check API payload
# Enable verbose mode to see request
btl_testmo create TC-NEW-*.yml --batch --verbose

# 4. Common 422 causes:
# - Missing name
# - Invalid priority value
# - Missing steps
# - Wrong data type (int instead of string)
```

---

## 🔍 Debug Mode

### Enable Verbose Logging

```bash
# Add to .env
DEBUG=true
LOG_LEVEL=DEBUG

# Or run with verbose flag
btl_testmo export --project-id 2 --output testmo/oneapp --verbose

# See detailed output:
# - API requests and responses
# - File operations
# - Hash computations
# - Error stack traces
```

---

## 📞 Getting More Help

### 1. Check Documentation

- [Getting Started](GETTING_STARTED.md) - Setup and basics
- [CLI Reference](CLI_REFERENCE.md) - Command documentation
- [YAML Format](YAML_FORMAT.md) - File format spec
- [Workflows](WORKFLOWS.md) - Common patterns
- [Architecture](ARCHITECTURE.md) - How it works

### 2. Check Logs

```bash
# Framework logs (if enabled)
tail -f logs/btl_testmo.log

# Python errors
python3 scripts/btl_testmo.py 2>&1 | tee error.log

# MCP logs (Claude Desktop)
# macOS: ~/Library/Logs/Claude/
```

### 3. Verify Environment

```bash
# Run diagnostic script
cat > diagnose.sh << 'EOF'
#!/bin/bash
echo "=== BTL TestCases Diagnostic ==="
echo ""
echo "Python version:"
python3 --version
echo ""
echo "Installed packages:"
pip list | grep -E "(requests|yaml|dotenv)"
echo ""
echo ".env file exists:"
test -f .env && echo "✓ Yes" || echo "✗ No"
echo ""
echo "API key set:"
grep -q "TESTMO_API_KEY" .env && echo "✓ Yes" || echo "✗ No"
echo ""
echo "Test cases directory:"
test -d testmo/oneapp/test-cases && echo "✓ Exists" || echo "✗ Not found"
echo ""
echo "Git status:"
git status --short
EOF

chmod +x diagnose.sh
./diagnose.sh
```

### 4. Report Issues

If issue persists:
1. Run diagnostic script above
2. Capture error output
3. Note what you were trying to do
4. Contact team with:
   - Error message
   - Diagnostic output
   - Steps to reproduce

---

## ✅ Prevention Checklist

Before running operations:

- [ ] API key is set in .env
- [ ] Project ID is correct
- [ ] Files are validated locally
- [ ] MCP connection works (if using export)
- [ ] Git working tree is clean
- [ ] Synced recently (no large merges)
- [ ] Using batch mode for multiple operations
- [ ] Have backups (git + exports)

---

**Troubleshooting Guide complete** ✅
