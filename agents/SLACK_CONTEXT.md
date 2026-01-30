# Slack Context Integration Guide

**Integration Type:** MCP (Model Context Protocol) Server
**Platform:** Claude Desktop
**Purpose:** Pull team discussions and context into test cases

---

## 🎯 What is Slack Context Integration?

Extract valuable context from team discussions:
- **Requirements Discovery** - Find feature specs in conversations
- **Technical Decisions** - Capture architecture choices
- **Bug History** - Learn from past similar issues
- **Tribal Knowledge** - Document team expertise

**Key Insight:** Your Slack history contains 1000s of hours of QA knowledge. Make it searchable and actionable!

---

## ⚙️ Setup (One-Time, 15 minutes)

### Step 1: Create Slack App

1. Go to https://api.slack.com/apps
2. Click "Create New App" → "From scratch"
3. App Name: "Test Case AI Assistant"
4. Workspace: Select your workspace
5. Click "Create App"

### Step 2: Configure Bot Permissions

In app settings:

1. Go to "OAuth & Permissions"
2. Add Bot Token Scopes:
   ```
   channels:history  - Read public channel messages
   channels:read     - View basic channel info
   groups:history    - Read private channel messages (if needed)
   groups:read       - View private channels (if needed)
   users:read        - View people in workspace
   search:read       - Search workspace messages
   ```

3. Click "Install to Workspace"
4. Authorize the app
5. Copy "Bot User OAuth Token" (starts with `xoxb-`)

### Step 3: Invite Bot to Channels

```
In each Slack channel you want to search:
1. Type: /invite @Test Case AI Assistant
2. Or use channel settings → Integrations → Add apps
```

**Recommended channels:**
- #dev-mobile
- #qa-testing
- #product
- #bugs
- #support

### Step 4: Configure Claude Desktop MCP

**Location:** `~/Library/Application Support/Claude/config.json` (Mac)

**Add Slack server:**
```json
{
  "mcpServers": {
    "slack": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-server-slack"],
      "env": {
        "SLACK_BOT_TOKEN": "xoxb-YOUR-TOKEN-HERE",
        "SLACK_TEAM_ID": "T01ABC123"
      }
    }
  }
}
```

**Find Team ID:**
```
Workspace Settings → About This Workspace
Or from any Slack URL: https://app.slack.com/client/TEAM_ID/...
```

### Step 5: Restart Claude Desktop

```bash
killall Claude
open -a Claude
```

### Step 6: Verify Setup

In Claude Desktop:
```
Search Slack #dev-mobile for "V2L"
```

If you see message results, setup complete! ✅

---

## 📋 Common Workflows

### Workflow 1: Extract Requirements from Discussions

**Goal:** Find feature requirements scattered across Slack discussions

**Prompt for Claude:**
```
Extract V2L feature requirements from Slack discussions

Search criteria:
- Channels: #product, #dev-mobile
- Keywords: "V2L", "vehicle to load", "power output"
- Timeframe: Last 6 months

Process:
1. Search Slack for relevant discussions
2. Extract requirements (bullet points):
   - What the feature should do
   - User flows
   - Edge cases mentioned
   - Technical constraints
   - Known issues

3. Organize by category:
   - Functional requirements
   - Non-functional requirements (performance, etc.)
   - Edge cases
   - Platform differences

4. Format output:
## V2L Feature Requirements (from Slack)

### Functional Requirements
- Power output display must update every 1 second
  Source: [Slack](https://app.slack.com/...message_link)
  From: @john.doe on 2025-12-15

- Low battery warning at 20%, disable at 15%
  Source: [Slack](...)
  Discussion: #product, multiple participants

### Edge Cases Discussed
- Vehicle in motion → auto-disable V2L
  Source: [Slack](...)
  Decision: Safety requirement per @safety.lead

### Save output to file:
File: docs/requirements/v2l-requirements-from-slack.md
```

**Result:** Comprehensive requirements doc in ~10 minutes

---

### Workflow 2: Enhance Test Case with Discussion Context

**Goal:** Add relevant discussion context to existing test case

**Prompt:**
```
Enhance test case TC66186 with context from Slack

Test case: testmo/oneapp/test-cases/home/charge/v2l-vehicle-to-load/TC66186-v2l-screen.yml

Search Slack for:
- Channels: #qa-testing, #dev-mobile, #bugs
- Keywords: "V2L screen", "power display", "V2L toggle"
- Focus on: Technical details, known issues, user feedback

Add to test case notes section:
## Discussion Context

### Technical Details
- **Real-time update requirement** ([Slack](link))
  Must update every 1 second, tolerance ±100ms
  Discussed: 2025-12-15 in #dev-mobile

- **Power range validation** ([Slack](link))
  ARIYA: 0.0-6.0 kW, LEAF: 0.0-3.0 kW
  Source: @dev.lead

### Known Issues
- **iOS simulator limitation** ([Slack](link))
  Simulator shows dummy values, test on real device
  Reported: 2025-11-20 in #qa-testing

### User Feedback
- **Button size complaint** ([Slack](link))
  Users find toggle too small on iPhone SE
  #support ticket mentioned

Preserve existing test case content, append context to notes.
```

