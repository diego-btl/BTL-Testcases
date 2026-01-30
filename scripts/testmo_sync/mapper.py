"""
Folder Mapping Module

Provides bidirectional mapping between local folder paths and Testmo folder IDs.
Caches mappings in .sync/folder-map.json for fast lookups.

Based on validation: TESTING_LOG.md - 162 folders with hierarchy up to 4 levels
"""

import json
from pathlib import Path
from typing import Dict, Optional, List


class FolderMapper:
    """Bidirectional mapping between folder paths and Testmo folder IDs."""

    def __init__(self, project_dir: Path):
        """
        Initialize mapper and load mappings from .sync/folder-map.json.

        Args:
            project_dir: Path to project directory (e.g., testmo/oneapp)
        """
        self.project_dir = project_dir
        self.sync_dir = project_dir / ".sync"
        self.map_file = self.sync_dir / "folder-map.json"

        # Load mappings
        self.id_to_folder: Dict[int, Dict] = {}  # folder_id -> folder info
        self.path_to_id: Dict[str, int] = {}     # path -> folder_id

        self._load_mappings()

    def _load_mappings(self) -> None:
        """Load mappings from folder-map.json."""
        if not self.map_file.exists():
            # No mappings yet - will be created during export
            return

        with open(self.map_file, 'r') as f:
            data = json.load(f)

        # Build both mappings
        for folder_id_str, folder_info in data.items():
            folder_id = int(folder_id_str)
            self.id_to_folder[folder_id] = folder_info
            self.path_to_id[folder_info['path']] = folder_id

    def save_mappings(self) -> None:
        """Save current mappings to folder-map.json."""
        # Ensure .sync directory exists
        self.sync_dir.mkdir(parents=True, exist_ok=True)

        # Convert to JSON-serializable format (keys must be strings)
        data = {str(folder_id): info for folder_id, info in self.id_to_folder.items()}

        with open(self.map_file, 'w') as f:
            json.dump(data, f, indent=2, sort_keys=True)

    def add_folder(self, folder_id: int, path: str, ui_name: str,
                   parent_id: Optional[int] = None, level: int = 1) -> None:
        """
        Add a folder to the mapping.

        Args:
            folder_id: Testmo folder ID
            path: Local folder path (e.g., "home/charge/v2l")
            ui_name: UI display name (e.g., "Home / Charge / V2L")
            parent_id: Parent folder ID (None for root folders)
            level: Folder depth level (1-4)
        """
        folder_info = {
            'path': path,
            'ui_name': ui_name,
            'parent_id': parent_id,
            'level': level
        }

        self.id_to_folder[folder_id] = folder_info
        self.path_to_id[path] = folder_id

    def get_folder_id(self, path: str) -> Optional[int]:
        """
        Get Testmo folder ID from local path.

        Args:
            path: Local folder path (e.g., "home/charge/v2l")

        Returns:
            Folder ID or None if not found
        """
        return self.path_to_id.get(path)

    def get_folder_path(self, folder_id: int) -> Optional[str]:
        """
        Get local folder path from Testmo folder ID.

        Args:
            folder_id: Testmo folder ID

        Returns:
            Local path or None if not found
        """
        folder_info = self.id_to_folder.get(folder_id)
        return folder_info['path'] if folder_info else None

    def get_folder_ui_name(self, folder_id: int) -> Optional[str]:
        """
        Get UI display name from Testmo folder ID.

        Args:
            folder_id: Testmo folder ID

        Returns:
            UI name (e.g., "Home / Charge / V2L") or None if not found
        """
        folder_info = self.id_to_folder.get(folder_id)
        return folder_info['ui_name'] if folder_info else None

    def get_all_folders(self) -> Dict[int, Dict]:
        """
        Get all folder mappings.

        Returns:
            Dictionary of folder_id -> folder_info
        """
        return self.id_to_folder.copy()

    def folder_exists(self, folder_id: int) -> bool:
        """Check if folder ID exists in mappings."""
        return folder_id in self.id_to_folder

    def path_exists(self, path: str) -> bool:
        """Check if path exists in mappings."""
        return path in self.path_to_id


# Example usage
if __name__ == "__main__":
    project_dir = Path("testmo/oneapp")
    mapper = FolderMapper(project_dir)

    print(f"Loaded {len(mapper.id_to_folder)} folders")

    # Test lookup
    folder_id = mapper.get_folder_id("home/charge/v2l-vehicle-to-load")
    if folder_id:
        print(f"Folder ID for 'home/charge/v2l-vehicle-to-load': {folder_id}")
        ui_name = mapper.get_folder_ui_name(folder_id)
        print(f"UI Name: {ui_name}")
