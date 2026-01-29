"""
Test Case Creator

Creates test case YAML files following BTL standards with AI assistance.

Features:
- Loads agent rules from agents/rules/
- Finds similar test cases for templates
- Generates sequential test IDs (TC001, TC002, etc.)
- Creates YAML files in correct folder structure
- Handles all BTL naming and formatting conventions
"""

import os
import re
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime


class TestCaseCreator:
    """
    Creates test case YAML files following BTL standards.

    Attributes:
        base_dir: Root directory of the repository
        test_cases_dir: Directory containing all test cases
        rules_dir: Directory containing agent rules
        rules: Loaded agent rules from markdown files
    """

    def __init__(self, base_dir: Optional[str] = None):
        """
        Initialize the test case creator.

        Args:
            base_dir: Root directory of the repository (defaults to current dir)
        """
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()
        self.test_cases_dir = self.base_dir / "test-cases"
        self.rules_dir = self.base_dir / "agents" / "rules"
        self.rules = self.load_rules()

    def load_rules(self) -> Dict[str, str]:
        """
        Load all agent rules from markdown files in agents/rules/.

        Returns:
            Dictionary mapping rule names to their content
        """
        rules = {}

        if not self.rules_dir.exists():
            return rules

        for rule_file in self.rules_dir.glob("*.md"):
            rule_name = rule_file.stem
            with open(rule_file, 'r', encoding='utf-8') as f:
                rules[rule_name] = f.read()

        return rules

    def get_rules_text(self) -> str:
        """
        Get all rules as formatted text for AI context.

        Returns:
            Formatted string containing all rules
        """
        if not self.rules:
            return "No rules loaded."

        sections = []
        for rule_name, content in self.rules.items():
            sections.append(f"# {rule_name.replace('_', ' ').title()}\n\n{content}")

        return "\n\n" + "="*80 + "\n\n".join(sections)

    def find_similar_tests(self, feature: str, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Find similar test cases in the same feature folder for templates.

        Args:
            feature: Feature folder name (e.g., "tesla-pricing")
            limit: Maximum number of examples to return

        Returns:
            List of test case dictionaries
        """
        feature_dir = self.test_cases_dir / feature

        if not feature_dir.exists():
            return []

        similar_tests = []

        for yaml_file in sorted(feature_dir.glob("TC*.yml"))[:limit]:
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    test_data = yaml.safe_load(f)
                    test_data['_filename'] = yaml_file.name
                    similar_tests.append(test_data)
            except Exception as e:
                print(f"Warning: Could not load {yaml_file}: {e}")
                continue

        return similar_tests

    def get_next_test_id(self, feature: str) -> str:
        """
        Generate the next sequential test ID for a feature.

        Args:
            feature: Feature folder name (e.g., "tesla-pricing")

        Returns:
            Next test ID (e.g., "TC001", "TC002")
        """
        feature_dir = self.test_cases_dir / feature

        if not feature_dir.exists():
            return "TC001"

        # Find all existing TC numbers
        tc_numbers = []
        for yaml_file in feature_dir.glob("TC*.yml"):
            match = re.match(r'TC(\d+)', yaml_file.stem)
            if match:
                tc_numbers.append(int(match.group(1)))

        if not tc_numbers:
            return "TC001"

        next_num = max(tc_numbers) + 1
        return f"TC{next_num:03d}"

    def slugify(self, text: str) -> str:
        """
        Convert text to kebab-case slug for filenames.

        Args:
            text: Text to slugify

        Returns:
            Kebab-case slug
        """
        # Convert to lowercase
        text = text.lower()
        # Replace spaces and underscores with hyphens
        text = re.sub(r'[\s_]+', '-', text)
        # Remove non-alphanumeric characters except hyphens
        text = re.sub(r'[^a-z0-9-]', '', text)
        # Remove multiple consecutive hyphens
        text = re.sub(r'-+', '-', text)
        # Strip hyphens from edges
        text = text.strip('-')
        return text

    def create_test_case(
        self,
        feature: str,
        name: str,
        description: str,
        preconditions: List[str],
        steps: List[Dict[str, str]],
        clickup_task_id: Optional[str] = None,
        priority: str = "medium",
        platforms: Optional[List[str]] = None,
        regions: Optional[List[str]] = None,
        notes: Optional[str] = None,
        filename_slug: Optional[str] = None
    ) -> Path:
        """
        Create a new test case YAML file.

        Args:
            feature: Feature folder name (e.g., "tesla-pricing")
            name: Test case name
            description: Test case description
            preconditions: List of precondition descriptions
            steps: List of step dictionaries with 'action' and 'expected' keys
            clickup_task_id: ClickUp task ID reference
            priority: Priority level (critical, high, medium, low)
            platforms: Target platforms (defaults to ["iOS", "Android"])
            regions: Target regions (defaults to ["USA", "Canada", "Mexico", "Brazil"])
            notes: Optional notes
            filename_slug: Optional custom filename slug (auto-generated if not provided)

        Returns:
            Path to created YAML file
        """
        # Generate test ID
        test_id = self.get_next_test_id(feature)

        # Generate filename
        if not filename_slug:
            filename_slug = self.slugify(name)
        filename = f"{test_id}-{filename_slug}.yml"

        # Ensure feature directory exists
        feature_dir = self.test_cases_dir / feature
        feature_dir.mkdir(parents=True, exist_ok=True)

        # Build test case structure
        test_case = {
            "metadata": {
                "testmo_id": None,
                "id": test_id,
                "name": name,
                "feature": feature,
                "priority": priority,
                "state": "draft",
                "platforms": platforms or ["iOS", "Android"],
                "regions": regions or ["USA", "Canada", "Mexico", "Brazil"],
                "tags": [],
                "custom_references": clickup_task_id,
                "created_at": datetime.now().strftime("%Y-%m-%d")
            },
            "description": description,
            "preconditions": [{"description": pc} for pc in preconditions],
            "steps": [
                {
                    "id": i + 1,
                    "action": step["action"],
                    "expected": step["expected"]
                }
                for i, step in enumerate(steps)
            ]
        }

        if notes:
            test_case["notes"] = notes

        # Write YAML file
        file_path = feature_dir / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(test_case, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

        return file_path

    def get_context_for_ai(self, feature: Optional[str] = None) -> str:
        """
        Get complete context for AI agent to create test cases.

        Args:
            feature: Optional feature to get similar tests from

        Returns:
            Formatted context string with rules and examples
        """
        context = []

        # Add rules
        context.append("# BTL Test Case Creation Rules\n")
        context.append(self.get_rules_text())

        # Add similar tests if feature specified
        if feature:
            similar = self.find_similar_tests(feature)
            if similar:
                context.append("\n\n# Example Test Cases from Same Feature\n")
                for i, test in enumerate(similar, 1):
                    context.append(f"\n## Example {i}: {test.get('metadata', {}).get('name', 'Unknown')}\n")
                    context.append(f"Filename: {test.get('_filename', 'Unknown')}\n")
                    context.append("```yaml\n")
                    # Remove _filename before dumping
                    test_copy = {k: v for k, v in test.items() if k != '_filename'}
                    context.append(yaml.dump(test_copy, default_flow_style=False, sort_keys=False))
                    context.append("```\n")

            # Add next test ID
            next_id = self.get_next_test_id(feature)
            context.append(f"\n# Next Test ID for '{feature}': {next_id}\n")

        return "".join(context)


# Convenience functions for direct use
def create_test_case(*args, **kwargs) -> Path:
    """Convenience function to create a test case without instantiating class."""
    creator = TestCaseCreator()
    return creator.create_test_case(*args, **kwargs)


def get_context(feature: Optional[str] = None) -> str:
    """Convenience function to get AI context without instantiating class."""
    creator = TestCaseCreator()
    return creator.get_context_for_ai(feature)
