# CRITICAL: Fix testmo_export.py to preserve folder hierarchy from Testmo

## Problem

Export is dumping all 284 NMEX test cases flat, ignoring Testmo's 45-folder structure.

## Reference Data

- PDF: `/Users/diegodelaguila/Downloads/Print_-_Repository_-_NMEX_-_Testmo.pdf` shows correct 45-folder hierarchy
- CSV: `/Users/diegodelaguila/Downloads/testmo-export-repository-37.csv` has case IDs and names
- Current bad export: `testmo/nmex/test-cases/` (all flat)

## Expected Structure

Based on PDF, NMEX has this hierarchy:

```
installation/ (5 cases)
demo-mode/ (21 cases)
landing-pages/
  └── login-page/ (4 cases)
login-flow/
  └── login-page/ (7 cases)
register-flow/
  └── login-page/ (9 cases)
home-page/ (26 cases)
  ├── vehicle-selector/ (4 cases)
  ├── add-vehicle/ (9 cases)
  ├── hero-module/ (4 cases)
  ├── telematics/ (2 cases)
  ├── notifications/ (10 cases)
  ├── mils/ (3 cases)
  ├── controls/ (3 cases)
  ├── climate/ (11 cases)
  ├── edit-cards/ (1 case)
  ├── push-notifications/ (4 cases)
  ├── device-notifications/ (3 cases)
  ├── alerts/ (24 cases)
  └── credit/
      ├── selectiviti-closed/ (4 cases)
      ├── leasing-closed/ (4 cases)
      └── tradicional-closed/ (5 cases)
vehicle-page/ (46 cases)
  ├── past-services/ (2 cases)
  ├── programar-servicio/ (8 cases)
  └── my-documents/ (5 cases)
map-page/ (6 cases)
  ├── search-bar/ (1 case)
  ├── poi-and-favorites/ (7 cases)
  └── dealers/ (1 case)
support/ (1 case)
  ├── let-us-help/ (5 cases)
  ├── faq/ (3 cases)
  ├── whatsapp/ (1 case)
  ├── nissan-concierge/ (1 case)
  ├── emergency-contacts/ (6 cases)
  └── personal-assistance/ (1 case)
settings/ (5 cases)
  ├── account-preferences/ (1 case)
  ├── theme/ (1 case)
  ├── security/ (1 case)
  └── legal/ (2 cases)
wearables/ (10 cases)
```

**Total: 45 folders, 284 test cases**

## Implementation

### 1. Add to scripts/testmo_client.py:

Add these two methods to the TestmoClient class:

```python
def get_folders(self, project_id: int) -> List[Dict]:
    """Get all folders for a project with hierarchy info"""
    url = f"{self.base_url}/api/index/1/projects/{project_id}/folders"
    response = requests.get(url, headers=self.headers)
    response.raise_for_status()
    return response.json()

def build_folder_map(self, folders: List[Dict]) -> Dict[int, str]:
    """Build map of folder_id -> full_path
    
    Example:
        folder_id 1234 -> "home-page/alerts/credit"
    """
    folder_map = {}
    
    def get_path(folder_id):
        if folder_id in folder_map:
            return folder_map[folder_id]
        
        folder = next((f for f in folders if f['id'] == folder_id), None)
        if not folder:
            return ""
        
        # Sanitize folder name for filesystem
        name = safe_filename(folder['name'])
        parent_id = folder.get('parent_id')
        
        if parent_id:
            parent_path = get_path(parent_id)
            path = f"{parent_path}/{name}" if parent_path else name
        else:
            path = name
        
        folder_map[folder_id] = path
        return path
    
    # Build paths for all folders
    for folder in folders:
        get_path(folder['id'])
    
    return folder_map
```

### 2. Modify scripts/testmo_export.py:

Find the section after this line (around line 100):
```python
console.print(f"[green]✓[/green] Found {len(cases)} test cases")
```

**ADD THIS CODE right after that line:**

```python
# Get folder structure
with console.status("[bold green]Fetching folder structure..."):
    folders = client.get_folders(project_id)
    folder_map = client.build_folder_map(folders)
    console.print(f"[green]✓[/green] Found {len(folders)} folders")
```

**THEN, modify the conversion loop** (around line 120-140):

