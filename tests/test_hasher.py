"""Unit tests for hasher module."""

import pytest
from pathlib import Path
import yaml
import sys

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from testmo_sync.hasher import ContentHasher


def test_compute_hash(tmp_path):
    """Test hash computation."""
    # Create test YAML file
    yaml_file = tmp_path / "test.yml"
    data = {
        'metadata': {'name': 'Test Case'},
        'test_case': {'description': 'Test description'}
    }
    with open(yaml_file, 'w') as f:
        yaml.dump(data, f)

    # Compute hash
    hash1 = ContentHasher.compute_hash(yaml_file)
    assert hash1.startswith('sha256:')

    # Compute again - should be same
    hash2 = ContentHasher.compute_hash(yaml_file)
    assert hash1 == hash2


def test_hash_ignores_testmo_section(tmp_path):
    """Test that testmo section doesn't affect hash."""
    yaml_file = tmp_path / "test.yml"

    # Version 1: No testmo section
    data1 = {
        'metadata': {'name': 'Test'},
        'test_case': {'description': 'Desc'}
    }
    with open(yaml_file, 'w') as f:
        yaml.dump(data1, f)
    hash1 = ContentHasher.compute_hash(yaml_file)

    # Version 2: With testmo section
    data2 = {
        'testmo': {'case_id': 123, 'folder_id': 456},
        'metadata': {'name': 'Test'},
        'test_case': {'description': 'Desc'}
    }
    with open(yaml_file, 'w') as f:
        yaml.dump(data2, f)
    hash2 = ContentHasher.compute_hash(yaml_file)

    # Hashes should be identical
    assert hash1 == hash2
