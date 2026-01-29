# Context System

## Overview

The context system provides AI agents with structured knowledge about the Bethink Labs environment, enabling them to make informed decisions when creating and managing test cases.

**Purpose**: Agents should understand:
- Which regions are supported
- Which brands operate in each region
- Which features are available per region
- Platform-specific considerations
- Business rules and constraints

**Philosophy**: Context as code - Machine-readable, version-controlled, single source of truth.

---

## Current Context Files

### 1. Region Codes (`region_codes.md`)

**Location**: `agents/rules/region_codes.md`

**Purpose**: Define the geographic regions where Nissan/Infiniti apps operate.

**Content**:
```yaml
Regions:
  NNA:
    full_name: "Nissan North America"
    country: "United States"
    brands: ["Nissan", "Infiniti"]
    code: "NNA"

  NCI:
    full_name: "Nissan Canada Inc."
    country: "Canada"
    brands: ["Nissan", "Infiniti"]
    code: "NCI"

  NMEX:
    full_name: "Nissan Mexico"
    country: "Mexico"
    brands: ["Nissan", "Infiniti"]
    code: "NMEX"

  NBA:
    full_name: "Nissan Brazil"
    country: "Brazil"
    brands: ["Nissan"]  # No Infiniti in Brazil
    code: "NBA"
```

**Usage**:
- Default test case regions: `[NNA, NCI, NMEX, NBA]`
- Region-specific features: Specify subset (e.g., `[NNA]` for Tesla Pricing)
- Brand-specific tests: Exclude NBA for Infiniti features

**Examples**:
```yaml
# Feature available everywhere
metadata:
  regions: [NNA, NCI, NMEX, NBA]

# US-only feature (Tesla Superchargers)
metadata:
  regions: [NNA]

# Infiniti feature (not in Brazil)
metadata:
  regions: [NNA, NCI, NMEX]

# North America only
metadata:
  regions: [NNA, NCI]
```

---

## Future Context Expansion

The context system is designed to grow into a comprehensive knowledge base. Here's the roadmap:

### Phase 1: Regional Context (Current)

**Files**:
- ✅ `region_codes.md` - Human-readable documentation
- 🔜 `regions.json` - Machine-readable data

**Structure** (`regions.json`):
```json
{
  "regions": {
    "NNA": {
      "name": "Nissan North America",
      "code": "NNA",
      "country": "United States",
      "country_code": "US",
      "brands": ["Nissan", "Infiniti"],
      "languages": ["en-US"],
      "currency": "USD",
      "testmo_project_id": 2,
      "active": true
    },
    "NCI": {
      "name": "Nissan Canada Inc.",
      "code": "NCI",
      "country": "Canada",
      "country_code": "CA",
      "brands": ["Nissan", "Infiniti"],
      "languages": ["en-CA", "fr-CA"],
      "currency": "CAD",
      "testmo_project_id": 2,
      "active": true
    },
    "NMEX": {
      "name": "Nissan Mexico",
      "code": "NMEX",
      "country": "Mexico",
      "country_code": "MX",
      "brands": ["Nissan", "Infiniti"],
      "languages": ["es-MX"],
      "currency": "MXN",
      "testmo_project_id": 6,
      "active": true
    },
    "NBA": {
      "name": "Nissan Brazil",
      "code": "NBA",
      "country": "Brazil",
      "country_code": "BR",
      "brands": ["Nissan"],
      "languages": ["pt-BR"],
      "currency": "BRL",
      "testmo_project_id": 5,
      "active": true
    }
  }
}
```

**Use Cases**:
- Validate region codes in test cases
- Auto-populate available brands per region
- Generate region-specific test runs
- Map regions to Testmo projects

### Phase 2: Brand Context

**File**: `brands.json`

**Structure**:
```json
{
  "brands": {
    "Nissan": {
      "name": "Nissan",
      "code": "nissan",
      "regions": ["NNA", "NCI", "NMEX", "NBA"],
      "app_identifiers": {
        "ios": "com.nissan.oneapp",
        "android": "com.nissan.oneapp"
      },
      "color_scheme": {
        "primary": "#C3002F",
        "secondary": "#000000"
      },
      "features": {
        "remote_services": true,
        "ev_features": true,
        "infiniti_offers": false
      }
    },
    "Infiniti": {
      "name": "Infiniti",
      "code": "infiniti",
      "regions": ["NNA", "NCI", "NMEX"],
      "app_identifiers": {
        "ios": "com.infiniti.oneapp",
        "android": "com.infiniti.oneapp"
      },
      "color_scheme": {
        "primary": "#000000",
        "secondary": "#C0C0C0"
      },
      "features": {
        "remote_services": true,
        "ev_features": false,
        "infiniti_offers": true
      }
    }
  }
}
```

