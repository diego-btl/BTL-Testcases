# ClickUp Integration Guide

**Integration Type:** MCP (Model Context Protocol) Server
**Platform:** Claude Desktop
**Purpose:** Link test cases with ClickUp tasks for complete traceability

---

## 🎯 What is ClickUp Integration?

Connect test cases to your project management system:
- **Bidirectional Links** - Test ↔ Task traceability
- **Coverage Tracking** - Which tasks have test coverage
- **Auto-task Creation** - Create bug tasks from test failures
- **Sprint Reports** - Test coverage by sprint/milestone

---

## ⚙️ Setup (One-Time, 10 minutes)

### Step 1: Get ClickUp API Key

1. Go to https://app.clickup.com/settings/apps
2. Click "Apps" → "API Token"
3. Generate new token
4. Copy token (starts with `pk_`)

### Step 2: Get Team ID

```bash
# Option 1: From URL
# When in ClickUp, URL is: https://app.clickup.com/TEAM_ID/...
# Copy the number after app.clickup.com/

# Option 2: Via API
curl "https://api.clickup.com/api/v2/team" \
  -H "Authorization: YOUR_API_TOKEN"
```

### Step 3: Configure Claude Desktop MCP

**Location:** `~/Library/Application Support/Claude/config.json` (Mac)

**Add ClickUp server:**
```json
{
  "mcpServers": {
    "clickup": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-server-clickup"],
      "env": {
        "CLICKUP_API_KEY": "pk_YOUR_TOKEN_HERE",
        "CLICKUP_TEAM_ID": "9014537789"
      }
    }
  }
}
```

### Step 4: Restart Claude Desktop

```bash
# Quit Claude Desktop completely
# Relaunch from Applications

# Or from terminal:
killall Claude
open -a Claude
```

### Step 5: Verify Setup

In Claude Desktop, ask:
```
Search ClickUp for tasks with "test"
```

If you see results, setup is complete! ✅

---

## 📋 Common Workflows

### Workflow 1: Link Test Case to Task

**Goal:** Create bidirectional link between test and requirement

**Prompt for Claude:**
```
Link test case TC66186 to ClickUp task

Task URL: https://app.clickup.com/t/8a2b4c
(or Task ID: 8a2b4c)

Steps:
1. Get task details from ClickUp:
   - Task name
   - Status
   - Priority
   - Assignee
   - Description

2. Read test case:
   File: testmo/oneapp/test-cases/home/charge/v2l-vehicle-to-load/TC66186-v2l-screen.yml

3. Add to test case notes section:
   ---
   ## Related ClickUp Tasks
   - **[V2L Power Display Feature](https://app.clickup.com/t/8a2b4c)**
     - Status: In Development
     - Priority: High
     - Assignee: John Doe

4. Save test case

5. Add comment to ClickUp task:
   "✅ Test Coverage Added

   Test Case: TC66186 - V2L Screen Display
   Link: https://bethinklabs.testmo.net/repositories/2/cases/66186

   Covers:
   - V2L screen navigation
   - Power output display
   - Toggle functionality
   - Real-time updates"

Result: Complete traceability established
```

**Verification:**
- Test case has ClickUp link in notes
- ClickUp task has comment with test case link
- Both visible to team

---

### Workflow 2: Track Sprint Test Coverage

**Goal:** Report test coverage for current sprint

**Prompt:**
```
Generate test coverage report for current sprint

Sprint: https://app.clickup.com/sprint/[sprint-id]
(or List: "Sprint 5.2")

Process:
1. Get all tasks in sprint from ClickUp
2. For each task:
   - Check if test case exists linking to it
   - Search test cases for task ID or URL
   - Categorize: Has Coverage / No Coverage

3. Output format:
## Sprint 5.2 Test Coverage Report

### Summary
- Total tasks: X
- Tasks with coverage: Y (Z%)
- Tasks without coverage: A (B%)

### Tasks with Test Coverage ✅
| Task | Test Cases | Priority |
|------|------------|----------|
| V2L Feature | TC66186, TC66187 | High |
| ...

### Tasks WITHOUT Test Coverage ❌
| Task | Priority | Assignee | Recommendation |
|------|----------|----------|----------------|
| Payment Flow | Critical | John | URGENT - Create tests |
| ...

### Recommendations
1. Critical priority tasks needing tests: [list]
2. High coverage areas: [list]
3. Gaps to address: [list]

**Action Items:**
- [ ] Create tests for [Critical task]
- [ ] Review [Task] test coverage
```

