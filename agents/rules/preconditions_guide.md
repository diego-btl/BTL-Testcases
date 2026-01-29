# Preconditions Writing Guide

## Purpose

Preconditions define the **MINIMUM state** required before test execution begins.

They answer: "What must be true before I can start this test?"

## Key Principles

### 1. Minimum Setup Only
- Include **only** what's needed to start the test
- Don't include test steps
- Don't include expected outcomes
- Keep it focused (2-4 preconditions ideal)

### 2. Clear State Definition
- **User state**: Where they are, what they've done
- **System state**: Feature flags, services, connections
- **Data state**: What data exists in the system

### 3. Testable Conditions
- Each precondition should be verifiable
- QA should know if precondition is met
- Automation can check preconditions before test

## Patterns and Templates

### User State Patterns

#### Navigation State
```yaml
preconditions:
  - description: User is on [Screen Name] screen
```

Examples:
- "User is on Home screen"
- "User is on Charge screen"
- "User is on Dealer Offers screen"
- "User is on Vehicle Profile screen"

#### Authentication State
```yaml
preconditions:
  - description: User is logged in
  - description: User is logged in with valid credentials
  - description: User is logged out
```

#### Data/Content State
```yaml
preconditions:
  - description: User has [data condition]
```

Examples:
- "User has at least one vehicle in account"
- "User has no vehicles in account"
- "User has a preferred dealer selected"
- "User has no preferred dealer set"

### System State Patterns

#### Feature Flags
```yaml
preconditions:
  - description: Feature flag "EnableFeatureName" is enabled
```

Examples:
- "Feature flag 'EnableTeslaPricing' is enabled"
- "Feature flag 'EnableDealerOffers' is enabled"
- "Feature flag 'EnableTeslaPricing' is disabled"

#### Network/Connectivity
```yaml
preconditions:
  - description: Network connection is available
  - description: GPS location services are enabled
  - description: Bluetooth is enabled
```

#### Device State
```yaml
preconditions:
  - description: Device has iOS 14 or later
  - description: Device location permissions are granted
  - description: Device has camera permissions enabled
```

### Data State Patterns

#### Database/Backend State
```yaml
preconditions:
  - description: [Data] exists in system
```

Examples:
- "Charging station database has active stations in user's area"
- "Dealer database contains dealers within 50 miles"
- "Vehicle VIN is registered in backend system"

#### Vehicle State
```yaml
preconditions:
  - description: Vehicle [condition]
```

Examples:
- "Vehicle is connected and online"
- "Vehicle battery is below 80%"
- "Vehicle is not stolen or pending"
- "Vehicle is enrolled in remote services"

#### Account State
```yaml
preconditions:
  - description: Account [condition]
```

Examples:
- "Account has active subscription"
- "Account has no pending actions"
- "Account has completed onboarding"

## Common Mistakes

### ❌ Mistake 1: Including Test Steps

**Wrong:**
```yaml
preconditions:
  - description: User taps on Settings button
  - description: User navigates to Account screen
```

**Right:**
```yaml
preconditions:
  - description: User is on Account screen
```

**Why:** Tapping buttons and navigating are test steps, not preconditions.

---

### ❌ Mistake 2: Too Many Preconditions

**Wrong:**
```yaml
preconditions:
  - description: User is logged in
  - description: User has completed profile
  - description: User has accepted terms
  - description: User has verified email
  - description: User has at least one vehicle
  - description: Vehicle is connected
  - description: Feature flag enabled
```

**Right:**
```yaml
preconditions:
  - description: User is logged in with a connected vehicle
  - description: Feature flag "EnableFeatureName" is enabled
```

**Why:** Combine related conditions, focus on essentials.

---

### ❌ Mistake 3: Vague Language

**Wrong:**
```yaml
preconditions:
  - description: The user should be on some screen
  - description: System might have some data
```

**Right:**
```yaml
preconditions:
  - description: User is on Home screen
  - description: User has at least one vehicle in account
```

**Why:** Be specific and definitive.

---

### ❌ Mistake 4: Testing Preconditions

**Wrong:**
```yaml
preconditions:
  - description: User verifies they are logged in
  - description: Check if feature flag is enabled
```

**Right:**
```yaml
preconditions:
  - description: User is logged in
  - description: Feature flag "EnableFeatureName" is enabled
```

**Why:** Preconditions are assumptions, not test steps.

---

### ❌ Mistake 5: Including Expected Outcomes

**Wrong:**
```yaml
preconditions:
  - description: User will see the dashboard
  - description: Data should be loaded
```

**Right:**
```yaml
preconditions:
  - description: User is on Dashboard screen
  - description: User data has been synced from backend
```

**Why:** "Will see" and "should be" are expectations, not preconditions.

## Writing Checklist

Before finalizing preconditions, check:

- [ ] **Minimum set**: Can't reduce further without breaking test
- [ ] **Clear state**: Each condition is unambiguous
- [ ] **Verifiable**: QA can check if condition is met
- [ ] **No test steps**: Not describing actions to take
- [ ] **Specific**: No vague terms like "some", "might", "should"
- [ ] **Necessary**: Every precondition is actually needed
- [ ] **2-4 items**: Not too few, not too many

## Examples by Feature

### Authentication Tests

```yaml
preconditions:
  - description: User is on Login screen
  - description: User has valid credentials
```

### Remote Services Tests

```yaml
preconditions:
  - description: User is logged in with a connected vehicle
  - description: Vehicle is enrolled in remote services
  - description: Feature flag "EnableRemoteStart" is enabled
```

### Tesla Pricing Tests

```yaml
preconditions:
  - description: User is on Charge screen
  - description: Feature flag "EnableTeslaPricing" is enabled
  - description: User has selected a Tesla charging station
```

### Dealer Offers Tests

```yaml
preconditions:
  - description: User is on Home screen
  - description: Feature flag "EnableDealerOffers" is enabled
  - description: User has a preferred dealer selected
```

### Settings Tests

```yaml
preconditions:
  - description: User is logged in
  - description: User is on Settings screen
```

## Special Cases

### Negative Tests

For tests that verify error handling:

```yaml
preconditions:
  - description: User is on Login screen
  - description: User has invalid credentials (wrong password)
```

### Edge Cases

For boundary conditions:

```yaml
preconditions:
  - description: User has exactly 0 vehicles in account
  - description: Vehicle battery is at 100%
```

### Platform-Specific

When test is platform-specific:

```yaml
preconditions:
  - description: User is on iOS device with iOS 14+
  - description: User has Face ID enabled
```

## Summary

**Good preconditions are:**
- ✅ Minimum necessary setup
- ✅ Clear and specific
- ✅ Verifiable by QA
- ✅ Free of test steps
- ✅ Focused (2-4 items)

**Bad preconditions have:**
- ❌ Test steps mixed in
- ❌ Vague language
- ❌ Too many items
- ❌ Expected outcomes
- ❌ Unnecessary details
