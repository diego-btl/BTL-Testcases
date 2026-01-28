#!/usr/bin/env python3
"""
Validate test case YAML files against JSON Schema
"""
import sys
import yaml
import json
from datetime import date, datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import click
from rich.console import Console
from rich.table import Table
from jsonschema import validate, ValidationError, Draft202012Validator

console = Console()

# Path to JSON Schema
SCHEMA_PATH = Path(__file__).parent.parent / "schemas" / "test-case.schema.json"


def load_schema() -> Dict[str, Any]:
    """Load the JSON Schema"""
    with open(SCHEMA_PATH, 'r') as f:
        return json.load(f)


def convert_dates_to_strings(obj: Any) -> Any:
    """Recursively convert date objects to ISO format strings"""
    if isinstance(obj, (date, datetime)):
        return obj.isoformat() if isinstance(obj, datetime) else obj.strftime("%Y-%m-%d")
    elif isinstance(obj, dict):
        return {k: convert_dates_to_strings(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_dates_to_strings(item) for item in obj]
    return obj


def validate_test_case(case: Dict[str, Any], schema: Dict[str, Any], filepath: Path) -> List[str]:
    """Validate a single test case against schema, return list of errors"""
    errors = []

    # Convert date objects to strings for JSON Schema validation
    case_normalized = convert_dates_to_strings(case)

    # JSON Schema validation
    validator = Draft202012Validator(schema)
    for error in validator.iter_errors(case_normalized):
        # Format the error path
        path = ".".join(str(p) for p in error.absolute_path) if error.absolute_path else "root"
        errors.append(f"{path}: {error.message}")

    # Additional custom validations
    errors.extend(custom_validations(case, filepath))

    return errors


def custom_validations(case: Dict[str, Any], filepath: Path) -> List[str]:
    """Additional validations beyond JSON Schema"""
    errors = []

    metadata = case.get("metadata", {})
    steps = case.get("steps", [])

    # Validate step IDs are sequential
    if steps:
        step_ids = [s.get("id") for s in steps if isinstance(s, dict)]
        expected_ids = list(range(1, len(step_ids) + 1))
        if step_ids != expected_ids:
            errors.append(f"Step IDs should be sequential starting from 1. Found: {step_ids}")

    # Validate filename matches ID
    expected_prefix = metadata.get("id", "").lower()
    if expected_prefix and not filepath.stem.lower().startswith(expected_prefix.lower()):
        errors.append(f"Filename should start with test case ID '{expected_prefix}'")

    # Validate regional variations reference valid steps
    regional_variations = case.get("regional_variations", {})
    valid_step_ids = {s.get("id") for s in steps if isinstance(s, dict)}

    for region, variations in regional_variations.items():
        if region not in ["USA", "Canada", "Mexico", "Brazil"]:
            errors.append(f"Invalid region in regional_variations: {region}")

        if isinstance(variations, list):
            for var in variations:
                if isinstance(var, dict) and var.get("step") not in valid_step_ids:
                    errors.append(f"Regional variation references non-existent step {var.get('step')}")

    # Validate automation test_file path format
    automation = case.get("automation", {})
    test_file = automation.get("test_file", "")
    if test_file and not test_file.startswith("tests/"):
        errors.append(f"automation.test_file should start with 'tests/'. Found: {test_file}")

    # Validate dates are in correct order
    created = metadata.get("created")
    updated = metadata.get("updated")
    # Convert to strings if they are date objects for comparison
    if isinstance(created, date):
        created = created.isoformat()
    if isinstance(updated, date):
        updated = updated.isoformat()
    if created and updated and created > updated:
        errors.append(f"Created date ({created}) cannot be after updated date ({updated})")

    return errors


def check_duplicate_ids(yaml_cases: List[Dict[str, Any]]) -> List[str]:
    """Check for duplicate test case IDs across all files"""
    errors = []
    seen_ids = {}

    for case_data in yaml_cases:
        case = case_data.get("case", {})
        filepath = case_data.get("filepath")
        test_id = case.get("metadata", {}).get("id")

        if test_id:
            if test_id in seen_ids:
                errors.append(f"Duplicate ID '{test_id}' found in {filepath} and {seen_ids[test_id]}")
            else:
                seen_ids[test_id] = filepath

    return errors


@click.command()
@click.option("--input-dir", type=Path, default="test-cases", help="Directory to validate")
@click.option("--strict", is_flag=True, help="Fail on any errors (exit code 1)")
@click.option("--format", "output_format", type=click.Choice(["table", "json", "summary"]), default="table", help="Output format")
@click.option("--file", "single_file", type=Path, help="Validate a single file")
def validate_yaml(input_dir: Path, strict: bool, output_format: str, single_file: Optional[Path]):
    """Validate test case YAML files against schema"""

    console.print("\n[bold blue]YAML Validation Tool[/bold blue]")
    console.print("=" * 50)

    # Load schema
    try:
        schema = load_schema()
        console.print(f"[green]✓[/green] Loaded schema from {SCHEMA_PATH}")
    except FileNotFoundError:
        console.print(f"[red]Error: Schema file not found at {SCHEMA_PATH}[/red]")
        sys.exit(1)
    except json.JSONDecodeError as e:
        console.print(f"[red]Error: Invalid JSON schema: {e}[/red]")
        sys.exit(1)

    # Find files to validate
    if single_file:
        if not single_file.exists():
            console.print(f"[red]Error: File {single_file} does not exist[/red]")
            sys.exit(1)
        yaml_files = [single_file]
    else:
        if not input_dir.exists():
            console.print(f"[red]Error: Directory {input_dir} does not exist[/red]")
            sys.exit(1)
        yaml_files = list(input_dir.rglob("*.yml")) + list(input_dir.rglob("*.yaml"))

    console.print(f"Found {len(yaml_files)} YAML files to validate\n")

    results = []
    all_cases = []
    total_errors = 0

    for yaml_file in yaml_files:
        try:
            with open(yaml_file, 'r') as f:
                case = yaml.safe_load(f)

            if not case:
                results.append({
                    "file": str(yaml_file.relative_to(input_dir) if not single_file else yaml_file),
                    "status": "error",
                    "errors": ["Empty file"]
                })
                total_errors += 1
                continue

            all_cases.append({"case": case, "filepath": yaml_file})
            errors = validate_test_case(case, schema, yaml_file)

            if errors:
                results.append({
                    "file": str(yaml_file.relative_to(input_dir) if not single_file else yaml_file),
                    "status": "error",
                    "errors": errors
                })
                total_errors += len(errors)
            else:
                results.append({
                    "file": str(yaml_file.relative_to(input_dir) if not single_file else yaml_file),
                    "status": "valid",
                    "errors": []
                })

        except yaml.YAMLError as e:
            results.append({
                "file": str(yaml_file.relative_to(input_dir) if not single_file else yaml_file),
                "status": "error",
                "errors": [f"YAML parse error: {e}"]
            })
            total_errors += 1
        except Exception as e:
            results.append({
                "file": str(yaml_file.relative_to(input_dir) if not single_file else yaml_file),
                "status": "error",
                "errors": [f"Unexpected error: {e}"]
            })
            total_errors += 1

    # Check for duplicate IDs
    duplicate_errors = check_duplicate_ids(all_cases)
    if duplicate_errors:
        for err in duplicate_errors:
            console.print(f"[red]Global Error: {err}[/red]")
        total_errors += len(duplicate_errors)

    # Output results
    if output_format == "json":
        output_json(results, duplicate_errors, total_errors)
    elif output_format == "summary":
        output_summary(results, total_errors)
    else:
        output_table(results)

    # Summary
    valid_count = sum(1 for r in results if r["status"] == "valid")
    invalid_count = sum(1 for r in results if r["status"] == "error")

    console.print(f"\n[bold]Summary:[/bold]")
    console.print(f"  Total files: {len(results)}")
    console.print(f"  Valid: [green]{valid_count}[/green]")
    console.print(f"  Invalid: [red]{invalid_count}[/red]")
    console.print(f"  Total errors: {total_errors}")

    if total_errors > 0:
        console.print(f"\n[red]Validation failed with {total_errors} errors[/red]")
        if strict:
            sys.exit(1)
    else:
        console.print(f"\n[green]✓ All files valid![/green]")


def output_table(results: List[Dict[str, Any]]):
    """Output results as a table"""
    table = Table(title="Validation Results")
    table.add_column("Status", style="cyan", width=8)
    table.add_column("File", style="magenta")
    table.add_column("Errors", style="red", overflow="fold")

    for result in results:
        status = "✅" if result["status"] == "valid" else "❌"
        error_text = "\n".join(result["errors"]) if result["errors"] else ""
        table.add_row(status, result["file"], error_text)

    console.print(table)


def output_json(results: List[Dict[str, Any]], global_errors: List[str], total_errors: int):
    """Output results as JSON"""
    output = {
        "total_files": len(results),
        "valid_count": sum(1 for r in results if r["status"] == "valid"),
        "invalid_count": sum(1 for r in results if r["status"] == "error"),
        "total_errors": total_errors,
        "global_errors": global_errors,
        "files": results
    }
    console.print(json.dumps(output, indent=2))


def output_summary(results: List[Dict[str, Any]], total_errors: int):
    """Output brief summary only"""
    valid = sum(1 for r in results if r["status"] == "valid")
    invalid = sum(1 for r in results if r["status"] == "error")

    if invalid > 0:
        console.print(f"[red]FAILED[/red]: {invalid}/{len(results)} files invalid ({total_errors} errors)")
        for result in results:
            if result["status"] == "error":
                console.print(f"  - {result['file']}")
    else:
        console.print(f"[green]PASSED[/green]: {valid}/{len(results)} files valid")


if __name__ == "__main__":
    validate_yaml()
