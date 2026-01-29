# Quick Start Guide

Get started with Git-First Test Case Management in 5 minutes.

## 🚀 Get Started

### Prerequisites
- **Python 3.11+** installed
- **Git** installed
- **Testmo account** with API key ([Get your API key](https://yourinstance.testmo.net/settings/api))

### Step 1: Setup (2 minutes)

```bash
# Navigate to project directory
cd BTL-TestCases

# Install Python dependencies
pip install -r requirements.txt

# Configure Testmo credentials
cp .env.testmo.example .env.testmo

# Edit .env.testmo with your credentials:
# TESTMO_URL=https://yourinstance.testmo.net
# TESTMO_API_KEY=your-api-key-here
# TESTMO_PROJECT_ID=2  # Your project ID
```

### Step 2: Test Connection (1 minute)

```bash
# Verify your Testmo connection
python -c "
from scripts.testmo_client import TestmoClient
import os
from dotenv import load_dotenv

load_dotenv('.env.testmo')
client = TestmoClient(
    base_url=os.getenv('TESTMO_URL'),
    api_key=os.getenv('TESTMO_API_KEY')
)
projects = client.get_projects()
print(f'✅ Connected! Found {len(projects)} projects')
for p in projects:
    print(f'  - {p[\"id\"]}: {p[\"name\"]}')
"
```

**Expected output:**
```
✅ Connected! Found 6 projects
  - 2: OneApp
  - 5: NBA
  - 6: NMEX
  ...
```

### Step 3: First Export (2 minutes)

```bash
# Export a specific folder from Testmo
# Replace with your project_id and folder_id
python scripts/testmo_export.py \
  --project-id 2 \
  --folder-id 7148 \
  --output-dir test-cases/my-first-export

# Validate the exported files
python scripts/yaml_converter.py validate \
  --input-dir test-cases/my-first-export

# View the results
ls -la test-cases/my-first-export/
```

**What you should see:**
```
✅ Exported 9 test cases to test-cases/my-first-export/
✅ Validation: 9/9 files valid
```

### 🎉 Done!

You now have:
- ✅ Test cases exported from Testmo
- ✅ Validated YAML format
- ✅ Ready for Git workflow

---

## Next Steps

### A. Initialize Git Repository

```bash
# Initialize Git (if not already done)
git init

# Add exported files
git add test-cases/
git commit -m "Initial export from Testmo

- Exported 9 test cases from Dealer Offers folder
- All files validated successfully"

# Push to remote (if configured)
git push origin main
```

### B. Try Creating a New Test Case

```bash
# Create a new YAML file
cat > test-cases/my-first-export/TC-new-test.yml <<'EOF'
metadata:
  testmo_id: null  # null for new cases
  name: "My First Test Case"
  priority: medium
  state: draft
  created_at: "2026-01-28"

description: |
  This is my first test case created in Git

preconditions:
  - User is logged in
  - User has appropriate permissions

steps:
  - action: Navigate to the feature
    expected: Feature page loads successfully

  - action: Perform the test action
    expected: Expected result is displayed

notes: |
  Created as part of Git-first workflow training
EOF

# Validate the new test case
python scripts/yaml_converter.py validate \
  --input-file test-cases/my-first-export/TC-new-test.yml

# Commit to Git
git add test-cases/my-first-export/TC-new-test.yml
git commit -m "Create: New test case for training"
```

### C. Import to Testmo

```bash
# Import the test cases to Testmo
# This will create them in a new folder
python scripts/testmo_import.py \
  --project-id 8 \
  --input-dir test-cases/my-first-export \
  --folder-name "My First Import"

# Check the results in Testmo UI
# Navigate to: Projects → Your Project → My First Import
```

### D. Full Workflow Example

```bash
# 1. Create feature branch
git checkout -b feature/improve-tests

# 2. Edit a test case
vim test-cases/my-first-export/TC-new-test.yml

# 3. Validate changes
python scripts/yaml_converter.py validate \
  --input-dir test-cases/my-first-export

# 4. Review what changed
git diff test-cases/my-first-export/TC-new-test.yml

# 5. Commit with clear message
git add test-cases/my-first-export/TC-new-test.yml
git commit -m "Update: Improve test case clarity

- Added more specific preconditions
- Enhanced step descriptions
- Added notes about edge cases"

# 6. Push and create PR (if using GitHub)
git push origin feature/improve-tests
```

---

## Common Commands

### Export Commands

```bash
# Export all cases from a project
python scripts/testmo_export.py \
  --project-id 2 \
  --output-dir test-cases/all

# Export specific folder
python scripts/testmo_export.py \
  --project-id 2 \
  --folder-id 7148 \
  --output-dir test-cases/dealer-offers

# Export with limit (for testing)
python scripts/testmo_export.py \
  --project-id 2 \
  --limit 10 \
  --output-dir test-cases/sample
```

### Import Commands

```bash
# Import to new folder
python scripts/testmo_import.py \
  --project-id 8 \
  --input-dir test-cases/dealer-offers \
  --folder-name "Dealer Offers"

# Dry run (see what would be imported without actually importing)
python scripts/testmo_import.py \
  --project-id 8 \
  --input-dir test-cases/dealer-offers \
  --folder-name "Test Import" \
  --dry-run
```

### Validation Commands

```bash
# Validate all YAML files in a directory
python scripts/yaml_converter.py validate \
  --input-dir test-cases/dealer-offers

# Validate a single file
python scripts/yaml_converter.py validate \
  --input-file test-cases/dealer-offers/TC-64839.yml

# Strict validation (fail on any warnings)
python scripts/yaml_converter.py validate \
  --input-dir test-cases/dealer-offers \
  --strict
```

### Git Commands

```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Check status
git status

# See what changed
git diff

# Stage changes
git add test-cases/

# Commit with message
git commit -m "Type: Description

- Detail 1
- Detail 2"

# Push branch
git push origin feature/your-feature-name

# Merge to main (after PR approval)
git checkout main
git merge feature/your-feature-name
git push origin main
```

---

## Troubleshooting

### Issue: "Connection refused" or "401 Unauthorized"

**Cause:** Incorrect Testmo credentials

**Solution:**
```bash
# Check your .env.testmo file
cat .env.testmo

# Verify the values:
# 1. TESTMO_URL should be https://yourinstance.testmo.net (no trailing slash)
# 2. TESTMO_API_KEY should be your API key from Testmo settings
# 3. No extra quotes or spaces

# Test connection again
python -c "from scripts.testmo_client import TestmoClient; ..."
```

### Issue: "Project not found" or "Folder not found"

**Cause:** Incorrect project or folder ID

**Solution:**
```bash
# List all projects to find the correct ID
python -c "
from scripts.testmo_client import TestmoClient
import os
from dotenv import load_dotenv

load_dotenv('.env.testmo')
client = TestmoClient(
    base_url=os.getenv('TESTMO_URL'),
    api_key=os.getenv('TESTMO_API_KEY')
)
projects = client.get_projects()
for p in projects:
    print(f'{p[\"id\"]}: {p[\"name\"]}')
"

# List folders in a project
python scripts/testmo_client.py list-folders --project-id 2
```

### Issue: "Invalid YAML format"

**Cause:** Malformed YAML syntax

**Solution:**
```bash
# Run validation to see specific errors
python scripts/yaml_converter.py validate \
  --input-file test-cases/your-file.yml

# Common YAML issues:
# - Missing quotes around strings with special characters
# - Incorrect indentation (use 2 spaces, not tabs)
# - Missing required fields (metadata, description, steps)

# Fix the issues and validate again
```

### Issue: "Module not found" or "ImportError"

**Cause:** Missing Python dependencies

**Solution:**
```bash
# Install/reinstall dependencies
pip install -r requirements.txt

# Or install specific packages
pip install pyyaml requests python-dotenv beautifulsoup4

# Check Python version (need 3.11+)
python --version
```

### Issue: Import succeeds but test cases not visible in Testmo

**Cause:** Cases imported to different folder than expected

**Solution:**
1. Check Testmo UI for folder named exactly as specified in `--folder-name`
2. Folder names are case-sensitive
3. If you see a folder with slightly different name, that's where they are
4. You can rename the folder in Testmo UI

### Issue: "testmo_id not found" warnings during export

**Cause:** Some test cases don't have the testmo_id field (normal for new cases)

**Solution:**
- This is expected for test cases created outside of Testmo
- After importing to Testmo, export again to capture the IDs
- These warnings are informational only

---

## Understanding the Workflow

### Git-First Workflow Diagram

```
┌─────────────────────────────────────────┐
│  1. Export from Testmo                  │
│     python scripts/testmo_export.py     │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│  2. Edit YAML files in Git              │
│     - Create new test cases             │
│     - Modify existing test cases        │
│     - Use Git branches and PRs          │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│  3. Validate changes                    │
│     python scripts/yaml_converter.py    │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│  4. Commit to Git                       │
│     git add . && git commit             │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│  5. Import back to Testmo               │
│     python scripts/testmo_import.py     │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│  6. Execute tests in Testmo UI          │
│     (Testmo remains execution layer)    │
└─────────────────────────────────────────┘
```

### File Structure

```
BTL-TestCases/
├── test-cases/              # Test cases in YAML format
│   ├── dealer-offers/
│   │   ├── TC-64839.yml
│   │   ├── TC-64840.yml
│   │   └── TC-64841.yml
│   └── authentication/
│       └── TC-12345.yml
│
├── scripts/                 # Python tools
│   ├── testmo_export.py     # Export from Testmo
│   ├── testmo_import.py     # Import to Testmo
│   ├── testmo_client.py     # API client
│   └── yaml_converter.py    # YAML ↔ HTML converter
│
├── docs/                    # Documentation
│   └── schema.md            # YAML format reference
│
├── .env.testmo              # Testmo credentials (not in Git)
├── .gitignore               # Git ignore rules
├── requirements.txt         # Python dependencies
└── README.md                # Project overview
```

---

## Resources

### Documentation
- [README.md](README.md) - Complete system overview
- [POC_SUMMARY.md](POC_SUMMARY.md) - PoC test results and findings
- [WORKFLOWS.md](WORKFLOWS.md) - Practical usage patterns
- [API_FINDINGS.md](API_FINDINGS.md) - Testmo API technical details
- [docs/schema.md](docs/schema.md) - YAML format specification

### Getting Help
- **Questions?** Check the docs above
- **Issues?** Review [API_FINDINGS.md](API_FINDINGS.md) for limitations
- **Workflow help?** See [WORKFLOWS.md](WORKFLOWS.md) for examples

---

## What's Next?

### For Individuals
1. ✅ Complete this quick start
2. 📖 Read [WORKFLOWS.md](WORKFLOWS.md) for advanced patterns
3. 🎯 Export your test cases
4. 🧪 Practice Git workflow
5. 🚀 Import back to Testmo

### For Teams
1. ✅ One person completes quick start
2. 👥 Train 2-3 QA champions
3. 📋 Pilot with one feature area
4. 🔄 Iterate on workflows
5. 🎓 Roll out to full team

### For Production
1. ✅ Pilot successful
2. 🗂️ Export all 900 test cases
3. 🔧 Setup GitHub Actions for automation
4. 👥 Train all 12 QAs
5. 📊 Monitor adoption and success metrics

---

## Tips for Success

### Do's ✅
- **Do** validate YAML before committing
- **Do** write clear commit messages
- **Do** use feature branches
- **Do** request PR reviews
- **Do** export after Testmo changes

### Don'ts ❌
- **Don't** edit test cases in both Git and Testmo simultaneously
- **Don't** commit without validating
- **Don't** push directly to main (use PRs)
- **Don't** skip the export step after import
- **Don't** manually edit testmo_ids (let export handle it)

---

**Need Help?** Contact: Diego Garcia (QA Engineering Manager)

**Ready to dive deeper?** Read [WORKFLOWS.md](WORKFLOWS.md)

---

**Last Updated:** January 28, 2026
**Version:** 1.0
**Status:** Production Ready
