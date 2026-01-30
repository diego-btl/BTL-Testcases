# MEGA PROMPT 4: Repository Deep Cleanup

**Date:** 2026-01-30
**Phase:** Final Cleanup
**Priority:** CRITICAL
**Estimated Time:** 15-20 minutes

---

## 🎯 OBJECTIVE

Perform a deep cleanup of the BTL-TestCases repository, removing ALL unnecessary files and keeping ONLY:
1. Production-ready code
2. Essential documentation
3. Mega prompts folder
4. Test cases (1340 YAML files)
5. Configuration files

**Everything else must be deleted.**

---

## 🗑️ FILES TO DELETE

### **Root Directory Cleanup**

Delete these files from root:
```bash
rm -f RESTRUCTURE_SUMMARY.md
rm -f DOCUMENTATION_SUMMARY.md
rm -f IMPLEMENTATION_SUMMARY.md
rm -f MCP_COMPARISON.md
rm -f PAGINATION_BUG_FIX.md
rm -f CSV_VS_API_STRUCTURE.md
rm -f *.csv
rm -f *.log
rm -f *.tmp
rm -f .DS_Store
```

### **Legacy/Reference Files**

Delete any remaining old documentation:
```bash
# Check for old docs (if any)
find . -name "*OLD*" -type f -delete
find . -name "*BACKUP*" -type f -delete
find . -name "*.bak" -type f -delete
find . -name "*~" -type f -delete
```

### **Development Artifacts**

Delete Python cache and artifacts:
```bash
# Python cache
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete
find . -type f -name "*.pyo" -delete
find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name ".coverage" -delete
find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
```

### **IDE Files**

Delete IDE-specific files:
```bash
rm -rf .vscode/
rm -rf .idea/
rm -f *.swp
rm -f *.swo
rm -f .DS_Store
find . -name ".DS_Store" -delete
```

### **Git Artifacts**

Clean git artifacts (but keep .gitignore):
```bash
# Remove any stray git files
rm -f .git/index.lock 2>/dev/null || true
```

---

## ✅ FILES TO KEEP

After cleanup, the repository should contain ONLY these:

### **Root Level:**
```
BTL-TestCases/
├── .gitignore              ✅ KEEP
├── .git/                   ✅ KEEP (entire git history)
├── README.md               ✅ KEEP
├── requirements.txt        ✅ KEEP
├── pyproject.toml          ✅ KEEP
└── TESTING_LOG.md          ✅ KEEP (validation proof)
```

### **Scripts (Production Code):**
```
scripts/
├── btl_testmo.py           ✅ KEEP (CLI entry point)
├── testmo_sync/            ✅ KEEP (entire package)
│   ├── __init__.py
│   ├── hasher.py
│   ├── mapper.py
│   ├── validator.py
│   ├── reader.py
│   ├── writer.py
│   ├── converter.py
│   └── sync_engine.py
└── legacy/                 ✅ KEEP (reference scripts)
    ├── README.md
    ├── testmo_client.py
    ├── testmo_export.py
    ├── testmo_import.py
    └── yaml_converter.py
```

### **Documentation:**
```
docs/
├── README.md               ✅ KEEP
├── GETTING_STARTED.md      ✅ KEEP
├── ARCHITECTURE.md         ✅ KEEP
├── CLI_REFERENCE.md        ✅ KEEP
├── YAML_FORMAT.md          ✅ KEEP
├── WORKFLOWS.md            ✅ KEEP
└── TROUBLESHOOTING.md      ✅ KEEP
```

### **Tests:**
```
tests/
├── __init__.py             ✅ KEEP
├── README.md               ✅ KEEP
├── test_hasher.py          ✅ KEEP
├── test_validator.py       ✅ KEEP
└── test_converter.py       ✅ KEEP
```

### **Prompts:**
```
prompts/
├── MEGA_PROMPT_1_RESTRUCTURE_REPOSITORY.md           ✅ KEEP
├── MEGA_PROMPT_2_COMPLETE_DOCUMENTATION.md           ✅ KEEP
├── MEGA_PROMPT_3_CORE_IMPLEMENTATION_PART1.md        ✅ KEEP
├── MEGA_PROMPT_3_CORE_IMPLEMENTATION_PART2.md        ✅ KEEP
├── MEGA_PROMPT_3_CORE_IMPLEMENTATION_PART3.md        ✅ KEEP
└── MEGA_PROMPT_4_DEEP_CLEANUP.md                     ✅ KEEP
```

