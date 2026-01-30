#!/usr/bin/env python3
"""
Export test cases from Testmo using REST API + testmo_sync modules.
This script implements the export workflow using the framework modules.
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Any
import requests
from dotenv import load_dotenv

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent))

from testmo_sync.converter import TestmoConverter
from testmo_sync.hasher import ContentHasher
from testmo_sync.mapper import FolderMapper

# Load environment variables
load_dotenv()

TESTMO_URL = os.getenv("TESTMO_URL", "").rstrip("/")
TESTMO_API_KEY = os.getenv("TESTMO_API_KEY")


class TestmoAPI:
    """Simple REST API client for Testmo."""

    def __init__(self):
        self.base_url = TESTMO_URL
        self.headers = {
            "Authorization": f"Bearer {TESTMO_API_KEY}",
            "Content-Type": "application/json"
        }

    def list_folders(self, project_id: int) -> List[Dict[str, Any]]:
        """List all folders with pagination."""
        all_folders = []
        page = 1

        while True:
            url = f"{self.base_url}/api/v1/projects/{project_id}/folders?page={page}"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()

            data = response.json()
            folders = data.get("result", [])
            all_folders.extend(folders)

            if not data.get("next_page"):
                break
            page = data["next_page"]

        return all_folders

    def list_cases(self, project_id: int) -> List[Dict[str, Any]]:
        """List all test cases with pagination."""
        all_cases = []
        page = 1

        while True:
            url = f"{self.base_url}/api/v1/projects/{project_id}/cases?page={page}&per_page=100"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()

            data = response.json()
            cases = data.get("result", [])
            all_cases.extend(cases)

            if not data.get("next_page"):
                break
            page = data["next_page"]

        return all_cases

    def get_project(self, project_id: int) -> Dict[str, Any]:
        """Get project details."""
        url = f"{self.base_url}/api/v1/projects/{project_id}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json().get("result", {})


def build_folder_map(folders: List[Dict[str, Any]]) -> Dict[int, Dict[str, Any]]:
    """Build folder ID to folder info map with paths."""
    folder_map = {}

    # First pass: create map
    for folder in folders:
        folder_map[folder["id"]] = {
            "id": folder["id"],
            "name": folder["name"],
            "parent_id": folder.get("parent_id"),
            "path": "",
            "name_ui": folder["name"]
        }

    # Second pass: build paths
    def get_path(folder_id: int) -> str:
        if folder_id not in folder_map:
            return ""

        folder = folder_map[folder_id]
        if folder["path"]:
            return folder["path"]

        parent_id = folder.get("parent_id")
        if parent_id:
            parent_path = get_path(parent_id)
            folder["path"] = f"{parent_path}/{TestmoConverter.slugify(folder['name'])}"
        else:
            folder["path"] = TestmoConverter.slugify(folder["name"])

        return folder["path"]

    # Compute all paths
    for folder_id in folder_map:
        get_path(folder_id)

    return folder_map


def export_project(project_id: int, output_dir: Path):
    """Export a Testmo project to YAML files."""
    print(f"\n{'='*80}")
    print(f"EXPORTING PROJECT {project_id}")
    print(f"{'='*80}\n")

    api = TestmoAPI()

    # Get project info
    print("📋 Fetching project info...")
    project = api.get_project(project_id)
    print(f"   Project: {project['name']}")

    # Get folders
    print("\n📁 Fetching folders...")
    folders = api.list_folders(project_id)
    print(f"   Found {len(folders)} folders")

    # Build folder map
    print("\n🗺️  Building folder map...")
    folder_map = build_folder_map(folders)

    # Get test cases
    print("\n📝 Fetching test cases...")
    cases = api.list_cases(project_id)
    print(f"   Found {len(cases)} test cases")

    # Create output directories
    test_cases_dir = output_dir / "test-cases"
    sync_dir = output_dir / ".sync"
    sync_dir.mkdir(parents=True, exist_ok=True)

    # Save project metadata
    project_file = sync_dir / "project.json"
    with open(project_file, 'w') as f:
        json.dump({
            "project_id": project_id,
            "name": project["name"],
            "exported_at": project.get("created_at", ""),
            "total_cases": len(cases),
            "total_folders": len(folders)
        }, f, indent=2)
    print(f"\n💾 Saved project metadata: {project_file}")

    # Save folder map
    folder_map_file = sync_dir / "folder-map.json"
    with open(folder_map_file, 'w') as f:
        json.dump(folder_map, f, indent=2)
    print(f"💾 Saved folder map: {folder_map_file}")

    # Convert and write cases
    print(f"\n🔄 Converting and writing {len(cases)} test cases...")
    hasher = ContentHasher()
    case_map = {}

    for i, case in enumerate(cases, 1):
        if i % 100 == 0:
            print(f"   Progress: {i}/{len(cases)} cases...")

        # Get folder info
        folder_id = case.get("folder_id")
        if folder_id and folder_id in folder_map:
            folder_info = folder_map[folder_id]
            folder_path = folder_info["path"]
            folder_name_ui = folder_info["name_ui"]
        else:
            folder_path = "uncategorized"
            folder_name_ui = "Uncategorized"

        # Convert to YAML format
        yaml_data = TestmoConverter.testmo_to_yaml(case, folder_path, folder_name_ui)

        # Generate filename
        case_name_slug = TestmoConverter.slugify(case["name"])
        filename = f"TC{case['id']}-{case_name_slug}.yml"

        # Create folder directory
        case_dir = test_cases_dir / folder_path
        case_dir.mkdir(parents=True, exist_ok=True)

        # Write YAML file
        yaml_file = case_dir / filename
        with open(yaml_file, 'w') as f:
            import yaml
            yaml.dump(yaml_data, f, sort_keys=False, allow_unicode=True)

        # Compute hash
        content_hash = hasher.compute_hash(yaml_file)

        # Track in case map
        case_map[str(case["id"])] = {
            "case_id": case["id"],
            "file_path": str(yaml_file.relative_to(output_dir)),
            "content_hash": content_hash,
            "folder_id": folder_id,
            "name": case["name"]
        }

    # Save case map
    case_map_file = sync_dir / "case-map.json"
    with open(case_map_file, 'w') as f:
        json.dump(case_map, f, indent=2)
    print(f"\n💾 Saved case map: {case_map_file}")

    # Summary
    print(f"\n{'='*80}")
    print(f"EXPORT COMPLETE")
    print(f"{'='*80}")
    print(f"Project: {project['name']} (ID: {project_id})")
    print(f"Folders: {len(folders)}")
    print(f"Test Cases: {len(cases)}")
    print(f"Output: {output_dir}")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python export_project.py <project_id> <output_dir>")
        print("Example: python export_project.py 5 testmo/nba")
        sys.exit(1)

    project_id = int(sys.argv[1])
    output_dir = Path(sys.argv[2])

    export_project(project_id, output_dir)
