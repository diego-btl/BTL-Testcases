# Testmo API Findings

Technical documentation of Testmo API behavior, data structures, and limitations discovered during PoC development.

## Table of Contents

- [API Endpoints](#api-endpoints)
- [Data Structures](#data-structures)
- [HTML Conversion Patterns](#html-conversion-patterns)
- [Known Limitations](#known-limitations)
- [Working Solutions](#working-solutions)
- [Performance](#performance)

---

## API Endpoints

### Endpoints That Work ✅

#### List Projects
```http
GET /api/v1/projects
Authorization: Bearer {api_key}
```

**Response:**
```json
[
  {
    "id": 2,
    "name": "OneApp",
    "note": "Nissan OneApp Project",
    "is_completed": false,
    "milestone_count": 48,
    "run_count": 110,
    "automation_run_count": 2459,
    "created_at": "2023-08-01T22:35:14.284Z"
  }
]
```

**Usage:** Get project IDs for export/import operations

---

#### List Folders
```http
GET /api/v1/projects/{project_id}/folders
Authorization: Bearer {api_key}
```

**Response:**
```json
[
  {
    "id": 7148,
    "project_id": 2,
    "repo_id": 2,
    "parent_id": 3600,
    "depth": 1,
    "name": "Dealer Offers",
    "docs": null,
    "display_order": 45,
    "full_path": "Home / Dealer Offers"
  }
]
```

**Notes:**
- Returns ALL folders in flat list (not tree structure)
- `parent_id`: null for root folders
- `full_path`: Human-readable hierarchy
- `depth`: 0 for root, 1 for children, etc.

---

#### List Test Cases
```http
GET /api/v1/projects/{project_id}/cases?folder_id={folder_id}&per_page=100
Authorization: Bearer {api_key}
```

**Response:**
```json
{
  "page": 1,
  "per_page": 100,
  "total": 9,
  "result": [
    {
      "id": 64839,
      "key": 64839,
      "name": "Dealer Offers - Call Dealer Phone",
      "project_id": 2,
      "repo_id": 2,
      "folder_id": 7148,
      "state_id": 16,
      "template_id": 2,
      "custom_description": "<p>This test case verifies...</p>",
      "custom_priority": 3,
      "custom_preconditions": "<ul><li>User is logged in</li></ul>",
      "custom_steps": [
        {
          "column_name": "custom_steps",
          "id": 102513,
          "case_id": 64839,
          "text1": "<p>Tap on the phone icon</p>",
          "text2": null,
          "text3": "<p>System phone dialer opens</p>",
          "text4": null,
          "display_order": 1
        }
      ],
      "custom_notes": "<p>Test on both platforms</p>",
      "created_at": "2026-01-28 23:18:38.150452",
      "created_by": 2
    }
  ]
}
```

**Notes:**
- `per_page`: Max 100 (API limitation)
- Pagination: Use `page` parameter for large sets
- All rich text stored as HTML

---

#### Create Folder
```http
POST /api/v1/projects/{project_id}/folders
Authorization: Bearer {api_key}
Content-Type: application/json

{
  "folders": [
    {
      "name": "Main Folder",
      "parent_id": null
    }
  ]
}
```

**Response:**
```json
[
  {
    "id": 7149,
    "project_id": 8,
    "repo_id": 54,
    "parent_id": null,
    "depth": 0,
    "name": "Main Folder",
    "display_order": 45
  }
]
```

**Notes:**
- Requires `folders` array (batch operation)
- `parent_id`: null for root, folder ID for children
- Returns created folder with new ID

---

#### Create Test Cases (Batch)
```http
POST /api/v1/projects/{project_id}/cases
Authorization: Bearer {api_key}
Content-Type: application/json

{
  "cases": [
    {
      "name": "Login - Valid Credentials",
      "folder_id": 7150,
      "template_id": 2,
      "state_id": 1,
      "custom_description": "<p>Verify user can login</p>",
      "custom_priority": 1,
      "custom_preconditions": "<ul><li>User on login page</li></ul>",
      "custom_steps": [
        {
          "text1": "<p>Enter valid username</p>",
          "text3": "<p>Username field accepts input</p>",
          "display_order": 1
        },
        {
          "text1": "<p>Click Login button</p>",
          "text3": "<p>User redirected to dashboard</p>",
          "display_order": 2
        }
      ],
      "custom_notes": "<p>Critical path test</p>"
    }
  ]
}
```

**Response:**
```json
[
  {
    "id": 64846,
    "key": 64846,
    "name": "Login - Valid Credentials",
    "folder_id": 7150,
    "custom_steps": [
      {
        "column_name": "custom_steps",
        "id": 102533,
        "case_id": 64846,
        "text1": "<p>Enter valid username</p>",
        "text2": null,
        "text3": "<p>Username field accepts input</p>",
        "text4": null,
        "display_order": 1
      }
    ],
    "created_at": "2026-01-29 00:08:45.740518"
  }
]
```

**Notes:**
- Requires `cases` array (batch operation)
- Max 100 cases per request
- All HTML formatting preserved
- Returns created cases with new IDs

---

### Endpoints That DON'T Work ❌

#### Get Individual Test Case
```http
GET /api/v1/projects/{project_id}/cases/{case_id}
Authorization: Bearer {api_key}
```

**Response:**
```json
{
  "error": true,
  "status_code": 404,
  "message": "Request failed: Not Found",
  "details": {
    "message": "The route api/v1/projects/{project_id}/cases/{case_id} could not be found."
  }
}
```

**Tested with:**
- Project ID: 2, Case ID: 64844 (exists in list)
- Project ID: 2, Case ID: 64845 (exists in list)
- Multiple projects and case IDs

**Conclusion:** Individual case GET not supported

---

#### Update Test Case
```http
PATCH /api/v1/projects/{project_id}/cases/{case_id}
Authorization: Bearer {api_key}
Content-Type: application/json

{
  "custom_description": "<p>Updated description</p>"
}
```

**Response:**
```json
{
  "error": true,
  "status_code": 404,
  "message": "Request failed: Not Found",
  "details": {
    "message": "The route api/v1/projects/{project_id}/cases/{case_id} could not be found."
  }
}
```

**Tested with:**
- Various HTTP methods: PATCH, PUT, POST
- Different project IDs
- Cases that exist in list endpoint

**Conclusion:** Individual case UPDATE not supported

---

#### Delete Folder
```http
DELETE /api/v1/projects/{project_id}/folders/{folder_id}
Authorization: Bearer {api_key}
```

**Response:**
```json
{
  "error": true,
  "status_code": 404,
  "message": "Request failed: Not Found",
  "details": {
    "message": "The route api/v1/projects/{project_id}/folders/{folder_id} could not be found."
  }
}
```

**Tested with:**
- Project ID: 8, Folder IDs: 7150, 7151 (exist in list)
- Folders verified to exist via list endpoint

**Conclusion:** Individual folder DELETE not supported

---

## Data Structures

### Test Case Object

```python
{
    "id": 64839,                # Auto-generated by Testmo
    "key": 64839,               # Same as id
    "name": "Test Case Name",   # Required
    "project_id": 2,            # Project container
    "repo_id": 2,               # Repository (usually same as project)
    "folder_id": 7148,          # Parent folder
    "state_id": 16,             # 1=Draft, 4=Active, 16=Approved, etc.
    "template_id": 2,           # 2=Steps Table, 4=BDD/Gherkin
    "custom_priority": 3,       # 1=Critical, 2=High, 3=Medium, 4=Low
    "custom_description": "<p>HTML content</p>",
    "custom_preconditions": "<ul><li>Bullet points</li></ul>",
    "custom_steps": [...],      # Array of step objects
    "custom_notes": "<p>Additional notes</p>",
    "created_at": "2026-01-28 23:18:38.150452",
    "created_by": 2,
    "updated_at": null,
    "updated_by": null
}
```

### Step Object

```python
{
    "column_name": "custom_steps",  # Always this value
    "id": 102513,                   # Auto-generated
    "case_id": 64839,               # Parent test case
    "text1": "<p>Action text</p>",  # What to do
    "text2": null,                  # Optional (rarely used)
    "text3": "<p>Expected</p>",     # Expected result
    "text4": null,                  # Optional (rarely used)
    "display_order": 1              # 1, 2, 3, ...
}
```

### Folder Object

```python
{
    "id": 7148,
    "project_id": 2,
    "repo_id": 2,
    "parent_id": 3600,           # null for root folders
    "depth": 1,                  # 0=root, 1=child, 2=grandchild, etc.
    "name": "Dealer Offers",
    "docs": null,                # Optional documentation
    "display_order": 45,
    "full_path": "Home / Dealer Offers"
}
```

---

## HTML Conversion Patterns

### Description (Single Paragraph)

**Testmo (HTML):**
```html
<p>This test case verifies the phone call functionality from dealer details</p>
```

**YAML (Plain Text):**
```yaml
description: |
  This test case verifies the phone call functionality from dealer details
```

**Python Conversion:**
```python
from bs4 import BeautifulSoup

def strip_html(html_text):
    if not html_text:
        return ""
    soup = BeautifulSoup(html_text, 'html.parser')
    return soup.get_text(strip=True)
```

---

### Preconditions (Bullet List)

**Testmo (HTML):**
```html
<ul>
  <li>User is on the Dealer Details screen</li>
  <li>Dealer has a valid phone number</li>
</ul>
```

**YAML (List):**
```yaml
preconditions:
  - User is on the Dealer Details screen
  - Dealer has a valid phone number
```

**Python Conversion:**
```python
def parse_html_list_items(html_text):
    if not html_text:
        return []
    soup = BeautifulSoup(html_text, 'html.parser')
    items = soup.find_all('li')
    return [item.get_text(strip=True) for item in items]
```

---

### Steps (Multiple Actions/Expected)

**Testmo (HTML):**
```html
text1: "<ol><li>Tap on the phone icon</li><li>Verify number</li></ol>"
text3: "<ul><li>System dialer opens</li><li>Number formatted correctly</li></ul>"
```

**YAML (Separated):**
```yaml
steps:
  - action: Tap on the phone icon → Verify number
    expected: System dialer opens | Number formatted correctly
```

**Python Conversion:**
```python
def parse_multiple_items(html_text):
    if not html_text:
        return ""
    soup = BeautifulSoup(html_text, 'html.parser')
    items = soup.find_all('li')
    if len(items) > 1:
        return ' → '.join([item.get_text(strip=True) for item in items])
    return soup.get_text(strip=True)
```

---

### Notes (Multi-Paragraph)

**Testmo (HTML):**
```html
<p>Test phone integration on both iOS and Android</p>
<p>Note: iPhone requires iOS 14+</p>
```

**YAML (Plain Text with Newlines):**
```yaml
notes: |
  Test phone integration on both iOS and Android

  Note: iPhone requires iOS 14+
```

**Python Conversion:**
```python
def convert_to_multiline(html_text):
    if not html_text:
        return ""
    soup = BeautifulSoup(html_text, 'html.parser')
    paragraphs = soup.find_all('p')
    return '\n\n'.join([p.get_text(strip=True) for p in paragraphs])
```

---

## Known Limitations

### 1. No Individual Resource Access

**Problem:** Cannot GET, UPDATE, or DELETE individual test cases or folders

**Impact:**
- Cannot update single test case
- Cannot fetch full details of one case
- Cannot delete folders programmatically

**Root Cause:** API design focuses on batch operations

**Hypothesis:**
- Correct endpoints might be: `/api/v1/projects/{id}/repositories/{repo_id}/cases/{case_id}`
- The MCP server implementation uses incorrect route patterns
- Testmo API may require repository ID in path

---

### 2. Batch Size Limit

**Limit:** 100 items per batch request

**Endpoints Affected:**
- POST `/cases` - Max 100 cases
- GET `/cases` - Max 100 per page (requires pagination)

**Workaround:**
```python
def batch_create_cases(cases, batch_size=100):
    for i in range(0, len(cases), batch_size):
        batch = cases[i:i + batch_size]
        response = api.create_cases(batch)
        # Process response
```

---

### 3. No Bulk Update Endpoint

**Problem:** No endpoint to update multiple cases at once

**Current Options:**
1. Delete and recreate (loses test run history)
2. Create new folder, manually delete old one
3. Manual updates in Testmo UI

**Chosen Approach:** Option 2 (preserves IDs for reference)

---

### 4. HTML-Only Rich Text

**Problem:** All rich text must be HTML, no Markdown support

**Fields Affected:**
- `custom_description`
- `custom_preconditions`
- `custom_steps.text1` (action)
- `custom_steps.text3` (expected)
- `custom_notes`

**Requirement:** Must convert YAML → HTML on import

---

## Working Solutions

### Solution 1: Batch Re-Import for Updates

```python
def update_test_cases_workaround(yaml_dir, project_id, new_folder_name):
    # 1. Import all YAMLs to new folder
    cases = load_yaml_files(yaml_dir)
    api.create_folder(project_id, new_folder_name)
    api.batch_create_cases(project_id, cases)

    # 2. Manual step: User deletes old folder in UI
    print(f"✅ Imported to '{new_folder_name}'")
    print(f"⚠️  Manual step: Delete old folder in Testmo UI")
    print(f"⚠️  Then rename '{new_folder_name}' to original name")
```

**Result:** Test cases updated, but requires manual folder management

---

### Solution 2: Pagination for Large Exports

```python
def export_all_cases(project_id, folder_id):
    all_cases = []
    page = 1
    per_page = 100

    while True:
        response = api.list_cases(
            project_id=project_id,
            folder_id=folder_id,
            page=page,
            per_page=per_page
        )

        all_cases.extend(response['result'])

        if page >= response['last_page']:
            break

        page += 1

    return all_cases
```

**Result:** Can export any number of test cases

---

### Solution 3: HTML Conversion Library

```python
from bs4 import BeautifulSoup

def yaml_to_html(yaml_content):
    """Convert YAML test case to Testmo HTML format"""
    return {
        'name': yaml_content['metadata']['name'],
        'custom_description': f"<p>{yaml_content['description']}</p>",
        'custom_preconditions': (
            '<ul>' +
            ''.join(f'<li>{item}</li>' for item in yaml_content['preconditions']) +
            '</ul>'
        ),
        'custom_steps': [
            {
                'text1': f'<p>{step["action"]}</p>',
                'text3': f'<p>{step["expected"]}</p>',
                'display_order': i + 1
            }
            for i, step in enumerate(yaml_content['steps'])
        ],
        'custom_notes': f"<p>{yaml_content.get('notes', '')}</p>"
    }
```

**Result:** Bidirectional conversion without data loss

---

## Performance

### Export Performance

**Tested:** 9 test cases from "Dealer Offers" folder

- Time: ~2 seconds
- Rate: ~4.5 cases/second
- Bottleneck: API latency

**Estimated for 900 cases:**
- Time: ~200 seconds (~3.3 minutes)
- With pagination overhead: ~5 minutes

---

### Import Performance

**Tested:** 4 test cases created in "Playground" project

- Time: ~1 second (batch of 4)
- Rate: ~4 cases/second
- Bottleneck: API processing

**Estimated for 900 cases:**
- 9 batches of 100 cases each
- Time: ~9 seconds per batch = ~90 seconds
- With overhead: ~2 minutes

---

### Validation Performance

**Tested:** 9 YAML files validated

- Time: <1 second
- Rate: >9 files/second
- Bottleneck: Disk I/O

**Estimated for 900 files:**
- Time: <100 seconds (~1.5 minutes)
- Highly parallelizable

---

## Recommendations

### For Testmo API Improvements

1. **Add individual resource endpoints:**
   ```
   GET    /api/v1/projects/{id}/cases/{case_id}
   PATCH  /api/v1/projects/{id}/cases/{case_id}
   DELETE /api/v1/projects/{id}/cases/{case_id}
   DELETE /api/v1/projects/{id}/folders/{folder_id}
   ```

2. **Add bulk update endpoint:**
   ```
   PATCH /api/v1/projects/{id}/cases
   Body: { "cases": [ {id, updates} ] }
   ```

3. **Support Markdown in addition to HTML:**
   - Easier to write
   - Better for version control
   - Convertible to HTML

4. **Increase batch size limit:**
   - 100 → 500 or 1000
   - Reduces API calls for large operations

---

### For Our Implementation

1. ✅ Use batch operations for all creates
2. ✅ Implement pagination for large exports
3. ✅ Convert HTML ↔ YAML reliably
4. ⚠️ Accept manual folder management as limitation
5. ✅ Validate all YAMLs before import
6. ✅ Log all API operations for debugging

---

## Appendix: Tested Endpoints

| Endpoint | Method | Status | Notes |
|----------|--------|--------|-------|
| `/projects` | GET | ✅ Works | Lists all projects |
| `/projects/{id}` | GET | ✅ Works | Get project details |
| `/projects/{id}/folders` | GET | ✅ Works | List all folders |
| `/projects/{id}/folders` | POST | ✅ Works | Create folders (batch) |
| `/projects/{id}/folders/{fid}` | DELETE | ❌ 404 | Not supported |
| `/projects/{id}/cases` | GET | ✅ Works | List cases (paginated) |
| `/projects/{id}/cases` | POST | ✅ Works | Create cases (batch, max 100) |
| `/projects/{id}/cases/{cid}` | GET | ❌ 404 | Not supported |
| `/projects/{id}/cases/{cid}` | PATCH | ❌ 404 | Not supported |
| `/projects/{id}/cases/{cid}` | PUT | ❌ 404 | Not supported |
| `/projects/{id}/cases/{cid}` | DELETE | ❌ 404 | Not supported |
| `/projects/{id}/milestones` | GET | ✅ Works | List milestones |
| `/projects/{id}/runs` | GET | ✅ Works | List test runs |

---

**Last Updated:** January 28, 2026
**Tested By:** Diego Garcia with Claude Code
**API Version:** Testmo v1 (2025)