**Result:** Test case enriched with team knowledge

---

### Workflow 3: Find Similar Bug Discussions

**Goal:** When writing test for bug, find similar past issues

**Prompt:**
```
Search Slack for similar bugs to help write regression test

Current bug: V2L power display shows incorrect values

Search for:
- Channels: #bugs, #qa-testing, #support
- Keywords: "V2L", "power display", "incorrect", "wrong value"
- Timeframe: All time

Find:
1. Similar symptoms
2. Root causes (if mentioned)
3. Workarounds discovered
4. How it was resolved

Output:
## Similar Issues from Slack

### Bug: V2L display frozen (2025-10-15)
- **Symptoms:** Display stops updating after 5 minutes
- **Root cause:** WebSocket connection timeout
- **Fix:** Added reconnection logic
- **Slack:** [Thread](link)

### Bug: Power value off by 10x (2025-09-20)
- **Symptoms:** Shows 15.0 kW instead of 1.5 kW
- **Root cause:** Decimal point formatting
- **Fix:** Updated conversion formula
- **Slack:** [Thread](link)

### Common Patterns Identified:
- Display issues often related to data polling
- iOS and Android behave differently
- Usually reproduced with specific vehicle models

### Recommendations for Test Case:
1. Test with different polling intervals
2. Include both iOS and Android
3. Test with multiple vehicle models (ARIYA, LEAF)
4. Add edge case: Long-running sessions (5+ minutes)

Use these insights to create comprehensive regression test.
```

---

### Workflow 4: Capture Tribal Knowledge

**Goal:** Document team expertise from Slack into test cases

**Prompt:**
```
Mine Slack for QA tribal knowledge about installation process

Channels: #qa-testing, #dev-mobile
Keywords: "installation", "install", "setup", "first launch"
Timeframe: Last year

Extract:
1. Common gotchas and tips
2. Platform differences (iOS vs Android)
3. Edge cases discovered
4. Testing best practices

Organize and save to:
File: docs/tribal-knowledge/installation-testing-guide.md

Format:
## Installation Testing - Tribal Knowledge

### Common Gotchas 🚨
- **iOS permission timing** ([Slack](link))
  Must request permissions in specific order or flow breaks
  Tip from @qa.expert

- **Android storage** ([Slack](link))
  Fails on devices with < 100MB free space
  Found by @tester.jane

### Platform Differences 📱
- **iOS:** [differences with Slack links]
- **Android:** [differences with Slack links]

### Edge Cases to Always Test 🎯
1. [Edge case with discovery story from Slack]
2. [Edge case with Slack link]

### Pro Tips from Team 💡
- [Tip 1 with attribution and Slack link]
- [Tip 2 with attribution and Slack link]

Last updated: [Date]
Sources: [List of Slack channels scanned]
```

**Result:** Team knowledge preserved and searchable

---

### Workflow 5: Create Test Cases from Feature Discussion

**Goal:** New feature discussed in Slack → Generate test cases

**Prompt:**
```
Create test suite based on Slack feature discussion

Feature: Vehicle Remote Climate Control
Discussion thread: [Slack thread URL or search in #product]

Process:
1. Read entire Slack discussion thread
2. Extract:
   - Feature description
   - User stories mentioned
   - Technical approach discussed
   - Edge cases raised
   - Platform considerations

3. Generate test cases:
   - Happy path (2-3 tests)
   - Error scenarios (2-3 tests)
   - Edge cases mentioned (1-2 tests)
   - Platform-specific (1 test per platform)

4. Each test case should have:
   - Description based on discussion
   - Source links to Slack messages
   - Participants' concerns addressed
   - Technical constraints noted

5. Save to:
   testmo/oneapp/test-cases/vehicle/remote-climate/TC-NEW-[scenario].yml

6. Add note to each test case:
## Source Discussion
This test case created from Slack feature discussion:
- Thread: [Slack link]
- Date: [Discussion date]
- Participants: @user1, @user2, @user3
- Key decisions: [Bullet points]

Report: Test cases created with Slack context.
```

---

## 🔍 Advanced Search Strategies

### Time-based Searches

```
Search strategies by timeframe:

Recent context (last month):
- Current feature development
- Latest bugs
- Recent decisions

Historical context (6+ months ago):
- Original feature requirements
- Past similar features
- Lessons learned

All time:
- Complete bug history
- Architecture decisions
- Recurring issues
```

