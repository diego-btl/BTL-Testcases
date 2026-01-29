# Slack MCP Integration Testing

**Status**: 🟡 Not Configured
**Date**: 2026-01-29
**Author**: QA Automation Team

---

## Executive Summary

The Slack Model Context Protocol (MCP) integration would enable AI agents to search Slack conversations, extract requirements, and enhance test case context with real-time discussions. This document outlines the current status, setup requirements, and expected benefits for QA workflows.

**Key Finding**: Slack MCP is available but not yet configured. Once enabled, it would provide direct access to engineering discussions, requirements clarifications, and bug reports within test case creation workflows.

---

## Current Status

### Available MCP Servers
```
✅ Testmo  - Test case management (active)
✅ ClickUp - Task/ticket tracking (active)
✅ IDE     - VS Code integration (active)
🟡 Slack   - Team communications (not configured)
```

### Slack MCP Configuration Found
**Location**: `~/.claude/plugins/marketplaces/claude-plugins-official/external_plugins/slack/.mcp.json`

**Configuration**:
```json
{
  "slack": {
    "type": "sse",
    "url": "https://mcp.slack.com/sse"
  }
}
```

**Connection Type**: Server-Sent Events (SSE)
**Endpoint**: `https://mcp.slack.com/sse`
**Authentication**: Requires Slack OAuth token

---

## Setup Instructions

### Prerequisites
1. Slack workspace access (BethinkLabs workspace)
2. Slack OAuth token with appropriate scopes
3. Claude Code CLI with MCP support

### Required Slack OAuth Scopes
```
channels:history     - Read messages in public channels
channels:read        - View basic channel information
groups:history       - Read messages in private channels
groups:read          - View basic private channel info
search:read          - Search messages and files
users:read           - View people in workspace
```

### Configuration Steps

1. **Generate Slack OAuth Token**
   - Go to: https://api.slack.com/apps
   - Create new app or select existing
   - Navigate to "OAuth & Permissions"
   - Add required scopes (listed above)
   - Install app to workspace
   - Copy "Bot User OAuth Token" (starts with `xoxb-`)

2. **Configure Claude Code MCP**
   ```bash
   # Add to ~/.claude/mcp.json or create if not exists
   {
     "mcpServers": {
       "slack": {
         "type": "sse",
         "url": "https://mcp.slack.com/sse",
         "env": {
           "SLACK_BOT_TOKEN": "xoxb-your-token-here"
         }
       }
     }
   }
   ```

3. **Restart Claude Code**
   ```bash
   # Exit current session
   exit

   # Start new session to load MCP
   claude-code
   ```

4. **Verify Connection**
   ```bash
   # In Claude Code session
   /mcp list
   # Should show "slack" in available servers
   ```

---

## Expected Capabilities

Once configured, the Slack MCP would provide the following tools:

### 1. Message Search
```
Tool: slack_search_messages
Purpose: Search messages across channels
Parameters:
  - query: Search terms
  - channel_id: Optional channel filter
  - date_from: Start date (ISO 8601)
  - date_to: End date (ISO 8601)
  - limit: Max results (default: 20)
```

### 2. Channel Listing
```
Tool: slack_list_channels
Purpose: List accessible channels
Parameters:
  - types: public, private, mpim, im
  - exclude_archived: true/false
```

### 3. Message Reading
```
Tool: slack_get_channel_history
Purpose: Read messages from specific channel
Parameters:
  - channel_id: Channel identifier
  - count: Number of messages
  - oldest: Timestamp (start)
  - latest: Timestamp (end)
```

### 4. Thread Reading
```
Tool: slack_get_thread_replies
Purpose: Read entire conversation thread
Parameters:
  - channel_id: Channel containing thread
  - thread_ts: Thread timestamp
```

### 5. User Information
```
Tool: slack_get_user_info
Purpose: Get user profile details
Parameters:
  - user_id: Slack user ID
```

---

## Mock Workflow Example

### Scenario: Creating Test Cases for "Tesla Pricing" Feature

**Step 1: Search Slack for Requirements**
```markdown
AI Agent Action:
> Searching Slack for "Tesla Pricing" discussions in last 30 days...

Tool Call:
slack_search_messages(
  query="Tesla Pricing",
  date_from="2025-12-30T00:00:00Z",
  date_to="2026-01-29T23:59:59Z",
  limit=50
)
```

