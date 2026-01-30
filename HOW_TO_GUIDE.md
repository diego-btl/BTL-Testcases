# How-To Guide: AI-Powered Test Case Management

**Version:** 2.0.0
**Last Updated:** 2026-01-30
**Focus:** AI-Assisted Workflows + Practical Test Management

---

## 🎯 Overview

This guide shows you how to leverage AI agents (Claude Code, Claude Desktop) to 10x your QA productivity by:
- **Improving test cases** with better descriptions, steps, and validation
- **Creating similar test cases** using patterns and templates
- **Connecting context** from ClickUp tickets and Slack discussions
- **Automating workflows** for bulk operations and quality audits
- **Managing 1,710+ test cases** across 3 projects efficiently

**Key Stat:** With AI assistance, test case creation goes from 30 minutes → 5 minutes per case.

---

## 🤖 Working with AI Agents

### What Can AI Agents Do?

**1. Improve Test Cases**
- Enhance vague descriptions → specific scenarios
- Add missing preconditions and edge cases
- Fix validation issues automatically
- Standardize format across test suites

**2. Create Similar Cases**
- Find patterns in existing tests
- Generate variations (platform, environment, user type)
- Batch creation from templates

**3. Connect Context**
- Link ClickUp tickets for traceability
- Pull Slack thread discussions
- Add documentation references
- Maintain bidirectional links

**4. Automate Workflows**
- Bulk tag updates
- Status synchronization
- Quality audits
- Coverage reports

### Available Agents

1. **Claude Code** (Terminal-based) - Direct file/command execution
2. **Claude Desktop** (Chat-based) - Interactive workflows with MCP
3. **MCP Servers** - ClickUp, Slack, Testmo integrations

See [agents/](agents/) for detailed documentation.

---

## 📋 Quick Start Workflows

### Workflow 1: Improve a Test Case

**Scenario:** TC66186 needs better steps and validation

**Prompt for Claude:**
```
Improve test case TC66186 with more detailed steps:

File: testmo/oneapp/test-cases/home/charge/v2l-vehicle-to-load/TC66186-v2l-screen.yml

Requirements:
1. Add preconditions (vehicle state, battery > 50%, parked)
2. Expand 3 steps → 7 steps with specific expected results
3. Add edge case for low battery (< 20%)
4. Keep existing YAML structure
5. Preserve testmo metadata (don't modify testmo: section)
6. Update the file directly

Context:
- V2L = Vehicle to Load feature
- Nissan ARIYA EV
- iOS & Android apps
```

**What Claude Code Will Do:**
1. Read current test case YAML
2. Analyze existing content
3. Enhance with specific details
4. Preserve all metadata
5. Write updated file
6. Compute new content hash

**Result:** Test case upgraded from basic → comprehensive in ~2 minutes.

---

### Workflow 2: Create Similar Test Cases

**Scenario:** Need 5 V2L test variations

**Prompt:**
```
Create 5 similar test cases based on TC66186-v2l-screen.yml

Variations:
1. V2L with low battery (< 20%)
2. V2L with vehicle in motion
3. V2L overnight charging mode
4. V2L emergency disconnect
5. V2L multiple devices connected

Requirements:
- Output folder: testmo/oneapp/test-cases/home/charge/v2l-vehicle-to-load/
- Filename format: TC-NEW-v2l-[scenario].yml
- Use TC66186 as template
- Each test has unique preconditions and expected results
- Add platform configurations (iOS/Android)

After creating files, validate with:
btl_testmo validate testmo/oneapp/test-cases/home/charge/v2l-vehicle-to-load/
```

**Result:** 5 new test cases created in ~5 minutes (vs 150 minutes manually).

---

### Workflow 3: Connect ClickUp Ticket

**Scenario:** Link test case to feature ticket for traceability

**Prerequisites:**
- ClickUp MCP configured in Claude Desktop
- Task ID or URL from ClickUp

**Prompt:**
```
Connect test case TC66186 to ClickUp task

Task: https://app.clickup.com/t/8a2b4c (or task ID: 8a2b4c)

Steps:
1. Get ClickUp task details using ClickUp MCP
2. Read test case: testmo/oneapp/.../TC66186-v2l-screen.yml
3. Add to test case notes section:
   ---
   ## Related Tickets
   - [Feature: V2L Power Display](https://app.clickup.com/t/8a2b4c)
     - **Status**: In Development
     - **Priority**: High
     - **Assignee**: [from ClickUp]
4. Save test case
5. Add comment to ClickUp task:
   "Test coverage added: TC66186 (V2L Screen Display)"
   Link: https://bethinklabs.testmo.net/repositories/2/cases/66186

Result: Bidirectional traceability
```

