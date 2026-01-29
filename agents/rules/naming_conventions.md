# Naming Conventions

## Test Case IDs

### Format
```
TC{sequential-number}
```

### Rules
- **Sequential within folder**: Each feature folder has its own sequence
- **Zero-padded**: Always 3 digits (TC001, TC002, ..., TC099, TC100)
- **Starts at TC001**: First test in any folder is TC001
- **No gaps**: Use next available number

### Examples by Folder

**tesla-pricing/**
- TC001-max-charge-limit.yml
- TC002-pricing-breakdown-modal.yml
- TC003-congestion-fees-display.yml

**dealer-offers/**
- TC001-set-preferred-dealer.yml
- TC002-search-dealers.yml
- TC003-download-offer.yml

**authentication/**
- TC001-login-valid-credentials.yml
- TC002-login-invalid-password.yml
- TC003-biometric-authentication.yml

### Why Separate Sequences?
- Easier to find tests within a feature
- Can reorganize folders without renumber everything
- Clear scope per feature

## Filenames

### Format
```
TC{number}-{kebab-case-description}.yml
```

### Rules
- **Starts with test ID**: TC001, TC002, etc.
- **Dash separator**: Between ID and description
- **Kebab-case**: Lowercase with hyphens
- **Concise**: 3-5 words ideal
- **Descriptive**: Clear what the test does
- **No version numbers**: Don't include "v1", "v2"
- **Extension**: Always `.yml` (not `.yaml`)

### Good Examples

✅ `TC001-max-charge-limit.yml`
- Clear, concise, describes the test

✅ `TC002-pricing-breakdown-modal.yml`
- Specific UI component and action

✅ `TC003-set-preferred-dealer.yml`
- Action-focused, clear intent

✅ `TC004-login-biometric-authentication.yml`
- Specific authentication method

✅ `TC005-remote-start-happy-path.yml`
- Includes scenario type

### Bad Examples

❌ `TC001-test.yml`
- Too vague, doesn't describe what's tested

❌ `TC002-MaxChargeLimit.yml`
- PascalCase instead of kebab-case

❌ `TC003_pricing_breakdown.yml`
- Snake_case instead of kebab-case

❌ `TC004-tesla-pricing-breakdown-modal-display-verification.yml`
- Too long, redundant words

❌ `TC005-test-case-for-dealer-offers.yml`
- Redundant "test-case-for" prefix

## Feature Folders

### Format
```
test-cases/{kebab-case-feature-name}/
```

### Rules
- **Kebab-case**: Lowercase with hyphens
- **Concise**: 1-3 words
- **Feature-focused**: Represents a feature area
- **Consistent**: Match feature flag names when possible
- **No nesting**: Flat structure (no subfolders within features)

### Standard Folders

```
test-cases/
├── authentication/          # Login, logout, biometrics
├── dealer-offers/           # Dealer promotions, preferred dealer
├── remote-services/         # Remote start, lock, unlock
├── vehicle-status/          # Battery, range, diagnostics
├── charging/                # Charging stations, history
├── tesla-pricing/           # Tesla-specific pricing
├── navigation/              # Maps, routing, POI
├── settings/                # App settings, preferences
└── onboarding/              # First-time user experience
```

### Creating New Folders

When adding a new feature:
1. Check existing folders first
2. Use kebab-case
3. Keep it short but clear
4. Create folder on first test case

### Examples

✅ Good folder names:
- `authentication`
- `dealer-offers`
- `tesla-pricing`
- `remote-services`
- `vehicle-status`

❌ Bad folder names:
- `Authentication` (not lowercase)
- `dealer_offers` (use hyphens)
- `tesla-pricing-feature` (redundant "-feature")
- `tests` (too generic)
- `misc` (not descriptive)

## Test Names (metadata.name)

### Format
```
[Feature Area] - [Specific Action/Scenario]
```

### Rules
- **Title Case**: Capitalize major words
- **Feature area first**: Context before action
- **Dash separator**: ` - ` (space-dash-space)
- **Clear and specific**: Describes exact test
- **No "Test" prefix**: Assumed it's a test
- **Action or scenario**: What is being verified

### Examples

✅ Good test names:
- "Tesla Pricing - Max Charge Limit Display"
- "Tesla Pricing - Pricing Breakdown Modal"
- "Dealer Offers - Set Preferred Dealer"
- "Authentication - Login with Biometrics"
- "Remote Services - Remote Start Happy Path"
- "Vehicle Status - Battery Level Indicator"

❌ Bad test names:
- "Test Tesla Pricing" (redundant "Test")
- "Tesla pricing feature" (vague)
- "TC001 - Pricing" (don't repeat ID)
- "Login Test Case" (redundant "Test Case")
- "authentication_login" (wrong format)

### Patterns by Test Type

**Happy Path:**
- "Feature - Primary Action Happy Path"
- "Feature - Standard User Flow"

**Edge Cases:**
- "Feature - Action with Empty State"
- "Feature - Action with Maximum Values"

**Error Handling:**
- "Feature - Invalid Input Validation"
- "Feature - Network Error Handling"

**UI Validation:**
- "Feature - Component Display Verification"
- "Feature - Dark Mode Appearance"

## ClickUp Task References

### Format
```yaml
metadata:
  custom_references: "86b7uey05"
```

### Rules
- **Task ID only**: No URL prefix
- **String format**: Wrap in quotes
- **Lowercase**: Preserve original case
- **From URL**: Extract from `https://app.clickup.com/t/{task_id}`

### Examples

Task URL: `https://app.clickup.com/t/86b7uey05`
Reference: `"86b7uey05"`

Task URL: `https://app.clickup.com/t/abc123xyz`
Reference: `"abc123xyz"`

### Multiple References

If test covers multiple tasks (rare):
```yaml
metadata:
  custom_references: "86b7uey05, 86b8abc12"
```

## Complete Naming Example

### Given:
- **Feature**: Tesla Pricing
- **ClickUp Task**: https://app.clickup.com/t/86b7uey05
- **Purpose**: Test pricing breakdown modal display
- **Test Number**: First test in folder

### Result:

**Filename:**
```
TC001-pricing-breakdown-modal.yml
```

**Location:**
```
test-cases/tesla-pricing/TC001-pricing-breakdown-modal.yml
```

**Metadata:**
```yaml
metadata:
  testmo_id: null
  id: TC001
  name: "Tesla Pricing - Pricing Breakdown Modal"
  feature: tesla-pricing
  custom_references: "86b7uey05"
  created_at: "2026-01-28"
```

## Naming Checklist

Before creating a test case:

- [ ] **Test ID**: Sequential for the feature (TC001, TC002...)
- [ ] **Filename**: `TC{num}-{kebab-case}.yml`
- [ ] **Feature folder**: Exists or will create (kebab-case)
- [ ] **Test name**: "Feature Area - Specific Action"
- [ ] **ClickUp ref**: Task ID extracted from URL
- [ ] **Consistent**: Follows all conventions above

## Quick Reference

| Element | Format | Example |
|---------|--------|---------|
| Test ID | `TC{num}` | `TC001` |
| Filename | `TC{num}-{kebab-case}.yml` | `TC001-pricing-modal.yml` |
| Folder | `{kebab-case}` | `tesla-pricing` |
| Test Name | `Feature - Action` | `Tesla Pricing - Pricing Modal` |
| ClickUp Ref | `"{task_id}"` | `"86b7uey05"` |

## Tools

### Generate Filename from Name

**Python:**
```python
import re

def generate_filename(test_name, test_num):
    # Extract action part after dash
    parts = test_name.split(' - ')
    if len(parts) > 1:
        action = parts[1]
    else:
        action = test_name

    # Convert to kebab-case
    slug = action.lower()
    slug = re.sub(r'[\s_]+', '-', slug)
    slug = re.sub(r'[^a-z0-9-]', '', slug)
    slug = re.sub(r'-+', '-', slug)
    slug = slug.strip('-')

    return f"TC{test_num:03d}-{slug}.yml"

# Example
name = "Tesla Pricing - Pricing Breakdown Modal"
num = 1
filename = generate_filename(name, num)
# Result: "TC001-pricing-breakdown-modal.yml"
```

### Extract ClickUp ID from URL

**Python:**
```python
def extract_clickup_id(url):
    # Extract ID from URL
    match = re.search(r'/t/([a-z0-9]+)', url)
    if match:
        return match.group(1)
    return None

# Example
url = "https://app.clickup.com/t/86b7uey05"
task_id = extract_clickup_id(url)
# Result: "86b7uey05"
```

## Summary

**Consistency is key:**
- Same format everywhere
- Easy to find and understand
- Scales to hundreds of tests
- Works with automation
- Clear for all team members

**When in doubt:**
- Look at existing tests
- Follow the patterns
- Keep it simple
- Make it readable
