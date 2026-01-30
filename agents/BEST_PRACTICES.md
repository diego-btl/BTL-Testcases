# AI Agent Best Practices

**Purpose:** Optimization tips, troubleshooting, and patterns for maximum productivity

---

## 🎯 Core Principles

### 1. Be Specific

**❌ Bad:**
```
Make this test better
```

**✅ Good:**
```
Improve test case TC66186 by:
1. Adding 3 preconditions (vehicle state, battery level, connection status)
2. Expanding from 3 to 6 steps with specific UI expectations
3. Adding low battery edge case (< 20%)
4. Preserving testmo: section unchanged

File: testmo/oneapp/test-cases/home/charge/v2l-vehicle-to-load/TC66186-v2l-screen.yml

Context: V2L feature for Nissan ARIYA, iOS & Android apps
```

**Why:** Specific instructions = predictable, high-quality results

---

### 2. Provide Context

**Essential context elements:**
```
1. File paths (exact location)
2. Feature description (what it does)
3. Related work (similar test cases, folders)
4. Constraints (what NOT to change)
5. Sources (where to find more info)
```

**Example:**
```
Context for improving V2L tests:

Files: testmo/oneapp/test-cases/home/charge/v2l-vehicle-to-load/
Feature: Vehicle to Load - power external devices from EV battery
Similar: V2H tests in /home/charge/v2h-vehicle-to-home/
Preserve: All testmo: sections (case_id, project_id, folder_id, timestamps)
Sources:
- ClickUp task #8a2b4c for requirements
- Slack #dev-mobile for technical discussions
- Existing tests TC66186-66190 as examples
```

---

### 3. Iterate

**Approach:**
```
1. Start simple
   "List all test cases in V2L folder"

2. Refine
   "Show me test cases that are missing preconditions"

3. Act
   "Add preconditions to TC66186 and TC66187"

4. Verify
   "Validate those files"

5. Scale
   "Apply same improvements to all V2L tests"
```

Don't try to do everything in one prompt. Build up complexity.

---

### 4. Always Validate

**After AI changes:**
```bash
# 1. YAML syntax check
btl_testmo validate testmo/oneapp/test-cases/folder/ --verbose

# 2. Git diff check
git diff testmo/oneapp/test-cases/folder/

# 3. Manual review (sample)
# Open 2-3 files and verify changes make sense

# 4. Test in Testmo (optional)
btl_testmo update testmo/oneapp/test-cases/folder/TC123.yml
```

**Never blindly trust AI output.** Always verify critical changes.

---

### 5. Preserve Metadata

**Critical rule:**
```
NEVER modify testmo: sections in YAML files

testmo:
  case_id: 66186          ← Don't touch
  project_id: 2           ← Don't touch
  folder_id: 7338         ← Don't touch
  created_at: "..."       ← Don't touch
  updated_at: "..."       ← Don't touch
```

**Remind AI in every prompt involving file edits:**
```
"Preserve the testmo: section exactly as-is. Only modify metadata: and test_case: sections."
```

---

## ✍️ Prompt Engineering

### Anatomy of a Great Prompt

```
[Goal] - What you want to achieve
Improve test case TC66186

[Specific changes] - Numbered list
1. Add 3 preconditions about vehicle state
2. Expand 3 steps → 6 detailed steps
3. Add edge case for low battery

[Constraints] - What NOT to do
Preserve testmo: section
Keep existing test structure

[Context] - Supporting information
File: testmo/oneapp/.../TC66186-v2l-screen.yml
Feature: V2L for Nissan ARIYA
Reference: Similar tests TC66187, TC66188

[Verification] - How to check results
Validate: btl_testmo validate [file]
```

---

### Prompt Templates

#### Template 1: Improve Test Case

```
Improve test case TC[ID] with [specific improvements]

File: [full path]

Improvements:
1. [Specific change 1]
2. [Specific change 2]
3. [Specific change 3]

Preserve:
- testmo: section unchanged
- Existing test structure

Context:
- Feature: [description]
- Reference: [similar tests]

Validate after: btl_testmo validate [file]
```