**Step 2: Expected Results**
```markdown
Found 23 messages across 4 channels:

#engineering-mobile (12 messages)
#product-discussions (7 messages)
#qa-testing (3 messages)
#design-reviews (1 message)
```

**Step 3: Extract Relevant Discussions**

#### Example Message 1: Requirements Clarification
```
Channel: #engineering-mobile
Date: 2026-01-15 14:23
User: @sarah.martinez (Product Manager)
Thread: 8 replies

"Clarification on Tesla Pricing display:
- Max charge limit banner should ONLY show at location level
- NOT at individual connector level
- Reasoning: Station operators set limits for entire location

This affects the UI hierarchy we discussed."

Replies include:
- @mike.chen (iOS Lead): "Confirmed, updating spec"
- @priya.patel (Android Lead): "Makes sense, will match iOS"
- @diego.delaguila (QA): "Will update test cases accordingly"
```

#### Example Message 2: Edge Case Discussion
```
Channel: #engineering-mobile
Date: 2026-01-18 10:45
User: @mike.chen (iOS Lead)
Thread: 5 replies

"Edge case found: What happens when tariffPricing.energyFee is null?
Currently crashes on iOS.

Options:
1. Show 'Pricing unavailable'
2. Hide pricing section entirely
3. Show $0.00 with disclaimer

Thoughts?"

Resolution (thread):
@sarah.martinez: "Option 1 - show 'Pricing unavailable' message"
@priya.patel: "Android will match this behavior"
```

#### Example Message 3: Platform Difference
```
Channel: #design-reviews
Date: 2026-01-12 16:30
User: @jessica.wong (Design Lead)

"Design spec updated: Pricing modal animations
- iOS: Native sheet presentation (swipe to dismiss)
- Android: Material bottom sheet (drag handle)
- Both: Same content, different native patterns

Link: [Figma Spec]"
```

**Step 4: Extract Structured Requirements**

```yaml
requirements_extracted:
  - id: REQ-001
    source: slack://engineering-mobile/2026-01-15-14:23
    type: clarification
    summary: Max charge limit banner at location level only
    priority: high
    affects: [TC64865]

  - id: REQ-002
    source: slack://engineering-mobile/2026-01-18-10:45
    type: edge_case
    summary: Handle null energyFee with 'Pricing unavailable' message
    priority: critical
    affects: [TC64861, TC64862]

  - id: REQ-003
    source: slack://design-reviews/2026-01-12-16:30
    type: platform_difference
    summary: Different modal animations per platform
    priority: medium
    affects: [TC64863]
    note: Same functionality, different native UI patterns
```

**Step 5: Enhance Test Case Context**

```yaml
# TC64861-tesla-pricing---connector-pricing-base-fees.yml
metadata:
  id: TC64861
  name: Tesla Pricing - Connector Pricing Base Fees
  slack_context:
    - channel: engineering-mobile
      date: 2026-01-18
      summary: "Handle null energyFee gracefully"
      link: slack://C12345/p1705586700
      participants: [@mike.chen, @sarah.martinez, @priya.patel]

steps:
  - id: 7
    action: Test connector where energyFee is null or missing
    expected: |
      Pricing section handles missing data gracefully
      Error message or "Pricing unavailable" displays
      No app crash or blank screen
      Other connector info remains visible

    # Context from Slack discussion:
    # Edge case discovered during development (2026-01-18)
    # Team decision: Show "Pricing unavailable" (not $0.00)
    # Critical for preventing crashes on malformed data
```

---

## Benefits for QA Workflows

### 1. **Requirement Traceability**
- Link test cases directly to Slack discussions
- Track why specific test steps exist
- Reference product/engineering decisions

**Example**:
```yaml
notes: |
  Test coverage based on Slack discussion (2026-01-15):
  - Product clarified banner shows at location level only
  - Engineering confirmed iOS/Android parity
  - Design approved visual treatment

  Slack references:
  - #engineering-mobile: slack://C12345/p1705331000
  - #product-discussions: slack://C67890/p1705334500
```

