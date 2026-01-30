# Workflows Guide

**Version:** 1.0.0
**Last Updated:** 2026-01-30

---

## 🎯 Overview

This guide covers common workflows for test case management using the BTL TestCases Framework. Each workflow includes step-by-step instructions, commands, and best practices.

---

## 📋 Table of Contents

1. [Daily Developer Workflows](#daily-developer-workflows)
2. [Batch Operations](#batch-operations)
3. [Team Collaboration](#team-collaboration)
4. [AI-Assisted Workflows](#ai-assisted-workflows)
5. [CI/CD Integration](#cicd-integration)
6. [Migration Workflows](#migration-workflows)

---

## 💼 Daily Developer Workflows

### Workflow 1: Update Single Test Case {#update-single-case}

**Scenario:** You need to update a test case description after a feature change.

**Steps:**

```bash
# 1. Pull latest changes from Testmo
btl_testmo sync --project testmo/oneapp --direction pull

# 2. Find the test case file
find testmo/oneapp -name "*login*" -type f

# 3. Edit the file
vim testmo/oneapp/test-cases/authentication/TC00535-email-login.yml

# 4. Validate your changes
btl_testmo validate testmo/oneapp/test-cases/authentication/TC00535-email-login.yml

# 5. Push changes to Testmo
btl_testmo update testmo/oneapp/test-cases/authentication/TC00535-email-login.yml

# 6. Commit to git
git add testmo/oneapp/test-cases/authentication/TC00535-email-login.yml
git commit -m "Update: Email login test description"
git push
```

**Time:** ~5 minutes
**Performance:** ~223ms API call

---

### Workflow 2: Create New Test Cases {#create-new-cases}

**Scenario:** You need to create multiple test cases for a new feature.

**Steps:**

```bash
# 1. Create folder if needed
mkdir -p testmo/oneapp/test-cases/new-feature

# 2. Create test case files with TC-NEW- prefix
cat > testmo/oneapp/test-cases/new-feature/TC-NEW-basic-functionality.yml << 'EOF'
metadata:
  name: "New Feature - Basic Functionality"
  priority: "high"
  tags:
    - new-feature
    - smoke-test

test_case:
  description: |
    Verify that new feature basic functionality works correctly.

  preconditions: |
    - Feature flag 'EnableNewFeature' is enabled
    - User has required permissions

  steps:
    - step: "Navigate to new feature"
      expected: "Feature screen displays"

    - step: "Test basic operation"
      expected: "Operation completes successfully"

  configurations:
    - "iOS, Prod"
    - "Android, Prod"
EOF

# 3. Create more test cases (repeat step 2)

# 4. Validate all new test cases
btl_testmo validate testmo/oneapp/test-cases/new-feature/TC-NEW-*.yml

# 5. Batch create in Testmo (fast!)
btl_testmo create testmo/oneapp/test-cases/new-feature/TC-NEW-*.yml --batch

# 6. Verify files were renamed
ls testmo/oneapp/test-cases/new-feature/

# 7. Commit to git
git add testmo/oneapp/test-cases/new-feature/
git commit -m "Add: New Feature test cases"
git push
```

**Time:** ~10 minutes for 5 test cases
**Performance:** ~393ms for batch create (5 cases)

---

### Workflow 3: Daily Sync

**Scenario:** Start your day by syncing with Testmo.

**Steps:**

```bash
# 1. Check what changed
btl_testmo status --project testmo/oneapp --remote

# 2. Pull remote changes (others' updates)
btl_testmo sync --project testmo/oneapp --direction pull

# 3. Review pulled changes
git diff

# 4. If changes look good, commit
git add testmo/oneapp/
git commit -m "Sync: Pull latest from Testmo"

# 5. Work on your test cases...

# 6. At end of day, push your changes
btl_testmo sync --project testmo/oneapp --direction push

# 7. Commit metadata updates
git add testmo/oneapp/
git commit -m "Sync: Push today's changes to Testmo"
git push
```

**Time:** ~5 minutes (morning + evening)
**Frequency:** Daily

---

## 🔄 Batch Operations {#batch-operations}

### Workflow 4: Batch Update Test Cases

**Scenario:** Update priority for multiple test cases.

**Steps:**

```bash
# 1. Find test cases to update
grep -l "priority: low" testmo/oneapp/test-cases/installation/*.yml

# 2. Update priority field in multiple files
for file in TC00535*.yml TC00536*.yml TC00537*.yml; do
  sed -i '' 's/priority: low/priority: medium/' "$file"
done

# 3. Validate changes
btl_testmo validate TC00535*.yml TC00536*.yml TC00537*.yml

# 4. Batch update (hybrid mode - faster!)
btl_testmo update --folder testmo/oneapp/test-cases/installation --batch

# 5. Commit changes
git add testmo/oneapp/test-cases/installation/
git commit -m "Update: Raise priority for installation tests"
```

**Time:** ~5 minutes for 10 cases
**Performance:** Hybrid batch ~1.5s for 5 cases (common field update)

---

### Workflow 5: Mass Tag Addition

**Scenario:** Add regression tag to all tests in a folder.

**Steps:**

```bash
# 1. Create a script to add tag
cat > add_regression_tag.py << 'EOF'
import yaml
import sys
from pathlib import Path

for file_path in sys.argv[1:]:
    with open(file_path) as f:
        data = yaml.safe_load(f)

    # Add regression tag if not present
    tags = data.get('metadata', {}).get('tags', [])
    if 'regression' not in tags:
        tags.append('regression')
        data['metadata']['tags'] = tags

    with open(file_path, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)

    print(f"✓ Updated {file_path}")
EOF

# 2. Run on all files in folder
python add_regression_tag.py testmo/oneapp/test-cases/checkout/*.yml

# 3. Validate
btl_testmo validate --folder testmo/oneapp/test-cases/checkout

# 4. Batch update
btl_testmo update --folder testmo/oneapp/test-cases/checkout --batch

# 5. Commit
git add testmo/oneapp/test-cases/checkout/
git commit -m "Add: Regression tag to checkout tests"
```

**Time:** ~10 minutes for 50 files
**Performance:** Batch update ~5s for 50 cases

---

## 👥 Team Collaboration {#team-collaboration}

### Workflow 6: Feature Branch Workflow

**Scenario:** Multiple team members working on different features.

**Steps:**

```bash
# Developer A: Working on Feature X
git checkout -b feature/new-checkout
# ... create/update test cases ...
git add testmo/oneapp/test-cases/checkout/
git commit -m "Add: New checkout test cases"
git push origin feature/new-checkout
# Create PR for review

# Developer B: Working on Feature Y (parallel)
git checkout -b feature/new-payment
# ... create/update test cases ...
git add testmo/oneapp/test-cases/payment/
git commit -m "Add: New payment test cases"
git push origin feature/new-payment
# Create PR for review

# After both PRs merged to main:
# Developer A
git checkout main
git pull
btl_testmo sync --project testmo/oneapp --direction push
# Now Testmo has both features' test cases
```

**Benefits:**
- Parallel development
- Code review for test cases
- Clean git history
- Safe experimentation

---

### Workflow 7: Test Case Review Process

**Scenario:** Review and approve test cases before they go live.

**Steps:**

```bash
# 1. Create test cases in draft state
cat > TC-NEW-feature.yml << 'EOF'
metadata:
  name: "New Feature Test"
  priority: "high"
  status: draft  # Start in draft

test_case:
  # ... test content ...
EOF

# 2. Create in Testmo (still draft)
btl_testmo create TC-NEW-feature.yml

# 3. Push to feature branch for review
git checkout -b feature/new-tests
git add TC66500-feature.yml
git commit -m "Draft: New feature test cases"
git push origin feature/new-tests

# 4. Create PR, request review

# 5. After approval, update status
vim TC66500-feature.yml
# Change: status: draft → status: approved

# 6. Update in Testmo
btl_testmo update TC66500-feature.yml

# 7. Merge PR to main
```

**Review Checklist:**
- [ ] Test name is descriptive
- [ ] Description starts with "Verify that..."
- [ ] Preconditions are clear
- [ ] Steps are specific and actionable
- [ ] Expected results are measurable
- [ ] Configurations specified
- [ ] Tags appropriate
- [ ] Priority correct

---

### Workflow 8: Conflict Resolution

**Scenario:** Same test case edited locally and in Testmo.

**Steps:**

```bash
# 1. Attempt sync
btl_testmo sync --project testmo/oneapp

# Output shows conflict:
# ⚠ Conflict detected: TC00535-email-login.yml
#
# Local changes:
#   - metadata.name
#
# Remote changes:
#   - test_case.description
#
# Resolution options:
#   1. Keep local (overwrite Testmo)
#   2. Keep remote (overwrite local)
#   3. Skip this case
#   4. Show full diff

# 2. Choose option 4 to see full diff
# 4
# Shows detailed diff of both versions

# 3. Choose resolution strategy:
# - Option 1: Your changes are more important
# - Option 2: Remote changes are more important
# - Option 3: Manual merge needed

# 4. If manual merge needed:
# Copy remote version to backup
btl_testmo export --project-id 2 --folder-id 7200 --output backup/

# 5. Manually merge changes
vim TC00535-email-login.yml
# Combine local metadata.name with remote test_case.description

# 6. Update Testmo with merged version
btl_testmo update TC00535-email-login.yml --force

# 7. Commit final version
git add TC00535-email-login.yml
git commit -m "Merge: Resolve conflict in TC00535"
```

**Prevention:**
- Sync regularly (daily)
- Communicate changes to team
- Use feature branches
- Update status field to indicate WIP

---

## 🤖 AI-Assisted Workflows {#ai-assisted-workflows}

### Workflow 9: AI Test Case Generation

**Scenario:** Use Claude Code to generate test cases from requirements.

**Process:**

```
User: "Claude, create test cases for the new Tesla Pricing feature
based on these requirements: [paste requirements]"

Claude: [Reads YAML format specification, similar tests for context]

1. Analyzes requirements
2. Identifies test scenarios
3. Generates TC-NEW-*.yml files following YAML format
4. Validates format
5. Suggests appropriate tags and priority
```

**Example Conversation:**

```
User: Create a test case for displaying Tesla charging pricing breakdown

Claude: I'll create a test case following the YAML format.

[Creates testmo/oneapp/test-cases/tesla-pricing/TC-NEW-pricing-breakdown.yml]

Done! Created:
- TC-NEW-pricing-breakdown-modal.yml

Key points:
- Priority: high (critical user feature)
- Tags: tesla-pricing, regression, tier-1
- Multiple expectations per step
- Covers happy path

Would you like me to:
1. Create additional negative test cases?
2. Add edge cases?
3. Create all test cases and batch upload to Testmo?

User: Yes, batch create all test cases

Claude: [Executes batch create command]
Created 5 test cases (IDs: 66306-66310)
Files renamed and synced.
```

**Benefits:**
- Faster test case creation
- Consistent format
- Follows best practices
- Reduces manual work

---

### Workflow 10: AI Test Case Enhancement

**Scenario:** Improve existing test cases with AI assistance.

**Process:**

```bash
# 1. Export test cases
btl_testmo export --project-id 2 --folder-id 7200 --output temp/

# 2. Ask Claude Code to review
"Claude, review these test cases and suggest improvements:
- testmo/oneapp/test-cases/login/*.yml

Focus on:
- Missing edge cases
- Vague steps
- Missing preconditions
- Better expected results"

# Claude analyzes and suggests:
# - Add "Forgot Password" negative case
# - Make step 3 more specific: "Tap blue Login button"
# - Add precondition: "Network connectivity available"
# - Split complex expectations into multiple steps

# 3. Apply suggestions (Claude can do this)
"Claude, implement these improvements in the files"

# 4. Validate
btl_testmo validate testmo/oneapp/test-cases/login/*.yml

# 5. Update in Testmo
btl_testmo update --folder testmo/oneapp/test-cases/login --batch

# 6. Commit improvements
git add testmo/oneapp/test-cases/login/
git commit -m "Enhance: Improve login test cases based on AI review"
```

---

## 🔧 CI/CD Integration {#cicd-integration}

### Workflow 11: Automated Sync on Merge

**Scenario:** Auto-sync test cases to Testmo when PR merges to main.

**GitHub Actions Workflow:**

```yaml
# .github/workflows/testmo-sync.yml
name: Sync Test Cases to Testmo

on:
  push:
    branches: [main]
    paths:
      - 'testmo/oneapp/test-cases/**/*.yml'

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Validate test cases
        run: |
          btl_testmo validate --folder testmo/oneapp/test-cases

      - name: Sync to Testmo
        env:
          TESTMO_API_KEY: ${{ secrets.TESTMO_API_KEY }}
        run: |
          btl_testmo sync \
            --project testmo/oneapp \
            --direction push \
            --resolve local

      - name: Commit metadata updates
        run: |
          git config user.name "Testmo Sync Bot"
          git config user.email "bot@company.com"
          git add testmo/oneapp/.sync/
          git commit -m "Sync: Update metadata from CI" || true
          git push
```

**Benefits:**
- Automatic sync on merge
- Validation before sync
- Prevents broken test cases in Testmo
- Audit trail in git

---

### Workflow 12: Nightly Full Sync

**Scenario:** Daily backup and sync of all test cases.

**Cron Job:**

```bash
#!/bin/bash
# scripts/nightly-sync.sh

set -e

echo "Starting nightly test case sync..."

# 1. Pull latest from git
cd /path/to/BTL-TestCases
git checkout main
git pull

# 2. Bidirectional sync
btl_testmo sync \
  --project testmo/oneapp \
  --direction both \
  --resolve remote  # Prefer Testmo on conflicts

# 3. Commit any pulled changes
if [[ -n $(git status -s) ]]; then
  git add testmo/oneapp/
  git commit -m "Nightly sync: $(date +%Y-%m-%d)"
  git push
fi

# 4. Create backup
timestamp=$(date +%Y%m%d_%H%M%S)
tar -czf "backups/testmo-backup-${timestamp}.tar.gz" testmo/

# 5. Cleanup old backups (keep last 30 days)
find backups/ -name "*.tar.gz" -mtime +30 -delete

echo "✓ Nightly sync complete"
```

**Crontab:**

```
# Run every night at 2 AM
0 2 * * * /path/to/scripts/nightly-sync.sh >> /var/log/testmo-sync.log 2>&1
```

---

## 🚚 Migration Workflows {#migration-workflows}

### Workflow 13: Project Migration

**Scenario:** Migrate all test cases from Project A to Project B.

**Steps:**

```bash
# 1. Export from source project
btl_testmo export \
  --project-id 2 \
  --output testmo/oneapp-backup

# 2. Verify export
find testmo/oneapp-backup -name "*.yml" | wc -l
# Expected: 1334

# 3. Validate all files
btl_testmo validate --folder testmo/oneapp-backup/test-cases

# 4. Review and modify as needed
# (e.g., update tags, priorities, folder structure)

# 5. Import to destination project
btl_testmo import \
  --project-id 9 \
  --source testmo/oneapp-backup \
  --folder-name "Migrated from Project 2"

# 6. Verify import
btl_testmo export \
  --project-id 9 \
  --output testmo/btl-testcases-verify

find testmo/btl-testcases-verify -name "*.yml" | wc -l
# Should match source count

# 7. Spot check random test cases
diff -u \
  testmo/oneapp-backup/test-cases/random-test.yml \
  testmo/btl-testcases-verify/test-cases/random-test.yml

# 8. Document migration
echo "Migration complete: $(date)" >> MIGRATION_LOG.md
```

**Time:** ~5 minutes for 1334 cases
**Data Loss:** 0% (validated in testing)

---

### Workflow 14: Selective Migration

**Scenario:** Migrate only specific folders/test cases.

**Steps:**

```bash
# 1. Export full project
btl_testmo export --project-id 2 --output full-export/

# 2. Copy only needed folders
mkdir -p selective-export/test-cases
cp -r full-export/test-cases/authentication selective-export/test-cases/
cp -r full-export/test-cases/checkout selective-export/test-cases/

# 3. Update metadata (optional)
# Edit test cases to update tags, priorities, etc.

# 4. Import to new project
btl_testmo import \
  --project-id 9 \
  --source selective-export

# 5. Verify selective import
ls selective-export/test-cases/
# Should show: authentication/ checkout/

btl_testmo status --project selective-export/
# Should show all files synced
```

---

## 📊 Performance Optimization

### Tips for Faster Operations

**1. Use Batch Mode**
```bash
# Slow: Individual updates (~223ms each)
for file in TC*.yml; do
  btl_testmo update "$file"
done

# Fast: Batch update (~1.5s for 5 cases)
btl_testmo update --folder testmo/oneapp/test-cases/folder --batch
```

**2. Validate Before Pushing**
```bash
# Catch errors early (locally, fast)
btl_testmo validate TC-NEW-*.yml

# Then batch create (no failures)
btl_testmo create TC-NEW-*.yml --batch
```

**3. Use --dry-run**
```bash
# Preview changes without API calls
btl_testmo sync --project testmo/oneapp --dry-run
```

**4. Filter with --folder-id**
```bash
# Sync specific folder only
btl_testmo sync \
  --project testmo/oneapp \
  --folder-id 7338
```

---

## 📚 Best Practices Summary

1. **Sync regularly** - Daily pulls prevent large merges
2. **Use feature branches** - Isolate changes, enable code review
3. **Validate locally** - Catch errors before pushing
4. **Batch operations** - 3-5x faster for multiple cases
5. **Git commit messages** - Use conventional commits (Add, Update, Fix)
6. **AI assistance** - Leverage Claude Code for generation and review
7. **CI/CD integration** - Automate sync on merge
8. **Backup regularly** - Nightly exports to git and archives
9. **Document workflows** - Team-specific processes in repo README
10. **Monitor performance** - Track sync times, optimize bottlenecks

---

## 📚 See Also

- [CLI Reference](CLI_REFERENCE.md) - All available commands
- [YAML Format](YAML_FORMAT.md) - Test case format specification
- [Architecture](ARCHITECTURE.md) - How the system works
- [Troubleshooting](TROUBLESHOOTING.md) - Common issues

---

**Workflows Guide complete** ✅
