# Claude Code Agent Guide

**Agent Type:** Terminal-based AI coding agent
**Access:** Direct file and command execution
**Best For:** File manipulation, batch operations, validations

---

## 🎯 What is Claude Code?

Claude Code is a terminal-based AI agent that can:
- **Read/Write Files** - Direct access to test case YAML files
- **Execute Commands** - Run Python scripts, bash commands, validations
- **Multi-file Operations** - Batch updates across test suites
- **No External Dependencies** - Works immediately, no MCP setup needed

---

## 🚀 Getting Started

### Prerequisites

```bash
# Verify Claude Code is installed
claude-code --version

# Navigate to project
cd /path/to/BTL-TestCases

# Start Claude Code session
claude-code
```

That's it! No additional configuration needed.

---

## 📋 Core Workflows

### Workflow 1: Improve Single Test Case

**Goal:** Make test case TC66186 more specific and detailed

**Prompt:**
```
Improve test case TC66186 with detailed steps:

File: testmo/oneapp/test-cases/home/charge/v2l-vehicle-to-load/TC66186-v2l-screen.yml

Changes needed:
1. Add preconditions:
   - Vehicle: Nissan ARIYA 2024
   - Battery level: > 50%
   - Vehicle state: Parked (P)
   - V2L device: Connected

2. Expand steps from 3 → 6 steps:
   - Be specific about UI elements
   - Include actual text/labels
   - Add expected timing (e.g., "updates every 1 second")

3. Add edge case section:
   - Low battery scenario (< 20%)

4. Preserve testmo: section (do NOT modify case_id, etc.)

5. Update file directly
```

**What Claude Code Does:**
1. Reads current YAML file
2. Analyzes structure
3. Enhances content with specifics
4. Preserves all metadata
5. Writes updated file
6. Shows diff of changes

**Result:** Test upgraded in ~2 minutes

---

### Workflow 2: Create Similar Test Cases

**Goal:** Generate 5 V2L test variations from template

**Prompt:**
```
Create 5 similar test cases based on TC66186-v2l-screen.yml

Variations to create:
1. TC-NEW-v2l-low-battery.yml
   - Scenario: Battery < 20%, V2L should warn/disable

2. TC-NEW-v2l-vehicle-moving.yml
   - Scenario: V2L active, vehicle starts moving

3. TC-NEW-v2l-overnight.yml
   - Scenario: V2L active for extended period (8+ hours)

4. TC-NEW-v2l-emergency-stop.yml
   - Scenario: Emergency disconnect button

5. TC-NEW-v2l-multiple-devices.yml
   - Scenario: Multiple devices drawing power simultaneously

Requirements for each:
- Use TC66186 as template
- Change description and steps for scenario
- Add unique preconditions
- Keep structure (metadata, test_case, testmo sections)
- Save to same folder: testmo/oneapp/test-cases/home/charge/v2l-vehicle-to-load/
- Leave testmo: section empty (will populate on upload)

After creation, validate:
btl_testmo validate testmo/oneapp/test-cases/home/charge/v2l-vehicle-to-load/TC-NEW-*.yml
```

**Result:** 5 new tests in ~5 minutes (vs 2.5 hours manually)

---

### Workflow 3: Bulk Tag Update

**Goal:** Add "release-5.2" tag to all V2L tests

**Prompt:**
```
Add "release-5.2" tag to all test cases in V2L folder

Folder: testmo/oneapp/test-cases/home/charge/v2l-vehicle-to-load/

Process:
1. Find all .yml files in folder (recursively if subfolders)
2. For each file:
   - Read YAML
   - Check if "release-5.2" already in metadata.tags
   - If not, append to tags array
   - Maintain existing tags
   - Write file

3. Report:
   - Files processed: X
   - Files updated: Y
   - Files skipped (already had tag): Z

After updates, validate:
btl_testmo validate testmo/oneapp/test-cases/home/charge/v2l-vehicle-to-load/
```

**Result:** 15 files tagged in ~30 seconds

---

### Workflow 4: Quality Audit

**Goal:** Find quality issues across test suite

**Prompt:**
```
Audit test cases in installation folder for quality issues

Folder: testmo/oneapp/test-cases/installation/

Quality checks:
1. Missing preconditions (empty or < 2 items)
2. Vague steps (keywords: "test", "check", "verify" without specifics)
3. Missing expected results (empty or "it works")
4. Missing configurations (empty array)
5. Outdated API versions (check for "v1", "old")

Output format:
## Quality Audit Report - Installation Tests

### Critical Issues (Block Release)
- **TC12345**: Missing preconditions entirely
- **TC12346**: Step "test the feature" too vague

### Medium Issues (Should Fix)
- **TC12347**: Only 1 precondition, should have more
- **TC12348**: Expected result "works" not specific

### Low Issues (Nice to Have)
- **TC12349**: Could add more edge cases

### Summary
- Total files audited: X
- Files with issues: Y (Z%)
- Critical: A, Medium: B, Low: C

### Recommendations
1. Focus on critical issues first
2. [Specific suggestion based on patterns]
```

