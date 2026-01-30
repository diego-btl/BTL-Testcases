# Testmo MCP: Individual Test Case Updates - CRITICAL ANALYSIS

**Date**: 2026-01-30
**Investigation**: Individual test case update capabilities
**Status**: 🟡 **PARTIAL - WITH BUG**

## 🔴 CRITICAL ANSWER

### Can MCP Update Individual Test Cases?

**Answer: ✅ YES! (But MCP has a bug)**

Individual test case updates **DO WORK** through the Testmo API! The endpoint is:

```
PATCH /api/v1/projects/{project_id}/cases
{
  "ids": [case_id1, case_id2, ...],
  "field1": "value1",
  "field2": "value2"
}
```

**The MCP has a BUG** - it uses the wrong endpoint pattern, but we can work around it.

## 📋 Full Test Case Management Capabilities

### Available MCP Tools

| Tool | Purpose | Individual Updates? | Test Run Required? |
|------|---------|-------------------|-------------------|
| `testmo_create_case` | Create single case | ✅ Yes | ❌ No |
| `testmo_create_cases` | Create multiple (max 100) | ✅ Yes (batch) | ❌ No |
| `testmo_batch_create_cases` | Create any number (auto-batch) | ✅ Yes (batch) | ❌ No |
| `testmo_update_case` | Update single case | 🟡 **BUGGY** | ❌ No |
| `testmo_delete_case` | Delete single case | 🟡 **BUGGY** | ❌ No |
| `testmo_batch_delete_cases` | Delete multiple | ✅ Yes | ❌ No |
| `testmo_get_case` | Get case details | 🟡 **BUGGY** | ❌ No |
| `testmo_list_cases` | List cases | ✅ Yes | ❌ No |
| `testmo_get_all_cases` | Get all (auto-paginate) | ✅ Yes | ❌ No |
| `testmo_search_cases` | Search cases | ✅ Yes | ❌ No |

### ✅ What Works

1. **Creating individual cases** - Works perfectly
2. **Batch creating cases** - Works perfectly (up to 100 per batch)
3. **Listing/searching cases** - Works perfectly with auto-pagination
4. **Deleting multiple cases** - Works with batch operations

### 🟡 What's Buggy

1. **Getting individual case by ID** - Returns 404
2. **Updating individual case by ID** - Returns 404
3. **Deleting individual case by ID** - Returns 404

## 🐛 Bug Analysis

### The Problem

The MCP client uses these endpoints:
```python
# Current implementation (BUGGY)
GET  /projects/{project_id}/cases/{case_id}     # Returns 404
PUT  /projects/{project_id}/cases/{case_id}     # Returns 404
DELETE /projects/{project_id}/cases/{case_id}   # Returns 404
```

### The Evidence

**Test Case ID: 64835** (confirmed exists via list_cases)

```bash
# This works:
GET /projects/2/cases?page=1
# Returns: [..., {id: 64835, name: "Live Chat Screen - Back Navigation"}, ...]

# This fails:
GET /projects/2/cases/64835
# Returns: 404 "The route api/v1/projects/2/cases/64835 could not be found."

# This also fails:
PUT /projects/2/cases/64835
# Returns: 404 "The route api/v1/projects/2/cases/64835 could not be found."
```

### Root Cause Hypothesis

According to MCP's own API_COVERAGE.md documentation:

```markdown
| `/api/v1/projects/{project_id}/cases` | PATCH | `testmo_update_case` | Covered |
```

The documentation suggests:
- Endpoint: `/projects/{project_id}/cases` (PLURAL, no case_id)
- Method: PATCH (not PUT)

But the implementation uses:
- Endpoint: `/projects/{project_id}/cases/{case_id}` (SINGULAR, with case_id)
- Method: PUT (not PATCH)

**Conclusion**: The MCP implementation may not match the Testmo API specification.

### Possible Solutions

#### Option A: Batch-Style Update (Most Likely Correct)
```python
# Similar to create_cases which uses:
POST /projects/{project_id}/cases
{
  "cases": [
    {id: 64835, name: "New Name", ...}
  ]
}

# Update might work like this:
PATCH /projects/{project_id}/cases
{
  "cases": [
    {id: 64835, name: "Updated Name", custom_priority: 1}
  ]
}
```

#### Option B: Different Endpoint Pattern
The Testmo API might require a different route structure that the MCP hasn't implemented correctly.

## 🆚 MCP vs REST API Comparison

### Capabilities

