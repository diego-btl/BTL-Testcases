# Region Codes Reference

## Overview
Bethink Labs manages Nissan and Infiniti connected vehicle applications across four regions. Test cases must specify which regions they apply to using standardized region codes.

## Region Codes

### NNA (Nissan North America)
- **Full Name:** Nissan North America
- **Country:** United States
- **App Brands:** Nissan, Infiniti
- **Code in Test Cases:** `NNA`

### NCI (Nissan Canada Inc.)
- **Full Name:** Nissan Canada Inc.
- **Country:** Canada
- **App Brands:** Nissan, Infiniti
- **Code in Test Cases:** `NCI`

### NMEX (Nissan Mexico)
- **Full Name:** Nissan Mexico
- **Country:** Mexico
- **App Brands:** Nissan, Infiniti
- **Code in Test Cases:** `NMEX`

### NBA (Nissan Brazil)
- **Full Name:** Nissan Brazil
- **Country:** Brazil
- **App Brands:** Nissan (Infiniti not available in Brazil)
- **Code in Test Cases:** `NBA`

## Usage in Test Cases

### All Regions (Default)
Most features apply to all regions:
```yaml
metadata:
  regions: [NNA, NCI, NMEX, NBA]
```

### Region-Specific Features
Some features are limited to specific regions:
```yaml
# USA only
metadata:
  regions: [NNA]

# USA and Canada only (North America)
metadata:
  regions: [NNA, NCI]

# Latin America only
metadata:
  regions: [NMEX, NBA]
```

## Brand-Specific Notes

### Infiniti Availability
- **Available:** NNA, NCI, NMEX
- **Not Available:** NBA (Brazil does not have Infiniti brand)

### Regional Feature Differences
- **Tesla Pricing:** NNA only (US charging infrastructure)
- **Dealer Offers:** All regions (region-specific dealer networks)
- **Remote Services:** All regions (may have different service providers)

## Testmo Project Mapping

Each region has a corresponding Testmo project:
- **NNA:** Project ID 2 (main OneApp project)
- **NCI:** Separate test runs within Project 2
- **NMEX:** Project ID 6
- **NBA:** Project ID 5

## Examples

### Feature Available Everywhere
```yaml
metadata:
  name: "Authentication - Biometric Login"
  regions: [NNA, NCI, NMEX, NBA]
```

### US-Only Feature (Tesla Charging)
```yaml
metadata:
  name: "Tesla Pricing - Max Charge Limit"
  regions: [NNA]
```

### Infiniti-Specific Feature
```yaml
metadata:
  name: "Infiniti Dealer Offers - Set Preferred Dealer"
  regions: [NNA, NCI, NMEX]  # Excluding NBA
```

## Guidelines

1. **Default to All Regions:** Unless explicitly stated in requirements, assume features apply to all regions
2. **Document Limitations:** If a feature is region-specific, note the reason in the test case description
3. **Brand Awareness:** Consider Infiniti availability when creating brand-specific tests
4. **ClickUp Tags:** ClickUp tasks may include region tags (e.g., [NNA], [USA]) - use these to determine region scope