#### Template 2: Bulk Operation

```
[Action] for all test cases in [folder]

Folder: [path]

Process:
1. [Step 1]
2. [Step 2]
3. [Step 3]

Requirements:
- [Requirement 1]
- [Requirement 2]

Report:
- Files processed: X
- Files updated: Y
- Validation results

Validate: btl_testmo validate [folder]
```

#### Template 3: Research & Analysis

```
Analyze [topic] across [scope]

Scope: [folder or file set]

Analysis criteria:
1. [Criterion 1]
2. [Criterion 2]

Output format:
## [Report Title]

### [Section 1]
[What to include]

### [Section 2]
[What to include]

### Recommendations
[Actionable next steps]
```

---

## 🔧 Troubleshooting

### Common Issues & Solutions

#### Issue 1: "Can't find file"

**Error:** "I don't see that test case file"

**Solutions:**
```
1. Provide full path from repo root
   testmo/oneapp/test-cases/folder/TC123-name.yml

2. Verify file exists
   ls -la testmo/oneapp/test-cases/folder/TC123-name.yml

3. Check current directory
   pwd  # Should be in BTL-TestCases root

4. Use glob patterns
   testmo/oneapp/test-cases/**/*v2l*.yml
```

---

#### Issue 2: "YAML syntax error after edit"

**Error:** YAML file won't parse

**Solutions:**
```bash
# 1. Check syntax
python -c "import yaml; yaml.safe_load(open('TC123.yml'))"

# 2. Common causes
- Indentation issues (use spaces, not tabs)
- Unescaped special characters (: @ # etc)
- Missing quotes around strings with colons

# 3. Fix manually or revert
git checkout testmo/oneapp/test-cases/folder/TC123.yml

# 4. Ask AI to fix
"Fix YAML syntax errors in TC123.yml, output valid YAML"
```

---

#### Issue 3: "testmo metadata got modified"

**Error:** case_id, project_id changed or deleted

**Prevention:**
```
Always include in prompt:
"Do NOT modify the testmo: section. Only edit metadata: and test_case: sections."
```

**Recovery:**
```bash
# Revert file
git checkout testmo/oneapp/test-cases/folder/TC123.yml

# Or restore testmo section from git
git show HEAD:testmo/.../TC123.yml | grep -A 10 "testmo:"
```

---

#### Issue 4: "Batch update partially failed"

**Error:** Some files updated, some failed

**Solutions:**
```bash
# 1. Identify failed files
btl_testmo validate testmo/oneapp/test-cases/folder/ --verbose

# 2. Check for common issues
# - YAML syntax errors
# - Missing required fields
# - File permissions

# 3. Process in smaller batches
# Instead of 50 files, do 10 at a time

# 4. Use --fix flag
btl_testmo validate testmo/oneapp/test-cases/folder/ --fix
```

---

#### Issue 5: "MCP not working"

**Error:** ClickUp or Slack integration fails

**Solutions:**
```bash
# 1. Check MCP configuration
cat ~/Library/Application\ Support/Claude/config.json

# 2. Verify API keys
# ClickUp:
curl "https://api.clickup.com/api/v2/team" \
  -H "Authorization: YOUR_API_KEY"

# Slack:
curl "https://slack.com/api/auth.test" \
  -H "Authorization: Bearer xoxb-YOUR-TOKEN"

# 3. Restart Claude Desktop
killall Claude && open -a Claude

# 4. Check MCP logs
tail -f ~/Library/Logs/Claude/mcp-*.log

# 5. Reinstall MCP server
npx -y @anthropic/mcp-server-clickup  # Test manually
```

---

## ⚡ Performance Optimization

### Speed Up Large Operations

**For 100+ files:**