### **Test Cases (CRITICAL - NEVER DELETE):**
```
testmo/
├── oneapp/
│   ├── .sync/              ✅ KEEP (metadata)
│   │   ├── project.json
│   │   ├── folder-map.json
│   │   ├── case-map.json
│   │   └── sync-log.jsonl
│   └── test-cases/         ✅ KEEP (ALL 1340 YAML files)
│       └── [entire hierarchy]
├── nmex/                   ✅ KEEP (placeholder)
└── nba/                    ✅ KEEP (placeholder)
```

---

## 📋 STEP-BY-STEP CLEANUP

### **PHASE 1: Safety Backup (2 min)**

```bash
# 1. Verify we're in the right place
pwd
# Expected: /Users/diegodelaguila/Projects/BTL-TestCases

# 2. Check git status (should be clean)
git status

# 3. Create safety tag (in case we need to revert)
git tag -a pre-cleanup -m "Before deep cleanup - safety checkpoint"

# 4. Verify test cases count (CRITICAL)
find testmo/oneapp/test-cases -name "*.yml" | wc -l
# Expected: 1340 files
# ⚠️ IF NOT 1340, STOP IMMEDIATELY
```

### **PHASE 2: Delete Root Level Clutter (3 min)**

```bash
# Delete summary files (info now in docs and git history)
rm -f RESTRUCTURE_SUMMARY.md
rm -f DOCUMENTATION_SUMMARY.md  
rm -f IMPLEMENTATION_SUMMARY.md

# Delete analysis files (kept in git history if needed)
rm -f MCP_COMPARISON.md
rm -f PAGINATION_BUG_FIX.md
rm -f CSV_VS_API_STRUCTURE.md

# Delete any CSV files (we use YAML now)
rm -f *.csv

# Delete temp/log files
rm -f *.log
rm -f *.tmp
rm -f *.bak
rm -f *~

# Delete OS files
rm -f .DS_Store
find . -name ".DS_Store" -delete
```

### **PHASE 3: Delete Development Artifacts (3 min)**

```bash
# Python cache
echo "Cleaning Python cache..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete
find . -type f -name "*.pyo" -delete

# Build artifacts
find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name "build" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true

# Test artifacts
find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name ".coverage" -delete
find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true

# Jupyter (if any)
find . -type d -name ".ipynb_checkpoints" -exec rm -rf {} + 2>/dev/null || true
```

### **PHASE 4: Delete IDE Files (2 min)**

```bash
# VSCode
rm -rf .vscode/

# IntelliJ/PyCharm
rm -rf .idea/

# Vim
find . -name "*.swp" -delete
find . -name "*.swo" -delete
find . -name "*.swn" -delete

# Emacs
find . -name "*~" -delete
find . -name "#*#" -delete
```

### **PHASE 5: Clean Empty Directories (2 min)**

```bash
# Find and remove empty directories (except .git and test-cases structure)
find . -type d -empty -not -path "./.git/*" -not -path "./testmo/*/test-cases/*" -delete 2>/dev/null || true
```

### **PHASE 6: Verify Keep List (3 min)**

```bash
# Verify ONLY essential files remain
echo "=== ROOT FILES ==="
ls -1

# Should show only:
# .git/
# .gitignore
# README.md
# requirements.txt
# pyproject.toml
# TESTING_LOG.md
# docs/
# scripts/
# tests/
# prompts/
# testmo/

echo ""
echo "=== SCRIPTS FILES ==="
find scripts -type f -name "*.py" | sort

# Should show only production code (no old scripts except in legacy/)

echo ""
echo "=== DOCS FILES ==="
ls -1 docs/

# Should show only the 7 core docs + README

echo ""
echo "=== TEST FILES ==="
ls -1 tests/

# Should show only test files + README + __init__

echo ""
echo "=== PROMPTS FILES ==="
ls -1 prompts/

# Should show only 6 mega prompts

echo ""
echo "=== TEST CASES COUNT ==="
find testmo/oneapp/test-cases -name "*.yml" | wc -l

# CRITICAL: Must show 1340
```

### **PHASE 7: Update .gitignore (2 min)**

Ensure .gitignore is comprehensive:

```bash
cat > .gitignore << 'EOF'
# BTL-TestCases .gitignore

# Sync metadata (except project.json which can be versioned)
testmo/*/.sync/sync-log.jsonl
testmo/*/.sync/case-map.json
testmo/*/.sync/folder-map.json

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
pip-wheel-metadata/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Testing
.pytest_cache/
.coverage
.coverage.*
htmlcov/
.tox/
.nox/
coverage.xml
*.cover
.hypothesis/

# Type checking
.mypy_cache/
.dmypy.json
dmypy.json
.pyre/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*.swn
*~
.project
.pydevproject
.settings/

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Environment
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Logs and temp
*.log
*.tmp
*.bak

# Build artifacts
*.egg-info/
dist/
build/

# Jupyter
.ipynb_checkpoints/

# Backup files
*~
*.orig
*.rej

# Summary files (info in docs now)
RESTRUCTURE_SUMMARY.md
DOCUMENTATION_SUMMARY.md
IMPLEMENTATION_SUMMARY.md
MCP_COMPARISON.md
PAGINATION_BUG_FIX.md
CSV_VS_API_STRUCTURE.md

# Data files (we use YAML)
*.csv
*.xlsx
*.xls
EOF
```

### **PHASE 8: Final Verification (3 min)**

```bash
# Run comprehensive check
echo "=== FINAL VERIFICATION ==="
echo ""

# 1. Count files by type
echo "Python files:"
find . -name "*.py" -not -path "./.git/*" | wc -l
echo "(Expected: ~20 files)"
echo ""

echo "Markdown files:"
find . -name "*.md" -not -path "./.git/*" | wc -l
echo "(Expected: ~20 files)"
echo ""

echo "YAML test cases:"
find testmo/oneapp/test-cases -name "*.yml" | wc -l
echo "(Expected: 1340 files)"
echo ""

# 2. Check for unwanted files
echo "Checking for unwanted files..."
echo ""

echo "CSV files (should be 0):"
find . -name "*.csv" -not -path "./.git/*" | wc -l

echo "Log files (should be 0):"
find . -name "*.log" -not -path "./.git/*" | wc -l

echo "Backup files (should be 0):"
find . -name "*.bak" -not -path "./.git/*" | wc -l

echo "Temp files (should be 0):"
find . -name "*.tmp" -not -path "./.git/*" | wc -l

echo "Python cache (should be 0):"
find . -type d -name "__pycache__" -not -path "./.git/*" | wc -l

echo "DS_Store files (should be 0):"
find . -name ".DS_Store" -not -path "./.git/*" | wc -l

echo ""
echo "✓ Verification complete"
```

---

## 📝 PHASE 9: Create Cleanup Summary (2 min)

```bash
# Create a record of what was cleaned
cat > CLEANUP_SUMMARY.md << 'EOF'
# Repository Cleanup Summary

**Date:** 2026-01-30
**Status:** ✅ COMPLETE

## What Was Removed

### Documentation Files (now in git history)
- RESTRUCTURE_SUMMARY.md
- DOCUMENTATION_SUMMARY.md
- IMPLEMENTATION_SUMMARY.md
- MCP_COMPARISON.md
- PAGINATION_BUG_FIX.md
- CSV_VS_API_STRUCTURE.md

### Development Artifacts
- All __pycache__ directories
- All *.pyc files
- All .pytest_cache directories
- All .mypy_cache directories
- All .egg-info directories
- All .coverage files

### IDE Files
- .vscode/ directory
- .idea/ directory
- All *.swp files
- All *.swo files

### Temp/Backup Files
- All *.log files
- All *.tmp files
- All *.bak files
- All *~ files
- All .DS_Store files

### Data Files
- All *.csv files (we use YAML now)

## What Was Kept

### Essential Files
✅ README.md
✅ requirements.txt
✅ pyproject.toml
✅ .gitignore
✅ TESTING_LOG.md

### Production Code
✅ scripts/btl_testmo.py
✅ scripts/testmo_sync/ (8 modules)
✅ scripts/legacy/ (4 reference scripts)

### Documentation
✅ docs/ (7 comprehensive documents)

### Tests
✅ tests/ (3 test files + README)

### Prompts
✅ prompts/ (6 mega prompts)

### Test Cases
✅ testmo/oneapp/test-cases/ (1340 YAML files)
✅ testmo/oneapp/.sync/ (metadata)

## Verification Results

- Python files: ~20 ✅
- Markdown files: ~20 ✅
- YAML test cases: 1340 ✅
- CSV files: 0 ✅
- Log files: 0 ✅
- Cache directories: 0 ✅
- Temp files: 0 ✅

## Repository Size

Before cleanup: [will be calculated]
After cleanup: [will be calculated]
Space saved: [will be calculated]

## Git Status

All changes committed: ✅
Tag created: pre-cleanup ✅
Working tree: Clean ✅

---

**Repository is now production-ready and clutter-free** ✅
EOF
```

