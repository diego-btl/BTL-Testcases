# Getting Started - Installation & Setup

**Time Required:** 15 minutes
**Goal:** Get the BTL TestCases framework running locally

---

## Prerequisites

Before you begin, ensure you have:

- **Python 3.8 or higher**
  ```bash
  python3 --version  # Should show 3.8+
  ```

- **Git**
  ```bash
  git --version
  ```

- **Testmo Account** - Access to https://bethinklabs.testmo.net

- **Claude Desktop** (Optional) - For MCP integrations (ClickUp, Slack)

---

## Step 1: Clone & Install (5 minutes)

### Clone Repository

```bash
# Clone the repository
git clone https://github.com/bethinklabs/BTL-TestCases.git
cd BTL-TestCases

# Verify you're in the right place
ls -la
# Should see: scripts/, testmo/, docs/, README.md, etc.
```

### Install Dependencies

```bash
# Install Python packages
pip install -r requirements.txt

# Or use virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Dependencies installed:**
- `requests` - API communication
- `pyyaml` - YAML file handling
- `python-dotenv` - Environment configuration

---

## Step 2: Configure API Keys (3 minutes)

### Create Environment File

```bash
# Copy example environment file
cp .env.example .env

# Edit with your API keys
nano .env  # Or use your favorite editor
```

### Configure Testmo

**Get Testmo API Key:**
1. Go to https://bethinklabs.testmo.net
2. Click your profile → Settings
3. Go to "API Tokens"
4. Generate new token
5. Copy token (starts with `testmo_api_`)

**Add to .env:**
```bash
# Testmo Configuration
TESTMO_URL=https://bethinklabs.testmo.net
TESTMO_API_KEY=testmo_api_YOUR_TOKEN_HERE
TESTMO_PROJECT_ID=2  # Optional: Default project (OneApp)
```

### Test Connection

```bash
# Test Testmo API connection
python3 -c "
import os
import requests
from dotenv import load_dotenv

