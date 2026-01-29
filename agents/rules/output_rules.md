# Test Case Output Rules

## File Structure

### Filename Format
```
TC{number}-{feature-name}.yml
```

- **Number**: Sequential within folder (TC001, TC002, TC003...)
- **Feature name**: Kebab-case, 3-5 words max
- **Extension**: Always `.yml`

### Location
```
test-cases/{feature-folder}/TC{number}-{kebab-case-name}.yml
```

### testmo_id Field
- **New cases**: `testmo_id: null`
- **Existing cases**: Numeric ID (filled after Testmo import)
- **Never manually edit**: Let export script handle it

## Metadata Section

### Required Fields

```yaml
metadata:
  testmo_id: null  # For new cases
  id: TC001  # Same as filename prefix
  name: "Feature Area - Specific Action/Scenario"
  feature: folder-name  # Must match folder
  priority: medium  # critical, high, medium, low
  state: draft  # draft, active, deprecated
  platforms: [iOS, Android]  # Target platforms
  regions: [NNA, NCI, NMEX, NBA]  # Target regions (NNA=USA, NCI=Canada, NMEX=Mexico, NBA=Brazil)
  tags: []  # Tagging system TBD
  custom_references: "TASK-ID"  # ClickUp task reference
  created_at: "2026-01-28"  # YYYY-MM-DD format
```

### Priority Levels
- **critical**: Core functionality, blocks release if broken
- **high**: Important features, needs fix before release
- **medium**: Standard features, fix in next sprint
- **low**: Edge cases, nice-to-have validation

### Platform Specification
- **Default**: `[iOS, Android]` (test both)
- **iOS only**: `[iOS]`
- **Android only**: `[Android]`
- **Specify explicitly** if test is platform-specific

### Region Specification
- **Region Codes**: Use standardized codes (see [region_codes.md](region_codes.md))
  - `NNA` - Nissan North America (USA)
  - `NCI` - Nissan Canada Inc. (Canada)
  - `NMEX` - Nissan Mexico (Mexico)
  - `NBA` - Nissan Brazil (Brazil)
- **Default**: `[NNA, NCI, NMEX, NBA]` (all regions)
- **Region-specific features**: Use only applicable codes (e.g., Tesla Pricing is `[NNA]` only)
- **Consider**: Feature flags, localization, market-specific behavior, Infiniti availability

## Description Section

### Format
```yaml
description: |
  Verify that [specific behavior or functionality]
```

### Rules
- ✅ **Start with "Verify that"** for consistency
- ✅ **Be specific**: What exactly is being tested
- ✅ **Include context**: Why this test matters
- ❌ **No generic phrases**: Avoid "This test case should cover..."
- ❌ **No implementation details**: Focus on behavior

### Examples

**Good:**
```yaml
description: |
  Verify that user can view detailed pricing breakdown modal for Tesla charging stations, including base rate, congestion fees, and total estimated cost
```

**Bad:**
```yaml
description: |
  This test case should cover the Tesla pricing feature
```

## Preconditions Section

### Format
```yaml
preconditions:
  - description: User is on [Screen Name] screen
  - description: Feature flag "EnableFeatureName" is enabled
  - description: User has [required data state]
```

### Rules
- **Minimum setup only**: Don't include test steps
- **Clear state definition**: User, system, and data states
- **Feature flags**: Always specify if needed
- **2-4 preconditions**: Keep it focused

### Common Patterns

**User State:**
- "User is logged in"
- "User is on [Screen] screen"
- "User has valid credentials"

**System State:**
- "Feature flag 'EnableFeatureName' is enabled"
- "Network connection is available"
- "GPS location services are enabled"

**Data State:**
- "User has at least one vehicle in account"
- "Charging station database has active stations in user's area"
- "User has no preferred dealer set"

## Steps Section

### Format
```yaml
steps:
  - id: 1
    action: Tap on the pricing information icon
    expected: Pricing breakdown modal appears with detailed cost information

  - id: 2
    action: Review pricing details including base rate and fees
    expected: Base rate is displayed | Congestion fees are shown | Total cost is calculated correctly

  - id: 3
    action: Tap outside modal to close
    expected: Modal closes and user returns to charging station details
```

### Action Rules
- **Imperative mood**: "Tap on...", "Enter...", "Select...", "Verify..."
- **Specific UI elements**: Name buttons, fields, screens explicitly
- **One primary action**: If multiple sub-actions, join with " → "
- **Be precise**: "Tap on 'Pricing' icon" not "Click the icon"

### Expected Rules
- **Declarative statements**: "Screen displays...", "Data updates...", "Modal appears..."
- **Specific outcomes**: What exactly should happen
- **Multiple expectations**: Join with " | " (pipe separator)
- **Measurable**: Can be verified as pass/fail

### Multiple Actions/Expectations

**Multiple actions in one step:**
```yaml
action: Enter username → Enter password → Tap Login button
```

**Multiple expectations:**
```yaml
expected: Dashboard loads within 2 seconds | Welcome message displays | User stats are visible
```

## Notes Section (Optional)

### When to Use
- Platform-specific behavior
- Known limitations
- Test data requirements
- Edge cases to consider
- Performance baselines

### Format
```yaml
notes: |
  Platform note: iOS requires iOS 14+
  Performance baseline: Screen should load within 2 seconds
  Test with multiple charging stations to verify consistency
```

## ClickUp Integration

### Reference Format
```yaml
metadata:
  custom_references: "86b7uey05"  # Task ID without URL
```

### Post-Creation Actions
After creating test case:
1. ✅ Validate YAML schema
2. ✅ Commit to Git
3. ✅ Comment in ClickUp task with link to YAML file
4. ✅ Update ClickUp task status (if configured)

## Validation Checklist

Before committing:
- [ ] File named correctly: `TC{num}-{slug}.yml`
- [ ] Located in correct feature folder
- [ ] `testmo_id: null` for new cases
- [ ] All required metadata fields present
- [ ] Description starts with "Verify that"
- [ ] Preconditions define minimum setup
- [ ] Steps have id, action, expected
- [ ] No generic phrases or TODO comments
- [ ] ClickUp task ID referenced

## Complete Example

```yaml
metadata:
  testmo_id: null
  id: TC001
  name: "Tesla Pricing - Pricing Breakdown Modal"
  feature: tesla-pricing
  priority: high
  state: draft
  platforms: [iOS, Android]
  regions: [NNA]
  tags: []
  custom_references: "86b7uey05"
  created_at: "2026-01-28"

description: |
  Verify that user can view detailed pricing breakdown modal for Tesla charging stations, including base rate, congestion fees, and total estimated cost

preconditions:
  - description: User is on Charge screen
  - description: Feature flag "EnableTeslaPricing" is enabled
  - description: User has selected a Tesla charging station

steps:
  - id: 1
    action: Tap on the pricing information icon next to station name
    expected: Pricing breakdown modal appears with title "Pricing Details"

  - id: 2
    action: Review pricing breakdown in modal
    expected: Base charging rate is displayed | Congestion fees are shown (if applicable) | Total estimated cost is calculated | All amounts show currency symbol

  - id: 3
    action: Tap "Close" button or tap outside modal
    expected: Modal closes | User returns to charging station details screen

notes: |
  Test with both congested and non-congested stations
  Verify pricing updates if station congestion status changes
  Performance: Modal should appear within 500ms
```
