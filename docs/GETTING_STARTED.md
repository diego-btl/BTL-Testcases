# Getting Started with BTL TestCases Framework

**Estimated Time:** 15 minutes
**Prerequisites:** Python 3.8+, Git, Testmo access

---

## 📋 Prerequisites

### Required Software
- **Python 3.8+** - Check: `python3 --version`
- **Git** - Check: `git --version`
- **Testmo Account** - Access to https://bethinklabs.testmo.net
- **Claude Desktop** (for MCP) - With Testmo MCP configured

### Required Access
- Testmo API key (from profile → API Keys)
- Read/write access to target Testmo projects
- Git repository access (if collaborating)

### Verify Claude Desktop MCP
```bash
# Check if Testmo MCP is configured
# Open Claude Desktop → Settings → Developer
# Should see: testmo MCP server listed
```

---

## 🔧 Installation

### Step 1: Clone Repository
```bash
git clone <repository-url>
cd BTL-TestCases
```

### Step 2: Install Dependencies
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### Step 3: Configure Environment
```bash
# Create .env file
cat > .env << 'EOF'
TESTMO_API_KEY=your_api_key_here
TESTMO_INSTANCE=bethinklabs
TESTMO_URL=https://bethinklabs.testmo.net
EOF

# Secure the file
chmod 600 .env
```

### Step 4: Verify Installation
```bash
# Test CLI
python scripts/btl_testmo.py --version

# Should output: BTL Testmo CLI v1.0.0
```

---

## 🚀 First Steps

### Export Test Cases from Testmo

**Scenario:** You want to export all test cases from OneApp project (ID: 2) to local YAML files.

```bash
# Export complete project
python scripts/btl_testmo.py export \
  --project-id 2 \
  --output testmo/oneapp

# What happens:
# 1. Connects to Testmo via MCP
# 2. Fetches all 162 folders (with hierarchy)
# 3. Fetches all 1334 test cases
# 4. Converts to YAML format
# 5. Saves to testmo/oneapp/test-cases/
# 6. Creates metadata in testmo/oneapp/.sync/

# Expected output:
# ✓ Found 162 folders
# ✓ Found 1334 test cases
# ✓ Written 1334 YAML files
# ✓ Export complete
```

### Verify Export

```bash
# Check folder structure
tree testmo/oneapp/test-cases -L 2

# Count files
find testmo/oneapp/test-cases -name "*.yml" | wc -l
# Expected: 1334

# View a sample file
cat testmo/oneapp/test-cases/installation/TC00535-fresh-install.yml
```

### Make Your First Edit

```bash
# 1. Open a test case
vim testmo/oneapp/test-cases/installation/TC00535-fresh-install.yml

# 2. Edit the description or add a step (stay in the editable sections)

# 3. Save the file

# 4. Push changes to Testmo
python scripts/btl_testmo.py update \
  testmo/oneapp/test-cases/installation/TC00535-fresh-install.yml

# Expected output:
# ✓ Case 535 updated in Testmo
# ✓ Local metadata synced
```

### Create a New Test Case

```bash
# 1. Create new YAML file with TC-NEW- prefix
cat > testmo/oneapp/test-cases/installation/TC-NEW-my-first-test.yml << 'EOF'
metadata:
  name: "My First Test Case"
  priority: "low"
  tags:
    - getting-started

test_case:
  description: |
    This is my first test case created with the framework.

  steps:
    - step: "Execute the test"
      expected: "Test passes"

  configurations:
    - "iOS, Prod"
EOF

# 2. Upload to Testmo
python scripts/btl_testmo.py create \
  testmo/oneapp/test-cases/installation/TC-NEW-my-first-test.yml

# Expected output:
# ✓ Case created in Testmo (ID: 66500)
# ✓ File renamed: TC-NEW-* → TC66500-*
# ✓ Metadata synced

# 3. Verify the file was renamed
ls testmo/oneapp/test-cases/installation/TC66500-*
```

---

## ✅ Verification

After completing the first steps, verify:

```bash
# 1. Export worked
test -d testmo/oneapp/test-cases && echo "✓ Export successful"

# 2. Metadata created
test -f testmo/oneapp/.sync/project.json && echo "✓ Metadata exists"

# 3. Can update cases
# (Check Testmo UI that your edit appeared)

# 4. Can create cases
# (Check Testmo UI that new case exists)
```

---

## 🎯 Next Steps

Now that you have the basics working:

1. **Read [YAML Format](YAML_FORMAT.md)** - Understand file structure
2. **Read [Workflows](WORKFLOWS.md)** - Learn common patterns
3. **Read [CLI Reference](CLI_REFERENCE.md)** - Explore all commands
4. **Try batch operations** - Update/create multiple cases at once

---

## 🐛 Troubleshooting

**Issue:** "TESTMO_API_KEY not set"
**Solution:** Check your `.env` file exists and has correct API key

**Issue:** "MCP server not found"
**Solution:** Verify Claude Desktop has Testmo MCP configured

**Issue:** "No test cases found"
**Solution:** Check project ID is correct: `--project-id 2`

**Issue:** "Permission denied"
**Solution:** Verify your Testmo API key has read/write access

For more issues, see [Troubleshooting Guide](TROUBLESHOOTING.md).

---

## 📚 Additional Resources

- [Architecture Documentation](ARCHITECTURE.md) - Understand how it works
- [Testing Log](../TESTING_LOG.md) - See validation results
- [Testmo Documentation](https://docs.testmo.com) - Platform docs

---

**You're ready to start managing test cases!** 🚀
