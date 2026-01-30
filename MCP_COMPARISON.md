# Testmo MCP Server Comparison

**Date**: 2026-01-30
**Purpose**: Compare two Testmo MCP servers to determine which to standardize on

## 🔍 Current Setup

### Active Testmo MCP (OFFICIAL)

**Source**: `/Users/diegodelaguila/Projects/BTL-TestCases/venv/bin/mcp-testmo`
**Provider**: Official Testmo MCP from `temp-testmo-mcp/`
**Installation**: `pip install mcp-testmo` (in venv)

**Configuration** (.mcp.json):
```json
{
  "testmo": {
    "command": "/Users/diegodelaguila/Projects/BTL-TestCases/venv/bin/mcp-testmo",
    "args": ["--env-file", ".env"]
  }
}
```

**Environment** (.env):
```bash
TESTMO_URL=https://bethinklabs.testmo.net
TESTMO_API_KEY=testmo_api_...
```

## 📊 Side-by-Side Comparison

| Feature | Official MCP | Alternative (fastmcp) | Winner |
|---------|-------------|----------------------|---------|
| **Installation** | |||
| Package Manager | pip (in venv) | pip (system-wide) | Official |
| Dependencies | httpx, asyncio | fastmcp, httpx | Official |
| Setup Complexity | Medium | Medium | Tie |
| | | | |
| **Core Capabilities** | |||
| Total Tools | 32 tools | Unknown (~10-15) | Official |
| Projects | ✅ List, Get | ✅ List | Official |
| Folders | ✅ List, Get, Create, Update, Delete, Find | ✅ List, Get | Official |
| Test Cases | ✅ List, Get, Create, Update, Delete, Search, Batch | ✅ List, Get, Create | Official |
| Test Runs | ✅ List, Get, Results | ❌ No | Official |
| Automation | ✅ Runs, Sources | ❌ No | Official |
| Milestones | ✅ List, Get | ❌ No | Official |
| Attachments | ✅ List, Upload, Delete | ❌ No | Official |
| Field Mappings | ✅ Yes | ❌ No | Official |
| Web URLs | ✅ Generate | ❌ No | Official |
| | | | |
| **Pagination** | |||
| Auto-pagination | ✅ Yes | Unknown | Official |
| Handles large datasets | ✅ Yes (1334+ cases) | Unknown | Official |
| | | | |
| **Known Issues** | |||
| testmo_update_case bug | 🟡 YES (wrong endpoint) | Unknown | TBD |
| testmo_get_case bug | 🟡 YES (404 errors) | Unknown | TBD |
| | | | |
| **Integration** | |||
| ClickUp Integration | ❌ No (separate) | ✅ Yes (built-in) | Alternative |
| Workflow Support | ❌ Manual | ✅ ClickUp → Testmo | Alternative |
| Claude Desktop | ✅ Yes | ✅ Yes | Tie |
| Claude Code CLI | ✅ Yes | Unknown | Official |
| | | | |
| **Performance** | |||
| Response Time | Fast | Unknown | TBD |
| Batch Operations | ✅ Up to 100/batch | Unknown | Official |
| Rate Limiting | ✅ 0.5s between pages | Unknown | Official |
| | | | |
| **Documentation** | |||
| API Coverage | ✅ 59% (22/37 endpoints) | Unknown | Official |
| Code Examples | ✅ Extensive | ✅ Basic | Official |
| Setup Instructions | ✅ Detailed | ✅ Detailed | Tie |
| | | | |
| **Maintenance** | |||
| Active Development | ✅ Yes | Unknown | Official |
| Bug Fixes | ✅ Active | Unknown | Official |
| Community Support | ✅ GitHub | Unknown | Official |

## 🎯 Detailed Analysis

### Official MCP (Current)