**Use Cases**:
- Validate brand availability per region
- Filter test cases by brand
- Generate brand-specific test data
- Verify app identifiers

### Phase 3: Feature Context

**File**: `features.json`

**Structure**:
```json
{
  "features": {
    "tesla-pricing": {
      "name": "Tesla Supercharger Pricing",
      "description": "Display detailed pricing for Tesla Superchargers",
      "regions": ["NNA"],
      "brands": ["Nissan"],
      "platforms": ["iOS", "Android"],
      "feature_flags": ["EnableTeslaPricing", "EnableTariffPricingV3"],
      "dependencies": {
        "schema": "tariffPricing V3",
        "api_endpoints": ["/charging/stations", "/charging/pricing"],
        "data_provider": "Tesla"
      },
      "test_folder": "test-cases/tesla-pricing",
      "testmo_folder_id": 7155,
      "priority": "high",
      "status": "active"
    },
    "remote-start": {
      "name": "Remote Engine Start",
      "description": "Start vehicle engine remotely",
      "regions": ["NNA", "NCI", "NMEX", "NBA"],
      "brands": ["Nissan", "Infiniti"],
      "platforms": ["iOS", "Android"],
      "feature_flags": ["EnableRemoteStart"],
      "dependencies": {
        "telematics": "required",
        "subscription": "basic"
      },
      "test_folder": "test-cases/remote-services",
      "testmo_folder_id": 7200,
      "priority": "critical",
      "status": "active"
    },
    "dealer-offers": {
      "name": "Dealer Offers & Promotions",
      "description": "View and manage dealer offers",
      "regions": ["NNA", "NCI", "NMEX", "NBA"],
      "brands": ["Nissan", "Infiniti"],
      "platforms": ["iOS", "Android"],
      "feature_flags": ["EnableDealerOffers"],
      "dependencies": {
        "api_endpoints": ["/dealers", "/offers"]
      },
      "test_folder": "test-cases/dealer-offers",
      "testmo_folder_id": 7180,
      "priority": "medium",
      "status": "active"
    }
  }
}
```

**Use Cases**:
- Auto-populate test case metadata (regions, platforms)
- Validate feature availability per region
- Generate feature-specific test folders
- Map features to Testmo folders
- Track feature dependencies

### Phase 4: Platform Context

**File**: `platforms.json`

**Structure**:
```json
{
  "platforms": {
    "iOS": {
      "name": "iOS",
      "code": "iOS",
      "min_version": "14.0",
      "target_version": "17.0",
      "languages": ["en", "es", "fr", "pt"],
      "identifiers": {
        "nissan": "com.nissan.oneapp",
        "infiniti": "com.infiniti.oneapp"
      },
      "automation": {
        "framework": "XCTest",
        "test_path": "ios/Tests"
      }
    },
    "Android": {
      "name": "Android",
      "code": "Android",
      "min_version": "8.0",
      "target_version": "14.0",
      "languages": ["en", "es", "fr", "pt"],
      "identifiers": {
        "nissan": "com.nissan.oneapp",
        "infiniti": "com.infiniti.oneapp"
      },
      "automation": {
        "framework": "Espresso",
        "test_path": "android/app/src/androidTest"
      }
    }
  }
}
```

**Use Cases**:
- Validate platform specifications
- Generate platform-specific test data
- Map to automation frameworks
- Verify OS version requirements

### Phase 5: API Context

**File**: `apis.json`

