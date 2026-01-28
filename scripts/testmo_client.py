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
        return self._request("GET", "/projects")
    
    def get_project(self, project_id: int) -> Dict[str, Any]:
        """Get project details"""
        return self._request("GET", f"/projects/{project_id}")
    
    # Folders
    def list_folders(self, project_id: int) -> List[Dict[str, Any]]:
        """List all folders in a project"""
        return self._request("GET", f"/projects/{project_id}/folders")
    
    def create_folder(self, project_id: int, name: str, parent_id: Optional[int] = None) -> Dict[str, Any]:
        """Create a new folder"""
        data = {"name": name}
        if parent_id:
            data["parent_id"] = parent_id
        return self._request("POST", f"/projects/{project_id}/folders", json=data)
    
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
        
        result = self._request("GET", f"/projects/{project_id}/cases", params=params)
        return result.get("cases", [])
    
    def get_all_cases(self, project_id: int, folder_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get all test cases (handles pagination)"""
        all_cases = []
        offset = 0
        limit = 250
        
        while True:
            params = {"limit": limit, "offset": offset}
            if folder_id:
                params["folder_id"] = folder_id
            
            result = self._request("GET", f"/projects/{project_id}/cases", params=params)
            cases = result.get("cases", [])
            
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
        return self._request("GET", f"/cases/{case_id}")
    
    def create_case(self, project_id: int, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a single test case"""
        return self._request("POST", f"/projects/{project_id}/cases", json=case_data)
    
    def create_cases_batch(self, project_id: int, cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create multiple test cases (max 100 per request)"""
        if len(cases) > 100:
            raise ValueError("Maximum 100 cases per batch")
        
        return self._request("POST", f"/projects/{project_id}/cases/bulk", json={"cases": cases})
    
    def update_case(self, case_id: int, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a test case"""
        return self._request("PUT", f"/cases/{case_id}", json=case_data)
    
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
        
        result = self._request("GET", f"/projects/{project_id}/cases/search", params=params)
        return result.get("cases", [])
