# Practical Workflows

This document describes real-world workflows for managing test cases using the Git-first approach.

## Table of Contents

- [Daily Workflows](#daily-workflows)
- [Common Tasks](#common-tasks)
- [Team Collaboration](#team-collaboration)
- [Advanced Workflows](#advanced-workflows)

---

## Daily Workflows

### Workflow 1: Periodic Export (Backup/Sync)

**Use Case**: Regular backup of test cases from Testmo to Git

```bash
# Export all test cases from a specific folder
python scripts/testmo_export.py \
  --project-id 2 \
  --folder-id 7148 \
  --output-dir test-cases/dealer-offers

# Commit to Git
git add test-cases/dealer-offers/
git commit -m "Sync: Weekly backup from Testmo - Dealer Offers"
git push origin main
```

**Frequency**: Weekly or after major Testmo updates
**Benefit**: Git becomes the source of truth, safe backup

---

### Workflow 2: Create New Test Cases in Git

**Use Case**: QA writes new test cases in YAML, submits for review

```bash
# 1. Create feature branch
git checkout -b feature/dealer-offers-validation

# 2. Create new YAML file
cat > test-cases/dealer-offers/TC-new-validation.yml <<EOF
metadata:
  testmo_id: null  # null for new cases
  name: "Dealer Offers - Validate Phone Format"
  priority: medium
  state: draft

description: |
  Verify that dealer phone numbers display in correct format

preconditions:
  - User is on Dealer Details screen

steps:
  - action: View dealer phone number
    expected: Phone displays as (XXX) XXX-XXXX format

  - action: Tap phone number
    expected: System dialer opens with formatted number
EOF

# 3. Validate the YAML
python scripts/yaml_converter.py validate \
  --input-dir test-cases/dealer-offers

# 4. Commit and push
git add test-cases/dealer-offers/TC-new-validation.yml
git commit -m "Create: New test for dealer phone validation

- Validates phone number format display
- Tests dialer integration
- Covers both iOS and Android

Relates to: JIRA-1234"

git push origin feature/dealer-offers-validation

# 5. Create PR on GitHub
# Team reviews the test case via PR

# 6. After PR is merged, import to Testmo
git checkout main
git pull origin main

python scripts/testmo_import.py \
  --project-id 2 \
  --input-dir test-cases/dealer-offers \
  --folder-name "Dealer Offers"

# 7. Export again to capture testmo_id
python scripts/testmo_export.py \
  --project-id 2 \
  --folder-id 7148 \
  --output-dir test-cases/dealer-offers

git commit -am "Sync: Update testmo_ids after import to Testmo"
git push origin main
```

**Benefit**: Code review before test case goes to Testmo

---

### Workflow 3: Update Existing Test Cases

**Use Case**: Fix or improve existing test cases

**⚠️ Note**: Due to Testmo API limitations, we cannot update individual cases. Use batch re-import strategy.

```bash
# 1. Create feature branch
git checkout -b fix/dealer-offers-typos

# 2. Edit YAML files (fix typos, add steps, etc.)
vim test-cases/dealer-offers/TC-64839.yml

# Make your changes:
# - Fix typo in step description
# - Add new edge case step
# - Update expected result

# 3. Validate changes
python scripts/yaml_converter.py validate \
  --input-dir test-cases/dealer-offers

# 4. Review diff before committing
git diff test-cases/dealer-offers/TC-64839.yml

# 5. Commit with clear description
git add test-cases/dealer-offers/TC-64839.yml
git commit -m "Fix: Correct step descriptions in dealer phone test

- Fixed typo in step 1 action
- Added edge case for missing phone number
- Updated expected results for clarity"

git push origin fix/dealer-offers-typos

# 6. Create PR, get review, merge

# 7. After merge, batch re-import folder
python scripts/testmo_import.py \
  --project-id 2 \
  --input-dir test-cases/dealer-offers \
  --folder-name "Dealer Offers - Updated"

# 8. Manual step in Testmo UI:
#    - Delete old "Dealer Offers" folder
#    - Rename "Dealer Offers - Updated" to "Dealer Offers"

# 9. Export to sync
python scripts/testmo_export.py \
  --project-id 2 \
  --folder-id NEW_FOLDER_ID \
  --output-dir test-cases/dealer-offers

git commit -am "Sync: Update after Testmo re-import"
```

**Limitation**: Requires manual folder management in Testmo UI
**Benefit**: Still get version control, code review, audit trail

---

### Workflow 4: Bulk Update Multiple Test Cases

**Use Case**: Update multiple test cases at once (e.g., add new precondition to all)

```bash
# 1. Create branch
git checkout -b update/add-login-precondition

# 2. Use script or text editor to update multiple files
# Example: Add "User must be logged in" to all test preconditions

for file in test-cases/dealer-offers/*.yml; do
  # Your bulk edit logic here
  # Could use sed, awk, or Python script
done

# 3. Validate all changes
python scripts/yaml_converter.py validate \
  --input-dir test-cases/dealer-offers

# 4. Review all changes
git diff test-cases/dealer-offers/

# 5. Commit
git add test-cases/dealer-offers/
git commit -m "Update: Add login precondition to all dealer tests

- Added 'User must be logged in' precondition
- Ensures consistent test setup
- Affects 9 test cases"

# 6. PR → Review → Merge

# 7. Batch re-import
python scripts/testmo_import.py \
  --project-id 2 \
  --input-dir test-cases/dealer-offers \
  --folder-name "Dealer Offers v2"
```

**Benefit**: Make consistent changes across many test cases easily

---

## Common Tasks

### Task: Search for Test Cases

```bash
# Search by name
grep -r "Dealer Offers" test-cases/

# Search by Jira reference
grep -r "IUG-1169" test-cases/

# Search by priority
grep -r "priority: high" test-cases/

# Find all test cases with specific step
grep -r "Tap on phone icon" test-cases/
```

**Benefit**: Full-text search across all test cases

---

### Task: Find Who Changed What

```bash
# See who last modified a test
git log test-cases/dealer-offers/TC-64839.yml

# See blame (line-by-line authors)
git blame test-cases/dealer-offers/TC-64839.yml

# See all changes to a test over time
git log -p test-cases/dealer-offers/TC-64839.yml

# Find when a specific step was added
git log -S "Tap on phone icon" test-cases/dealer-offers/
```

**Benefit**: Complete audit trail

---

### Task: Rollback Changes

```bash
# Undo last commit (keep changes)
git reset HEAD~1

# Revert a specific commit
git revert abc123

# Restore file to previous version
git checkout HEAD~1 test-cases/dealer-offers/TC-64839.yml

# After rollback, re-import to Testmo
python scripts/testmo_import.py \
  --project-id 2 \
  --input-dir test-cases/dealer-offers \
  --folder-name "Dealer Offers - Rollback"
```

**Benefit**: Easy recovery from mistakes

---

### Task: Compare Versions

```bash
# Compare working directory vs last commit
git diff test-cases/dealer-offers/TC-64839.yml

# Compare two branches
git diff main feature/my-changes -- test-cases/

# Compare two commits
git diff abc123 def456 -- test-cases/

# Show changes in last commit
git show HEAD:test-cases/dealer-offers/TC-64839.yml
```

**Benefit**: Visual diff of test case changes

---

## Team Collaboration

### Scenario: Two QAs Working on Same Feature

**Diego's work:**
```bash
git checkout -b diego/add-error-cases
# Edit test-cases/dealer-offers/TC-64839.yml
# Add error handling steps
git commit -am "Add error cases for phone validation"
git push origin diego/add-error-cases
```

**Sarah's work:**
```bash
git checkout -b sarah/add-accessibility
# Edit test-cases/dealer-offers/TC-64839.yml
# Add accessibility testing steps
git commit -am "Add accessibility validation steps"
git push origin sarah/add-accessibility
```

**Merging:**
```bash
# Diego's PR is merged first
# Sarah rebases her branch
git checkout sarah/add-accessibility
git rebase main

# If conflicts:
git status  # See conflicted files
vim test-cases/dealer-offers/TC-64839.yml  # Resolve conflicts
git add test-cases/dealer-offers/TC-64839.yml
git rebase --continue

# Push updated branch
git push origin sarah/add-accessibility --force

# Create PR → Merge
```

**Benefit**: Git handles parallel development gracefully

---

### Scenario: Code Review Feedback

**Reviewer comment**: "Step 2 expected result is unclear"

**Author responds:**
```bash
# On feature branch
git checkout feature/my-test-case

# Fix the issue
vim test-cases/dealer-offers/TC-64839.yml

# Commit with reference to review
git commit -am "Review fix: Clarify step 2 expected result

Per Sarah's feedback in PR review"

git push origin feature/my-test-case

# PR automatically updates
```

**Benefit**: Feedback loop is visible and traceable

---

## Advanced Workflows

### Workflow: AI-Assisted Test Creation (Future)

**Vision**: AI agent generates test cases from ClickUp tasks

```bash
# User runs command (future feature)
python scripts/ai_generate_test.py \
  --clickup-task "https://app.clickup.com/t/xxxxx" \
  --output test-cases/dealer-offers/TC-new.yml

# AI agent:
# 1. Reads ClickUp task requirements
# 2. Generates YAML test case
# 3. Creates PR for human review

# Human reviews PR:
# - Check test coverage
# - Validate steps make sense
# - Approve or request changes

# After approval:
# - AI agent imports to Testmo
# - Updates YAML with testmo_id
# - Closes ClickUp task
```

**Status**: Planned for Phase 1 (Q1 2026)

---

### Workflow: Cross-Feature Analysis

```bash
# Find all tests that reference "login"
grep -r "login" test-cases/ | wc -l

# Find all high priority tests
find test-cases/ -name "*.yml" -exec grep -l "priority: high" {} \;

# Generate coverage report
python scripts/analyze_coverage.py \
  --input-dir test-cases/ \
  --output reports/coverage.html
```

**Status**: Custom scripts as needed

---

### Workflow: Template-Based Creation

```bash
# Use template
cp templates/test-case-template.yml \
   test-cases/new-feature/TC-new.yml

# Edit with vim/VS Code
vim test-cases/new-feature/TC-new.yml

# Template has:
# - Standardized structure
# - Comments with guidance
# - Common patterns
```

**Benefit**: Consistency across team

---

## Workflow Summary

| Workflow | Frequency | Complexity | Value |
|----------|-----------|------------|-------|
| Periodic Export | Weekly | Low | High (backup) |
| Create New Test | Daily | Low | High |
| Update Test | As needed | Medium | High |
| Bulk Update | Monthly | Medium | Medium |
| Team Collaboration | Daily | Medium | High |
| Rollback | Rare | Low | High (safety net) |
| AI Generation | Future | High | Very High |

---

## Best Practices

### Commit Messages

**Good:**
```
Create: New test for dealer phone validation

- Validates phone number format
- Tests dialer integration
- Covers iOS and Android

Relates to: JIRA-1234
```

**Bad:**
```
update test
```

### Branch Naming

**Good:**
- `feature/dealer-offers-validation`
- `fix/typo-in-steps`
- `update/add-preconditions`

**Bad:**
- `my-branch`
- `test`
- `asdf`

### PR Reviews

**Checklist:**
- [ ] Test case follows schema
- [ ] Steps are clear and actionable
- [ ] Expected results are specific
- [ ] Preconditions are complete
- [ ] Jira reference is included (if applicable)
- [ ] Validation passes

---

## Troubleshooting

### Issue: Merge Conflicts

```bash
# See conflicted files
git status

# Edit files to resolve
vim test-cases/dealer-offers/TC-64839.yml

# Look for conflict markers:
# <<<<<<< HEAD
# =======
# >>>>>>> feature-branch

# After resolving:
git add test-cases/dealer-offers/TC-64839.yml
git commit
```

### Issue: Validation Failures

```bash
# Run validation with verbose output
python scripts/yaml_converter.py validate \
  --input-dir test-cases/dealer-offers \
  --verbose

# Check specific file
python -c "import yaml; print(yaml.safe_load(open('test-cases/dealer-offers/TC-64839.yml')))"
```

### Issue: Import Fails

```bash
# Check Testmo API credentials
echo $TESTMO_API_KEY

# Verify project and folder IDs
python scripts/testmo_client.py list-projects
python scripts/testmo_client.py list-folders --project-id 2

# Try dry-run first
python scripts/testmo_import.py \
  --project-id 2 \
  --input-dir test-cases/dealer-offers \
  --folder-name "Test" \
  --dry-run
```

---

## Next Steps

1. ✅ Read this workflow guide
2. 📖 Review [QUICKSTART.md](QUICKSTART.md) for setup
3. 🎯 Try "Create New Test Cases" workflow
4. 👥 Practice with your team
5. 🔄 Iterate and improve workflows

**Questions?** Check [API_FINDINGS.md](API_FINDINGS.md) for technical details.

---

**Last Updated:** January 28, 2026
**Maintainer:** Diego Garcia
