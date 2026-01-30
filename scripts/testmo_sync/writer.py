"""
Testmo Writer Module - REST API Wrapper

Provides write operations via Testmo REST API.
All operations use REST API because MCP has known bugs in update_case.

Based on validation: TESTING_LOG.md
- Individual update: ~223ms per case (PATCH)
- Batch update: Hybrid approach (common fields batch, unique fields individual)
- Individual create: ~150ms + ID sync (POST)
- Batch create: ~393ms for 5 cases (true batch, 3.3x faster)
"""

import os
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime


class TestmoWriter:
    """Write operations via Testmo REST API."""

    def __init__(self, project_id: int, api_key: Optional[str] = None,
                 instance: str = "bethinklabs"):
        """
        Initialize writer for a specific project.

        Args:
            project_id: Testmo project ID
            api_key: Testmo API key (or None to read from env)
            instance: Testmo instance name (default: bethinklabs)
        """
        self.project_id = project_id
        self.api_key = api_key or os.getenv('TESTMO_API_KEY')
        self.instance = instance
        self.base_url = f"https://{instance}.testmo.net/api/v1"

        if not self.api_key:
            raise ValueError("TESTMO_API_KEY not set in environment or provided")

        self.headers = {
            'X-API-Key': self.api_key,
            'Content-Type': 'application/json'
        }

    def update_case(self, case_id: int, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a single test case.

        Args:
            case_id: Testmo case ID
            updates: Dictionary of fields to update
                   Example: {'name': 'New Name', 'custom_notes': 'Updated notes'}

        Returns:
            Updated case data from API

        Raises:
            requests.HTTPError: If API request fails

        Performance:
            Validated: ~223ms per case
        """
        url = f"{self.base_url}/projects/{self.project_id}/cases"

        payload = {
            'ids': [case_id],
            **updates
        }

        response = requests.patch(url, headers=self.headers, json=payload)
        response.raise_for_status()

        return response.json()

    def update_cases_batch(self, case_ids: List[int],
                          common_updates: Dict[str, Any],
                          individual_updates: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """
        Update multiple test cases using hybrid approach.

        Hybrid approach:
        - Common fields (priority, status, tags, notes): Single batch PATCH
        - Unique fields (name, description): Individual PATCH calls

        Args:
            case_ids: List of case IDs to update
            common_updates: Fields with same value for all cases
                          Example: {'custom_notes': 'Sprint 5'}
            individual_updates: List of dicts with unique updates per case
                              Must match order of case_ids
                              Example: [{'name': 'Test 1'}, {'name': 'Test 2'}]

        Returns:
            List of update results

        Performance:
            Validated: ~1.5s for 5 cases with hybrid approach
            - Batch (common fields): 264ms for 5 cases (53ms per case)
            - Individual (unique fields): 1193ms for 5 cases (239ms per case)
        """
        results = []

        # Step 1: Batch update common fields (if any)
        if common_updates:
            url = f"{self.base_url}/projects/{self.project_id}/cases"
            payload = {
                'ids': case_ids,
                **common_updates
            }

            response = requests.patch(url, headers=self.headers, json=payload)
            response.raise_for_status()
            results.append(response.json())

        # Step 2: Individual updates for unique fields (if any)
        if individual_updates:
            if len(individual_updates) != len(case_ids):
                raise ValueError("individual_updates must match length of case_ids")

            for case_id, updates in zip(case_ids, individual_updates):
                if updates:  # Only update if there are changes
                    result = self.update_case(case_id, updates)
                    results.append(result)

        return results

    def create_case(self, folder_id: int, case_data: Dict[str, Any]) -> int:
        """
        Create a single test case.

        Args:
            folder_id: Testmo folder ID where case will be created
            case_data: Case data dictionary
                      Example: {
                          'name': 'Test Case Name',
                          'description': 'Test description',
                          'custom_steps': [...],
                          'custom_priority': 'medium',
                          'custom_tags': ['tag1', 'tag2']
                      }

        Returns:
            New case ID

        Raises:
            requests.HTTPError: If API request fails

        Performance:
            Validated: ~150ms per case
        """
        url = f"{self.base_url}/projects/{self.project_id}/cases"

        # Batch format is required even for single case
        payload = {
            'cases': [{
                'folder_id': folder_id,
                **case_data
            }]
        }

        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()

        result = response.json()
        # Extract case ID from response
        return result[0]['id']

    def create_cases_batch(self, cases: List[Dict[str, Any]]) -> List[int]:
        """
        Create multiple test cases in a single batch operation.

        Args:
            cases: List of case data dictionaries, each must include folder_id
                  Example: [
                      {
                          'folder_id': 7338,
                          'name': 'Test 1',
                          'description': 'Description 1',
                          ...
                      },
                      {
                          'folder_id': 7338,
                          'name': 'Test 2',
                          'description': 'Description 2',
                          ...
                      }
                  ]

        Returns:
            List of new case IDs in same order as input

        Performance:
            Validated: ~393ms for 5 cases (79ms per case)
            - 3.3x faster than individual creates
            - True batch operation (same timestamp proves atomic)

        Scaling:
            - 10 cases: ~456ms
            - 50 cases: ~2.3s
            - 100 cases: ~4.6s (likely API limit)
        """
        url = f"{self.base_url}/projects/{self.project_id}/cases"

        payload = {'cases': cases}

        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()

        result = response.json()

        # Extract case IDs in order
        case_ids = [case['id'] for case in result]

        return case_ids

    def get_case(self, case_id: int) -> Dict[str, Any]:
        """
        Get a single case via REST API (for verification).

        This is a read operation but included here because MCP get_case has bugs.

        Args:
            case_id: Testmo case ID

        Returns:
            Case data dictionary
        """
        url = f"{self.base_url}/projects/{self.project_id}/cases/{case_id}"

        response = requests.get(url, headers=self.headers)
        response.raise_for_status()

        return response.json()


# Example usage
if __name__ == "__main__":
    import sys

    # Example: Update a single case
    if len(sys.argv) >= 3 and sys.argv[1] == "update":
        case_id = int(sys.argv[2])

        writer = TestmoWriter(project_id=2)

        result = writer.update_case(
            case_id=case_id,
            updates={
                'custom_notes': f'Updated via writer.py at {datetime.now().isoformat()}'
            }
        )

        print(f"✓ Case {case_id} updated")
        print(f"Response: {result}")

    # Example: Create a new case
    elif len(sys.argv) >= 2 and sys.argv[1] == "create":
        writer = TestmoWriter(project_id=2)

        new_id = writer.create_case(
            folder_id=7338,  # V2L folder
            case_data={
                'name': 'Test Case from writer.py',
                'description': 'Created via REST API',
                'custom_priority': 'low',
                'custom_tags': ['test', 'api']
            }
        )

        print(f"✓ Case created with ID: {new_id}")

    else:
        print("Usage:")
        print("  python writer.py update <case_id>")
        print("  python writer.py create")
