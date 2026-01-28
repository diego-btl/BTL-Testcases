# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Prerequisites
- Python 3.11+
- Git
- Testmo account with API key

### Step 1: Clone and Setup (1 minute)

```bash
# Clone repository
cd testcase-management

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Testmo credentials:
# - TESTMO_URL=https://your-instance.testmo.net
# - TESTMO_API_KEY=your-api-key
# - TESTMO_PROJECT_ID=your-project-id
```

### Step 2: Test Connection (1 minute)

```bash
# Check configuration
python scripts/tcm.py info

# You should see:
# ✓ Testmo URL configured
# ✓ Project ID set
```

### Step 3: Export Test Cases (2 minutes)

```bash
# Export 10 test cases as a trial
python scripts/testmo_export.py \
  --project-id YOUR_PROJECT_ID \
  --limit 10 \
  --feature trial

# Validate exported files
python scripts/validate_yaml.py --input-dir test-cases/trial
```

### Step 4: Review Results (1 minute)

```bash
# View exported files
ls -la test-cases/trial/

# Look at a test case
cat test-cases/trial/TC*.yml
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
git init
git add .
git commit -m "Initial export from Testmo"
```

### B. Try the Demo

```bash
./demo.sh
```

This interactive demo shows:
- Git branching workflow
- Making changes to test cases
- Validation process
- Commit and PR workflow

### C. Full Export

```bash
# Export all test cases
python scripts/testmo_export.py \
  --project-id YOUR_PROJECT_ID \
  --feature all

# This may take a few minutes for large test suites
```

### D. Setup GitHub

1. Create private GitHub repository
2. Push your code:
   ```bash
   git remote add origin https://github.com/your-org/testcase-management.git
   git push -u origin main
   ```
3. Configure GitHub secrets:
   - `TESTMO_URL`
   - `TESTMO_API_KEY`
   - `TESTMO_PROJECT_ID`
4. Enable GitHub Actions

---

## Common Commands

### Export from Testmo
```bash
# All cases in a project
python scripts/testmo_export.py --project-id 1

# Specific folder
python scripts/testmo_export.py --project-id 1 --folder-id 123

# With feature categorization
python scripts/testmo_export.py --project-id 1 --feature remote-services
```

### Import to Testmo
```bash
# Dry run (see what would be imported)
python scripts/testmo_import.py --project-id 1 --dry-run

# Import to specific folder
python scripts/testmo_import.py --project-id 1 --folder-name "My Tests"

# Update existing cases
python scripts/testmo_import.py --project-id 1 --update-existing
```

### Validate YAML
```bash
# Validate all
python scripts/validate_yaml.py

# Validate specific directory
python scripts/validate_yaml.py --input-dir test-cases/remote-services

# Strict mode (fail on any errors)
python scripts/validate_yaml.py --strict
```

### CLI Tool
```bash
# Show info
python scripts/tcm.py info

# Export
python scripts/tcm.py export --project-id 1 --limit 10

# Import
python scripts/tcm.py import --project-id 1 --dry-run

# Validate
python scripts/tcm.py validate
```

---

## Troubleshooting

### "API Error: 401 Unauthorized"
- Check your `TESTMO_API_KEY` in `.env`
- Verify the key is correct in Testmo settings

### "Project not found"
- Verify `TESTMO_PROJECT_ID` is correct
- List projects: Check Testmo UI for project ID

### "Invalid YAML format"
- Run validation: `python scripts/validate_yaml.py`
- Check error messages for specific issues
- Compare with example: `test-cases/examples/TC00001*.yml`

### "Module not found"
- Install dependencies: `pip install -r requirements.txt`
- Check Python version: `python --version` (need 3.11+)

---

## Resources

📚 **Full Documentation**
- [README.md](README.md) - Complete system overview
- [POC_SUMMARY.md](POC_SUMMARY.md) - Proof of concept results
- [TEAM_WORKFLOW.md](docs/TEAM_WORKFLOW.md) - Team collaboration guide
- [COMPARISON.md](docs/COMPARISON.md) - Git-first vs API-first
- [schema.md](docs/schema.md) - YAML format reference

🎬 **Examples**
- [TC00001-remote-engine-start-happy-path.yml](test-cases/examples/TC00001-remote-engine-start-happy-path.yml) - Complete example
- [demo.sh](demo.sh) - Interactive demonstration

🛠️ **Scripts**
- `scripts/testmo_export.py` - Export from Testmo
- `scripts/testmo_import.py` - Import to Testmo
- `scripts/validate_yaml.py` - Validate YAML files
- `scripts/tcm.py` - Unified CLI tool

---

## Support

**Questions?** Check the documentation in the `docs/` folder.

**Issues?** Review [POC_SUMMARY.md](POC_SUMMARY.md) for common scenarios.

**Need help?** Contact your QA team lead.

---

## What's Next?

1. ✅ You've completed the quick start
2. 📖 Read [TEAM_WORKFLOW.md](docs/TEAM_WORKFLOW.md) for daily workflows
3. 🎮 Run `./demo.sh` to see Git workflow in action
4. 🚀 Export your full test suite
5. 👥 Train your team
6. 🔄 Setup GitHub Actions for automation

**Welcome to Git-first test case management!** 🎉