**Structure**:
```json
{
  "apis": {
    "graphql": {
      "name": "OneGraph API",
      "type": "GraphQL",
      "base_url": "https://api.nissan.com/graphql",
      "regions": ["NNA", "NCI", "NMEX", "NBA"],
      "schemas": {
        "tariffPricing": {
          "version": "v3",
          "fields": ["maxChargeLimit", "energyFee", "sessionFee", "idlingFee", "congestionFee"]
        },
        "vehicle": {
          "version": "v2",
          "fields": ["id", "vin", "model", "year", "batteryLevel"]
        }
      }
    },
    "rest": {
      "name": "Legacy REST API",
      "type": "REST",
      "base_url": "https://api.nissan.com/v1",
      "regions": ["NNA", "NCI"],
      "endpoints": [
        {
          "path": "/dealers",
          "methods": ["GET", "POST"],
          "authentication": "OAuth2"
        },
        {
          "path": "/vehicles/{vin}/remote-start",
          "methods": ["POST"],
          "authentication": "OAuth2"
        }
      ]
    }
  }
}
```

**Use Cases**:
- Document API dependencies
- Validate schema versions
- Generate API test data
- Track endpoint availability per region

---

## Using Context in Test Cases

### Example 1: Regional Feature

```yaml
# Feature available only in USA
metadata:
  name: "Tesla Pricing - Connector Fees"
  feature: tesla-pricing
  regions: [NNA]  # From regions.json
  platforms: [iOS, Android]

preconditions:
  - description: Feature flag "EnableTeslaPricing" is enabled
  - description: User is in NNA region (US market)
```

### Example 2: Brand-Specific Feature

```yaml
# Infiniti feature (not available in Brazil)
metadata:
  name: "Infiniti Offers - Set Preferred Dealer"
  feature: dealer-offers
  regions: [NNA, NCI, NMEX]  # Exclude NBA (no Infiniti)
  platforms: [iOS, Android]
```

### Example 3: Multi-Region with Variations

```yaml
metadata:
  name: "Remote Start - Happy Path"
  feature: remote-services
  regions: [NNA, NCI, NMEX, NBA]
  platforms: [iOS, Android]

regional_variations:
  NMEX:
    - step: 2
      note: "Spanish language UI displays 'Iniciar Motor Remoto'"
  NBA:
    - step: 3
      note: "Portuguese language UI displays 'Início Remoto'"
```

---

## Context Validation

### Schema Validation

**Goal**: Ensure test cases use valid context values.

**Future Tool** (`scripts/validate_context.py`):
```python
def validate_test_case(yaml_file: Path) -> List[str]:
    """Validate test case against context data"""
    errors = []

    # Load context
    regions = load_json("agents/context/regions.json")
    features = load_json("agents/context/features.json")

    # Load test case
    test = load_yaml(yaml_file)

    # Validate regions
    for region in test["metadata"]["regions"]:
        if region not in regions["regions"]:
            errors.append(f"Invalid region: {region}")

    # Validate feature availability
    feature = test["metadata"]["feature"]
    if feature in features["features"]:
        feature_regions = features["features"][feature]["regions"]
        for region in test["metadata"]["regions"]:
            if region not in feature_regions:
                errors.append(
                    f"Feature '{feature}' not available in region '{region}'"
                )

    return errors
```

**Usage**:
```bash
# Validate single test case
python scripts/validate_context.py test-cases/tesla-pricing/TC001.yml

# Validate all test cases
python scripts/validate_context.py test-cases/**/*.yml

# Run in CI/CD
pre-commit hook: validate_context.py
```

---

## Context Evolution

### Adding a New Region

**Steps**:
1. Update `regions.json`
2. Update `region_codes.md` documentation
3. Add to Testmo (create project if needed)
4. Update existing test cases (if applicable)
5. Document region-specific behavior

**Example - Adding Europe**:
```json
"NEU": {
  "name": "Nissan Europe",
  "code": "NEU",
  "country": "European Union",
  "country_code": "EU",
  "brands": ["Nissan"],
  "languages": ["en-GB", "de-DE", "fr-FR", "es-ES"],
  "currency": "EUR",
  "testmo_project_id": 9,
  "active": true
}
```

### Adding a New Feature

**Steps**:
1. Add to `features.json`
2. Specify regions, brands, platforms
3. Document dependencies (APIs, feature flags)
4. Create test folder
5. Link to Testmo folder

