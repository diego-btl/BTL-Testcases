"""Unit tests for converter module."""

import pytest
import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from testmo_sync.converter import TestmoConverter


def test_testmo_to_yaml():
    """Test conversion from Testmo format to YAML."""
    testmo_case = {
        'id': 123,
        'name': 'Test Case',
        'folder_id': 456,
        'project_id': 2,
        'custom_priority': 'high',
        'custom_tags': ['tag1'],
        'description': 'Test description',
        'created_at': '2024-01-01T00:00:00Z'
    }

    yaml_data = TestmoConverter.testmo_to_yaml(testmo_case, "test/folder", "Test / Folder")

    assert yaml_data['testmo']['case_id'] == 123
    assert yaml_data['metadata']['name'] == 'Test Case'
    assert yaml_data['metadata']['priority'] == 'high'
    assert yaml_data['test_case']['description'] == 'Test description'


def test_slugify():
    """Test slugify function."""
    assert TestmoConverter.slugify("V2L Screen - Set Min SoC") == "v2l-screen-set-min-soc"
    assert TestmoConverter.slugify("Test (ABC) 123!") == "test-abc-123"