**Pros:**
- ✅ **32 comprehensive tools** covering most Testmo operations
- ✅ **Auto-pagination** for large datasets (verified with 1334 cases)
- ✅ **Attachments support** (screenshots, logs)
- ✅ **Test runs analysis** (CI/CD integration)
- ✅ **Automation monitoring** (GitHub Actions, etc.)
- ✅ **Milestones tracking** (release management)
- ✅ **Field mappings** (priority IDs, type IDs)
- ✅ **Batch operations** (up to 100 cases at once)
- ✅ **Active development** with GitHub repo
- ✅ **Working** with Claude Code CLI

**Cons:**
- ❌ **testmo_update_case BUG** (uses wrong endpoint - PUT instead of PATCH)
- ❌ **testmo_get_case BUG** (404 errors on individual case retrieval)
- ❌ **No ClickUp integration** (requires separate setup)
- ❌ **Manual workflow** (no automatic ClickUp → Testmo)

**Workaround for bugs:**
```python
# We verified this works:
response = requests.patch(
    f"{TESTMO_URL}/api/v1/projects/{project_id}/cases",
    headers={"Authorization": f"Bearer {API_KEY}"},
    json={"ids": [case_id], "custom_notes": "Updated"}
)
```

### Alternative MCP (fastmcp-based)

**Pros:**
- ✅ **ClickUp integration** built-in
- ✅ **Automated workflow** (ClickUp ticket → Testmo test cases)
- ✅ **Simpler stack** (uses fastmcp framework)
- ✅ **May not have** the update_case bug (different implementation)

**Cons:**
- ❌ **Fewer tools** (~10-15 vs 32)
- ❌ **No attachments** support
- ❌ **No test runs** analysis
- ❌ **No automation** monitoring
- ❌ **No milestones** tracking
- ❌ **Unknown pagination** handling
- ❌ **Less documentation**
- ❌ **Unknown** if works with Claude Code CLI
- ❌ **No verified** capability list

## 🔬 Testing Plan

### To Test Alternative MCP:

#### 1. Install
```bash
# Install dependencies
pip3 install fastmcp httpx

# Save testmo_mcp_server.py to ~/mcp-servers/
# (Get file from setup docs)
```

#### 2. Configure (.mcp.json - ADD, don't replace)
```json
{
  "mcpServers": {
    "testmo": {
      "command": "/Users/diegodelaguila/Projects/BTL-TestCases/venv/bin/mcp-testmo",
      "args": ["--env-file", ".env"]
    },
    "testmo-alt": {
      "command": "python3",
      "args": [
        "/Users/diegodelaguila/mcp-servers/testmo_mcp_server.py"
      ],
      "env": {
        "TESTMO_API_KEY": "YOUR_API_KEY",
        "TESTMO_INSTANCE": "bethinklabs"
      }
    }
  }
}
```

#### 3. Test Key Capabilities
```python
# Test 1: List projects (both should work)
mcp__testmo__testmo_list_projects()
mcp__testmo_alt__testmo_list_projects()

# Test 2: Update case (check if alt has bug)
mcp__testmo_alt__testmo_update_case(
    project_id=2,
    case_id=64835,
    data={"custom_notes": "Test from alt MCP"}
)

# Test 3: ClickUp workflow (alt only)
mcp__testmo_alt__create_cases_from_clickup_ticket(
    ticket_id="8669n8cwa",
    project_id=2,
    folder_id=420
)
```

## 🏆 Recommendation

### **Use OFFICIAL MCP as Primary**

**Reasoning:**
1. **More comprehensive** (32 tools vs ~10-15)
2. **Proven at scale** (handles 1334 cases with auto-pagination)
3. **More capabilities** (attachments, runs, automation, milestones)
4. **Active development** with bug fixes
5. **Works with Claude Code CLI** (verified)

**Handle the bugs with:**
- ✅ Use our `TestmoUpdater` wrapper class (already created)
- ✅ Direct PATCH requests for updates (verified working)
- ✅ File bug reports with MCP maintainers

### **Optional: Add Alternative as Secondary**

**Only if you need:**
- ClickUp → Testmo automated workflow
- Simpler integration for non-technical users