```
1. Process in batches of 10-20
   Batch 1: Files 1-20
   Batch 2: Files 21-40
   etc.

2. Validate after each batch
   Catch errors early

3. Use parallel operations when safe
   Multiple independent changes = can run in parallel
   Dependent changes = must run sequentially

4. Monitor progress
   Request progress reports every 10 files
```

---

### Reduce API Calls

**Pattern: Read once, modify many**

```
Instead of:
- Read file 1 → modify → write
- Read file 2 → modify → write
- Read file 3 → modify → write

Do:
- Read all files → batch modify → write all
```

**Pattern: Batch validation**

```
Instead of:
btl_testmo validate file1.yml
btl_testmo validate file2.yml
btl_testmo validate file3.yml

Do:
btl_testmo validate folder/
```

---

### Cache Common Queries

**Create reference docs:**

```
Instead of asking AI to search every time:

1. Generate reference once:
   "List all V2L test cases with descriptions"
   Save to: docs/reference/v2l-test-inventory.md

2. Reference in prompts:
   "See docs/reference/v2l-test-inventory.md for existing tests"

3. Update quarterly
```

---

## 🎨 Advanced Patterns

### Pattern 1: Template-Based Generation

**Concept:** Create one perfect test, replicate with variations

```
1. Create master template
   TC-TEMPLATE-feature.yml
   Make it comprehensive and perfect

2. Generate variations
   "Create 5 test cases based on TC-TEMPLATE-feature.yml
    Variations: [list specific scenarios]"

3. Review and refine master
   Improve template based on generated results

4. Repeat for other test types
```

---

### Pattern 2: Progressive Enhancement

**Concept:** Improve test suite incrementally

```
Week 1: Add missing preconditions
"Find all tests with < 2 preconditions, add appropriate ones"

Week 2: Enhance steps
"Find all tests with vague steps, make them specific"

Week 3: Add edge cases
"Add low battery edge case to all power-related tests"

Week 4: Platform differences
"Document iOS vs Android differences in all tests"
```

---

### Pattern 3: Quality Gates

**Concept:** Automated quality checks before release

```
Create quality gate prompt:

"Run quality audit on [folder]:

Critical checks (must pass):
1. All tests have ≥ 2 preconditions
2. No vague steps ("test", "check" without specifics)
3. All tests have platform configurations
4. testmo metadata intact

Report critical failures and block if any found.
"
```

---

### Pattern 4: Knowledge Extraction

**Concept:** Build institutional knowledge from Slack/ClickUp

```
Monthly task:

"Extract QA knowledge from last month:
1. Search Slack #qa-testing for tips, gotchas
2. Search ClickUp closed bugs for lessons
3. Synthesize into:
   - docs/lessons-learned/[YYYY-MM].md
   - Update relevant test case notes
"

Result: Growing knowledge base
```

---

## 🎓 Agent-Specific Tips

### Claude Code

**Best for:**
- Direct file manipulation
- Batch operations
- Command execution
- No external API dependencies

**Tips:**
```
1. Use glob patterns for file discovery
   testmo/**/*login*.yml

2. Chain commands
   "Validate folder, fix issues, validate again"

3. Request progress updates
   "Report progress every 10 files"
```

---

### ClickUp MCP

**Best for:**
- Linking tests to requirements
- Coverage tracking
- Task automation

**Tips:**
```
1. Use task IDs, not URLs
   ✅ "8a2b4c"
   ❌ "https://app.clickup.com/t/8a2b4c"

2. Batch link operations
   Link multiple tests to one task

3. Cache task data
   Get all sprint tasks once, process locally
```

---

### Slack MCP

**Best for:**
- Requirements extraction
- Historical context
- Bug patterns

**Tips:**
```
1. Use specific keywords
   ✅ "V2L power display API"
   ❌ "V2L issue"

2. Limit timeframe for speed
   Last 3 months vs All time

3. Search multiple channels in one prompt
   "Search #dev-mobile and #qa-testing for [topic]"
```

---

## 📊 Quality Control

### Review Checklist

