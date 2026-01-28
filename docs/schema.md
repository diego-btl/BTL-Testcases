# Test Case YAML Schema

## Standard Format

Every test case follows this YAML structure:

```yaml
metadata:
  id: string                    # Unique identifier (e.g., TC010)
  name: string                  # Test case name
  feature: string               # Feature category
  priority: enum                # critical, high, medium, low
  platforms: list               # [iOS, Android] or both
  regions: list                 # [USA, Canada, Mexico, Brazil]
  tags: list                    # [smoke, regression, critical-path, etc.]
  created: date                 # YYYY-MM-DD
  updated: date                 # YYYY-MM-DD
  author: string                # Author username
  testmo_id: integer            # Testmo case ID (auto-populated)
  
preconditions:
  - description: string         # Precondition description
    automation_id: string       # Optional automation reference
    
steps:
  - id: integer                 # Step number
    action: string              # What to do
    expected: string            # Expected result
    element:                    # Optional UI element info
      id: string
      ios_identifier: string
      android_identifier: string
      figma_link: string
    api_call:                   # Optional API info
      mutation: string
      query: string
    timeout: string             # Optional timeout (e.g., "30s")

regional_variations:           # Optional regional differences
  [region]:
    - step: integer
      note: string
      
automation:
  framework: string             # maestro, restassured, etc.
  test_file: string             # Path to automation file
  coverage: enum                # full, partial, none
  
traceability:
  clickup_task: string          # ClickUp URL
  user_story: string            # JIRA/story reference
  figma_link: string            # Figma design link

change_log:
  - date: date
    author: string
    change: string
```

## Field Validations

- **priority**: Must be one of: critical, high, medium, low
- **platforms**: Must include iOS, Android, or both
- **regions**: Must be from: USA, Canada, Mexico, Brazil
- **automation.coverage**: Must be: full, partial, none
- **steps**: Must have at least 1 step
- **id**: Must be unique across all test cases

## Example

See `examples/TC001-example.yml` for a complete example.
