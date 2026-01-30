"""
Testmo API Client
Handles all interactions with the Testmo API
"""
import os
import requests
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

load_dotenv()


class TestmoClient:
    """Client for interacting with Testmo API"""
    
    def __init__(self, url: Optional[str] = None, api_key: Optional[str] = None):
        self.base_url = (url or os.getenv("TESTMO_URL", "")).rstrip("/")
        self.api_key = api_key or os.getenv("TESTMO_API_KEY")
        
        if not self.base_url or not self.api_key:
            raise ValueError("TESTMO_URL and TESTMO_API_KEY must be set")
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to Testmo API"""
        url = f"{self.base_url}/api/v1/{endpoint.lstrip('/')}"
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                **kwargs
            )
            response.raise_for_status()
            return response.json() if response.text else {}
        except requests.exceptions.RequestException as e:
            print(f"API Error: {e}")
            if hasattr(e.response, 'text'):
                print(f"Response: {e.response.text}")
            raise
    
    # Projects
    def list_projects(self) -> List[Dict[str, Any]]:
        """List all projects"""
        response = self._request("GET", "/projects")
        return response.get("result", [])
    
    def get_project(self, project_id: int) -> Dict[str, Any]:
        """Get project details"""
        response = self._request("GET", f"/projects/{project_id}")
        return response.get("result", {})
    
    # Folders
    def list_folders(self, project_id: int) -> List[Dict[str, Any]]:
        """List all folders in a project with pagination"""
        all_folders = []
        page = 1

        while True:
            response = self._request("GET", f"/projects/{project_id}/folders?page={page}")
            folders = response.get("result", [])
            all_folders.extend(folders)

            next_page = response.get("next_page")
            if not next_page:
                break
            page = next_page

        return all_folders
    
    def create_folder(self, project_id: int, name: str, parent_id: Optional[int] = None) -> Dict[str, Any]:
        """Create a new folder"""
        # Testmo API requires 'folders' array with folder objects
        data = {
            "folders": [
                {
                    "name": name,
                    "parent_id": parent_id
                }
            ]
        }
        response = self._request("POST", f"/projects/{project_id}/folders", json=data)
        # API returns array of created folders, return first one
        result = response.get("result", [])
        if result:
            return result[0]
        return response
    
    def get_folder_by_name(self, project_id: int, name: str, parent_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """Find folder by name"""
        folders = self.list_folders(project_id)
        for folder in folders:
            if folder["name"] == name:
                if parent_id is None or folder.get("parent_id") == parent_id:
                    return folder
        return None

    def get_or_create_folder_hierarchy(
        self,
        project_id: int,
        folder_path: str,
        verbose: bool = False
    ) -> Optional[int]:
        """Get or create folder hierarchy from path

        Args:
            project_id: Target project
            folder_path: Path like "home-page/alerts/credit"
            verbose: Print creation messages

        Returns:
            folder_id of the deepest folder, or None for root

        Example:
            path = "home-page/alerts/credit"
            Creates:
            1. home-page (parent=None) -> folder_id=100
            2. alerts (parent=100) -> folder_id=101
            3. credit (parent=101) -> folder_id=102
            Returns: 102
        """
        if not folder_path or folder_path == ".":
            return None

        # Get existing folders map
        folders_map = self.get_folders_map(project_id)

        # Reverse map: path -> folder_id
        path_to_id = {v['path']: k for k, v in folders_map.items()}

        # Check if path already exists
        if folder_path in path_to_id:
            return path_to_id[folder_path]

        # Split path and create hierarchy
        parts = folder_path.split('/')
        parent_id = None
        current_path = ""

        for i, part in enumerate(parts):
            # Build current path
            if current_path:
                current_path = f"{current_path}/{part}"
            else:
                current_path = part

            # Check if this level exists
            if current_path in path_to_id:
                parent_id = path_to_id[current_path]
            else:
                # Create this folder level
                folder = self.create_folder(
                    project_id=project_id,
                    name=part,
                    parent_id=parent_id
                )
                folder_id = folder['id']

                # Update maps
                path_to_id[current_path] = folder_id
                parent_id = folder_id

                if verbose:
                    print(f"  Created folder: {current_path} (ID: {folder_id})")

        return parent_id
    
    # Test Cases
    def list_cases(self, project_id: int, folder_id: Optional[int] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """List test cases"""
        params = {"limit": limit}
        if folder_id:
            params["folder_id"] = folder_id

        response = self._request("GET", f"/projects/{project_id}/cases", params=params)
        return response.get("result", [])
    
    def get_all_cases(self, project_id: int, folder_id: Optional[int] = None, debug: bool = False) -> List[Dict[str, Any]]:
        """Get all test cases (handles pagination)"""
        all_cases = []
        page = 1

        while True:
            params = {"page": page}
            if folder_id:
                params["folder_id"] = folder_id

            response = self._request("GET", f"/projects/{project_id}/cases", params=params)
            cases = response.get("result", [])
            total = response.get("total", 0)
            last_page = response.get("last_page", 1)
            next_page = response.get("next_page")

            if debug:
                print(f"  Page {page}/{last_page}: Fetched {len(cases)} cases (total available: {total}, collected so far: {len(all_cases) + len(cases)})")

            if not cases:
                break

            all_cases.extend(cases)

            # Check if there's a next page
            if not next_page or page >= last_page:
                break

            page = next_page

        return all_cases
    
    def get_case(self, case_id: int) -> Dict[str, Any]:
        """Get test case details"""
        response = self._request("GET", f"/cases/{case_id}")
        return response.get("result", {})
    
    def create_case(self, project_id: int, case_data: Dict[str, Any], folder_id: Optional[int] = None) -> Dict[str, Any]:
        """Create a single test case"""
        # Use batch method with single case
        result = self.create_cases_batch(project_id, [case_data], folder_id)
        # Return first created case
        created = result.get("result", [])
        if created:
            return created[0]
        return result

    def create_cases_batch(self, project_id: int, cases: List[Dict[str, Any]], folder_id: Optional[int] = None) -> Dict[str, Any]:
        """Create multiple test cases in batch"""
        if len(cases) > 100:
            raise ValueError("Maximum 100 cases per batch")

        # Ensure all cases have folder_id
        for case in cases:
            if folder_id and "folder_id" not in case:
                case["folder_id"] = folder_id

        # Testmo API requires 'cases' wrapper
        data = {
            "cases": cases
        }

        response = self._request("POST", f"/projects/{project_id}/cases", json=data)
        return response
    
    def update_case(self, project_id: int, case_id: int, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing test case"""
        # Testmo API uses /cases/{id} for updates, not /projects/{project_id}/cases/{id}
        response = self._request("PUT", f"/cases/{case_id}", json=case_data)
        return response.get("result", {})
    
    def delete_case(self, case_id: int) -> None:
        """Delete a test case"""
        self._request("DELETE", f"/cases/{case_id}")
    
    def search_cases(
        self,
        project_id: int,
        query: Optional[str] = None,
        folder_id: Optional[int] = None,
        tags: Optional[List[str]] = None,
        state_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Search test cases"""
        params = {}
        if query:
            params["query"] = query
        if folder_id:
            params["folder_id"] = folder_id
        if tags:
            params["tags"] = ",".join(tags)
        if state_id:
            params["state_id"] = state_id

        response = self._request("GET", f"/projects/{project_id}/cases/search", params=params)
        return response.get("result", [])

    # Folder Hierarchy Methods
    def get_folders_map(self, project_id: int) -> Dict[int, Dict[str, Any]]:
        """
        Get all folders with hierarchy for a project.
        Returns a map of folder_id -> {id, name, parent_id, path}
        """
        folders = self.list_folders(project_id)
        folders_map = {}

        # First pass: build basic map
        for folder in folders:
            folders_map[folder['id']] = {
                'id': folder['id'],
                'name': folder['name'],
                'parent_id': folder.get('parent_id'),
                'path': None  # Will be computed
            }

        # Second pass: compute paths
        for folder_id in folders_map:
            folders_map[folder_id]['path'] = self._build_folder_path(folder_id, folders_map)

        return folders_map

    def _build_folder_path(self, folder_id: int, folders_map: Dict[int, Dict]) -> str:
        """
        Build full path like 'necn/plug-charge' from folder hierarchy.
        Uses recursion to build path from root to leaf.
        """
        if folder_id not in folders_map:
            return ""

        folder = folders_map[folder_id]
        path_parts = [self._safe_folder_name(folder['name'])]
        parent_id = folder.get('parent_id')

        # Recursively build path from root
        while parent_id and parent_id in folders_map:
            parent = folders_map[parent_id]
            path_parts.insert(0, self._safe_folder_name(parent['name']))
            parent_id = parent.get('parent_id')

        return '/'.join(path_parts)

    def _safe_folder_name(self, name: str) -> str:
        """Sanitize folder name for filesystem"""
        # Remove special characters, replace spaces with hyphens
        safe = "".join(c if c.isalnum() or c in (' ', '-', '_') else '-' for c in name)
        safe = safe.replace(' ', '-').lower()
        # Remove consecutive dashes
        while '--' in safe:
            safe = safe.replace('--', '-')
        # Strip leading/trailing dashes
        return safe.strip('-')
