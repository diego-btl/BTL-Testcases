# Team Workflow Guide

## For QA Engineers: Working with Git-First Test Cases

### Daily Workflow

#### 1. Starting Work

```bash
# Pull latest changes
git checkout main
git pull origin main

# Create feature branch
git checkout -b improve-remote-services
```

#### 2. Finding Test Cases

```bash
# Browse by feature
ls test-cases/remote-services/
ls test-cases/authentication/
ls test-cases/vehicle-status/

# Search by name
find test-cases -name "*remote-start*"

# Search content
grep -r "biometric" test-cases/
```

#### 3. Editing Test Cases

Open the YAML file in your favorite editor:

```bash
# Using VS Code
code test-cases/remote-services/TC00123-remote-start.yml

# Using vim
vim test-cases/remote-services/TC00123-remote-start.yml
```

**Common Edits:**

- Adding a step:
  ```yaml
  - id: 6
    action: "New step action"
    expected: "Expected result"
  ```

- Adding edge case:
  ```yaml
  - id: 7
    action: "Test with no internet connection"
    expected: "Error message: 'No connection. Please try again.'"
  ```

- Updating regional variations:
  ```yaml
  regional_variations:
    Brazil:
      - step: 3
        note: "Temperature shown in Celsius"
  ```

#### 4. Validating Your Changes

```bash
# Validate YAML format
python scripts/validate_yaml.py

# Check specific file
python scripts/validate_yaml.py --input-dir test-cases/remote-services
```

#### 5. Committing Changes

```bash
# Stage your changes
git add test-cases/

# Commit with descriptive message
git commit -m "Add timeout edge case for remote start"

# Push to remote
git push origin improve-remote-services
```

#### 6. Creating Pull Request

1. Go to GitHub repository
2. Click "Compare & pull request"
3. Fill in PR template:
   ```markdown
   ## Changes
   - Added timeout edge case (step 7)
   - Updated expected behavior for network errors
   
   ## Testing
   - [ ] Validated YAML format
   - [ ] Reviewed with team lead
   
   ## Related
   - ClickUp: https://app.clickup.com/t/xxxxx
   ```

4. Request review from team lead or peer
5. Wait for approval

#### 7. After Merge

Your changes are automatically synced to Testmo via GitHub Actions!

---

## Common Scenarios

### Scenario 1: Bug Found During Execution

**Problem:** Test case missing validation step

```bash
# 1. Create bug fix branch
git checkout -b fix-missing-validation

# 2. Edit test case
# Add missing step in YAML

# 3. Commit and push
git add test-cases/
git commit -m "Fix: Add validation step for error message"
git push origin fix-missing-validation

# 4. Create PR with "Fix:" prefix
```

### Scenario 2: New Feature Test Cases

**Problem:** New remote service feature needs tests

```bash
# 1. Create feature branch
git checkout -b new-remote-lock-tests

# 2. Create new YAML files
cp test-cases/examples/TC00001-remote-engine-start-happy-path.yml \
   test-cases/remote-services/TC00456-remote-lock-happy-path.yml

# 3. Edit metadata and steps
# Update: id, name, steps, etc.

# 4. Validate
python scripts/validate_yaml.py

# 5. Commit and push
git add test-cases/
git commit -m "Add remote lock test cases"
git push origin new-remote-lock-tests

# 6. Create PR
```

### Scenario 3: Regional Variation Update

**Problem:** Brazil needs different button text

```bash
# 1. Find affected test cases
grep -r "Remote Start" test-cases/

# 2. Edit regional_variations section
# Add Brazil note

# 3. Commit
git add test-cases/
git commit -m "Update Brazil regional variations"
```

### Scenario 4: Automation Coverage Update

**Problem:** New automation implemented

```bash
# 1. Edit automation section in YAML
automation:
  framework: maestro
  test_file: "tests/new-test.yaml"
  coverage: full  # Changed from partial
  notes: "Fully automated as of Sprint 24"

# 2. Commit
git commit -am "Update automation coverage to full"
```