**Benefits:**
- QA ↔ Dev visibility
- Requirement coverage tracking
- Status synchronization

---

### Workflow 4: Pull Slack Context

**Scenario:** Test case needs context from team discussion

**Prerequisites:**
- Slack MCP configured
- Channel name or thread URL

**Prompt:**
```
Enhance TC66186 with context from Slack discussions about V2L feature

Search:
- Channels: #dev-mobile, #qa-testing, #product
- Keywords: "V2L", "vehicle to load", "power output"
- Time range: Last 3 months

Process:
1. Search Slack using Slack MCP
2. Extract key points:
   - Technical requirements
   - Edge cases mentioned
   - Known issues
   - User feedback
3. Add to test case "notes" section with Slack links
4. Format as:
   ---
   ## Discussion Context
   - **Power output display** ([Slack](link)): Must update every 1 second
   - **Low battery behavior** ([Slack](link)): Warning at 20%, disable at 15%
   - **Known issue** ([Slack](link)): iOS simulator doesn't show real values

Preserve existing content, append new context.
```

**Result:** Test case enriched with tribal knowledge.

---

### Workflow 5: Bulk Tag Update

**Scenario:** Add "release-5.2" tag to all V2L tests

**Prompt:**
```
Add "release-5.2" tag to all test cases in V2L folder

Folder: testmo/oneapp/test-cases/home/charge/v2l-vehicle-to-load/

Process:
1. Find all .yml files in folder recursively
2. For each file:
   - Read YAML
   - Add "release-5.2" to metadata.tags array (if not already present)
   - Maintain other tags
   - Write file
3. Report count of files updated

Then validate:
btl_testmo validate testmo/oneapp/test-cases/home/charge/v2l-vehicle-to-load/
```

**Result:** 15 files tagged in ~30 seconds (vs 15 minutes manually).

---

### Workflow 6: Quality Audit

**Scenario:** Audit test cases for quality issues

**Prompt:**
```
Audit test cases in installation folder for quality issues

Folder: testmo/oneapp/test-cases/installation/

Check for:
1. Missing preconditions (empty or < 2 items)
2. Vague steps (e.g., "test the feature", "verify it works")
3. Missing expected results
4. Missing platform configurations
5. Outdated references (old API versions)

Output format:
## Quality Audit Report

### Critical Issues (Block release)
- TC[ID]: [issue description]

### Medium Issues (Should fix)
- TC[ID]: [issue description]

### Low Issues (Nice to have)
- TC[ID]: [issue description]

### Summary
- Total files audited: X
- Files with issues: Y
- Critical: N, Medium: M, Low: L
```

---

## 🔗 ClickUp Integration

### Setup

**Configure ClickUp MCP in Claude Desktop:**
1. Open Claude Desktop settings
2. Add MCP server configuration:
```json
{
  "clickup": {
    "command": "npx",
    "args": ["-y", "@anthropic/mcp-server-clickup"],
    "env": {
      "CLICKUP_API_KEY": "your-key",
      "CLICKUP_TEAM_ID": "your-team-id"
    }
  }
}
```
3. Restart Claude Desktop
4. Verify: Ask Claude "Search ClickUp for tasks"

### Common Use Cases

**1. Link Test Cases to Requirements**
```
For each test case in [folder], find related ClickUp tasks and add links

Folder: testmo/oneapp/test-cases/home/

Process:
1. List all test cases
2. For each case:
   - Extract feature name from file path
   - Search ClickUp for tasks with that feature
   - Add task links to test case notes
   - Add test case links to ClickUp task descriptions
```

**2. Track Test Coverage**
```
Generate test coverage report for ClickUp sprint

Sprint: https://app.clickup.com/sprint/[id]

Output:
## Sprint Test Coverage

### Tasks with Test Coverage ✅
- [Task] - Tests: TC123, TC456

### Tasks without Test Coverage ❌
- [Task] - No tests found

### Recommendations
- Priority tasks needing tests: [list]
```

