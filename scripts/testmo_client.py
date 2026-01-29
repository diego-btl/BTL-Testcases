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
        """List all folders in a project"""
        response = self._request("GET", f"/projects/{project_id}/folders")
        return response.get("result", [])
    
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
    
    # Test Cases
    def list_cases(self, project_id: int, folder_id: Optional[int] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """List test cases"""
        params = {"limit": limit}
        if folder_id:
            params["folder_id"] = folder_id

        response = self._request("GET", f"/projects/{project_id}/cases", params=params)
        return response.get("result", [])
    
    def get_all_cases(self, project_id: int, folder_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get all test cases (handles pagination)"""
        all_cases = []
        offset = 0
        limit = 250

        while True:
            params = {"limit": limit, "offset": offset}
            if folder_id:
                params["folder_id"] = folder_id

            response = self._request("GET", f"/projects/{project_id}/cases", params=params)
            cases = response.get("result", [])
            
            if not cases:
                break
            
            all_cases.extend(cases)
            offset += limit
            
            # If we got fewer than limit, we've reached the end
            if len(cases) < limit:
                break
        
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
