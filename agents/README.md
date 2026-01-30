# AI Agents Documentation

**Purpose:** Comprehensive guides for using AI agents with the BTL TestCases Framework

---

## 🤖 Available Agents

### 1. Claude Code
**Type:** Terminal-based coding agent
**Best for:** Direct file manipulation, command execution, batch operations
**Documentation:** [CLAUDE_CODE.md](CLAUDE_CODE.md)

**Key Capabilities:**
- Read/write test case YAML files
- Execute Python scripts and CLI commands
- Run validations and sync operations
- Batch file operations

---

### 2. ClickUp Integration
**Type:** MCP-based project management integration
**Best for:** Linking test cases to tickets, tracking coverage, creating tasks
**Documentation:** [CLICKUP_INTEGRATION.md](CLICKUP_INTEGRATION.md)

**Key Capabilities:**
- Search ClickUp tasks
- Link test cases to tickets
- Create bug tasks from test failures
- Track test coverage per sprint

---

### 3. Slack Context
**Type:** MCP-based communication integration
**Best for:** Pulling discussion context, finding requirements, capturing knowledge
**Documentation:** [SLACK_CONTEXT.md](SLACK_CONTEXT.md)

**Key Capabilities:**
- Search Slack discussions
- Extract requirements from threads
- Find similar issues
- Capture tribal knowledge

---

## 🚀 Quick Start

### Choose Your Agent

**For file operations:**
→ Use **Claude Code**
- Improve test cases
- Create new tests
- Bulk updates
- Quality audits

**For project tracking:**
→ Use **ClickUp Integration** (via Claude Desktop + MCP)
- Link tests to tickets
- Track coverage
- Create bug tasks

**For team knowledge:**
→ Use **Slack Context** (via Claude Desktop + MCP)
- Pull requirements
- Extract decisions
- Find discussions

---

## 📚 Documentation Structure

```
agents/
├── README.md                     ← You are here (overview)
├── CLAUDE_CODE.md                ← Terminal-based agent workflows
├── CLICKUP_INTEGRATION.md        ← ClickUp MCP integration
├── SLACK_CONTEXT.md              ← Slack MCP integration
└── BEST_PRACTICES.md             ← Optimization tips & troubleshooting
```

---

## 🎯 Common Workflows by Agent

### Claude Code Workflows

1. **Improve Test Case** - Make test more specific and detailed
2. **Create Similar Tests** - Generate variations from template
3. **Bulk Tag Update** - Add tags to multiple tests
4. **Quality Audit** - Find issues across test suite
5. **Format Standardization** - Ensure consistent structure

**Start here:** [CLAUDE_CODE.md](CLAUDE_CODE.md)

---

### ClickUp Integration Workflows

1. **Link Test to Ticket** - Create bidirectional traceability
2. **Coverage Report** - Show which tasks have tests
3. **Create Bug Task** - Auto-create task from test failure
4. **Sprint Coverage** - Track test coverage for sprint

**Setup required:** [CLICKUP_INTEGRATION.md](CLICKUP_INTEGRATION.md)

---

### Slack Context Workflows

1. **Extract Requirements** - Pull feature specs from discussions
2. **Find Similar Issues** - Search past bug discussions
3. **Enhance with Context** - Add discussion context to tests
4. **Knowledge Mining** - Capture tribal knowledge

**Setup required:** [SLACK_CONTEXT.md](SLACK_CONTEXT.md)

---

## 🔧 Setup Overview

### Claude Code (No Setup Needed)
✅ Works immediately if you have Claude Code CLI installed