**Example - Adding Subscription Management**:
```json
"subscription-management": {
  "name": "Subscription Management",
  "description": "Manage vehicle subscriptions",
  "regions": ["NNA", "NCI"],
  "brands": ["Nissan", "Infiniti"],
  "platforms": ["iOS", "Android"],
  "feature_flags": ["EnableSubscriptions"],
  "dependencies": {
    "api_endpoints": ["/subscriptions", "/payment"],
    "payment_provider": "Stripe"
  },
  "test_folder": "test-cases/subscriptions",
  "testmo_folder_id": 7250,
  "priority": "high",
  "status": "beta"
}
```

---

## Best Practices

### 1. Always Specify Regions

**❌ Bad** (Implicit):
```yaml
metadata:
  name: "Remote Start"
  # Missing regions - ambiguous
```

**✅ Good** (Explicit):
```yaml
metadata:
  name: "Remote Start"
  regions: [NNA, NCI, NMEX, NBA]  # Available everywhere
```

### 2. Document Regional Differences

**❌ Bad** (Hidden):
```yaml
# Test case doesn't mention that behavior differs in Mexico
```

**✅ Good** (Explicit):
```yaml
regional_variations:
  NMEX:
    - step: 2
      note: "Spanish UI: 'Iniciar Motor' instead of 'Start Engine'"
  NBA:
    - step: 2
      note: "Portuguese UI: 'Iniciar Motor' instead of 'Start Engine'"
```

### 3. Validate Brand Availability

**❌ Bad** (Invalid):
```yaml
metadata:
  name: "Infiniti Offers"
  regions: [NNA, NCI, NMEX, NBA]  # NBA doesn't have Infiniti!
```

**✅ Good** (Valid):
```yaml
metadata:
  name: "Infiniti Offers"
  regions: [NNA, NCI, NMEX]  # Exclude NBA
```

### 4. Use Context for Defaults

**Pattern**:
```yaml
# If feature applies to all regions, specify explicitly
regions: [NNA, NCI, NMEX, NBA]

# If feature is region-specific, document why
regions: [NNA]  # Tesla Superchargers only in USA
```

---

## Integration with AI Agents

### Agent Prompt Enhancement

**Before Context**:
```
Create a test case for Remote Start feature.
```

**With Context**:
```
Create a test case for Remote Start feature.

Context:
- Feature: remote-services
- Available regions: NNA, NCI, NMEX, NBA (all)
- Brands: Nissan, Infiniti
- Platforms: iOS, Android
- Feature flags: EnableRemoteStart
- Dependencies: Telematics subscription required

Use regions: [NNA, NCI, NMEX, NBA] in metadata.
Consider language variations for NMEX and NBA.
```

### Validation Hooks

**Pre-Commit Hook**:
```bash
#!/bin/bash
# .git/hooks/pre-commit

# Validate context in modified test cases
for file in $(git diff --cached --name-only | grep '\.yml$'); do
  python scripts/validate_context.py "$file"
  if [ $? -ne 0 ]; then
    echo "Context validation failed for $file"
    exit 1
  fi
done
```

---

## Future Enhancements

### 1. Context API

**Endpoint**: `/api/context`

```javascript
// Query available regions
GET /api/context/regions
→ { "regions": ["NNA", "NCI", "NMEX", "NBA"] }

// Query feature availability
GET /api/context/features/tesla-pricing
→ {
    "regions": ["NNA"],
    "brands": ["Nissan"],
    "platforms": ["iOS", "Android"]
  }

// Validate test case
POST /api/context/validate
Body: { test_case: {...} }
→ { "valid": true, "errors": [] }
```

### 2. Context Dashboard

**UI Features**:
- View all regions and their features
- See feature availability matrix
- Validate test cases in bulk
- Track context changes over time

### 3. Automated Context Updates

**Goal**: Keep context in sync with production.

**Sources**:
- Feature flags (LaunchDarkly)
- API schemas (GraphQL introspection)
- App versions (App Store / Play Store)
- Testmo projects (API sync)

---

## Conclusion

The context system provides AI agents with the knowledge they need to make informed decisions about test case creation and management. By encoding business rules, regional differences, and feature availability as machine-readable data, we enable:

- **Consistent test case metadata** across the repository
- **Automatic validation** of regional and brand availability
- **Intelligent test generation** by AI agents
- **Single source of truth** for product context

As the system evolves from documentation (`*.md`) to structured data (`*.json`), we'll unlock more powerful validation, automation, and integration capabilities.