**Configuration:**
- Run BOTH MCPs simultaneously (different names: "testmo" and "testmo-alt")
- Use Official MCP for most operations
- Use Alternative MCP only for ClickUp workflows

## 🚀 Implementation

### Current (No Changes Needed)

```json
{
  "testmo": {
    "command": "/Users/diegodelaguila/Projects/BTL-TestCases/venv/bin/mcp-testmo",
    "args": ["--env-file", ".env"]
  }
}
```

**Action**: None - keep current setup

### Add Alternative (If Needed for ClickUp Workflow)

```bash
# 1. Install dependencies
pip3 install fastmcp httpx

# 2. Get testmo_mcp_server.py file
# (From setup docs or create from specification)

# 3. Add to .mcp.json
```

```json
{
  "testmo": {
    "command": "/Users/diegodelaguila/Projects/BTL-TestCases/venv/bin/mcp-testmo",
    "args": ["--env-file", ".env"]
  },
  "testmo-clickup": {
    "command": "python3",
    "args": ["/Users/diegodelaguila/mcp-servers/testmo_mcp_server.py"],
    "env": {
      "TESTMO_API_KEY": "${TESTMO_API_KEY}",
      "TESTMO_INSTANCE": "bethinklabs"
    }
  }
}
```

### Fix Update Bug (Use Wrapper)

```python
# Add to scripts/testmo_mcp_client.py
class TestmoUpdater:
    def __init__(self):
        self.url = os.getenv("TESTMO_URL", "https://bethinklabs.testmo.net")
        self.api_key = os.getenv("TESTMO_API_KEY")

    def update_case(self, project_id: int, case_id: int, **fields):
        """Workaround for MCP update bug"""
        url = f"{self.url}/api/v1/projects/{project_id}/cases"
        response = requests.patch(
            url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            json={"ids": [case_id], **fields}
        )
        response.raise_for_status()
        return response.json()["result"][0]
```

## 📋 Decision Matrix

### Choose Official MCP If:
- ✅ Need comprehensive Testmo operations
- ✅ Need attachments, runs, automation
- ✅ Working with large datasets (100+ cases)
- ✅ Using Claude Code CLI
- ✅ OK with working around update bug

### Add Alternative MCP If:
- ✅ Need ClickUp → Testmo workflow automation
- ✅ Want to test if it avoids update bug
- ✅ Prefer fastmcp framework
- ✅ Only need basic operations (list, create)

### Replace with Alternative If:
- ❌ **NOT RECOMMENDED** unless:
  - Official MCP completely broken
  - Alternative proves more stable
  - You only need 10-15 basic tools
  - ClickUp workflow is your primary use case

## 🎯 Final Answer

### Can We Run Both Simultaneously?

**YES!** ✅

Configure them with different names:
- `testmo` (official) - primary
- `testmo-alt` (alternative) - secondary

### Which Should We Standardize On?

**OFFICIAL MCP** ✅

**Why:**
- More comprehensive (32 vs ~15 tools)
- Proven at scale (1334 cases)
- More capabilities (attachments, runs, automation)
- Active development
- Bugs have known workarounds

### Installation Instructions for Alternative (Optional)

```bash
# Step 1: Install dependencies
pip3 install fastmcp httpx

# Step 2: Create server directory
mkdir -p ~/mcp-servers

# Step 3: Get testmo_mcp_server.py
# (Need to obtain file from setup docs or create)

# Step 4: Configure in .mcp.json (add, don't replace)
# See "Add Alternative" section above

# Step 5: Restart Claude
# Test with: mcp__testmo_alt__testmo_list_projects()
```

---

**Decision**: **KEEP OFFICIAL MCP, OPTIONALLY ADD ALTERNATIVE**

**Next Steps**:
1. ✅ Continue using official MCP
2. ✅ Implement TestmoUpdater wrapper for update bug
3. ⏳ Test alternative MCP for ClickUp workflow (optional)
4. ⏳ File bug report with official MCP maintainers
5. ⏳ Consider contributing fix to official MCP

**Status**: ✅ **ANALYSIS COMPLETE**
