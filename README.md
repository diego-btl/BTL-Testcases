# Git-First Test Case Management System

A proof-of-concept system that uses **Git as the source of truth** for test cases, with bidirectional sync to Testmo.

## Why Git-First?

**Problems with API-only systems:**
- No real version control (snapshots, not history)
- Limited offline capability
- Vendor lock-in
- Difficult code review process
- No branching/merging workflows

**Git-first advantages:**
- ✅ Real version control (branch, merge, PRs)
- ✅ Distributed work (each QA works locally)
- ✅ Code review for test cases (PR diffs)
- ✅ Clear ownership (git blame)
- ✅ Zero vendor lock-in (portable YAML)
- ✅ CI/CD integration (GitHub Actions)
- ✅ Offline-first workflow
- ✅ Claude Skills via Git distribution

## Architecture

```
┌─────────────────────────────────────────────────┐
│                                                 │
│  Git Repository (Source of Truth)              │
│  ├── test-cases/                               │
│  │   ├── remote-services/                      │
│  │   ├── authentication/                       │
│  │   └── vehicle-status/                       │
│  └── scripts/                                   │
│      ├── testmo_export.py                      │
│      └── testmo_import.py                      │
│                                                 │
└─────────────────────────────────────────────────┘
                    ↕ Sync
┌─────────────────────────────────────────────────┐
│                                                 │
│  Testmo (Presentation Layer)                   │
│  - Test execution                              │
│  - Test runs & reporting                       │
│  - Stakeholder visibility                      │
│                                                 │
└─────────────────────────────────────────────────┘
```

## Quick Start

### 1. Setup

```bash
# Clone repository
git clone <repo-url>
cd testcase-management

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Testmo credentials
```

### 2. Export from Testmo (Initial Migration)

```bash
# Export all test cases from a project
python scripts/testmo_export.py --project-id 1 --feature remote-services

# Export with limit (for testing)
python scripts/testmo_export.py --project-id 1 --limit 10

# Export specific folder
python scripts/testmo_export.py --project-id 1 --folder-id 123
```

### 3. Git Workflow

```bash
# Initialize Git repository
git init
git add .
git commit -m "Initial export from Testmo"

# Create feature branch for improvements
git checkout -b improve-remote-start-tests

# Make changes to YAML files
# ... edit test-cases/remote-services/TC00123-remote-start.yml

# Commit changes
git add test-cases/
git commit -m "Add edge case for network timeout"

# Push and create PR
git push origin improve-remote-start-tests
```

### 4. Sync back to Testmo

```bash
# Dry run to see what would be imported
python scripts/testmo_import.py --project-id 1 --dry-run

# Import new/updated cases
python scripts/testmo_import.py --project-id 1 --folder-name "Remote Services"

# Update existing cases (matches by testmo_id)
python scripts/testmo_import.py --project-id 1 --update-existing
```

## YAML Test Case Format

See `docs/schema.md` for complete documentation.

**Example:**

```yaml
metadata:
  id: TC00001
  name: "Remote Engine Start - Happy Path"
  feature: remote_services
  priority: high
  platforms: [iOS, Android]
  regions: [USA, Canada]
  tags: [smoke, critical-path]
  testmo_id: 12345

preconditions:
  - description: "Vehicle enrolled and connected"

steps:
  - id: 1
    action: "Navigate to vehicle dashboard"
    expected: "Dashboard loads successfully"
  
  - id: 2
    action: "Tap Remote Start button"
    expected: "Confirmation modal appears"

automation:
  framework: maestro
  coverage: partial
```

## Workflows

### Improving Existing Tests

1. Create feature branch
2. Edit YAML files
3. Commit and push
4. Create PR for review
5. After merge, sync to Testmo

### Creating New Tests

1. Create new YAML file following schema
2. Add to appropriate feature directory
3. Git workflow as above
4. Import to Testmo

### Executing Tests

1. Use Testmo UI for test runs
2. QAs execute and mark pass/fail
3. If test case needs fixing:
   - Create branch in Git
   - Fix YAML
   - PR → Merge → Sync

## Scripts

### testmo_export.py

Export test cases from Testmo to YAML format.

```bash
python scripts/testmo_export.py --help

Options:
  --project-id INTEGER    Testmo project ID
  --folder-id INTEGER     Specific folder to export
  --output-dir PATH       Output directory (default: test-cases)
  --limit INTEGER         Limit number of cases
  --feature TEXT          Feature name for categorization
```

### testmo_import.py

Import test cases from YAML to Testmo.

```bash
python scripts/testmo_import.py --help

Options:
  --project-id INTEGER    Testmo project ID
  --input-dir PATH        Input directory (default: test-cases)
  --folder-name TEXT      Target folder in Testmo
  --dry-run              Show what would be imported
  --update-existing      Update cases by testmo_id
```

## CI/CD Integration

GitHub Actions workflow (coming soon):

```yaml
# .github/workflows/sync-testmo.yml
name: Sync to Testmo
on:
  push:
    branches: [main]
    paths: ['test-cases/**']

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: pip install -r requirements.txt
      - run: python scripts/testmo_import.py
        env:
          TESTMO_API_KEY: ${{ secrets.TESTMO_API_KEY }}
```

## Team Collaboration

**For 12 QA Engineers:**

1. **Onboarding**: Clone repo → Ready to work
2. **Distributed work**: Each QA works on branches
3. **Quality gates**: PR reviews required
4. **Skills sharing**: Commit skills → Everyone benefits
5. **Offline capable**: Git works locally
6. **Consistent tooling**: Same Claude Projects for all

## Claude Projects Integration

**Project Setup:**
- Name: "OneApp QA Test Case Management"
- Knowledge: Complete test-cases directory + schemas
- Custom Skills: test-improver, test-generator
- Team Plan: Share with all 12 QAs

See `docs/claude-skills.md` for skill definitions.

## Next Steps

1. ✅ Export initial test cases from Testmo
2. ✅ Review and validate YAML format
3. ⏳ Create Claude Skills
4. ⏳ Setup GitHub Actions
5. ⏳ Train team on Git workflow
6. ⏳ Full migration (900+ tests)

## Cost Analysis

- **Claude Team Plan**: $30/user × 12 = $360/month
- **Testmo**: Already have
- **GitHub**: Free (private repos)

**Total incremental cost: $360/month**

## Support

For questions or issues:
1. Check `docs/` directory
2. Review example files in `test-cases/examples/`
3. Contact: Diego Garcia (QA Engineering Manager)

## License

Internal use - Bethink Labs / Nissan OneApp QA Team
