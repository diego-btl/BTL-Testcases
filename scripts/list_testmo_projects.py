#!/usr/bin/env python3
"""Quick script to list all Testmo projects and their IDs."""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

TESTMO_URL = os.getenv("TESTMO_URL")
TESTMO_API_KEY = os.getenv("TESTMO_API_KEY")

def list_projects():
    """List all Testmo projects."""
    url = f"{TESTMO_URL}/api/v1/projects"
    headers = {
        "Authorization": f"Bearer {TESTMO_API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    data = response.json()
    projects = data.get("result", [])

    print("\n" + "="*80)
    print("TESTMO PROJECTS")
    print("="*80)

    for project in projects:
        print(f"\nProject ID: {project['id']}")
        print(f"Name: {project['name']}")
        print(f"Key: {project.get('key', 'N/A')}")
        print(f"URL: {TESTMO_URL}/repositories/{project['id']}")
        print("-" * 80)

    print(f"\nTotal Projects: {len(projects)}\n")

if __name__ == "__main__":
    list_projects()
