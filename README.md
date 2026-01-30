# BTL TestCases Framework

![Production Ready](https://img.shields.io/badge/status-production--ready-brightgreen) ![Test Cases](https://img.shields.io/badge/test--cases-1710-blue) ![Projects](https://img.shields.io/badge/projects-3-blue) ![AI Powered](https://img.shields.io/badge/AI-powered-purple)

**Version:** 2.0.0
**Status:** ✅ Production Ready
**Last Updated:** 2026-01-30

---

## 🎯 What Is This?

**AI-powered test case management framework** for Nissan/Infiniti connected vehicle apps. Sync 1,710+ test cases between local YAML files and Testmo platform with intelligent change detection.

**Built for QA teams** to leverage AI agents (Claude Code, Claude Desktop) for 10x productivity gains in test case creation, improvement, and maintenance.

---

## ✨ Key Features

### Core Capabilities
- **3 Projects Synced** - OneApp (1,334 cases), NMEX (284), NBA (92)
- **Smart Sync** - SHA-256 hash-based change detection
- **Version Controlled** - Git-based test case management
- **Fast** - Export 1,334 cases in ~60 seconds

### AI-Assisted Workflows
- **Claude Code Integration** - Direct file manipulation, batch operations
- **ClickUp Connected** - Link test cases to tickets for traceability
- **Slack Context** - Pull discussion context for better test cases
- **Automated Quality** - AI-powered audits and improvements

**With AI:** Test case creation goes from **30 min → 5 min** per case (6x faster)

---

## 🚀 Quick Start

### 1. Install (5 minutes)

```bash
# Clone repository
git clone <repo-url>
cd BTL-TestCases

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Testmo API key
```

See [GETTING_STARTED.md](GETTING_STARTED.md) for detailed setup.

### 2. Export Test Cases (2 minutes)

```bash
# Export OneApp project
python3 scripts/export_project.py 2 testmo/oneapp

# Or export other projects
python3 scripts/export_project.py 5 testmo/nba    # NBA
python3 scripts/export_project.py 6 testmo/nmex   # NMEX
```

### 3. Improve with AI (2 minutes)

**Prompt for Claude Code:**
```
Improve test case TC66186 with detailed steps:

File: testmo/oneapp/test-cases/home/charge/v2l-vehicle-to-load/TC66186-v2l-screen.yml

Add:
1. 3 preconditions (vehicle state, battery, connection)
2. Expand 3 steps → 6 detailed steps
3. Add low battery edge case

Preserve testmo: section.
```

**Result:** Test case upgraded in ~2 minutes vs 30 minutes manually.

See [HOW_TO_GUIDE.md](HOW_TO_GUIDE.md) for 30+ AI-assisted workflows.

---

## 📚 Documentation

### Essential Guides
- **[Getting Started](GETTING_STARTED.md)** - Installation & setup (15 min)
- **[How-To Guide](HOW_TO_GUIDE.md)** - AI workflows & practical examples (⭐ START HERE)
- **[Architecture](ARCHITECTURE.md)** - Technical design & decisions
- **[Agents](agents/)** - AI agent integration guides

### AI Agent Guides
- **[Claude Code](agents/CLAUDE_CODE.md)** - Terminal-based workflows
- **[ClickUp Integration](agents/CLICKUP_INTEGRATION.md)** - Task linking
- **[Slack Context](agents/SLACK_CONTEXT.md)** - Discussion mining
- **[Best Practices](agents/BEST_PRACTICES.md)** - Optimization & troubleshooting

### Reference
- **[TESTING_LOG.md](TESTING_LOG.md)** - Validation results (5/5 tests passed)

---

## 👥 For QA Team (12 People)

### Daily Workflows

**Improve a test:**
```bash
# Ask Claude Code:
"Improve test case TC[ID] with better steps and preconditions"
```

**Create similar tests:**
```bash
# Ask Claude Code:
"Create 5 similar test cases based on TC[ID] for different scenarios"
```

**Bulk tag update:**
```bash
# Ask Claude Code:
"Add 'release-5.2' tag to all tests in [folder]"
```

**Link to ClickUp ticket:**
```bash
# Ask Claude Desktop with ClickUp MCP:
"Link test case TC[ID] to ClickUp task [task-url]"
```

**Quality audit:**
```bash
# Ask Claude Code:
"Audit test cases in [folder] for quality issues"
```

**Full guide:** [HOW_TO_GUIDE.md](HOW_TO_GUIDE.md)

---

## 📊 Project Stats

### Test Cases by Project

| Project | Test Cases | Folders | Size | Status |
|---------|-----------|---------|------|--------|
| **OneApp** | 1,334 | 162 | 5.9 MB | ✅ Complete |
| **NMEX** | 284 | 45 | 1.4 MB | ✅ Complete |
| **NBA** | 92 | 19 | 420 KB | ✅ Complete |
| **Total** | **1,710** | **226** | **7.7 MB** | ✅ Production |

### Validation Results

| Operation | Status | Performance |
|-----------|--------|-------------|
| Export | ✅ PASS | ~60s for 1,334 cases |
| Update Individual | ✅ PASS | ~223ms per case |
| Batch Create | ✅ PASS | ~393ms for 5 cases (3.3x faster) |
| Validation | ✅ 100% | All 1,710 cases pass |

### Repository Stats
- **Production Ready:** ✅ Yes
- **Repository Size:** 32 MB
- **Code Lines:** ~2,136 (8 core modules)
- **Documentation:** 10 comprehensive files
- **Test Coverage:** Unit tests for core utilities

---

## 🗂️ Repository Structure

```
BTL-TestCases/
├── README.md                    # This file (overview)
├── GETTING_STARTED.md           # Installation & setup
├── ARCHITECTURE.md              # Technical reference
├── HOW_TO_GUIDE.md              # AI workflows (⭐ KEY DOC)
├── TESTING_LOG.md               # Validation proof
│
├── agents/                      # AI agent guides
│   ├── README.md                    - Agent overview
│   ├── CLAUDE_CODE.md               - Terminal agent
│   ├── CLICKUP_INTEGRATION.md       - Task linking
│   ├── SLACK_CONTEXT.md             - Discussion mining
│   └── BEST_PRACTICES.md            - Optimization tips
│
├── scripts/                     # Production code
│   ├── btl_testmo.py                - CLI entry point
│   ├── export_project.py            - Export script
│   ├── testmo_sync/                 - Core package (8 modules)
│   └── legacy/                      - Reference scripts
│
├── testmo/                      # Test case data
│   ├── oneapp/                      - 1,334 cases
│   ├── nba/                         - 92 cases
│   └── nmex/                        - 284 cases
│
└── tests/                       # Unit tests
    ├── test_hasher.py
    ├── test_validator.py
    └── test_converter.py
```

---

## 🤖 AI Integration

### What AI Agents Can Do

**Improve Test Cases**
- Vague → Specific steps
- Add missing preconditions
- Include edge cases
- Fix validation issues

**Create Test Cases**
- Generate variations from templates
- Batch creation (5-10x faster)
- Extract requirements from discussions

**Connect Context**
- Link ClickUp tickets
- Pull Slack discussions
- Add documentation references

**Automate Workflows**
- Bulk tag updates
- Quality audits
- Coverage reports
- Status synchronization

**See:** [HOW_TO_GUIDE.md](HOW_TO_GUIDE.md) for 30+ example workflows

---

## 💡 Example: AI-Assisted Test Creation

**Scenario:** New V2G feature needs 15 test cases

**Traditional Method:** 7.5 hours (30 min per test)

**With AI Agent:**
```
Claude Code prompt:

"Create comprehensive test suite for V2G feature

Reference: V2L tests in testmo/oneapp/.../v2l-vehicle-to-load/
Output: testmo/oneapp/.../v2g-vehicle-to-grid/

Generate 15 tests:
- Happy path (5 tests)
- Error handling (5 tests)
- Edge cases (3 tests)
- Platform differences (2 tests)

Each with detailed steps, preconditions, expected results."
```

**Result:** 15 tests in ~30 minutes
**Time Saved:** 7 hours (15x faster)

---

## 🎓 Learning Path

**Week 1: Basics**
1. Read [GETTING_STARTED.md](GETTING_STARTED.md) - Setup
2. Try improving 1 test case
3. Create 3 similar tests

**Week 2: Integration**
1. Setup ClickUp MCP
2. Link tests to tickets
3. Generate coverage report

**Week 3: Advanced**
1. Setup Slack MCP
2. Extract requirements from discussions
3. Create test suite from context

**Week 4: Mastery**
1. Master [BEST_PRACTICES.md](agents/BEST_PRACTICES.md)
2. Create custom workflows
3. Share with team

---

## 🔗 External Links

- **Testmo Platform:** https://bethinklabs.testmo.net
- **Projects:**
  - OneApp: https://bethinklabs.testmo.net/repositories/2
  - NBA: https://bethinklabs.testmo.net/repositories/5
  - NMEX: https://bethinklabs.testmo.net/repositories/6

---

## 🤝 Contributing

**Internal Bethink Labs project**

For questions or improvements:
- **Contact:** Diego Del Aguila (diego@bethinklabs.com)
- **Slack:** #qa-testing channel
- **Issues:** Create PR or discuss in Slack

---

## 📜 License

Internal use only - Bethink Labs © 2026

---

## 🎯 Key Takeaways

1. **AI-Powered** - 10x productivity with Claude Code & Claude Desktop
2. **Production Ready** - 1,710 cases synced, 100% validated
3. **Well Documented** - 10 comprehensive guides
4. **Easy Start** - 15 minutes to first export
5. **Team Friendly** - Built for 12-person QA team
6. **Git-Based** - Version control for all test cases

---

**🚀 Ready to get started?**

→ New to the framework? Read [GETTING_STARTED.md](GETTING_STARTED.md)
→ Want AI workflows? Jump to [HOW_TO_GUIDE.md](HOW_TO_GUIDE.md) ⭐
→ Technical details? See [ARCHITECTURE.md](ARCHITECTURE.md)
→ Agent integration? Check [agents/](agents/)

**Let's 10x your QA productivity with AI!** 🚀
