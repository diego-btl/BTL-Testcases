# Slack Integration - Usage Guide

## Current Status
- ✅ Slack MCP configured and functional
- ✅ Can list channels
- ⚠️ Cannot read messages (bot not member of channels)

## Recommended Workflow

### Option A: Claude in Slack (Preferred)
Use @Claude directly in Slack for context gathering:
1. In any Slack channel: @Claude search for "Tesla Pricing" discussions
2. Claude returns relevant messages and context
3. Copy findings to test case creation prompt
4. AI incorporates Slack context into test cases

**Advantages:**
- Already works (no additional setup)
- Access to all channels
- Real-time search capability

### Option B: Manual Search
1. Search Slack manually for relevant discussions
2. Copy important messages/decisions
3. Paste into test case creation prompt
4. Include as context for AI agent

### Option C: Bot Channel Membership (Future)
**Only if we automate:**
- Add bot to 3-5 key channels (#qa-testing, #engineering-mobile, #product-discussions)
- Enables automated daily context gathering
- Worth it for CI/CD pipelines, not manual use

## Example Usage

### Getting Context for New Feature
User in Slack: @Claude search for discussions about "Dealer Offers V2" in last 60 days
Claude: [returns 15 messages with requirements and edge cases]
User: [copies to Code tab]
User in Code: Create test cases for Dealer Offers V2. Context: [paste]

### Enhancing Existing Test Case
User: Find Slack discussions about "null pricing data" edge case
[Copy relevant technical discussions]
[Add to TC001 notes section as context]

## When to Use Slack Context
- ✅ New feature test case creation
- ✅ Edge case discovery
- ✅ Platform parity clarification
- ✅ Business rule validation
- ❌ Simple happy path tests (not needed)

## Current Limitations
- Bot cannot read channel history (not a member)
- No workspace-wide search via MCP
- Workaround: Use Claude in Slack or manual search

## Future Automation (Optional)
If we build CI/CD pipelines:
1. Add bot to key channels
2. Scheduled jobs search for new requirements
3. Auto-generate test case drafts
4. Notify QA team

**Decision: Not needed for manual test creation**
