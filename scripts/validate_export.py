#!/usr/bin/env python3
"""
Validate exported test cases against Testmo API.

Checks:
1. Case count matches (local vs Testmo)
2. Folder structure matches
3. All YAMLs have valid testmo_ids
4. No orphaned files
5. Folder hierarchy preserved
"""

import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple
import yaml
from rich.console import Console
from rich.table import Table
from rich.progress import Progress
from testmo_client import TestmoClient

console = Console()


def load_yaml_cases(directory: Path) -> Dict[int, Path]:
    """Load all YAML test cases and map testmo_id -> filepath"""
    cases = {}

    yaml_files = list(directory.rglob("*.yml"))

    with Progress() as progress:
        task = progress.add_task(
            "[cyan]Loading YAML files...",
            total=len(yaml_files)
        )

        for yaml_file in yaml_files:
            try:
                with open(yaml_file, 'r') as f:
                    data = yaml.safe_load(f)
                    testmo_id = data.get('metadata', {}).get('testmo_id')

                    if testmo_id:
                        cases[testmo_id] = yaml_file
                    else:
                        console.print(
                            f"[yellow]Warning:[/yellow] No testmo_id in {yaml_file.relative_to(directory)}"
                        )
            except Exception as e:
                console.print(
                    f"[red]Error:[/red] Failed to load {yaml_file.relative_to(directory)}: {e}"
                )

            progress.update(task, advance=1)

    return cases


def get_testmo_cases(client: TestmoClient, project_id: int) -> Set[int]:
    """Get all case IDs from Testmo API"""
    console.print(f"[cyan]Fetching cases from Testmo (Project {project_id})...")

    cases = client.get_all_cases(project_id)
    case_ids = {case['id'] for case in cases}

    console.print(f"[green]✓[/green] Found {len(case_ids)} cases in Testmo")
    return case_ids


def get_local_folder_structure(directory: Path) -> Dict[str, int]:
    """Get folder structure with case counts"""
    structure = {}

    for folder in directory.rglob("*"):
        if folder.is_dir():
            yaml_count = len(list(folder.glob("*.yml")))
            if yaml_count > 0:
                rel_path = str(folder.relative_to(directory))
                structure[rel_path] = yaml_count

    return structure


def get_testmo_folder_structure(
    client: TestmoClient,
    project_id: int
) -> Dict[str, int]:
    """Get Testmo folder structure with case counts"""
    console.print("[cyan]Fetching folder structure from Testmo...")

    # Get all cases with folder info
    cases = client.get_all_cases(project_id)

    # Get folder map
    folders_map = client.get_folders_map(project_id)

    # Count cases per folder path
    folder_counts = {}
    for case in cases:
        folder_id = case.get('folder_id')
        if folder_id and folder_id in folders_map:
            folder_path = folders_map[folder_id]['path']
            folder_counts[folder_path] = folder_counts.get(folder_path, 0) + 1

    console.print(f"[green]✓[/green] Found {len(folder_counts)} folders in Testmo")
    return folder_counts


def validate_project(
    project_id: int,
    project_name: str,
    local_path: Path,
    client: TestmoClient
) -> Dict:
    """Validate a single project"""
    console.rule(f"[bold blue]Validating {project_name} (Project {project_id})")

    results = {
        'project_id': project_id,
        'project_name': project_name,
        'success': True,
        'errors': [],
        'warnings': []
    }

    # 1. Load local cases
    console.print("\n[bold]Step 1:[/bold] Loading local YAML files...")
    local_cases = load_yaml_cases(local_path)
    console.print(f"[green]✓[/green] Loaded {len(local_cases)} YAML files")

    # 2. Get Testmo cases
    console.print("\n[bold]Step 2:[/bold] Fetching Testmo cases...")
    testmo_cases = get_testmo_cases(client, project_id)

    # 3. Compare counts
    console.print("\n[bold]Step 3:[/bold] Comparing case counts...")
    local_count = len(local_cases)
    testmo_count = len(testmo_cases)

    if local_count == testmo_count:
        console.print(f"[green]✓[/green] Case counts match: {local_count}")
    else:
        msg = f"Case count mismatch: Local={local_count}, Testmo={testmo_count}"
        console.print(f"[red]✗[/red] {msg}")
        results['errors'].append(msg)
        results['success'] = False

    # 4. Find missing cases
    console.print("\n[bold]Step 4:[/bold] Checking for missing cases...")
    local_ids = set(local_cases.keys())

    missing_in_local = testmo_cases - local_ids
    extra_in_local = local_ids - testmo_cases

    if missing_in_local:
        msg = f"Missing {len(missing_in_local)} cases in local export"
        console.print(f"[red]✗[/red] {msg}")
        console.print(f"   Missing IDs: {sorted(list(missing_in_local))[:10]}...")
        results['errors'].append(msg)
        results['success'] = False

    if extra_in_local:
        msg = f"Found {len(extra_in_local)} extra cases in local (not in Testmo)"
        console.print(f"[yellow]⚠[/yellow] {msg}")
        console.print(f"   Extra IDs: {sorted(list(extra_in_local))[:10]}...")
        results['warnings'].append(msg)

    if not missing_in_local and not extra_in_local:
        console.print("[green]✓[/green] All cases present and accounted for")

    # 5. Validate folder structure
    console.print("\n[bold]Step 5:[/bold] Validating folder structure...")
    local_folders = get_local_folder_structure(local_path)
    testmo_folders = get_testmo_folder_structure(client, project_id)

    console.print(f"   Local folders: {len(local_folders)}")
    console.print(f"   Testmo folders: {len(testmo_folders)}")

    # Compare folder counts
    mismatched_folders = []
    for folder_path, testmo_count in testmo_folders.items():
        local_count = local_folders.get(folder_path, 0)
        if local_count != testmo_count:
            mismatched_folders.append(
                (folder_path, local_count, testmo_count)
            )

    if mismatched_folders:
        console.print(f"[yellow]⚠[/yellow] {len(mismatched_folders)} folders have count mismatches:")
        for path, local_c, testmo_c in mismatched_folders[:5]:
            console.print(f"   {path}: Local={local_c}, Testmo={testmo_c}")
        results['warnings'].append(
            f"{len(mismatched_folders)} folders with count mismatches"
        )
    else:
        console.print("[green]✓[/green] All folder counts match")

    # Store stats
    results['local_count'] = local_count
    results['testmo_count'] = testmo_count
    results['local_folders'] = len(local_folders)
    results['testmo_folders'] = len(testmo_folders)
    results['missing_cases'] = len(missing_in_local)
    results['extra_cases'] = len(extra_in_local)

    return results