---

### Workflow 3: Create Bug Tasks from Test Failures

**Goal:** Auto-create ClickUp tasks for test failures

**Prompt:**
```
Create ClickUp bug tasks for failed test cases

Failed tests:
- TC66186: V2L power display shows incorrect values
- TC66187: V2L toggle doesn't respond
- TC66188: V2L screen crashes on iOS

ClickUp list: "Bugs" (or List ID: 12345)

For each failed test:
1. Create task in Bugs list
2. Title: "[TEST FAILURE] [Test case name]"
3. Description:
   ```
   ## Test Failure

   **Test Case:** TC[ID] - [Name]
   **Link:** https://bethinklabs.testmo.net/repositories/2/cases/[ID]

   **Failure:** [Description]

   **Expected:** [From test case]
   **Actual:** [Failure description]

   **Platform:** [iOS/Android]
   **Environment:** [Prod/Staging]

   ## Steps to Reproduce
   [From test case]

   ## Priority Justification
   [Based on test priority + severity]
   ```

4. Set priority (map test priority → task priority):
   - Critical test → Urgent priority
   - High test → High priority
   - etc.

5. Add labels: "test-failure", "qa", "automated"

6. Assign to: [QA Lead or Dev Lead]

7. Add comment to test case:
   "Bug ticket created: [Task URL]"

Report created tasks with URLs.
```

**Result:** Bugs tracked in 2 minutes (vs 20 minutes manually)

---

### Workflow 4: Find Tasks Needing Test Coverage

**Goal:** Identify requirements without tests

**Prompt:**
```
Find ClickUp tasks that need test coverage

Criteria:
- List: "Features" or "Sprint Backlog"
- Status: In Progress, Testing, or Review
- Priority: High or Critical

Process:
1. Search ClickUp for tasks matching criteria
2. For each task:
   - Extract task name/description
   - Search test cases for related tests:
     * Search by feature name
     * Search by task ID in notes
     * Search by keywords from task

3. Categorize:
   - Has Coverage (1+ test cases)
   - Partial Coverage (< 3 test cases, complex feature)
   - No Coverage (0 test cases)

Output:
## Tasks Needing Test Coverage

### No Coverage ❌ (Priority: Create Tests)
| Task | Priority | Assignee | Suggested Tests |
|------|----------|----------|-----------------|
| New Payment Flow | Critical | John | Happy path, errors, edge cases |
| ...

### Partial Coverage ⚠️ (Priority: Review)
| Task | Current Tests | Priority | Gaps |
|------|---------------|----------|------|
| V2L Feature | 2 tests | High | Missing edge cases, iOS specific |
| ...

### Good Coverage ✅
| Task | Tests | Status |
|------|-------|--------|
| Login Flow | 8 tests | Complete |
| ...

**Recommendations:**
1. Critical gaps: [list with task URLs]
2. Quick wins: [simple tests to add]
3. Complex features needing deep testing: [list]
```

---

## 🔗 Advanced Use Cases

### Auto-Update Task Status from Test Results

**Prompt:**
```
Update ClickUp task statuses based on test results

Input: Test execution results (pass/fail)

Rules:
- All tests pass → Move task to "Ready for Release"
- Some tests fail → Move to "In Testing" + add comment
- Critical test fails → Move to "Blocked" + high priority comment

For each task:
1. Find related tests
2. Check test results
3. Determine new status
4. Update ClickUp task
5. Add comment with test summary

Comment format:
📊 Test Results Update

✅ Passed: X tests
❌ Failed: Y tests
⏭️ Skipped: Z tests

[Details of failures if any]

Updated: [timestamp]
```

---

### Generate Coverage Matrix

