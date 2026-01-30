# Critical Fix: Test Cases in Root Instead of Folders

**Date**: 2026-01-30
**Issue**: 528 OneApp test cases dumped in root instead of folders

## Problem

Export script was writing test cases with deleted/missing folder_ids to root directory instead of a proper folder.

### Root Cause

Test cases referenced `folder_id=7144` (and others) that were deleted/archived in Testmo. When `folder_id` wasn't in `folders_map`, the script wrote files to root.

### Impact

- **OneApp**: 528 cases in root (40% of total)
- **NMEX**: 0 cases in root ✅
- **NBA**: 0 cases in root ✅
- **Enrique**: 0 cases in root ✅

## Fix Applied

Changed `scripts/testmo_export.py` lines 186-198:

**BEFORE (Broken):**
```python
if folder_path:
    target_dir = output_dir / folder_path
else:
    target_dir = output_dir  # ❌ Writes to root!
```

**AFTER (Fixed):**
```python
if folder_id and folder_id in folders_map:
    folder_path = folders_map[folder_id]['path']
elif folder_id:
    # Deleted folder - move to uncategorized
    folder_path = "uncategorized"
else:
    # No folder_id - move to uncategorized
    folder_path = "uncategorized"

# NEVER write to root - always use a folder
target_dir = output_dir / folder_path
```

## Results After Fix

| Project | Root Files (Before) | Root Files (After) | Uncategorized |
|---------|---------------------|-------------------|---------------|
| **OneApp** | 528 ❌ | 0 ✅ | 528 |
| **NMEX** | 0 ✅ | 0 ✅ | 0 |
| **NBA** | 0 ✅ | 0 ✅ | 0 |
| **Enrique** | 0 ✅ | 0 ✅ | 0 |

## Verification

```bash
# OneApp structure
find testmo/oneapp/test-cases -maxdepth 1 -name "*.yml" | wc -l
# Output: 0 (no root files)

ls testmo/oneapp/test-cases/uncategorized/*.yml | wc -l  
# Output: 528 (orphaned cases)

find testmo/oneapp/test-cases -name "*.yml" | wc -l
# Output: 1334 (all files accounted for)
```

## Why Cases Were Orphaned

The 528 cases in `uncategorized/` were referencing:
- `folder_id=7144` - Deleted folder (no longer exists in Testmo)
- Other deleted/archived folders

These cases need to be:
1. Manually reviewed in Testmo UI
2. Moved to proper folders in Testmo
3. Re-exported to get correct folder structure

## Next Steps

1. ✅ Fix applied to export script
2. ✅ All projects re-exported
3. ⏳ Clean up: Move cases from uncategorized/ to proper folders in Testmo
4. ⏳ Re-export after cleanup to remove uncategorized/

## Files Modified

- `scripts/testmo_export.py` - Fixed folder assignment logic
- Added warnings for cases with deleted folders
- Added summary count of orphaned cases

## Success Criteria

- ✅ No test cases written to root directory
- ✅ Cases with deleted folders moved to "uncategorized/"
- ✅ All test cases accounted for
- ✅ Folder structure preserved for valid folders

**Status**: ✅ **FIXED AND VERIFIED**