**3. Create Bug Tasks from Test Failures**
```
Create ClickUp tasks for all test failures in last run

Input: Test results from [file or manual list]

For each failure:
1. Create task in "Bugs" list
2. Title: "[TEST FAILURE] [Test case name]"
3. Description:
   - Test case ID and link
   - Failure details
   - Steps to reproduce
   - Platform
4. Priority: Based on test priority
5. Labels: "test-failure", "qa"
```

---

## 💬 Slack Context Integration

### Setup

**Configure Slack MCP in Claude Desktop:**
```json
{
  "slack": {
    "command": "npx",
    "args": ["-y", "@anthropic/mcp-server-slack"],
    "env": {
      "SLACK_BOT_TOKEN": "xoxb-your-token",
      "SLACK_TEAM_ID": "your-team-id"
    }
  }
}
```

### Use Cases

**1. Extract Requirements from Discussions**
```
Search Slack for feature requirements and create test cases

Feature: Vehicle Remote Control
Channels: #product, #dev-mobile
Time range: Last 2 months

Process:
1. Search Slack for discussions
2. Extract requirements (bullet points)
3. For each requirement, create test case:
   - Name from requirement
   - Description from discussion context
   - Steps inferred from requirements
   - Source link to Slack message
```

**2. Find Similar Issues**
```
When writing test case for [bug], search Slack for similar issues

Bug: V2L power display incorrect

Search for:
- Similar symptoms in #bugs, #qa-testing
- Previous discussions about V2L
- Workarounds or known issues

Add findings to test case:
- Related issues section
- Known workarounds
- Links to Slack threads
```

**3. Capture Tribal Knowledge**
```
Create test case knowledge base from Slack

Channels to mine: #qa-testing, #dev-mobile, #support
Topics: Edge cases, gotchas, platform differences

For each topic:
- Collect relevant Slack messages
- Summarize key points
- Create test cases or enhance existing ones
- Link to original discussions
```

---

## 🎨 Test Case Improvement Patterns

### Pattern 1: Vague → Specific

**Before:**
```yaml
test_case:
  description: "Test V2L feature"
  steps:
    - step: "Test the screen"
      expected: "It works"
```

**After:**
```yaml
test_case:
  description: |
    Verify V2L (Vehicle to Load) screen displays real-time power output
    and correctly handles state transitions between ON/OFF modes.

  preconditions: |
    - Vehicle: Nissan ARIYA 2024
    - Battery level: > 50%
    - Vehicle state: Parked (P)
    - V2L device: Connected to outlet

  steps:
    - step: "Navigate to Home → Charge → V2L screen"
      expected: |
        V2L screen displays with:
        - Power output meter (default: 0 kW)
        - ON/OFF toggle (default: OFF)
        - Device status indicator

    - step: "Toggle V2L switch to ON position"
      expected: |
        - Toggle animates to ON state
        - Power meter activates (shows values)
        - Status changes to "Active - Supplying Power"

    - step: "Verify power output updates in real-time"
      expected: |
        - Power value updates every 1 second
        - Shows format: "X.X kW" (e.g., "1.5 kW")
        - Range: 0.0 - 6.0 kW for ARIYA

    - step: "Toggle V2L switch to OFF"
      expected: |
        - Power supply stops
        - Meter shows "0.0 kW"
        - Status: "Inactive"
```

**Prompt to achieve this:**
```
Improve test case TC66186 from vague to specific:

1. Expand description with feature context
2. Add 4+ preconditions about vehicle state
3. Expand 2 vague steps → 4 detailed steps
4. Add specific expected results with actual UI text
5. Include units and ranges for measurements
```

---

### Pattern 2: Add Edge Cases

**Prompt:**
```
Add 3 edge cases to test case TC66186

Edge cases to add:
1. Low battery scenario (< 20%)
   - Expected: Warning message, V2L disabled

2. Vehicle in motion
   - Expected: V2L deactivates, safety warning

3. Multiple devices drawing power
   - Expected: Total power displayed, individual device breakdown

Create new test steps for each edge case in same file.
```

---

### Pattern 3: Add Platform Differences

**Prompt:**
```
Document iOS vs Android differences for TC66186

Research existing test cases for patterns, then add section:

## Platform Differences

### iOS
- Power meter: Uses native UISlider
- Update frequency: Exactly 1 second
- Low battery warning: iOS native alert

### Android
- Power meter: Custom Material Design component
- Update frequency: ~1 second (can vary)
- Low battery warning: Snackbar notification

Add this to notes section of test case.
```