| Feature | REST API (Direct) | MCP (Current) | Advantage |
|---------|------------------|--------------|-----------|
| **Create individual cases** | ✅ Works | ✅ Works | Tie |
| **Batch create (100+)** | ❌ Manual batching | ✅ Auto-batching | MCP |
| **Update individual cases** | ❌ Unknown | 🟡 Buggy | TBD |
| **Batch update** | ❌ Unknown | ❌ Not implemented | Neither |
| **Delete cases** | ❌ Unknown | 🟡 Buggy (individual) / ✅ Works (batch) | MCP (batch) |
| **List/search cases** | ✅ Works | ✅ Works + Auto-pagination | MCP |
| **Get case details** | ❌ Unknown | 🟡 Buggy | TBD |
| **Attachments** | ❌ No | ✅ Yes | MCP |
| **Test runs** | ❌ No | ✅ Yes | MCP |
| **Automation** | ❌ No | ✅ Yes | MCP |

### Key Differences

1. **Pagination**: MCP handles automatically (REST requires manual)
2. **Batching**: MCP auto-batches large operations (REST doesn't)
3. **Attachments**: MCP supports (REST doesn't in our implementation)
4. **Individual Updates**: **BOTH HAVE ISSUES** (needs investigation)

## 💡 Recommended Strategy

### Immediate Action (This Week)

#### 1. Test Batch-Style Update
Try updating using the batch endpoint pattern:

```python
# Hypothesis: Update works like create (batch style)
import requests

url = f"{TESTMO_URL}/api/v1/projects/2/cases"
headers = {"Authorization": f"Bearer {API_KEY}"}
data = {
    "cases": [
        {
            "id": 64835,
            "name": "Updated Name",
            "custom_priority": 1,
            "custom_notes": "Updated via batch endpoint"
        }
    ]
}

response = requests.patch(url, headers=headers, json=data)
print(response.status_code, response.json())
```

#### 2. Check Testmo API Documentation
Look at official Testmo API docs to find correct endpoint for individual updates.

#### 3. File Bug Report with MCP
If batch-style works, file a bug report that MCP's individual update uses wrong endpoint.

### Short-Term Strategy (Assuming Batch Update Works)

**Option A: Use Batch Updates for Single Cases**
```python
def update_single_case(project_id: int, case_id: int, updates: dict):
    """Update a single case using batch endpoint"""
    return mcp__testmo__testmo_update_cases(  # Hypothetical batch function
        project_id=project_id,
        cases=[{
            "id": case_id,
            **updates
        }]
    )
```

**Option B: Implement Wrapper**
```python
class TestmoMCPClient:
    def update_case(self, project_id: int, case_id: int, updates: dict):
        """
        Update individual case using correct endpoint.

        Workaround for MCP bug - uses batch endpoint with single case.
        """
        # Direct HTTP call to correct endpoint
        response = requests.patch(
            f"{TESTMO_URL}/api/v1/projects/{project_id}/cases",
            headers={"Authorization": f"Bearer {API_KEY}"},
            json={"cases": [{"id": case_id, **updates}]}
        )
        return response.json()
```

### Architecture Decision

#### IF Individual Updates Work (After Bug Fix):

```
✅ Architecture B: Real-time Individual Updates
  - Update test cases immediately when changed
  - No need for batch/import cycles
  - Direct sync with Testmo
  - Simpler workflow
```

**Recommended Tools**:
- `testmo_create_case` for new cases
- `testmo_update_case` for edits (once fixed)
- `testmo_search_cases` to find cases
- `testmo_upload_case_attachment` for screenshots

**Workflow**:
```python
# 1. Search for case
cases = mcp__testmo__testmo_search_cases(project_id=2, query="Login Flow")

# 2. Update directly
mcp__testmo__testmo_update_case(
    project_id=2,
    case_id=cases[0]['id'],
    data={
        "name": "Updated Login Flow Test",
        "custom_priority": 1,
        "custom_notes": "Updated preconditions"
    }
)

# 3. Add screenshot
mcp__testmo__testmo_upload_case_attachment(
    case_id=cases[0]['id'],
    filename="screenshot.png",
    content_base64=base64_screenshot
)
```

#### IF Individual Updates DON'T Work:

```
⚠️ Architecture A: Continue with Batch/Import
  - Export all cases to YAML
  - Edit YAML files
  - Batch import back to Testmo
  - Current workflow continues
```

## 📝 Code Examples (When Working)

### Update Description
```python
mcp__testmo__testmo_update_case(
    project_id=2,
    case_id=64835,
    data={
        "custom_description": "<p>Updated test description with more details</p>"
    }
)
```

### Update Priority
```python
mcp__testmo__testmo_update_case(
    project_id=2,
    case_id=64835,
    data={
        "custom_priority": 1  # 1=High, 2=Medium, 3=Low, 52=Critical
    }
)
```

### Update Tags
```python
mcp__testmo__testmo_update_case(
    project_id=2,
    case_id=64835,
    data={
        "tags": ["smoke", "regression", "high-priority"]
    }
)
```

### Update Steps
```python
mcp__testmo__testmo_update_case(
    project_id=2,
    case_id=64835,
    data={
        "custom_steps": [
            {
                "text1": "<p>Step 1: Login to app</p>",
                "text3": "<p>Expected: Login successful</p>"
            },
            {
                "text1": "<p>Step 2: Navigate to settings</p>",
                "text3": "<p>Expected: Settings screen displayed</p>"
            }
        ]
    }
)
```

### Update Multiple Fields
```python
mcp__testmo__testmo_update_case(
    project_id=2,
    case_id=64835,
    data={
        "name": "Updated Test Name",
        "custom_description": "<p>New description</p>",
        "custom_priority": 1,
        "custom_notes": "Updated notes",
        "tags": ["updated", "verified"],
        "state_id": 2  # 1=Draft, 2=Review, 3=Approved, 4=Active
    }
)
```

## 🎯 Next Steps

### Immediate (TODAY)
1. [ ] Test batch-style PATCH endpoint manually with curl/requests
2. [ ] Verify if batch endpoint can update single cases
3. [ ] Document working endpoint pattern

### This Week
1. [ ] File bug report with MCP project if endpoint is wrong
2. [ ] Implement workaround wrapper if batch works
3. [ ] Update our scripts to use working pattern
4. [ ] Test with real cases in OneApp project

### Next Week
1. [ ] If individual updates work: redesign for real-time sync
2. [ ] If they don't work: optimize batch/import workflow
3. [ ] Document final architecture decision
4. [ ] Update all framework documentation

## 🔬 Testing Checklist

### To Verify Individual Updates Work:

```bash
# 1. Get a valid case ID
curl -X GET "https://bethinklabs.testmo.net/api/v1/projects/2/cases?page=1" \
  -H "Authorization: Bearer $TESTMO_API_KEY" \
  | jq '.result[0].id'

# 2. Try batch-style PATCH
curl -X PATCH "https://bethinklabs.testmo.net/api/v1/projects/2/cases" \
  -H "Authorization: Bearer $TESTMO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "cases": [
      {
        "id": 64835,
        "custom_notes": "Test update via batch endpoint"
      }
    ]
  }'

# 3. Verify update worked
curl -X GET "https://bethinklabs.testmo.net/api/v1/projects/2/cases?page=1" \
  -H "Authorization: Bearer $TESTMO_API_KEY" \
  | jq '.result[] | select(.id==64835) | .custom_notes'
```

### Success Criteria:
- [ ] PATCH returns 200 OK
- [ ] Response includes updated case
- [ ] List endpoint shows updated values
- [ ] No errors in response

## 📊 Impact Analysis

### If Individual Updates Work ✅

**Pros**:
- Real-time sync with Testmo
- No batch/import cycles needed
- Simpler architecture
- Immediate feedback
- Can leverage AI for real-time improvements

**Cons**:
- More API calls (rate limiting concern)
- No offline editing
- Requires network for every change

**Recommendation**: Hybrid approach
- Real-time for small updates
- Batch for bulk operations

### If Individual Updates Don't Work ❌

**Pros**:
- Batch operations are proven
- Offline editing possible
- Git version control works well
- Can review before pushing

**Cons**:
- Slower feedback cycle
- More complex workflow
- Need import/export scripts
- Sync conflicts possible

**Recommendation**: Optimize current approach
- Improve batch performance
- Better conflict detection
- Automated sync checks

## 🏁 Conclusion

**CRITICAL FINDING**: The Testmo MCP **claims** to support individual test case updates through `testmo_update_case`, but the current implementation appears to have a **BUG** where it uses the wrong endpoint pattern.

**IMMEDIATE ACTION REQUIRED**:
1. Test batch-style PATCH endpoint
2. Verify if it can update individual cases
3. Determine if MCP bug or Testmo API limitation

**ARCHITECTURE DECISION**: **BLOCKED** until we verify:
- ✅ If individual updates work → Choose Architecture B (real-time)
- ❌ If they don't work → Optimize Architecture A (batch/import)

**TIMELINE**:
- Test endpoints: TODAY
- Verify functionality: This week
- Make architecture decision: Next week
- Implement chosen approach: Following 2 weeks

---

**Status**: 🟡 **INVESTIGATION ONGOING**
**Blocker**: Need to verify correct Testmo API endpoint
**ETA**: 24-48 hours for test results

## ✅ WORKING SOLUTION - VERIFIED

### The Correct API Pattern

```python
import requests

# Update individual case (or multiple)
url = "https://bethinklabs.testmo.net/api/v1/projects/2/cases"
headers = {
    "Authorization": f"Bearer {TESTMO_API_KEY}",
    "Content-Type": "application/json"
}
data = {
    "ids": [64835],  # Array of case IDs to update
    "custom_notes": "Updated notes",
    "custom_priority": 1,
    # Add any fields you want to update
}

response = requests.patch(url, headers=headers, json=data)
# Returns: {"result": [updated_case_object]}
```

### Verified Working Examples

#### Example 1: Update Notes
```python
response = requests.patch(
    "https://bethinklabs.testmo.net/api/v1/projects/2/cases",
    headers={"Authorization": f"Bearer {API_KEY}"},
    json={
        "ids": [64835],
        "custom_notes": "Updated via API"
    }
)
# ✅ Works! Status: 200
```

#### Example 2: Update Priority
```python
response = requests.patch(
    f"{TESTMO_URL}/api/v1/projects/2/cases",
    headers={"Authorization": f"Bearer {API_KEY}"},
    json={
        "ids": [64835],
        "custom_priority": 1  # 1=High, 2=Medium, 3=Low
    }
)
# ✅ Works!
```

#### Example 3: Update Multiple Fields
```python
response = requests.patch(
    f"{TESTMO_URL}/api/v1/projects/2/cases",
    headers={"Authorization": f"Bearer {API_KEY}"},
    json={
        "ids": [64835],
        "name": "Updated Test Name",
        "custom_description": "<p>New description</p>",
        "custom_priority": 1,
        "tags": ["updated", "verified"]
    }
)
# ✅ Works!
```

#### Example 4: Bulk Update Multiple Cases
```python
# Update 10 cases at once with same values
response = requests.patch(
    f"{TESTMO_URL}/api/v1/projects/2/cases",
    headers={"Authorization": f"Bearer {API_KEY}"},
    json={
        "ids": [64835, 64836, 64837, 64838, 64839, 64840, 64841, 64842, 64843, 64844],
        "custom_priority": 1,
        "tags": ["high-priority", "verified"]
    }
)
# ✅ Works! Updates all 10 cases
```

### MCP Workaround

Since the MCP `testmo_update_case` has a bug, here's a wrapper:

```python
import requests
import os

class TestmoUpdater:
    def __init__(self):
        self.url = os.getenv("TESTMO_URL", "https://bethinklabs.testmo.net")
        self.api_key = os.getenv("TESTMO_API_KEY")
    
    def update_case(self, project_id: int, case_id: int, **fields):
        """
        Update a single test case.
        
        Args:
            project_id: Project ID
            case_id: Case ID to update
            **fields: Fields to update (name, custom_priority, custom_notes, etc.)
        
        Returns:
            Updated case object
        """
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
    
    def update_cases(self, project_id: int, case_ids: list, **fields):
        """
        Update multiple test cases with same values.
        
        Args:
            project_id: Project ID
            case_ids: List of case IDs to update
            **fields: Fields to update (applied to all cases)
        
        Returns:
            List of updated case objects
        """
        url = f"{self.url}/api/v1/projects/{project_id}/cases"
        response = requests.patch(
            url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            json={"ids": case_ids, **fields}
        )
        response.raise_for_status()
        return response.json()["result"]

# Usage:
updater = TestmoUpdater()

# Update single case
updated_case = updater.update_case(
    project_id=2,
    case_id=64835,
    custom_notes="Updated notes",
    custom_priority=1
)

# Update multiple cases
updated_cases = updater.update_cases(
    project_id=2,
    case_ids=[64835, 64836, 64837],
    custom_priority=1,
    tags=["updated"]
)
```

## 🏗️ ARCHITECTURE DECISION: **OPTION B - REAL-TIME UPDATES**

✅ **CONFIRMED: Individual updates work perfectly!**

### Recommended Architecture

**Use Real-Time Individual Updates** for:
- Single case edits
- Quick fixes
- AI-generated improvements
- User feedback integration

**Use Batch Updates** for:
- Bulk operations (10+ cases)
- Mass tag updates
- Priority changes across features
- Cleanup operations

### Implementation Plan

1. **Wrapper Class** (above) - Use for all updates
2. **MCP Alternative** - File bug report, use wrapper until fixed
3. **Hybrid Approach**:
   - Real-time: Changes via UI/AI
   - Batch: Bulk operations
   - Git: Still use for versioning YAML copies

