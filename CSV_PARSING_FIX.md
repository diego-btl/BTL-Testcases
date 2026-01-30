# CSV Parsing Fix: Testmo Export

**Date**: 2026-01-30
**Issue**: CSV folder mappings not loading (0 instead of 1334)

## Problem

When using `--csv-map` with Testmo CSV exports, the script was:
- Reading wrong headers: "Project ID, 2" (metadata row)
- Loading 0 folder mappings (should be 1334)
- Sending all cases to "uncategorized" folder
- Warning: "TC535 has folder_id=39 not in API"

## Root Cause

Testmo CSV exports have this structure:
```csv
"Project ID","2"                    ← Line 1: Metadata
"Project","OneApp"                  ← Line 2: Metadata
"Exported at","2026-01-30..."       ← Line 3: Metadata
                                    ← Line 4: Empty
"Case","Description","Folder",...   ← Line 5: REAL headers
"Fresh Install","","Installation",... ← Line 6+: Data
```

The bug: `csv.DictReader(f)` treats the **first line** as headers, so it read `"Project ID","2"` instead of the real headers on line 5.

## Fix Applied

Modified `scripts/testmo_export.py` function `build_csv_folder_map()`:

**Before:**
```python
with open(csv_path, 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)  # ❌ Reads line 1 as headers
```

**After:**
```python
with open(csv_path, 'r', encoding='utf-8-sig') as f:
    # Skip first 4 lines (3 metadata rows + 1 empty line)
    for _ in range(4):
        next(f)

    # Now line 5 has the real column headers
    reader = csv.DictReader(f)  # ✅ Reads line 5 as headers
```

## Verification Results

### Test 1: Small Export (10 cases)
```bash
python3 scripts/testmo_export.py \
  --project-id 2 \
  --csv-map data/oneapp-repo-export.csv \
  --limit 10
```

**Results:**
- ✅ "Loaded folder mappings for 1334 test cases from CSV" (was 0)
- ✅ "CSV columns found: Case ID, Folder, and 23 others" (correct)
- ✅ Sample mappings: TC535 → installation/, TC536 → installation/
- ✅ Cases exported to proper folders: enhanced-in-app-chat (8), data-anniversary (2)
- ✅ No warnings about "folder_id not in API"

### Test 2: Medium Export (100 cases)
```bash
python3 scripts/testmo_export.py \
  --project-id 2 \
  --csv-map data/oneapp-repo-export.csv \
  --limit 100
```

**Results:**
- ✅ Loaded 1334 folder mappings
- ✅ 100 cases exported to 22 different folders
- ✅ No "uncategorized" folder created
- ✅ 0 root files
- ✅ No warnings

**Folder Distribution (100 cases):**
```
charge: 19 cases
necn-nissan-energy-charge-network: 11 cases
second-delivery-discovery-cta-display: 9 cases
enhanced-in-app-chat: 8 cases
second-delivery-booking-virtual: 8 cases
map: 6 cases
data-anniversary: 5 cases
... and 15 more folders
```

### Test 3: Final Verification
```bash
# Check for root files (should be 0)
find test-cases/oneapp-final-verify -maxdepth 1 -name '*.yml' | wc -l
# Output: 0 ✅

# Check for uncategorized folder (should not exist)
ls -d test-cases/oneapp-final-verify/uncategorized
# Output: No such file or directory ✅

# Check proper folder structure
find test-cases/oneapp-final-verify -type d | head -15
# Output: 22 proper folders (charge, necn, map, favorites, etc.) ✅
```

## Success Criteria

| Criterion | Before | After |
|-----------|--------|-------|
| CSV mappings loaded | ❌ 0 | ✅ 1334 |
| Root files created | ❌ Many | ✅ 0 |
| Uncategorized folder | ❌ Yes | ✅ No |
| Warnings about folder_id | ❌ Many | ✅ None |
| Proper folder structure | ❌ No | ✅ Yes |

## Files Modified

- `scripts/testmo_export.py` - Fixed `build_csv_folder_map()` function (lines 46-95)
  - Added logic to skip first 4 lines before creating DictReader
  - Updated docstring to document CSV structure

## Next Steps

1. ✅ Fix applied and tested
2. ✅ Verified with 10, 100 case exports
3. ⏳ Ready for full OneApp export (1334 cases)
4. ⏳ Can now use CSV-based folder mapping for all Testmo exports

**Status**: ✅ **FIXED AND VERIFIED**