**Result:** 50 files audited in ~2 minutes

---

### Workflow 5: Format Standardization

**Goal:** Ensure consistent format across folder

**Prompt:**
```
Standardize format for all test cases in login-flow folder

Folder: testmo/oneapp/test-cases/login-flow/

Standard format:
1. Description: Clear overview (2-3 sentences)
2. Preconditions: Bulleted list (at least 2 items)
3. Steps: Numbered, each with "step" and "expected"
4. Configurations: Array with at least "iOS, Prod" and "Android, Prod"
5. Notes: Optional, but if present, use markdown sections (## headers)

Process each file:
- Read YAML
- Check against standards
- Fix formatting issues
- Preserve content (don't change meaning)
- Preserve testmo: section
- Write back

Report:
- Files standardized: X
- Issues fixed per type: [breakdown]
```

**Result:** Consistent format across 30 files in ~5 minutes

---

## 🎨 Advanced Workflows

### Create Test Suite from Requirements

**Prompt:**
```
Create comprehensive test suite for new V2X feature

Context:
- Feature: Vehicle to Everything (V2X)
- Combines V2L + V2G + V2H
- Reference existing tests in:
  * testmo/oneapp/test-cases/home/charge/v2l-vehicle-to-load/
  * testmo/oneapp/test-cases/home/charge/v2g-vehicle-to-grid/

Output:
Folder: testmo/oneapp/test-cases/home/charge/v2x-vehicle-to-everything/

Test categories (20 tests total):
1. Core functionality (6 tests):
   - V2X mode selection
   - Power flow management
   - Status monitoring
   - Mode switching
   - Emergency stop
   - System health check

2. Integration tests (5 tests):
   - V2L device compatibility
   - V2G grid connection
   - V2H home integration
   - Multi-mode scenarios
   - Billing/metering

3. Error handling (5 tests):
   - Connection failures
   - Power interruption
   - Grid instability
   - Device overload
   - Communication errors

4. Edge cases (4 tests):
   - Low battery behavior
   - Extreme temperatures
   - Network latency
   - Long duration sessions

Each test should have:
- Comprehensive description
- 4+ preconditions
- 5-7 detailed steps with expected results
- Platform configurations (iOS/Android)
- Notes with technical details

File naming: TC-NEW-v2x-[scenario].yml

After creation:
1. Validate all: btl_testmo validate [folder]
2. Report file count and any validation errors
```

**Result:** 20-test suite in ~20 minutes (vs 10+ hours)

---

### Generate Regression Tests from Git History

**Prompt:**
```
Generate regression test cases from recent bug fixes in git

Steps:
1. Search git log for bug fix commits:
   git log --all --grep="fix\|bug" --since="3 months ago" --oneline

2. For each relevant commit:
   - Read commit message
   - Identify affected feature/file
   - Create regression test:
     * Name: "Regression: [Brief description]"
     * Description: "Verify bug from commit [hash] is fixed"
     * Steps: Reproduce original bug scenario
     * Expected: Bug no longer occurs
     * Tags: ["regression", "bug-fix"]
     * Notes: Link to commit

3. Group tests by feature/folder

4. Create YAML files:
   - Filename: TC-NEW-regression-[commit-hash-short].yml
   - Place in appropriate feature folder

5. Report:
   - Commits analyzed: X
   - Tests created: Y
   - Grouped by folder: [list]

After creation, validate and show summary.
```

---

### Migrate from Excel/CSV

**Prompt:**
```
Migrate test cases from Excel file to YAML format

Input: tests-export.xlsx (in project root)

Column mapping:
- "Test ID" → preserve in notes
- "Test Name" → metadata.name
- "Priority" (High/Medium/Low) → metadata.priority
- "Feature" → folder structure
- "Description" → test_case.description
- "Steps" (multiline) → test_case.steps (parse)
- "Tags" (comma-separated) → metadata.tags

Process:
1. Read Excel file using pandas or openpyxl
2. For each row:
   - Map fields to YAML structure
   - Infer folder from "Feature" column (slugify)
   - Parse steps (look for numbered list or line breaks)
   - Create TC-NEW-[slugified-name].yml

3. Folder structure:
   testmo/oneapp/test-cases/[feature-folder]/TC-NEW-[name].yml

4. Add migration metadata to notes:
   ```
   ## Migration Info
   - Original ID: [Excel Test ID]
   - Migrated: 2026-01-30
   - Source: tests-export.xlsx
   ```

5. Validate all created files

6. Report:
   - Total rows: X
   - Tests created: Y
   - Validation errors: Z (list files)
   - Grouped by folder: [breakdown]
```