---

## 🚀 Advanced Workflows

### Create Test Suite from Feature Doc

**Scenario:** New V2G (Vehicle to Grid) feature specification ready

**Prompt:**
```
Create complete test suite from V2G feature specification

Context:
- Feature: Vehicle to Grid (V2G) - sell power back to grid
- Similar to V2L but with grid connection and billing
- Reference: V2L tests in testmo/oneapp/.../v2l-vehicle-to-load/

Sources to use:
1. Existing V2L tests (as template)
2. ClickUp: Search for "V2G" tasks
3. Slack: Search #product for V2G discussions
4. Feature spec: [if available as file or URL]

Output:
- Folder: testmo/oneapp/test-cases/home/charge/v2g-vehicle-to-grid/
- Test cases (15-20):
  * Happy path (5 tests)
  * Error handling (5 tests)
  * Edge cases (3 tests)
  * Platform differences (2 tests)
  * Billing/metering (3 tests)

Each test should have:
- Comprehensive description
- All preconditions
- 5-7 detailed steps
- Expected results with UI specifics
- Platform configurations
- Links to requirements (ClickUp)
- Discussion context (Slack)

After creation:
1. Validate: btl_testmo validate testmo/oneapp/.../v2g-vehicle-to-grid/
2. Create folder in Testmo
3. Upload tests: btl_testmo create --folder testmo/oneapp/.../v2g-vehicle-to-grid/
```

**Result:** Complete test suite (15-20 tests) in 30-45 minutes (vs 8-10 hours manually).

---

### Generate Regression Tests from Bugs

**Prompt:**
```
Generate regression test cases from closed ClickUp bugs

Criteria:
- List: "Bugs"
- Status: "Closed"
- Date: Last 3 months
- Priority: High or Critical

Process:
1. Search ClickUp for bugs matching criteria
2. For each bug:
   a. Extract bug description
   b. Identify affected feature/screen
   c. Create regression test case:
      - Name: "Regression: [Bug title]"
      - Description: "Verify bug #[ID] is fixed and doesn't regress"
      - Steps: Reproduce original bug scenario
      - Expected: Bug doesn't occur
      - Tags: ["regression", "bug-[ID]"]
      - Notes: Link to original bug ticket
   d. Place in appropriate feature folder

3. Generate summary report:
   - Bugs processed: X
   - Tests created: Y
   - Coverage by priority

Output files to: testmo/oneapp/test-cases/[feature-folders]/
Prefix: TC-NEW-regression-bug-[bugID].yml
```

---

### Migrate Tests from Other Tools

**Prompt:**
```
Migrate test cases from Excel file to BTL YAML format

Input: tests.xlsx (uploaded or path)

Process:
1. Read Excel file
2. Map columns:
   - "Test Name" → metadata.name
   - "Priority" → metadata.priority
   - "Description" → test_case.description
   - "Steps" → test_case.steps (parse)
   - "Tags" → metadata.tags

3. Infer folder structure from:
   - "Feature" column → folder name
   - Group by feature

4. Create YAML files:
   - Filename: TC-NEW-[slugified-name].yml
   - Preserve original ID in notes
   - Add migration metadata

5. Validate all files

6. Generate migration report:
   - Total migrated: X
   - Validation errors: Y
   - Files created by folder

After migration, run:
btl_testmo validate testmo/oneapp/test-cases/ --fix
```

---

## 📊 Reporting & Analytics

### Coverage Report

**Prompt:**
```
Generate test coverage report for OneApp project

Analyze: testmo/oneapp/test-cases/

Metrics:
1. Test count by feature folder
2. Priority distribution (critical/high/medium/low)
3. Platform coverage (iOS-only, Android-only, Both)
4. Tag analysis (most common tags)
5. Quality issues:
   - Missing preconditions
   - Vague steps
   - Missing configurations
6. Recent activity (files changed last 30 days)
7. Coverage gaps (folders with < 3 tests)

Output: Markdown report with recommendations

## Test Coverage Report - OneApp

### Summary
- Total test cases: 1,334
- Folders: 162
- Average tests per folder: 8.2

### Coverage by Feature
[Table with test counts]

### Quality Metrics
- Complete tests: 85%
- Need improvement: 15%

### Recommendations
1. [Priority gap to address]
2. [Quality improvement needed]
```