### Multi-channel Searches

```
Search across multiple channels for complete context:

For feature requirements:
- #product (business requirements)
- #dev-mobile (technical feasibility)
- #design (UX/UI requirements)

For bug investigation:
- #bugs (reported issues)
- #qa-testing (test results)
- #support (user reports)
- #dev-mobile (technical discussion)
```

### Keyword Strategies

**✅ Good Keywords:**
```
Specific and technical:
- "V2L power display API"
- "installation permission flow"
- "charging UI requirements"
```

**❌ Bad Keywords:**
```
Too generic:
- "bug"
- "issue"
- "problem"
```

---

## 📊 Reporting from Slack

### Feature Coverage Analysis

**Prompt:**
```
Analyze Slack discussions to find features needing test coverage

Search:
- Channels: #product, #dev-mobile
- Timeframe: Last 3 months
- Look for: New features announced, requirements discussed

Compare with test cases:
- Which features have tests?
- Which features discussed but no tests created?

Report:
## Features Discussed vs Test Coverage

### Features WITH Test Coverage ✅
- V2L (discussed 2025-12-01) → 8 test cases created
- ...

### Features WITHOUT Test Coverage ❌
- Remote climate control (discussed 2025-11-15) → 0 tests
  - Slack: [Discussion link]
  - Participants: @product, @dev
  - Status: In development
  - **RECOMMENDATION:** Create test suite (estimate 10 tests)

### Recently Mentioned Features (Monitor)
- ...
```

---

### Bug Pattern Analysis

**Prompt:**
```
Analyze bug patterns from Slack history

Search #bugs channel for last 6 months

Categorize by:
1. Frequency (most reported bugs)
2. Severity (impact on users)
3. Feature area
4. Platform (iOS vs Android)

Output:
## Bug Pattern Analysis (from Slack)

### Most Frequent Issues
1. V2L display issues (12 mentions)
   - [Links to discussions]
   - Common causes: Polling, timeout, data format

2. Installation failures (8 mentions)
   - [Links]
   - Common causes: Permissions, storage, network

### Critical Bugs by Feature Area
- **Charging:** X bugs
- **Vehicle Control:** Y bugs
- ...

### Platform-specific Patterns
- **iOS:** Common issues: [list]
- **Android:** Common issues: [list]

### Recommendations for Test Suite
1. Add regression tests for top 5 frequent issues
2. Increase coverage for [feature area]
3. Platform-specific test suites for [areas]
```

---

## 🐛 Troubleshooting

### Issue: "Bot can't see messages"

**Cause:** Bot not in channel or missing permissions

**Solution:**
```bash
# 1. Verify bot is in channel
/invite @Test Case AI Assistant

# 2. Check bot permissions in app settings
# Required scopes: channels:history, search:read

# 3. Re-install app if permissions changed
```

### Issue: "Search returns no results"

**Causes & Solutions:**
```
1. Keywords too specific
   → Try broader terms

2. Wrong timeframe
   → Expand date range

3. Messages in private channel
   → Add groups:history scope
   → Invite bot to private channel

4. Rate limiting
   → Wait 1 minute, try again
```

### Issue: "Can't access thread messages"

**Solution:**
```
Slack API requires thread_ts to access replies.

Ask Claude to:
1. First search for main message
2. Then get thread replies using thread_ts
3. Combine results
```

---

## 💡 Best Practices

### Privacy & Security

```
⚠️ Important:
- Only invite bot to appropriate channels
- Don't search in #private-confidential channels
- Review permissions regularly
- Audit bot access every quarter
```

### Maintaining Context Quality

```
Guidelines for team:
1. Use consistent keywords in Slack
   ✅ "Feature: V2L" not "v2l feature"
   ✅ "Bug: Display" not "display is broken"

2. Link to requirements in discussions
   Include: Jira/ClickUp links, doc links

3. Summarize decisions
   Pin important messages

4. Use threads for discussions
   Keeps context organized
```

### Updating Test Cases

```
Schedule quarterly:
1. Review old test cases
2. Search Slack for new context
3. Update test cases with latest knowledge
4. Archive outdated references
```

---

## 📚 Additional Resources

- **[How-To Guide](../HOW_TO_GUIDE.md)** - More workflow examples
- **[Best Practices](BEST_PRACTICES.md)** - General optimization tips
- **Slack API Docs:** https://api.slack.com/docs
- **MCP Documentation:** https://modelcontextprotocol.io

---

**Setup complete?** Try Workflow 1 to extract your first requirements!

**Need help?** See [BEST_PRACTICES.md](BEST_PRACTICES.md) for troubleshooting.

---

**Pro Tip:** Your Slack history is a goldmine. Spend 1 hour mining it for tribal knowledge, save yourself 10 hours of rediscovering things later! 💎
