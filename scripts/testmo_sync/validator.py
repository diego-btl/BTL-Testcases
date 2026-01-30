"""
YAML Validation Module

Validates test case YAML files against the BTL-TestCases schema.
Checks required sections, field types, and enum values.

Based on: docs/YAML_FORMAT.md specification
"""

import yaml
from pathlib import Path
from typing import Tuple, List, Dict, Any, Optional


class ValidationError:
    """Represents a validation error."""

    def __init__(self, field: str, message: str, severity: str = "error"):
        self.field = field
        self.message = message
        self.severity = severity  # "error" or "warning"

    def __str__(self):
        return f"[{self.severity.upper()}] {self.field}: {self.message}"


class YAMLValidator:
    """Validate test case YAML files."""

    # Valid enum values
    VALID_PRIORITIES = ["low", "medium", "high", "critical"]
    VALID_STATUSES = ["active", "deprecated", "draft"]
    VALID_AUTOMATION = ["yes", "no", "partial"]

    @staticmethod
    def validate_file(yaml_file: Path) -> Tuple[bool, List[ValidationError]]:
        """
        Validate a single YAML file.

        Args:
            yaml_file: Path to YAML file

        Returns:
            Tuple of (is_valid, list of errors)
        """
        errors = []

        # Check file exists
        if not yaml_file.exists():
            errors.append(ValidationError("file", f"File not found: {yaml_file}"))
            return False, errors

        # Parse YAML
        try:
            with open(yaml_file, 'r') as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            errors.append(ValidationError("yaml", f"YAML parsing error: {e}"))
            return False, errors

        if not isinstance(data, dict):
            errors.append(ValidationError("root", "Root must be a dictionary"))
            return False, errors

        # Validate sections
        errors.extend(YAMLValidator._validate_metadata(data.get('metadata')))
        errors.extend(YAMLValidator._validate_test_case(data.get('test_case')))
        errors.extend(YAMLValidator._validate_testmo(data.get('testmo')))

        # Check for errors (not warnings)
        has_errors = any(e.severity == "error" for e in errors)

        return not has_errors, errors

    @staticmethod
    def _validate_metadata(metadata: Any) -> List[ValidationError]:
        """Validate metadata section."""
        errors = []

        if metadata is None:
            errors.append(ValidationError("metadata", "Missing required section"))
            return errors

        if not isinstance(metadata, dict):
            errors.append(ValidationError("metadata", "Must be a dictionary"))
            return errors

        # Validate name (required)
        if 'name' not in metadata:
            errors.append(ValidationError("metadata.name", "Required field missing"))
        elif not isinstance(metadata['name'], str) or not metadata['name'].strip():
            errors.append(ValidationError("metadata.name", "Must be a non-empty string"))

        # Validate priority (optional)
        if 'priority' in metadata:
            if metadata['priority'] not in YAMLValidator.VALID_PRIORITIES:
                errors.append(ValidationError(
                    "metadata.priority",
                    f"Invalid value '{metadata['priority']}'. Must be one of: {YAMLValidator.VALID_PRIORITIES}"
                ))

        # Validate status (optional)
        if 'status' in metadata:
            if metadata['status'] not in YAMLValidator.VALID_STATUSES:
                errors.append(ValidationError(
                    "metadata.status",
                    f"Invalid value '{metadata['status']}'. Must be one of: {YAMLValidator.VALID_STATUSES}"
                ))

        # Validate automation (optional)
        if 'automation' in metadata:
            if metadata['automation'] not in YAMLValidator.VALID_AUTOMATION:
                errors.append(ValidationError(
                    "metadata.automation",
                    f"Invalid value '{metadata['automation']}'. Must be one of: {YAMLValidator.VALID_AUTOMATION}"
                ))

        # Validate tags (optional)
        if 'tags' in metadata:
            if not isinstance(metadata['tags'], list):
                errors.append(ValidationError("metadata.tags", "Must be a list"))
            else:
                for i, tag in enumerate(metadata['tags']):
                    if not isinstance(tag, str):
                        errors.append(ValidationError(f"metadata.tags[{i}]", "Must be a string"))

        # Validate estimate (optional)
        if 'estimate' in metadata:
            if not isinstance(metadata['estimate'], (int, float)) or metadata['estimate'] < 0:
                errors.append(ValidationError("metadata.estimate", "Must be a non-negative number"))

        return errors

    @staticmethod
    def _validate_test_case(test_case: Any) -> List[ValidationError]:
        """Validate test_case section."""
        errors = []

        if test_case is None:
            errors.append(ValidationError("test_case", "Missing required section"))
            return errors

        if not isinstance(test_case, dict):
            errors.append(ValidationError("test_case", "Must be a dictionary"))
            return errors

        # Validate description (optional but recommended)
        if 'description' in test_case:
            if not isinstance(test_case['description'], str):
                errors.append(ValidationError("test_case.description", "Must be a string"))

        # Validate steps (optional but recommended)
        if 'steps' in test_case:
            if not isinstance(test_case['steps'], list):
                errors.append(ValidationError("test_case.steps", "Must be a list"))
            else:
                for i, step in enumerate(test_case['steps']):
                    if not isinstance(step, dict):
                        errors.append(ValidationError(f"test_case.steps[{i}]", "Must be a dictionary"))
                    else:
                        if 'step' not in step:
                            errors.append(ValidationError(f"test_case.steps[{i}].step", "Required field missing"))
                        if 'expected' not in step:
                            errors.append(ValidationError(f"test_case.steps[{i}].expected", "Required field missing"))

        # Validate configurations (optional)
        if 'configurations' in test_case:
            if not isinstance(test_case['configurations'], list):
                errors.append(ValidationError("test_case.configurations", "Must be a list"))
            else:
                for i, config in enumerate(test_case['configurations']):
                    if not isinstance(config, str):
                        errors.append(ValidationError(f"test_case.configurations[{i}]", "Must be a string"))

        return errors

    @staticmethod
    def _validate_testmo(testmo: Any) -> List[ValidationError]:
        """Validate testmo section (warnings only - this is auto-generated)."""
        errors = []

        if testmo is None:
            # testmo section is optional (for new cases)
            return errors

        if not isinstance(testmo, dict):
            errors.append(ValidationError("testmo", "Must be a dictionary", severity="warning"))
            return errors

        # Check for expected fields (warnings only)
        expected_fields = ['case_id', 'folder_id', 'project_id', 'content_hash']
        for field in expected_fields:
            if field not in testmo:
                errors.append(ValidationError(
                    f"testmo.{field}",
                    f"Auto-generated field missing",
                    severity="warning"
                ))

        return errors

    @staticmethod
    def validate_batch(folder: Path) -> Dict[str, Tuple[bool, List[ValidationError]]]:
        """
        Validate all YAML files in a folder.

        Args:
            folder: Path to folder containing YAML files

        Returns:
            Dictionary mapping file paths to (is_valid, errors) tuples
        """
        results = {}

        for yaml_file in folder.rglob("*.yml"):
            is_valid, errors = YAMLValidator.validate_file(yaml_file)
            results[str(yaml_file)] = (is_valid, errors)

        return results

    @staticmethod
    def auto_fix(yaml_file: Path) -> bool:
        """
        Attempt to auto-fix common issues in YAML file.

        Returns:
            True if fixes were applied, False otherwise
        """
        try:
            with open(yaml_file, 'r') as f:
                data = yaml.safe_load(f)

            fixed = False

            # Ensure metadata section exists
            if 'metadata' not in data:
                data['metadata'] = {}
                fixed = True

            # Ensure test_case section exists
            if 'test_case' not in data:
                data['test_case'] = {}
                fixed = True

            # Fix invalid priority
            if 'priority' in data.get('metadata', {}):
                if data['metadata']['priority'] not in YAMLValidator.VALID_PRIORITIES:
                    data['metadata']['priority'] = 'medium'
                    fixed = True

            # Fix tags (ensure it's a list)
            if 'tags' in data.get('metadata', {}):
                if not isinstance(data['metadata']['tags'], list):
                    data['metadata']['tags'] = []
                    fixed = True

            if fixed:
                with open(yaml_file, 'w') as f:
                    yaml.dump(data, f, default_flow_style=False, sort_keys=False)

            return fixed

        except Exception:
            return False


# Example usage
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python validator.py <yaml_file>")
        sys.exit(1)

    yaml_path = Path(sys.argv[1])

    is_valid, errors = YAMLValidator.validate_file(yaml_path)

    if is_valid:
        print(f"✓ {yaml_path} is valid")
    else:
        print(f"✗ {yaml_path} has errors:")
        for error in errors:
            print(f"  {error}")

    sys.exit(0 if is_valid else 1)