---

## Best Practices

### ✅ DO

1. **Create descriptive branch names**
   - ✅ `improve-remote-services`
   - ✅ `fix-auth-test-steps`
   - ✅ `add-vehicle-status-tests`

2. **Write clear commit messages**
   - ✅ `Add edge case for network timeout`
   - ✅ `Fix: Correct expected behavior in step 3`
   - ✅ `Update regional variations for Mexico`

3. **Validate before committing**
   ```bash
   python scripts/validate_yaml.py --strict
   ```

4. **Reference ClickUp tasks**
   ```yaml
   traceability:
     clickup_task: "https://app.clickup.com/t/xxxxx"
   ```

5. **Keep PRs focused**
   - One feature/fix per PR
   - Related changes grouped together

### ❌ DON'T

1. **Commit directly to main**
   - ❌ `git push origin main`
   - ✅ Use branches and PRs

2. **Skip validation**
   - ❌ Push without running validate script
   - ✅ Always validate first

3. **Use vague commit messages**
   - ❌ `updated tests`
   - ✅ `Add timeout validation to remote start test`

4. **Break YAML format**
   - ❌ Mix tabs and spaces
   - ✅ Use consistent 2-space indentation

5. **Delete testmo_id**
   - ❌ Remove `testmo_id` field
   - ✅ Keep it for sync tracking

---

## Conflict Resolution

### Merge Conflicts in YAML

If you get a merge conflict:

```bash
# 1. Fetch latest changes
git fetch origin main

# 2. Rebase your branch
git rebase origin/main

# 3. If conflicts occur, Git will show:
# CONFLICT (content): Merge conflict in test-cases/...
```

**Resolving:**

```yaml
# Your file will look like:
<<<<<<< HEAD
  - id: 5
    action: "Your change"
=======
  - id: 5
    action: "Their change"
>>>>>>> origin/main

# Edit to keep correct version or combine:
  - id: 5
    action: "Combined change"
```

Then:
```bash
git add test-cases/
git rebase --continue
```

---

## Tips & Tricks

### Quick Search

```bash
# Find test by ID
grep -r "TC00123" test-cases/

# Find by feature
ls test-cases/remote-services/

# Find by tag
grep -r "smoke" test-cases/ | grep "tags:"

# Find automation gaps
grep -r "coverage: none" test-cases/
```

### VS Code Extensions

Recommended:
- **YAML** by Red Hat (syntax highlighting)
- **GitLens** (Git blame inline)
- **Git Graph** (visual Git history)

### Command Aliases

Add to `.bashrc` or `.zshrc`:

```bash
alias tc-validate='python scripts/validate_yaml.py'
alias tc-export='python scripts/testmo_export.py'
alias tc-import='python scripts/testmo_import.py'
alias tc-find='find test-cases -name'
```

---

## Getting Help

1. **YAML format issues**: Check `docs/schema.md`
2. **Git questions**: Ask team lead or check [Git docs](https://git-scm.com/doc)
3. **Script errors**: Check script help: `python scripts/validate_yaml.py --help`
4. **Testmo sync issues**: Verify `.env` configuration

---

## Cheat Sheet

```bash
# Daily workflow
git checkout main && git pull
git checkout -b my-feature
# ... make changes ...
python scripts/validate_yaml.py
git add test-cases/ && git commit -m "..."
git push origin my-feature

# Quick validation
python scripts/validate_yaml.py --input-dir test-cases/remote-services

# Search
grep -r "keyword" test-cases/

# View Git history
git log --oneline test-cases/remote-services/TC00123.yml

# See who changed what
git blame test-cases/remote-services/TC00123.yml

# Undo last commit (not pushed)
git reset --soft HEAD~1

# Sync from Testmo (initial/refresh)
python scripts/testmo_export.py --project-id 1 --feature remote-services
```

---

## Questions?

Contact: Diego Garcia (QA Engineering Manager)
Slack: #qa-test-management