### ClickUp MCP (One-time Setup)
1. Get ClickUp API key from [clickup.com/settings](https://app.clickup.com/settings)
2. Configure MCP in Claude Desktop
3. Restart Claude Desktop
4. Test with "Search ClickUp for tasks"

**Detailed setup:** [CLICKUP_INTEGRATION.md#setup](CLICKUP_INTEGRATION.md#setup)

### Slack MCP (One-time Setup)
1. Create Slack app and get bot token
2. Configure MCP in Claude Desktop
3. Invite bot to channels
4. Test with "Search Slack for messages"

**Detailed setup:** [SLACK_CONTEXT.md#setup](SLACK_CONTEXT.md#setup)

---

## 💡 Best Practices

### General Guidelines

1. **Be Specific** - Clear instructions get better results
2. **Provide Context** - Link to related files, tickets, docs
3. **Iterate** - Start simple, refine based on output
4. **Validate** - Always review AI-generated content
5. **Preserve Metadata** - Don't modify `testmo:` sections

### Agent Selection

**Use Claude Code when:**
- Working with files directly
- Need to run commands
- Batch operations
- No external integrations needed

**Use Claude Desktop + MCP when:**
- Need ClickUp integration
- Need Slack integration
- Interactive workflows
- Multiple context sources

**Full guide:** [BEST_PRACTICES.md](BEST_PRACTICES.md)

---

## 📊 Productivity Gains

### With AI Agents

| Task | Manual Time | AI Time | Speedup |
|------|-------------|---------|---------|
| Improve 1 test case | 30 min | 2 min | **15x** |
| Create 5 similar tests | 150 min | 5 min | **30x** |
| Add tags to 20 tests | 20 min | 1 min | **20x** |
| Quality audit (100 tests) | 8 hours | 5 min | **96x** |
| Link 10 tests to ClickUp | 30 min | 3 min | **10x** |

**Average:** ~25x faster with AI assistance

---

## 🎓 Learning Path

### Week 1: Basics
- Read [CLAUDE_CODE.md](CLAUDE_CODE.md)
- Try Workflow 1: Improve a test case
- Try Workflow 2: Create similar tests
- Practice prompt engineering

### Week 2: Integration
- Setup ClickUp MCP
- Link tests to tickets
- Generate coverage reports
- Read [CLICKUP_INTEGRATION.md](CLICKUP_INTEGRATION.md)

### Week 3: Advanced
- Setup Slack MCP
- Extract requirements from discussions
- Create test suites from specs
- Read [SLACK_CONTEXT.md](SLACK_CONTEXT.md)

### Week 4: Optimization
- Master [BEST_PRACTICES.md](BEST_PRACTICES.md)
- Create custom agent instructions
- Develop team-specific workflows
- Share learnings

---

## 🆘 Troubleshooting

### Common Issues

**"Can't find test case file"**
→ Provide full file path from repo root

**"Changes broke testmo metadata"**
→ Remind agent to preserve `testmo:` section

**"MCP not working"**
→ Check configuration in Claude Desktop settings

**"Batch update failed"**
→ Validate files first, try smaller batches

**Full troubleshooting guide:** [BEST_PRACTICES.md#troubleshooting](BEST_PRACTICES.md#troubleshooting)

---

## 📚 Additional Resources

- **[How-To Guide](../HOW_TO_GUIDE.md)** - Practical workflows with prompts
- **[Architecture](../ARCHITECTURE.md)** - Technical design details
- **[Getting Started](../GETTING_STARTED.md)** - Installation and setup
- **[TESTING_LOG.md](../TESTING_LOG.md)** - Validation results

---

## 🤝 Contributing

Found a great workflow? Improved a prompt? Share it!

1. Document your workflow
2. Test with real examples
3. Add to appropriate agent doc
4. Create PR or share in Slack

---

**Ready to get started?**

→ No setup needed? Start with [CLAUDE_CODE.md](CLAUDE_CODE.md)
→ Want ClickUp integration? See [CLICKUP_INTEGRATION.md](CLICKUP_INTEGRATION.md)
→ Need Slack context? Check [SLACK_CONTEXT.md](SLACK_CONTEXT.md)
→ Looking for tips? Read [BEST_PRACTICES.md](BEST_PRACTICES.md)

Let's 10x your QA productivity! 🚀