load_dotenv()
url = f\"{os.getenv('TESTMO_URL')}/api/v1/projects\"
headers = {'Authorization': f\"Bearer {os.getenv('TESTMO_API_KEY')}\"}
response = requests.get(url, headers=headers)
print('✅ Connected!' if response.status_code == 200 else '❌ Error')
print(f'Projects: {len(response.json().get(\"result\", []))}')
"
```

**Expected output:**
```
✅ Connected!
Projects: 7
```

---

## Step 3: Verify Installation (2 minutes)

### Run Validation Tests

```bash
# Run unit tests
python3 -m pytest tests/ -v

# Should see:
# test_hasher.py::test_testmo_to_yaml PASSED
# test_validator.py::test_valid_yaml PASSED
# test_converter.py::test_slugify PASSED
```

### List Available Projects

```bash
# List Testmo projects
python3 scripts/list_testmo_projects.py
```

**Expected output:**
```
================================================================================
TESTMO PROJECTS
================================================================================

Project ID: 2
Name: OneApp
URL: https://bethinklabs.testmo.net/repositories/2
--------------------------------------------------------------------------------

Project ID: 5
Name: NBA
URL: https://bethinklabs.testmo.net/repositories/5
--------------------------------------------------------------------------------

Project ID: 6
Name: NMEX
URL: https://bethinklabs.testmo.net/repositories/6
--------------------------------------------------------------------------------
```

---

## Step 4: First Export (5 minutes)

### Export OneApp Project

```bash
# Export OneApp test cases (1,334 cases)
python3 scripts/export_project.py 2 testmo/oneapp

# Watch progress:
# ✓ Found 162 folders
# ✓ Found 1334 test cases
# Progress: 100/1334 cases...
# Progress: 200/1334 cases...
# ...
# ✓ Export complete
```

**Expected output:**
```
================================================================================
EXPORT COMPLETE
================================================================================
Project: OneApp (ID: 2)
Folders: 162
Test Cases: 1334
Output: testmo/oneapp
================================================================================
```

### Verify Export

```bash
# Count exported files
find testmo/oneapp -name "*.yml" | wc -l
# Output: 1334

# Check folder structure
ls -la testmo/oneapp/
# Should see:
# .sync/         - Metadata (project.json, folder-map.json, case-map.json)
# test-cases/    - YAML files organized in folders

# View a test case
cat testmo/oneapp/test-cases/home/TC66186-*.yml | head -30
```

---

## ✅ You're Ready!

Your installation is complete. You now have:

- ✅ Framework installed and configured
- ✅ Testmo API connection verified
- ✅ 1,334 test cases exported from OneApp
- ✅ Local YAML files ready for editing

---

## Next Steps

### Start Using AI Workflows

**Read the How-To Guide (recommended):**
```bash
# Open in browser or editor
cat HOW_TO_GUIDE.md
```

**Key starting points:**
- [HOW_TO_GUIDE.md](HOW_TO_GUIDE.md) - 30+ AI-assisted workflows ⭐
- [agents/CLAUDE_CODE.md](agents/CLAUDE_CODE.md) - Claude Code integration
- [agents/BEST_PRACTICES.md](agents/BEST_PRACTICES.md) - Optimization tips

### Try Your First AI Workflow

**Improve a test case with Claude Code:**
```
Prompt:

Improve test case TC66186:
File: testmo/oneapp/test-cases/home/charge/v2l-vehicle-to-load/TC66186-v2l-screen.yml

Add:
1. 3 preconditions
2. Expand steps with details
3. Add edge case

Preserve testmo: section.
```

### Export Other Projects (Optional)

```bash
# Export NBA (92 cases)
python3 scripts/export_project.py 5 testmo/nba

# Export NMEX (284 cases)
python3 scripts/export_project.py 6 testmo/nmex
```

---

## Troubleshooting

### Issue: "Module not found" error

**Solution:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: "API key invalid"

**Solution:**
```bash
# Verify API key in .env file
cat .env | grep TESTMO_API_KEY

# Test manually
curl "https://bethinklabs.testmo.net/api/v1/projects" \
  -H "Authorization: Bearer YOUR_API_KEY"

# Should return JSON with projects list
```

### Issue: "Permission denied" when running scripts

**Solution:**
```bash
# Make scripts executable
chmod +x scripts/*.py

# Or run with python3 explicitly
python3 scripts/export_project.py 2 testmo/oneapp
```

### Issue: "Export fails partway through"

**Solution:**
```bash
# Check internet connection
ping bethinklabs.testmo.net

# Check API rate limits (100 req/min)
# Wait 1 minute and retry

# Try smaller export first
python3 scripts/export_project.py 5 testmo/nba  # Only 92 cases
```

---

## Optional: Setup MCP Integrations

### ClickUp Integration

**For linking test cases to ClickUp tickets:**

See [agents/CLICKUP_INTEGRATION.md](agents/CLICKUP_INTEGRATION.md) for setup.

**Quick start:**
1. Get ClickUp API key
2. Configure in Claude Desktop
3. Test with: "Search ClickUp for tasks"

### Slack Integration

**For pulling discussion context:**

See [agents/SLACK_CONTEXT.md](agents/SLACK_CONTEXT.md) for setup.

**Quick start:**
1. Create Slack app
2. Get bot token
3. Configure in Claude Desktop
4. Test with: "Search Slack for messages"

---

## Getting Help

- **Documentation:** [HOW_TO_GUIDE.md](HOW_TO_GUIDE.md)
- **Technical Details:** [ARCHITECTURE.md](ARCHITECTURE.md)
- **Slack:** #qa-testing channel
- **Contact:** Diego Del Aguila (diego@bethinklabs.com)

---

**Installation complete!** 🎉

Now read [HOW_TO_GUIDE.md](HOW_TO_GUIDE.md) to learn AI-powered workflows and 10x your productivity!