---

## 🔧 Command Reference

### Validation

```bash
# Validate single file
btl_testmo validate testmo/oneapp/test-cases/folder/TC123.yml

# Validate folder
btl_testmo validate testmo/oneapp/test-cases/folder/

# Validate with auto-fix
btl_testmo validate testmo/oneapp/test-cases/folder/ --fix

# Verbose output
btl_testmo validate testmo/oneapp/test-cases/folder/ --verbose
```

### Status Check

```bash
# Check for local changes
btl_testmo status testmo/oneapp/

# Show changed files
btl_testmo status testmo/oneapp/ --verbose
```

### Upload New Tests

```bash
# Create new tests in Testmo (TC-NEW-* only)
btl_testmo create --folder testmo/oneapp/test-cases/feature/ --new-only

# Create with specific project ID
btl_testmo create --project-id 2 --folder testmo/oneapp/test-cases/feature/
```

---

## 💡 Tips & Tricks

### Prompt Engineering

**✅ Good Prompt:**
```
Improve TC66186 by:
1. Adding 3 preconditions (vehicle, battery, state)
2. Expanding 3 steps → 6 steps with UI specifics
3. Adding low battery edge case
4. Preserving testmo: section
File: testmo/oneapp/.../TC66186-v2l-screen.yml
```

**❌ Bad Prompt:**
```
Make TC66186 better
```

### File Path Patterns

```bash
# Glob patterns work
testmo/oneapp/test-cases/**/*.yml

# Relative from repo root
testmo/oneapp/test-cases/home/TC123.yml

# Use tab completion
testmo/oneapp/test-cases/[TAB]
```

### Batch Operations

```bash
# Find files first
find testmo/oneapp/test-cases -name "*v2l*.yml"

# Then operate on them
# Claude can process results and update each file
```

---

## 🐛 Troubleshooting

### Issue: "File not found"

**Cause:** Wrong path or file doesn't exist

**Solution:**
```bash
# Verify file exists
ls -la testmo/oneapp/test-cases/folder/TC123.yml

# Check current directory
pwd

# Should be in BTL-TestCases root
cd /path/to/BTL-TestCases
```

### Issue: "YAML syntax error after edit"

**Cause:** Indentation or special characters

**Solution:**
```bash
# Validate YAML syntax
python -c "import yaml; print(yaml.safe_load(open('TC123.yml')))"

# Use git to revert if broken
git checkout testmo/oneapp/test-cases/folder/TC123.yml

# Ask Claude to fix:
"Fix YAML syntax errors in TC123.yml"
```

### Issue: "testmo metadata got modified"

**Cause:** Agent changed testmo: section

**Solution:**
```bash
# Revert file
git checkout testmo/oneapp/test-cases/folder/TC123.yml

# Remind Claude:
"Do NOT modify the testmo: section with case_id, project_id, etc.
Only modify metadata: and test_case: sections."
```

---

## 📊 Performance Tips

### Parallel Operations

Claude Code can process multiple files, but for large batches:

```
Process files in batches of 10-20 for stability
Allow 2-3 seconds per file for complex operations
Validate after each batch
```

### Large Test Suites

```
For 100+ files:
1. Start with quality audit (read-only)
2. Identify top issues
3. Fix in smaller batches
4. Validate after each batch
5. Commit incrementally
```

---

## 🎓 Learning Path

**Day 1:** Practice Workflow 1 (Improve single test)
**Day 2:** Try Workflow 2 (Create similar tests)
**Day 3:** Master Workflow 3 (Bulk updates)
**Week 2:** Advanced workflows (test suite creation)
**Week 3:** Custom workflows for your team

---

## 📚 Related Documentation

- **[How-To Guide](../HOW_TO_GUIDE.md)** - More workflow examples with prompts
- **[Best Practices](BEST_PRACTICES.md)** - Optimization and troubleshooting
- **[Architecture](../ARCHITECTURE.md)** - Technical details

---

**Ready to start?**

Try Workflow 1 right now with one of your test cases. You'll see results in minutes!

Questions? See [BEST_PRACTICES.md](BEST_PRACTICES.md) for more help.
