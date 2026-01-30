"""Unit tests for validator module."""

import pytest
from pathlib import Path
import yaml
import sys

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from testmo_sync.validator import YAMLValidator


def test_valid_yaml(tmp_path):
    """Test validation of valid YAML."""
    yaml_file = tmp_path / "test.yml"
    data = {
        'metadata': {
            'name': 'Test Case',
            'priority': 'medium',
            'tags': ['tag1', 'tag2']
        },
        'test_case': {
            'description': 'Test',
            'steps': [
                {'step': 'Step 1', 'expected': 'Result 1'}
            ]
        }
    }
    with open(yaml_file, 'w') as f:
        yaml.dump(data, f)

    is_valid, errors = YAMLValidator.validate_file(yaml_file)
    assert is_valid
    assert len(errors) == 0


def test_invalid_priority(tmp_path):
    """Test validation catches invalid priority."""
    yaml_file = tmp_path / "test.yml"
    data = {
        'metadata': {
            'name': 'Test',
            'priority': 'invalid'  # Should be low/medium/high/critical
        },
        'test_case': {}
    }
    with open(yaml_file, 'w') as f:
        yaml.dump(data, f)

    is_valid, errors = YAMLValidator.validate_file(yaml_file)
    assert not is_valid
    assert any('priority' in str(e) for e in errors)