**Prompt:**
```
Create requirements vs test cases coverage matrix

ClickUp Source:
- List: "Features" or Space: "Project Name"
- Timeframe: Last 3 months

Output:
## Requirements Coverage Matrix

| Requirement | Test Cases | Coverage | Priority | Status |
|-------------|------------|----------|----------|--------|
| Feature A | TC1, TC2, TC3 | 100% | High | ✅ |
| Feature B | TC4 | 30% | Critical | ⚠️ Need more tests |
| Feature C | None | 0% | High | ❌ No coverage |

### Coverage by Priority
- Critical: 85% (17/20 requirements)
- High: 70% (14/20 requirements)
- Medium: 50% (10/20 requirements)

### Recommendations
1. Critical gap: [Requirement] has 0 tests
2. High priority features under-tested: [list]
3. Well-covered areas: [list]
```

---

### Sync Test Case Tags with ClickUp Labels

**Prompt:**
```
Sync test case tags with ClickUp task labels

Direction: ClickUp → Test Cases

For tasks linked to test cases:
1. Get task labels from ClickUp
2. Find related test case files
3. Add matching tags to test case metadata.tags
4. Maintain existing tags
5. Report changes

Example:
- ClickUp task has labels: "v2l", "critical", "release-5.2"
- Test case TC66186 gets tags: ["v2l", "critical", "release-5.2"]

Report:
- Tasks processed: X
- Test cases updated: Y
- Tags added: [breakdown]
```

---

## 📊 Reporting

### Weekly Test Coverage Report

**Prompt:**
```
Generate weekly test coverage report

ClickUp data:
- Tasks completed this week
- Tasks in testing
- Tasks in review

Test data:
- New test cases created
- Test cases updated
- Test execution results

Output:
## Weekly Test Activity Report
Week of [Date]

### ClickUp Activity
- Tasks completed: X
- Tasks in testing: Y
- Tasks in review: Z

### Test Coverage
- New tests created: A
- Tests updated: B
- Coverage increase: +C%

### Highlights
- ✅ [Feature] fully covered
- ⚠️ [Feature] needs attention
- 🚀 [Achievement]

### Next Week Focus
1. [Priority task] needs tests
2. [Feature] in review - verify coverage
3. [Area] quality improvements
```

---

## 🐛 Troubleshooting

### Issue: "ClickUp MCP not responding"

**Symptoms:** Claude says "I can't access ClickUp"

**Solutions:**
```bash
# 1. Check MCP configuration
cat ~/Library/Application\ Support/Claude/config.json

# 2. Verify API key is valid
curl "https://api.clickup.com/api/v2/team" \
  -H "Authorization: YOUR_API_KEY"

# 3. Restart Claude Desktop
killall Claude && open -a Claude

# 4. Check MCP logs
tail -f ~/Library/Logs/Claude/mcp-server-clickup.log
```

### Issue: "Can't find task by URL"

**Cause:** Task ID format not recognized

**Solution:**
```
Use task ID directly instead of URL:
- ❌ "https://app.clickup.com/t/8a2b4c"
- ✅ "8a2b4c"

Or extract ID from URL and provide separately.
```

### Issue: "Rate limit exceeded"

**Cause:** Too many API calls

**Solution:**
```
ClickUp API limits: 100 requests/minute

For bulk operations:
1. Process in smaller batches
2. Add delays between batches
3. Use search instead of individual gets when possible
```

---

## 💡 Best Practices

### Naming Conventions

**ClickUp Task Tags:**
```
Use consistent tags that match test case tags:
- "v2l-feature"
- "critical-path"
- "release-5.2"
```

**Test Case References:**
```
In ClickUp task descriptions, always use format:
Test Case: TC[ID] - [Name]
Link: https://bethinklabs.testmo.net/repositories/[project]/cases/[ID]
```

### Maintaining Links

```
Review links quarterly:
1. Find orphaned test cases (no ClickUp link)
2. Find orphaned tasks (no test reference)
3. Update or archive as needed
```

---

## 📚 Additional Resources

- **[How-To Guide](../HOW_TO_GUIDE.md)** - More workflow examples
- **[Best Practices](BEST_PRACTICES.md)** - General agent optimization
- **ClickUp API Docs:** https://clickup.com/api
- **MCP Documentation:** https://modelcontextprotocol.io

---

**Setup complete?** Try Workflow 1 to link your first test case!

**Need help?** See [BEST_PRACTICES.md](BEST_PRACTICES.md) for troubleshooting tips.