Change FROM:
```python
for case in cases:
    yaml_case = converter.testmo_to_yaml(case, feature=feature)
    metadata = yaml_case.get("metadata", {})
    
    test_id = metadata.get("id", "TC00000")
    test_name = metadata.get("name", "untitled")
    filename = f"{test_id}-{safe_filename(test_name)}.yml"
    
    filepath = output_dir / filename
    
    with open(filepath, 'w') as f:
        yaml.dump(yaml_case, f, ...)
```

Change TO:
```python
for case in cases:
    yaml_case = converter.testmo_to_yaml(case, feature=feature)
    metadata = yaml_case.get("metadata", {})
    
    # Get folder path from Testmo
    folder_id = case.get('folder_id')
    folder_path = folder_map.get(folder_id, "uncategorized")
    
    # Create nested directory structure
    case_dir = output_dir / folder_path
    case_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate filename
    test_id = metadata.get("id", "TC00000")
    test_name = metadata.get("name", "untitled")
    filename = f"{test_id}-{safe_filename(test_name)}.yml"
    
    # Write to correct folder
    filepath = case_dir / filename
    
    with open(filepath, 'w') as f:
        yaml.dump(yaml_case, f, ...)
```

### 3. Test with NMEX:

```bash
# Clear old export
rm -rf testmo/nmex/test-cases/*

# Re-export with folder structure
python scripts/testmo_export.py \
  --project-id 6 \
  --output-dir testmo/nmex/test-cases

# Verify structure
tree testmo/nmex/test-cases/ | head -100

# Count files
find testmo/nmex/test-cases -name "*.yml" | wc -l
# Should output: 284

# Count folders
find testmo/nmex/test-cases -type d | wc -l  
# Should be ~45+ (including nested)
```

### 4. Generate Summary Report:

After successful export, create a summary:

```bash
# List all folders
echo "# NMEX Folder Structure" > testmo/nmex/EXPORT_SUMMARY.md
echo "" >> testmo/nmex/EXPORT_SUMMARY.md
echo "## Folders Found:" >> testmo/nmex/EXPORT_SUMMARY.md
find testmo/nmex/test-cases -type d | sort >> testmo/nmex/EXPORT_SUMMARY.md

echo "" >> testmo/nmex/EXPORT_SUMMARY.md
echo "## Case Count by Folder:" >> testmo/nmex/EXPORT_SUMMARY.md
for dir in testmo/nmex/test-cases/*/; do
  if [ -d "$dir" ]; then
    count=$(find "$dir" -name "*.yml" | wc -l)
    echo "- $(basename "$dir"): $count cases" >> testmo/nmex/EXPORT_SUMMARY.md
  fi
done

echo "" >> testmo/nmex/EXPORT_SUMMARY.md
echo "## Total:" >> testmo/nmex/EXPORT_SUMMARY.md
total=$(find testmo/nmex/test-cases -name "*.yml" | wc -l)
echo "- **Total Test Cases:** $total" >> testmo/nmex/EXPORT_SUMMARY.md
```

## Success Criteria

✅ 284 test cases exported
✅ 45+ folders created with correct hierarchy  
✅ No flat structure - all cases in proper folders
✅ Folder names match PDF (sanitized for filesystem)
✅ Each folder contains the correct number of test cases

## Debug if Issues

If export fails or structure is wrong:

```python
# Add debug logging to see what's happening:
print(f"DEBUG: Folders fetched: {len(folders)}")
print(f"DEBUG: Sample folder: {folders[0] if folders else 'None'}")
print(f"DEBUG: Folder map size: {len(folder_map)}")
print(f"DEBUG: Sample mapping: {list(folder_map.items())[:3]}")

# For each case:
print(f"DEBUG: Case {case['id']} -> folder_id={case.get('folder_id')} -> path={folder_path}")
```

## Expected Output Structure

After running the fixed export, you should see:

```
testmo/nmex/test-cases/
├── installation/
│   ├── TC-xxxx-fresh-install.yml
│   ├── TC-xxxx-overinstall.yml
│   └── ... (5 total)
├── demo-mode/
│   ├── TC-xxxx-landing-page.yml
│   └── ... (21 total)
├── landing-pages/
│   └── login-page/
│       └── ... (4 total)
├── home-page/
│   ├── TC-xxxx-placas-card-connected.yml
│   ├── vehicle-selector/
│   │   └── ... (4 total)
│   ├── alerts/
│   │   └── credit/
│   │       ├── selectiviti-closed/
│   │       │   └── ... (4 total)
│   │       └── ... 
│   └── ...
└── ... (45 folders total)
```

Execute this fix NOW. This is blocking all other work.