**After AI generates/modifies test cases:**

- [ ] **Logical sense** - Test makes sense for feature
- [ ] **Specific steps** - No vague "test the feature" steps
- [ ] **Verifiable results** - Expected results can be objectively verified
- [ ] **Complete preconditions** - All required setup documented
- [ ] **Metadata intact** - testmo: section unchanged
- [ ] **Links work** - ClickUp/Slack references valid
- [ ] **Platform coverage** - iOS & Android when applicable
- [ ] **YAML valid** - Passes validation

**Red flags (review more carefully):**
- ⚠️ Steps have no expected results
- ⚠️ Preconditions empty or generic
- ⚠️ Copy-paste errors (wrong feature name)
- ⚠️ testmo: section modified

---

### Spot Check Strategy

**For large batches:**

```
1. Sample randomly
   Check files #5, #17, #33 (not sequential)

2. Check edge cases
   First file, last file, middle file

3. Look for patterns
   If file #5 has issue, check similar files

4. Trust but verify
   AI is usually 95%+ accurate
   5% needs human review
```

---

## 🤝 Team Collaboration

### Sharing Prompts

```
Document successful prompts:

File: .claude/prompts/improve-test-case.md

Content:
# Improve Test Case Prompt

Use this prompt template to improve any test case:

[Template]

Examples of successful use:
- TC66186: [link to commit]
- TC66187: [link to commit]

Tips:
- [Specific tips for this workflow]
```

---

### Agent Best Practices Guide

**Create team guide:**

```
File: docs/team/agent-guidelines.md

## Our Team's AI Guidelines

### Do's
- Always validate after AI changes
- Provide specific prompts
- Document custom workflows
- Share successful patterns

### Don'ts
- Never commit without review
- Don't modify testmo: sections
- Don't use AI for subjective decisions
- Don't skip validation step
```

---

### Code Review for AI Changes

**Review AI-generated PRs:**

```
Checklist:
1. Validate files (btl_testmo validate)
2. Spot check 3-5 random files
3. Check testmo: metadata preserved
4. Verify git diff is reasonable
5. Test one file in Testmo (optional)

If all pass → Approve
If issues → Request changes
```

---

## 📚 Learning Resources

### Practice Exercises

**Week 1: Basics**
1. Improve single test case (Workflow 1)
2. Create 3 similar tests (Workflow 2)
3. Bulk tag update (Workflow 3)

**Week 2: Integration**
1. Setup ClickUp MCP
2. Link 5 tests to tasks
3. Generate coverage report

**Week 3: Advanced**
1. Setup Slack MCP
2. Extract requirements from discussion
3. Create test suite from context

**Week 4: Mastery**
1. Create custom workflow
2. Document pattern
3. Share with team

---

### Recommended Reading

- **[How-To Guide](../HOW_TO_GUIDE.md)** - Comprehensive workflows
- **[Claude Code Guide](CLAUDE_CODE.md)** - Terminal agent
- **[ClickUp Integration](CLICKUP_INTEGRATION.md)** - Task linking
- **[Slack Context](SLACK_CONTEXT.md)** - Discussion mining

---

## 🎯 Key Takeaways

1. **Be Specific** - Detailed prompts get better results
2. **Provide Context** - File paths, feature info, constraints
3. **Iterate** - Start simple, build complexity
4. **Always Validate** - Never trust AI output blindly
5. **Preserve Metadata** - testmo: sections are sacred
6. **Learn Patterns** - Document what works
7. **Share Knowledge** - Help team be productive
8. **Review Carefully** - Quality over speed

---

**Remember:** AI agents are tools to amplify your expertise, not replace it. Your judgment, context, and domain knowledge are irreplaceable. Use AI to handle tedious work so you can focus on high-value QA activities.

---

**Questions?** Create issue or ask in #qa-testing Slack channel.

**Found a great pattern?** Document it and share with the team!

Let's build the best AI-assisted QA workflow together! 🚀
