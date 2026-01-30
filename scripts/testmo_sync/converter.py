"""
Format Conversion Module

Converts between Testmo API format and YAML file format.
Handles all field mappings and data transformations.

Based on: docs/YAML_FORMAT.md specification
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import re


class TestmoConverter:
    """Convert between Testmo API format and YAML format."""

    # Field mapping: YAML path -> Testmo API field
    FIELD_MAP = {
        'metadata.name': 'name',
        'metadata.priority': 'custom_priority',
        'metadata.type': 'custom_type',
        'metadata.status': 'state',
        'metadata.estimate': 'estimate',
        'metadata.automation': 'custom_automation',
        'metadata.tags': 'custom_tags',
        'test_case.description': 'description',
        'test_case.preconditions': 'custom_preconditions',
        'test_case.steps': 'custom_steps',
        'test_case.configurations': 'custom_configurations',
        'test_case.notes': 'custom_notes'
    }

    @staticmethod
    def testmo_to_yaml(case: Dict[str, Any], folder_path: str = "",
                      folder_name_ui: str = "") -> Dict[str, Any]:
        """
        Convert Testmo API case format to YAML dictionary.

        Args:
            case: Case data from Testmo API
            folder_path: Local folder path (e.g., "home/charge/v2l")
            folder_name_ui: UI folder name (e.g., "Home / Charge / V2L")

        Returns:
            Dictionary ready to be written as YAML
        """
        yaml_data = {
            'testmo': {
                'case_id': case['id'],
                'folder_id': case.get('folder_id'),
                'project_id': case.get('project_id'),
                'folder_path': folder_path,
                'folder_name_ui': folder_name_ui,
                'created_at': case.get('created_at'),
                'updated_at': case.get('updated_at'),
                'last_sync': datetime.now().isoformat() + 'Z',
                'url': f"https://bethinklabs.testmo.net/repositories/{case.get('project_id')}/cases/{case['id']}"
                # content_hash will be added by hasher
            },
            'metadata': {
                'name': case.get('name', ''),
                'priority': case.get('custom_priority', 'medium'),
                'type': case.get('custom_type', 'functional'),
                'status': case.get('state', 'active'),
                'estimate': case.get('estimate'),
                'automation': case.get('custom_automation', 'no'),
                'tags': case.get('custom_tags', [])
            },
            'test_case': {
                'description': case.get('description', ''),
                'preconditions': case.get('custom_preconditions', ''),
                'steps': case.get('custom_steps', []),
                'configurations': case.get('custom_configurations', []),
                'notes': case.get('custom_notes', '')
            }
        }

        # Remove None values from metadata
        yaml_data['metadata'] = {k: v for k, v in yaml_data['metadata'].items() if v is not None}

        # Remove empty strings from test_case
        yaml_data['test_case'] = {k: v for k, v in yaml_data['test_case'].items()
                                  if v is not None and v != '' and v != []}

        return yaml_data

    @staticmethod
    def yaml_to_testmo(yaml_file: Path) -> Dict[str, Any]:
        """
        Convert YAML file to Testmo API format.

        Args:
            yaml_file: Path to YAML file

        Returns:
            Dictionary ready for Testmo API
        """
        with open(yaml_file, 'r') as f:
            data = yaml.safe_load(f)

        # Extract editable sections
        metadata = data.get('metadata', {})
        test_case = data.get('test_case', {})

        # Convert to Testmo format
        testmo_data = {
            'name': metadata.get('name', ''),
            'custom_priority': metadata.get('priority'),
            'custom_type': metadata.get('type'),
            'state': metadata.get('status'),
            'estimate': metadata.get('estimate'),
            'custom_automation': metadata.get('automation'),
            'custom_tags': metadata.get('tags', []),
            'description': test_case.get('description', ''),
            'custom_preconditions': test_case.get('preconditions', ''),
            'custom_steps': test_case.get('steps', []),
            'custom_configurations': test_case.get('configurations', []),
            'custom_notes': test_case.get('notes', '')
        }

        # Remove None values (don't update fields that weren't set)
        testmo_data = {k: v for k, v in testmo_data.items() if v is not None}

        return testmo_data

    @staticmethod
    def yaml_to_testmo_dict(yaml_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert YAML dictionary to Testmo API format.

        Similar to yaml_to_testmo but works with dictionary instead of file.

        Args:
            yaml_data: YAML data as dictionary

        Returns:
            Dictionary ready for Testmo API
        """
        metadata = yaml_data.get('metadata', {})
        test_case = yaml_data.get('test_case', {})

        testmo_data = {
            'name': metadata.get('name', ''),
            'custom_priority': metadata.get('priority'),
            'custom_type': metadata.get('type'),
            'state': metadata.get('status'),
            'estimate': metadata.get('estimate'),
            'custom_automation': metadata.get('automation'),
            'custom_tags': metadata.get('tags', []),
            'description': test_case.get('description', ''),
            'custom_preconditions': test_case.get('preconditions', ''),
            'custom_steps': test_case.get('steps', []),
            'custom_configurations': test_case.get('configurations', []),
            'custom_notes': test_case.get('notes', '')
        }

        testmo_data = {k: v for k, v in testmo_data.items() if v is not None}

        return testmo_data

    @staticmethod
    def slugify(text: str, max_length: int = 50) -> str:
        """
        Convert text to filename-safe slug.

        Args:
            text: Text to slugify (e.g., "V2L Screen - Set Minimum SoC")
            max_length: Maximum length of slug

        Returns:
            Slug (e.g., "v2l-screen-set-minimum-soc")
        """
        # Convert to lowercase
        slug = text.lower()

        # Replace spaces and special chars with hyphens
        slug = re.sub(r'[^a-z0-9]+', '-', slug)

        # Remove leading/trailing hyphens
        slug = slug.strip('-')

        # Truncate to max length
        if len(slug) > max_length:
            slug = slug[:max_length].rsplit('-', 1)[0]

        return slug

    @staticmethod
    def generate_filename(case_id: int, name: str) -> str:
        """
        Generate filename for a test case.

        Args:
            case_id: Testmo case ID
            name: Case name

        Returns:
            Filename (e.g., "TC66186-v2l-screen-set-minimum-soc.yml")
        """
        slug = TestmoConverter.slugify(name)
        return f"TC{case_id}-{slug}.yml"

    @staticmethod
    def extract_case_id_from_filename(filename: str) -> Optional[int]:
        """
        Extract case ID from filename.

        Args:
            filename: Filename (e.g., "TC66186-v2l-screen.yml")

        Returns:
            Case ID or None if not found
        """
        match = re.match(r'TC(\d+)-', filename)
        if match:
            return int(match.group(1))
        return None


# Example usage
if __name__ == "__main__":
    # Example: Convert Testmo case to YAML
    testmo_case = {
        'id': 66186,
        'name': 'V2L Screen - Set Minimum SoC',
        'folder_id': 7338,
        'project_id': 2,
        'custom_priority': 'medium',
        'custom_tags': ['v2l', 'charge'],
        'description': 'Test V2L screen functionality',
        'custom_steps': [
            {'step': 'Navigate to V2L screen', 'expected': 'Screen loads'}
        ],
        'created_at': '2023-08-01T23:08:19Z',
        'updated_at': '2025-02-06T18:11:36Z'
    }

    yaml_data = TestmoConverter.testmo_to_yaml(
        testmo_case,
        folder_path="home/charge/v2l-vehicle-to-load",
        folder_name_ui="Home / Charge / V2L Vehicle to Load"
    )

    print("YAML Data:")
    print(yaml.dump(yaml_data, default_flow_style=False, sort_keys=False))

    print("\nFilename:")
    print(TestmoConverter.generate_filename(66186, "V2L Screen - Set Minimum SoC"))