### 2. **Edge Case Discovery**
- AI agents search Slack for "bug", "crash", "edge case"
- Extract real-world issues before they reach production
- Add preventive test coverage

**Search Query**:
```
"Tesla Pricing" AND (bug OR crash OR "edge case" OR "what if")
```

**Result**:
```markdown
Found 5 edge cases discussed:
1. Null energyFee → Add TC64861 step 7
2. Zero grace period on idling → Add TC64862 step 2
3. Multiple time-of-day rates → Covered in TC64861 step 2
4. Missing additionalInfo → Add TC64863 step 6
5. CCS vs NACS pricing differences → Add TC64861 step 6
```

### 3. **Platform Parity Verification**
- Search for "iOS", "Android", "platform difference"
- Ensure test cases cover both platforms appropriately
- Document expected differences vs bugs

**Enhancement**:
```yaml
# Test case automatically notes platform differences
platforms: [iOS, Android]
platform_notes:
  ios: "Native sheet presentation with swipe gesture"
  android: "Material bottom sheet with drag handle"
  parity: "Content identical, animations differ (by design)"
  slack_source: slack://design-reviews/p1705072200
```

### 4. **Stakeholder Context**
- Know who made decisions (PM, Designer, Engineer)
- Understand business reasoning behind features
- Connect test priorities to user impact

**Example**:
```markdown
## Test Case Rationale

**TC64861 Priority: Critical**

Business Context (from Slack):
- Pricing accuracy directly affects user trust
- Incorrect fees could lead to billing disputes
- Tesla partnership requires 100% pricing accuracy

Source: #product-discussions (2026-01-08)
Decision Maker: @sarah.martinez (Product Manager)
Revenue Impact: High
```

### 5. **Living Documentation**
- Test cases reference real conversations
- Context stays fresh (not stale specs)
- New team members understand "why"

**Before Slack Integration**:
```yaml
description: Verify pricing displays correctly
# Why? What format? Which edge cases?
```

**After Slack Integration**:
```yaml
description: |
  Verify connector pricing displays energy fees (flat, time-of-day, tiered)
  and session fees correctly, per engineering discussion (2026-01-15).

  Key Requirements:
  - Must handle null energyFee (show "Pricing unavailable")
  - Time-of-day rates must show non-overlapping windows
  - CCS and NACS connectors may have different pricing

  Context: slack://engineering-mobile/p1705331000
```

### 6. **Automated Context Gathering**
AI agents can automatically:
1. Search Slack when creating test cases
2. Extract relevant discussions
3. Add context to test case notes
4. Flag missing coverage based on discussions

**Workflow**:
```
User: "Create test cases for Tesla Pricing"

AI Agent:
1. ✅ Search ClickUp for tasks (17 found)
2. ✅ Analyze coverage needs (5 test cases)
3. 🆕 Search Slack for discussions (23 messages)
4. 🆕 Extract edge cases (5 scenarios)
5. 🆕 Add Slack context to test cases
6. ✅ Create test cases with rich context
```

---

## Integration with Existing Workflow

### Current Workflow (No Slack)
```mermaid
graph LR
    A[ClickUp Tasks] --> B[Coverage Analysis]
    B --> C[Test Case Design]
    C --> D[Create YAML]
    D --> E[Export to Testmo]
```

### Enhanced Workflow (With Slack)
```mermaid
graph LR
    A[ClickUp Tasks] --> B[Coverage Analysis]
    F[Slack Search] --> B
    B --> C[Test Case Design]
    F --> C
    C --> D[Create YAML with Context]
    D --> E[Export to Testmo]
    F --> D
```

### Practical Example

**Command**: "Create test cases for Tesla Pricing with Slack context"

**AI Agent Actions**:
```bash
# Step 1: Gather ClickUp tasks
clickup.searchTasks(terms=["Tesla Pricing"])
# Result: 17 tasks found

# Step 2: Search Slack discussions
slack.search_messages(
  query="Tesla Pricing",
  date_from="2025-12-01",
  channels=["engineering-mobile", "product-discussions", "qa-testing"]
)
# Result: 23 messages, 8 threads

# Step 3: Extract requirements
- 12 clarifications
- 5 edge cases
- 3 platform differences
- 2 design decisions

# Step 4: Design test coverage
- 17 ClickUp tasks analyzed
- 5 additional edge cases from Slack
- Result: 5 test cases with enriched context

# Step 5: Create test cases
for each test_case:
  - Add ClickUp task references
  - Add Slack discussion links
  - Include edge cases from Slack
  - Document platform differences
  - Link to stakeholder decisions
```

