# BTL Test Case Agent Framework

AI-powered test case creation and management for BTL/Nissan OneApp QA.

## Overview

This agent framework enables Claude Code to create test cases following BTL standards by providing:
- **Rules**: Comprehensive guidelines for test case format and content
- **Templates**: Example test cases from similar features
- **Tools**: Python classes for test case creation and workflow orchestration

## Quick Start

### For Claude Code Users

Ask Claude to read the rules and create a test case:

```
Claude, please read the test case creation rules and create a test case
for Tesla Pricing feature based on ClickUp task 86b7uey05
```

Claude will:
1. Load all rules from `agents/rules/`
2. Find similar test cases for templates
3. Generate next sequential test ID
4. Create YAML file following BTL standards

### For Python Developers

```python
from agents import TestCaseCreator, WorkflowOrchestrator

# Get context for AI
orchestrator = WorkflowOrchestrator()
context = orchestrator.get_context(feature="tesla-pricing")
print(context)

# Create a test case
creator = TestCaseCreator()
file_path = creator.create_test_case(
    feature="tesla-pricing",
    name="Tesla Pricing - Max Charge Limit",
    description="Verify that user can view max charge limit...",
    preconditions=["User is on Charge screen"],
    steps=[
        {"action": "Tap on max charge slider", "expected": "Slider responds to touch"},
        {"action": "Adjust to 90%", "expected": "Limit updates to 90%"}
    ],
    clickup_task_id="86b7uey05"
)
print(f"Created: {file_path}")
```

## Architecture

```
agents/
├── __init__.py                  # Package initialization
├── test_case_creator.py         # Test case creation logic
├── workflow_orchestrator.py     # Multi-step workflows
├── rules/                       # Agent rules (markdown)
│   ├── output_rules.md          # Output format rules
│   ├── preconditions_guide.md   # Preconditions writing guide
│   └── naming_conventions.md    # Naming standards
└── README.md                    # This file
```

## Components

### TestCaseCreator

Creates test case YAML files following BTL standards.

**Key methods:**
- `load_rules()` - Load all markdown rules
- `find_similar_tests(feature)` - Find template tests
- `get_next_test_id(feature)` - Sequential ID generation
- `create_test_case()` - Main creation method
- `get_context_for_ai()` - Get rules and examples for AI

### WorkflowOrchestrator

Coordinates multi-step workflows.

**Key methods:**
- `get_context(feature)` - Get all rules and context for AI
- `create_from_clickup()` - ClickUp → YAML workflow
- `validate_test_case()` - Run YAML validation
- `git_commit()` - Commit files to Git
- `import_to_testmo()` - Import to Testmo
- `export_from_testmo()` - Export from Testmo

## Rules

All rules are in markdown format in `agents/rules/`:

### output_rules.md
- File structure and naming
- Metadata requirements
- Description format
- Preconditions format
- Steps format
- ClickUp integration
- Complete example

### preconditions_guide.md
- Purpose of preconditions
- Patterns and templates
- User/system/data state patterns
- Common mistakes to avoid
- Examples by feature

### naming_conventions.md
- Test ID format (TC001, TC002...)
- Filename format (kebab-case)
- Feature folder naming
- Test name format
- ClickUp reference format

## Workflows

### Create Test from ClickUp

1. **Read ClickUp task** (manual or via MCP)
2. **Get context** with rules and similar tests
3. **Create YAML file** using TestCaseCreator
4. **Validate** using yaml_converter.py
5. **Commit to Git** with clear message
6. **Import to Testmo** (optional)
7. **Sync testmo_id** back to Git

### Export from Testmo

1. **Export folder** to YAML files
2. **Validate** all exported files
3. **Commit to Git** as backup

### Batch Update

1. **Modify YAMLs** in Git
2. **Validate changes**
3. **Commit to Git**
4. **Re-import to Testmo** with new folder name
5. **Manual cleanup** in Testmo UI (delete old folder, rename new)

## Usage Examples

### Example 1: Get Context for AI

```python
from agents import get_context

# Get context for Tesla Pricing feature
context = get_context(feature="tesla-pricing")

# Context includes:
# - All rules from agents/rules/
# - Similar test cases from test-cases/tesla-pricing/
# - Next test ID (TC001, TC002, etc.)
```

### Example 2: Create Test Case