---

## 🎯 PHASE 10: Final Git Commit (2 min)

```bash
# Stage all deletions
git add -A

# Show what will be committed
git status

# Commit cleanup
git commit -m "chore: Deep cleanup - remove all non-essential files

Removed:
- Summary files (info now in docs and git history)
- Development artifacts (cache, build, test artifacts)
- IDE files (.vscode, .idea, swap files)
- Temp/backup files (*.log, *.tmp, *.bak)
- OS files (.DS_Store)
- CSV files (we use YAML now)

Kept:
- Production code (scripts/testmo_sync/)
- Documentation (docs/ - 7 files)
- Tests (tests/ - 3 files)
- Prompts (prompts/ - 6 files)
- Test cases (testmo/ - 1340 YAML files)
- Essential config (requirements.txt, pyproject.toml)

Repository is now production-ready and clutter-free.

See: CLEANUP_SUMMARY.md for complete details"

# Verify commit
git log -1 --stat

# Show final state
echo ""
echo "=== REPOSITORY FINAL STATE ==="
tree -L 2 -I '__pycache__|*.pyc|.git'
```

---

## ✅ SUCCESS CRITERIA

After cleanup, verify:

1. ✅ Test cases intact: 1340 YAML files
2. ✅ No CSV files remaining
3. ✅ No log files remaining
4. ✅ No cache directories
5. ✅ No IDE files
6. ✅ No temp/backup files
7. ✅ All production code present
8. ✅ All documentation present
9. ✅ All tests present
10. ✅ All prompts present
11. ✅ Clean git status
12. ✅ Safety tag created

---

## 🚨 CRITICAL WARNINGS

1. **NEVER delete testmo/ directory** - Contains 1340 test cases
2. **NEVER delete .git/ directory** - All history lives here
3. **Always verify test case count** before and after: 1340 files
4. **Create safety tag** before starting cleanup
5. **Check git status** before final commit

---

## 🔄 ROLLBACK (if needed)

If something goes wrong:

```bash
# Restore to pre-cleanup state
git reset --hard pre-cleanup

# Or restore specific file
git checkout pre-cleanup -- path/to/file

# Verify test cases
find testmo/oneapp/test-cases -name "*.yml" | wc -l
# Must be 1340
```

---

## 📊 EXPECTED RESULTS

### Before Cleanup:
```
~100+ files total
Clutter everywhere
Development artifacts
Multiple summary files
```

### After Cleanup:
```
~60-70 essential files
Clean structure
Production-ready
Professional repository
```

### Repository Structure After Cleanup:
```
BTL-TestCases/
├── .git/                   [git history]
├── .gitignore              [comprehensive]
├── README.md               [main readme]
├── requirements.txt        [dependencies]
├── pyproject.toml          [package config]
├── TESTING_LOG.md          [validation proof]
├── CLEANUP_SUMMARY.md      [cleanup record]
├── docs/                   [7 docs]
├── scripts/                [production code]
│   ├── btl_testmo.py
│   ├── testmo_sync/
│   └── legacy/
├── tests/                  [unit tests]
├── prompts/                [6 mega prompts]
└── testmo/                 [1340 test cases]
    └── oneapp/
        ├── .sync/
        └── test-cases/
```

---

## 🎯 FINAL CHECKLIST

After completing all phases:

- [ ] Safety tag created: `pre-cleanup`
- [ ] Test cases verified: 1340 files
- [ ] Root clutter removed
- [ ] Development artifacts removed
- [ ] IDE files removed
- [ ] Temp/backup files removed
- [ ] .gitignore updated
- [ ] Final verification passed
- [ ] CLEANUP_SUMMARY.md created
- [ ] All changes committed
- [ ] Working tree clean
- [ ] Repository professional

---

**END OF MEGA PROMPT 4**

Execute carefully and verify at each step.
This is the final polish that makes the repository production-ready.