**Result**:
```yaml
# TC64861-tesla-pricing---connector-pricing-base-fees.yml
metadata:
  clickup_tasks: [86b848n6q, 86b7uewfy]
  slack_context:
    - channel: engineering-mobile
      thread: p1705586700
      summary: Handle null energyFee edge case
      participants: [mike.chen, sarah.martinez]
    - channel: product-discussions
      thread: p1705334500
      summary: CCS vs NACS pricing differences are expected
      decision_maker: sarah.martinez

notes: |
  Edge Case Coverage (from Slack):
  1. Null energyFee → Step 7 (discovered 2026-01-18)
  2. Time-of-day overlaps → Step 2 validation
  3. Platform differences → Step 6 comparison

  All edge cases have been incorporated into test steps.
```

---

## Recommended Slack Channels to Monitor

Based on BTL QA workflows, these channels would provide the most value:

### High Priority
- `#engineering-mobile` - iOS/Android development discussions
- `#product-discussions` - Requirements and feature decisions
- `#qa-testing` - Bug reports and test coordination
- `#design-reviews` - UI/UX specifications

### Medium Priority
- `#nna-tsp` - Tesla Service Platform specific
- `#btl-engineering` - General engineering updates
- `#release-management` - Release notes and blockers

### Low Priority (Contextual)
- `#general` - Company-wide announcements
- `#random` - Team discussions (may contain insights)

---

## Search Query Examples

### For Test Case Creation
```
Query: "Tesla Pricing" AND (requirement OR spec OR "should work")
Purpose: Find formal requirements
Channels: #product-discussions, #engineering-mobile
```

### For Edge Cases
```
Query: "Tesla Pricing" AND (bug OR crash OR "edge case" OR "what if" OR null)
Purpose: Discover potential issues
Channels: #engineering-mobile, #qa-testing
```

### For Platform Differences
```
Query: "Tesla Pricing" AND (iOS OR Android OR platform OR difference)
Purpose: Identify platform-specific behavior
Channels: #engineering-mobile, #design-reviews
```

### For Stakeholder Decisions
```
Query: "Tesla Pricing" AND (decision OR approved OR "let's go with")
Purpose: Track decision makers and rationale
Channels: #product-discussions
```

---

## Privacy and Security Considerations

### Access Control
- Slack MCP respects channel permissions
- Private channels require explicit invitation
- DMs are not accessible via MCP (by design)

### Data Handling
- Slack content is read-only
- No messages are posted via MCP
- Search queries are logged by Slack
- AI agents don't store Slack data long-term

### Best Practices
1. ✅ Use Slack context for requirements traceability
2. ✅ Reference public channels only in test cases
3. ✅ Sanitize sensitive information (tokens, passwords)
4. ❌ Don't copy private discussions to public docs
5. ❌ Don't store customer data from Slack

---

## Implementation Roadmap

### Phase 1: Setup (Week 1)
- [ ] Generate Slack OAuth token with required scopes
- [ ] Configure `~/.claude/mcp.json` with Slack credentials
- [ ] Verify connection and available tools
- [ ] Test basic search functionality

### Phase 2: Manual Testing (Week 2)
- [ ] Search Slack for "Tesla Pricing" discussions
- [ ] Extract requirements manually
- [ ] Compare Slack findings vs ClickUp tasks
- [ ] Identify gaps in test coverage
- [ ] Document 3-5 examples of value-add

### Phase 3: Workflow Integration (Week 3-4)
- [ ] Update test case schema to include `slack_context` field
- [ ] Modify test case creation prompts to search Slack
- [ ] Create agent rule: "Search Slack when creating test cases"
- [ ] Test automated context gathering
- [ ] Validate against 2-3 real features

### Phase 4: Team Adoption (Month 2)
- [ ] Train QA team on Slack-enhanced test cases
- [ ] Document search query patterns
- [ ] Create examples for each feature type
- [ ] Gather feedback and iterate
- [ ] Measure impact (coverage improvement, bug prevention)