```python
from agents import TestCaseCreator

creator = TestCaseCreator()

# Create test case
file_path = creator.create_test_case(
    feature="tesla-pricing",
    name="Tesla Pricing - Pricing Breakdown Modal",
    description="Verify that user can view detailed pricing breakdown...",
    preconditions=[
        "User is on Charge screen",
        "Feature flag 'EnableTeslaPricing' is enabled",
        "User has selected a Tesla charging station"
    ],
    steps=[
        {
            "action": "Tap on pricing information icon",
            "expected": "Pricing breakdown modal appears"
        },
        {
            "action": "Review pricing details",
            "expected": "Base rate is displayed | Fees are shown | Total cost is calculated"
        },
        {
            "action": "Tap Close button",
            "expected": "Modal closes | User returns to station details"
        }
    ],
    clickup_task_id="86b7uey05",
    priority="high"
)

print(f"✅ Created: {file_path}")
# Output: ✅ Created: test-cases/tesla-pricing/TC001-pricing-breakdown-modal.yml
```

### Example 3: Complete Workflow

```python
from agents import WorkflowOrchestrator

orchestrator = WorkflowOrchestrator()

# Create test case
result = orchestrator.create_from_clickup(
    clickup_task_id="86b7uey05",
    feature="tesla-pricing",
    name="Tesla Pricing - Max Charge Limit",
    description="Verify that user can adjust max charge limit...",
    preconditions=["User is on Charge screen"],
    steps=[
        {"action": "Tap max charge slider", "expected": "Slider active"},
        {"action": "Adjust to 90%", "expected": "Limit updates to 90%"}
    ],
    priority="high"
)

# Result includes:
# - test_case_path: Path to YAML file
# - test_id: TC001
# - clickup_task_id: 86b7uey05

# Validate
validation = orchestrator.validate_test_case(result['test_case_path'])
if validation['success']:
    print("✅ Validation passed")

# Commit to Git
commit = orchestrator.git_commit(
    files=[result['test_case_path']],
    message=f"Create: {result['test_id']} for ClickUp task {result['clickup_task_id']}"
)
if commit['success']:
    print(f"✅ Committed: {commit['commit_hash']}")
```

## Claude Code Integration

When using with Claude Code, the agent can:

1. **Read all rules** from `agents/rules/`
2. **Find similar tests** in the target feature folder
3. **Generate next test ID** automatically
4. **Create YAML file** following all BTL standards
5. **Validate** the created file
6. **Suggest Git commit** message

### Example Conversation

```
User: Create a test case for Tesla Pricing max charge limit
feature based on ClickUp task 86b7uey05

Claude: I'll create a test case following BTL standards.

[Claude reads rules and similar tests]

I've created test-cases/tesla-pricing/TC001-max-charge-limit.yml

The test includes:
- ID: TC001 (first test in tesla-pricing folder)
- Proper metadata with ClickUp reference
- Clear description starting with "Verify that"
- Minimal preconditions (3 items)
- 3 steps with clear actions and expectations

Would you like me to:
1. Validate the YAML file?
2. Create a Git commit?
3. Show you the file contents?
```

## Best Practices

### For AI Agents (Claude)

1. **Always read rules** before creating test cases
2. **Find similar tests** for templates and patterns
3. **Use next sequential ID** for the feature
4. **Validate** before committing
5. **Include ClickUp reference** in metadata
6. **Follow BTL naming conventions** exactly

### For Developers

1. **Use provided classes** instead of manual YAML writing
2. **Validate all test cases** before committing
3. **Keep rules updated** as standards evolve
4. **Add examples** to rules for clarity
5. **Test the agent** with real ClickUp tasks

## Extending the Framework

### Adding New Rules

1. Create markdown file in `agents/rules/`
2. Follow existing format (headings, examples, checklists)
3. Update this README with new rule description
4. Test with Claude Code to ensure it's readable

### Adding New Features

1. Add method to TestCaseCreator or WorkflowOrchestrator
2. Document in docstring
3. Add example to this README
4. Test with real workflow

## Troubleshooting

### Issue: Rules not loading

**Check:**
- Rules directory exists: `agents/rules/`
- Files are `.md` format
- Files are UTF-8 encoded

### Issue: Test ID conflicts

**Check:**
- Sequential numbering within folder
- No gaps in sequence
- Use `get_next_test_id()` method

### Issue: YAML validation fails

**Check:**
- All required metadata fields present
- Steps have id, action, expected
- Preconditions use correct format
- Description not empty

## Support

- **Documentation**: See `/docs/` folder
- **Examples**: See `test-cases/examples/`
- **Issues**: Check `API_FINDINGS.md` for known limitations

## Status

✅ **Production Ready**

Framework is tested and ready for:
- Creating test cases from ClickUp tasks
- AI-assisted test case generation
- Full Git-first workflow
- Testmo synchronization

---

**Version**: 1.0.0
**Last Updated**: January 28, 2026
**Maintainer**: Diego Garcia (QA Engineering Manager)