---

### Find Duplicate Tests

**Prompt:**
```
Find potential duplicate test cases in login folder

Folder: testmo/oneapp/test-cases/login-flow/

Analysis:
1. Compare test names (similarity > 80%)
2. Compare steps (identical or very similar)
3. Compare expected results
4. Check if testing same functionality

Output:
## Potential Duplicates

### High Confidence (>90% similar)
- TC123: "Login with email"
- TC456: "Email login test"
  Similarity: 95%
  Recommendation: Merge into TC123, update, delete TC456

### Medium Confidence (70-90% similar)
- [List with explanation]

### Action Items
1. Review high confidence duplicates
2. Merge or differentiate
3. Update descriptions to clarify differences
```

---

## 🎯 Best Practices

### Prompt Engineering for Test Cases

**✅ Good Prompts:**
```
Improve test case TC66186 by:
1. Adding 3 preconditions about vehicle state and battery
2. Expanding from 3 to 6 steps with specific expected results
3. Including edge case for low battery (< 20%)
4. Adding platform differences (iOS vs Android)
5. Preserving testmo metadata
6. Updating file directly

Context: V2L feature for Nissan ARIYA, see similar tests in same folder
```

**❌ Bad Prompts:**
```
Make this test better
```

**Why good prompts work:**
- Specific, numbered requirements
- Context provided
- Clear success criteria
- Preservation instructions
- Reference to similar work

---

### Context Management

**Always provide:**
1. **File paths** - Exact location of test cases
2. **Feature context** - What the feature does
3. **Related work** - Similar test cases or folders
4. **Constraints** - What NOT to change (testmo metadata)
5. **Sources** - Where to find more info (ClickUp, Slack)

**Example:**
```
Context package for improving V2L tests:

Files: testmo/oneapp/test-cases/home/charge/v2l-vehicle-to-load/
Feature: Vehicle to Load - power external devices from EV battery
Similar: V2H tests in same parent folder
Preserve: All testmo: sections (case_id, project_id, etc.)
Sources:
- ClickUp: Search "V2L" for requirements
- Slack #dev-mobile: Technical discussions
- Existing tests: TC66186, TC66187 as examples
```

---

### Validation & Review

**Always validate AI changes:**
```bash
# After AI makes changes, run validation
btl_testmo validate testmo/oneapp/test-cases/[folder]/ --verbose

# Check for:
# - YAML syntax errors
# - Missing required fields
# - testmo metadata preservation
# - Consistent formatting
```

**Review checklist:**
- [ ] Test case makes logical sense
- [ ] Steps are specific and actionable
- [ ] Expected results are verifiable
- [ ] Preconditions are complete
- [ ] testmo metadata untouched
- [ ] Links work (ClickUp, Slack)
- [ ] Platform configurations present

---

### When to Use AI vs Manual

**✅ Use AI for:**
- Bulk formatting/standardization
- Creating similar test variations
- Finding duplicates
- Pulling context from multiple sources
- Quality audits across many files
- Tag/metadata updates
- Generating reports

**🤚 Manual is better for:**
- Final quality judgment
- Complex test logic design
- Subjective priority decisions
- Security-sensitive changes
- Critical path tests

---

## 🔧 Troubleshooting

### "Can't find test case file"

**Problem:** Claude says "I don't see that file"

**Solution:**
```
Provide full absolute path:
/Users/[you]/Projects/BTL-TestCases/testmo/oneapp/test-cases/[folder]/TC[ID]-[name].yml

Or use relative from repo root:
testmo/oneapp/test-cases/[folder]/TC[ID]-[name].yml
```

---

### "Changes broke testmo metadata"

**Problem:** Testmo sync fails after AI changes

**Solution:**
```
Tell Claude explicitly:

"Do NOT modify anything in the testmo: section:
testmo:
  case_id: [ID]
  project_id: [ID]
  folder_id: [ID]
  created_at: [date]
  updated_at: [date]

Only modify metadata: and test_case: sections."
```

**Restore from git if needed:**
```bash
git checkout testmo/oneapp/test-cases/[folder]/TC[ID]-[name].yml
```

---

### "Batch update failed"

**Problem:** btl_testmo update fails on multiple files

