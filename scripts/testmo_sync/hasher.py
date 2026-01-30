"""
Content Hashing Module

Provides SHA-256 hashing of YAML test case files for change detection.
Only hashes editable content (metadata + test_case sections), ignoring
auto-generated testmo metadata.

Based on validation: TESTING_LOG.md - Hash-based change detection
"""

import hashlib
import yaml
from pathlib import Path
from typing import Dict, List, Tuple, Optional


class ContentHasher:
    """Compute and verify content hashes for test case YAML files."""

    @staticmethod
    def compute_hash(yaml_file: Path) -> str:
        """
        Compute SHA-256 hash of editable content in YAML file.

        Only includes:
        - metadata section (editable by users/AI)
        - test_case section (editable by users/AI)

        Excludes:
        - testmo section (auto-generated)

        Args:
            yaml_file: Path to YAML file

        Returns:
            Hash string in format "sha256:abc123..."

        Raises:
            FileNotFoundError: If yaml_file doesn't exist
            yaml.YAMLError: If YAML parsing fails
        """
        if not yaml_file.exists():
            raise FileNotFoundError(f"YAML file not found: {yaml_file}")

        with open(yaml_file, 'r') as f:
            data = yaml.safe_load(f)

        # Extract only editable content
        editable_content = {
            'metadata': data.get('metadata', {}),
            'test_case': data.get('test_case', {})
        }

        # Deterministic serialization (sorted keys)
        content_str = yaml.dump(editable_content, sort_keys=True, default_flow_style=False)

        # Compute SHA-256 hash
        hash_obj = hashlib.sha256(content_str.encode('utf-8'))
        hash_value = hash_obj.hexdigest()

        return f"sha256:{hash_value}"

    @staticmethod
    def needs_sync(yaml_file: Path) -> bool:
        """
        Check if file has changed since last sync by comparing hashes.

        Args:
            yaml_file: Path to YAML file

        Returns:
            True if file has changed (needs sync), False otherwise
        """
        try:
            # Compute current hash
            current_hash = ContentHasher.compute_hash(yaml_file)

            # Read saved hash from YAML
            with open(yaml_file, 'r') as f:
                data = yaml.safe_load(f)

            saved_hash = data.get('testmo', {}).get('content_hash')

            if not saved_hash:
                # No saved hash = new file or needs sync
                return True

            return current_hash != saved_hash

        except Exception as e:
            # On error, assume needs sync
            print(f"Warning: Error checking sync status for {yaml_file}: {e}")
            return True

    @staticmethod
    def batch_check(folder: Path) -> List[Path]:
        """
        Find all YAML files in folder that need sync (have changed).

        Args:
            folder: Path to folder containing YAML files

        Returns:
            List of Path objects for files that need sync
        """
        changed_files = []

        # Find all YAML files recursively
        for yaml_file in folder.rglob("*.yml"):
            if ContentHasher.needs_sync(yaml_file):
                changed_files.append(yaml_file)

        return changed_files

    @staticmethod
    def update_hash_in_file(yaml_file: Path) -> None:
        """
        Compute and update the content_hash in YAML file's testmo section.

        Args:
            yaml_file: Path to YAML file to update
        """
        # Compute new hash
        new_hash = ContentHasher.compute_hash(yaml_file)

        # Read file
        with open(yaml_file, 'r') as f:
            data = yaml.safe_load(f)

        # Update hash in testmo section
        if 'testmo' not in data:
            data['testmo'] = {}

        data['testmo']['content_hash'] = new_hash

        # Write back
        with open(yaml_file, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)


# Example usage
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python hasher.py <yaml_file>")
        sys.exit(1)

    yaml_path = Path(sys.argv[1])

    try:
        hash_value = ContentHasher.compute_hash(yaml_path)
        print(f"Hash: {hash_value}")

        needs_sync = ContentHasher.needs_sync(yaml_path)
        print(f"Needs sync: {needs_sync}")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