---

## Success Metrics

### Quantitative
- **Edge Case Discovery**: +20% edge cases found pre-development
- **Context Richness**: 100% test cases link to source discussions
- **Coverage Gaps**: -30% "why does this test exist?" questions
- **Time to Context**: -50% time spent hunting for requirements

### Qualitative
- Test cases are easier to understand
- New team members onboard faster
- Fewer "we should have tested that" moments
- Stronger product/QA collaboration

---

## Current Limitations

### Technical
- ❌ Slack MCP not configured yet (requires setup)
- ❌ No direct integration with test case creation workflow
- ❌ Manual schema updates needed for `slack_context` field

### Process
- ⚠️ Team may not discuss requirements in Slack (could use email, meetings)
- ⚠️ Search results quality depends on how teams communicate
- ⚠️ Requires discipline to maintain Slack context in test cases

### Workarounds
- **Short-term**: Manually search Slack and add links to test case notes
- **Medium-term**: Configure Slack MCP and test manually
- **Long-term**: Automate Slack search in test case creation workflow

---

## Conclusion

The Slack MCP integration has **high potential** for enhancing QA workflows at BTL:

### Key Benefits
1. ✅ **Richer Context**: Test cases linked to real discussions
2. ✅ **Edge Case Discovery**: Find issues before they reach production
3. ✅ **Requirement Traceability**: Clear lineage from discussion → test
4. ✅ **Team Alignment**: QA sees product/engineering reasoning
5. ✅ **Living Documentation**: Context stays fresh and relevant

### Next Steps
1. **Immediate**: Generate Slack OAuth token and configure MCP
2. **Short-term**: Manual test with "Tesla Pricing" search
3. **Medium-term**: Integrate into automated test case creation
4. **Long-term**: Expand to all features, measure impact

### Recommendation
**Proceed with Phase 1 setup**. The effort to configure Slack MCP is low (< 1 hour), and the potential value is high. Even a single prevented production bug would justify the investment.

---

## Appendix A: Slack MCP Configuration Template

```json
{
  "mcpServers": {
    "testmo": {
      "type": "sse",
      "url": "https://bethinklabs.testmo.net/api/mcp",
      "env": {
        "TESTMO_API_KEY": "your-testmo-key"
      }
    },
    "clickup": {
      "type": "sse",
      "url": "https://api.clickup.com/mcp",
      "env": {
        "CLICKUP_API_TOKEN": "your-clickup-token"
      }
    },
    "slack": {
      "type": "sse",
      "url": "https://mcp.slack.com/sse",
      "env": {
        "SLACK_BOT_TOKEN": "xoxb-your-slack-bot-token-here"
      }
    }
  }
}
```

**Location**: `~/.claude/mcp.json`

---

## Appendix B: Test Case Schema Extension

```yaml
# Proposed addition to test-case.schema.json
slack_context:
  type: array
  description: Slack discussions that informed this test case
  items:
    type: object
    properties:
      channel:
        type: string
        description: Slack channel name (without #)
      thread_id:
        type: string
        description: Thread timestamp or message ID
      date:
        type: string
        format: date
        description: Message date (YYYY-MM-DD)
      summary:
        type: string
        description: Brief summary of relevant discussion
      participants:
        type: array
        items:
          type: string
        description: Key participants (Slack handles)
      link:
        type: string
        format: uri
        description: Direct link to Slack message
      type:
        type: string
        enum: [requirement, edge_case, platform_difference, design_decision, bug_report]
        description: Type of discussion
```

**Example Usage**:
```yaml
metadata:
  id: TC64861
  name: Tesla Pricing - Connector Pricing Base Fees
  slack_context:
    - channel: engineering-mobile
      thread_id: p1705586700
      date: 2026-01-18
      summary: Handle null energyFee edge case gracefully
      participants: [mike.chen, sarah.martinez, priya.patel]
      link: https://bethinklabs.slack.com/archives/C12345/p1705586700
      type: edge_case
```

---

**Document Version**: 1.0
**Last Updated**: 2026-01-29
**Next Review**: After Phase 1 completion
