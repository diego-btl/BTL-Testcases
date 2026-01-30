#!/usr/bin/env python3
"""Compare two Testmo projects to verify structure matches"""

import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from testmo_client import TestmoClient
from rich.console import Console
from rich.table import Table


def compare_projects(source_id: int, target_id: int):
    """Compare folder structure between two projects"""
    console = Console()
    client = TestmoClient()

    console.print(f"[cyan]Comparing Project {source_id} -> Project {target_id}...\n")

    # Get source structure
    console.print(f"[dim]Fetching source project {source_id}...")
    source_cases = client.get_all_cases(source_id, debug=False)
    source_folders_map = client.get_folders_map(source_id)

    # Get target structure
    console.print(f"[dim]Fetching target project {target_id}...[/dim]\n")
    target_cases = client.get_all_cases(target_id, debug=False)
    target_folders_map = client.get_folders_map(target_id)

    # Compare counts
    console.rule("[bold]Case Counts")
    console.print(f"  Source: {len(source_cases)}")
    console.print(f"  Target: {len(target_cases)}")

    if len(source_cases) == len(target_cases):
        console.print(f"  [green]✓ Counts match[/green]")
        count_match = True
    else:
        console.print(f"  [red]✗ Count mismatch![/red]")
        count_match = False

    # Compare folder paths
    source_paths = {v['path'] for v in source_folders_map.values() if v['path']}
    target_paths = {v['path'] for v in target_folders_map.values() if v['path']}

    console.rule("[bold]Folder Structure")
    console.print(f"  Source folders: {len(source_paths)}")
    console.print(f"  Target folders: {len(target_paths)}")

    missing = source_paths - target_paths
    extra = target_paths - source_paths

    if missing:
        console.print(f"\n[yellow]Missing folders in target ({len(missing)}):[/yellow]")
        for path in sorted(missing)[:20]:
            console.print(f"  - {path}")
        if len(missing) > 20:
            console.print(f"  [dim]... and {len(missing) - 20} more[/dim]")

    if extra:
        console.print(f"\n[yellow]Extra folders in target ({len(extra)}):[/yellow]")
        for path in sorted(extra)[:20]:
            console.print(f"  + {path}")
        if len(extra) > 20:
            console.print(f"  [dim]... and {len(extra) - 20} more[/dim]")

    if not missing and not extra:
        console.print(f"  [green]✓ Folder structure matches perfectly[/green]")
        folder_match = True
    else:
        folder_match = False

    # Overall result
    console.print("\n")
    console.rule("[bold]Comparison Result")

    if count_match and folder_match:
        console.print("[bold green]✓ Projects match perfectly![/bold green]")
        return 0
    else:
        console.print("[bold yellow]⚠ Projects have differences[/bold yellow]")
        if not count_match:
            console.print("  • Case counts don't match")
        if not folder_match:
            console.print("  • Folder structures don't match")
        return 1


def main():
    if len(sys.argv) != 3:
        print("Usage: python compare_projects.py <source_project_id> <target_project_id>")
        print()
        print("Examples:")
        print("  python compare_projects.py 8 9   # Compare Enrique (8) with clone (9)")
        print("  python compare_projects.py 2 10  # Compare OneApp (2) with clone (10)")
        sys.exit(1)

    source = int(sys.argv[1])
    target = int(sys.argv[2])

    sys.exit(compare_projects(source, target))


if __name__ == '__main__':
    main()