def print_summary(all_results: List[Dict]):
    """Print summary table"""
    console.rule("[bold blue]Validation Summary")

    table = Table(title="Export Validation Results")
    table.add_column("Project", style="cyan")
    table.add_column("Local Cases", justify="right")
    table.add_column("Testmo Cases", justify="right")
    table.add_column("Match", justify="center")
    table.add_column("Folders", justify="right")
    table.add_column("Status", justify="center")

    total_local = 0
    total_testmo = 0
    total_success = 0

    for result in all_results:
        match_icon = "✓" if result['local_count'] == result['testmo_count'] else "✗"
        match_style = "green" if result['local_count'] == result['testmo_count'] else "red"

        status_icon = "✓" if result['success'] else "✗"
        status_style = "green" if result['success'] else "red"

        table.add_row(
            result['project_name'],
            str(result['local_count']),
            str(result['testmo_count']),
            f"[{match_style}]{match_icon}[/{match_style}]",
            f"{result['local_folders']}/{result['testmo_folders']}",
            f"[{status_style}]{status_icon}[/{status_style}]"
        )

        total_local += result['local_count']
        total_testmo += result['testmo_count']
        if result['success']:
            total_success += 1

    table.add_row(
        "[bold]TOTAL[/bold]",
        f"[bold]{total_local}[/bold]",
        f"[bold]{total_testmo}[/bold]",
        "",
        "",
        f"[bold]{total_success}/{len(all_results)}[/bold]"
    )

    console.print(table)

    # Print errors and warnings
    for result in all_results:
        if result['errors']:
            console.print(f"\n[red]Errors in {result['project_name']}:[/red]")
            for error in result['errors']:
                console.print(f"  • {error}")

        if result['warnings']:
            console.print(f"\n[yellow]Warnings in {result['project_name']}:[/yellow]")
            for warning in result['warnings']:
                console.print(f"  • {warning}")

    # Overall status
    if total_success == len(all_results):
        console.print("\n[bold green]✓ All projects validated successfully![/bold green]")
        return 0
    else:
        console.print(f"\n[bold red]✗ {len(all_results) - total_success} projects failed validation[/bold red]")
        return 1


def main():
    """Main validation routine"""
    console.print("[bold cyan]Testmo Export Validation[/bold cyan]\n")

    # Initialize client
    client = TestmoClient()

    # Projects to validate
    projects = [
        {
            'id': 2,
            'name': 'OneApp',
            'path': Path('testmo/oneapp/test-cases')
        },
        {
            'id': 6,
            'name': 'NMEX',
            'path': Path('testmo/nmex/test-cases')
        },
        {
            'id': 5,
            'name': 'NBA',
            'path': Path('testmo/nba/test-cases')
        },
        {
            'id': 8,
            'name': 'Enrique Playground',
            'path': Path('testmo/enrique-playground/test-cases')
        }
    ]

    # Validate each project
    all_results = []
    for project in projects:
        if not project['path'].exists():
            console.print(f"[yellow]⚠[/yellow] Skipping {project['name']} - path not found")
            continue

        result = validate_project(
            project['id'],
            project['name'],
            project['path'],
            client
        )
        all_results.append(result)
        console.print()  # Blank line between projects

    # Print summary
    exit_code = print_summary(all_results)
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