**Solution:**
```bash
# 1. Validate files first
btl_testmo validate testmo/oneapp/test-cases/[folder]/ --verbose

# 2. Check YAML syntax
python -c "import yaml; yaml.safe_load(open('TC123.yml'))"

# 3. Try smaller batches
# Instead of updating all 50 files, do 5-10 at a time

# 4. Check API rate limits (wait 1 minute between batches)
```

---

### "ClickUp/Slack MCP not working"

**Problem:** Agent can't access ClickUp or Slack

**Solution:**
```
1. Verify MCP configuration in Claude Desktop settings
2. Check API keys are valid
3. Restart Claude Desktop
4. Test manually:
   "Search ClickUp for task 'V2L'"
   "Search Slack #dev-mobile for 'V2L'"
5. Check MCP server logs:
   ~/.config/claude-desktop/mcp-logs/
```

---

## 📖 Example: Complete AI Workflow

**Scenario:** New V2X (Vehicle to Everything) feature needs test coverage from scratch

**Phase 1: Gather Context (5 minutes)**
```
Search ClickUp for V2X requirements
Search Slack #product and #dev-mobile for V2X discussions
List similar features (V2L, V2G, V2H) for reference
```

**Phase 2: Plan Test Suite (5 minutes)**
```
Based on context, create test plan:

Folder: testmo/oneapp/test-cases/home/charge/v2x-vehicle-to-everything/

Test categories:
1. Core functionality (5 tests)
2. Error handling (5 tests)
3. Edge cases (3 tests)
4. Platform differences (2 tests)
5. Integration with grid (3 tests)
6. Billing/metering (2 tests)

Total: 20 test cases
```

**Phase 3: Create Test Cases (15 minutes)**
```
Create all 20 test cases based on plan

Template: Use V2L tests as starting point
Enhance: Add V2X-specific features
Link: Add ClickUp requirements and Slack context
Validate: Run btl_testmo validate after creation
```

**Phase 4: Review & Refine (10 minutes)**
```
Review checklist:
- Completeness (all scenarios covered)
- Consistency (naming, structure)
- Quality (specific steps, expected results)
- Links (ClickUp, Slack references)
- Platform coverage (iOS & Android)
```

**Phase 5: Create in Testmo (5 minutes)**
```bash
# Create folder structure in Testmo
btl_testmo folders --project 2 --create "home/charge/v2x-vehicle-to-everything"

# Upload all tests
btl_testmo create --folder testmo/oneapp/test-cases/home/charge/v2x-vehicle-to-everything/ --new-only

# Verify in Testmo UI
# https://bethinklabs.testmo.net/repositories/2
```

**Phase 6: Link & Document (5 minutes)**
```
Add test case links to ClickUp V2X feature tickets
Update team wiki with test coverage summary
Notify team in Slack #qa-testing
```

**Total Time:** 45 minutes for 20 comprehensive test cases
**Manual Time:** 10+ hours
**Savings:** 13x faster with AI assistance

---

## 🚀 Next Steps

**Master these workflows in order:**

1. **Week 1:** Basic improvements (Workflows 1-3)
   - Improve existing tests
   - Create similar tests
   - Connect ClickUp tickets

2. **Week 2:** Bulk operations (Workflows 4-6)
   - Pull Slack context
   - Bulk tag updates
   - Quality audits

3. **Week 3:** Advanced (Workflows 7-9)
   - Create test suites from specs
   - Generate regression tests
   - Migration workflows

4. **Week 4:** Optimization
   - Custom agent instructions
   - Team-specific patterns
   - Automation integration

---

## 📚 Additional Resources

- **[Architecture](ARCHITECTURE.md)** - Technical design and API details
- **[Agents Documentation](agents/)** - Deep dives per agent type
- **[Getting Started](GETTING_STARTED.md)** - Installation and setup
- **[TESTING_LOG.md](TESTING_LOG.md)** - Validation results and benchmarks
- **Testmo Platform:** https://bethinklabs.testmo.net
- **ClickUp Workspace:** [Your workspace URL]
- **Slack Workspace:** [Your workspace URL]

---

**This guide is your key to 10x QA productivity with AI agents.** 🚀

Start with Workflow 1, practice the prompts, and gradually incorporate more advanced techniques. Within a month, you'll be managing test cases faster and better than ever before.

Questions? Check [agents/BEST_PRACTICES.md](agents/BEST_PRACTICES.md) or ask in #qa-testing Slack channel.
