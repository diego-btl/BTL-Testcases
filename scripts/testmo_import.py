#!/usr/bin/env python3
"""
Import test cases from Git YAML format to Testmo
"""
import os
import sys
import yaml
from pathlib import Path
from typing import List, Dict, Any
import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from testmo_client import TestmoClient
from yaml_converter import YAMLConverter

console = Console()


def load_yaml_files(directory: Path) -> Dict[Path, Dict[str, Any]]:
    """Load all YAML test case files from directory

    Returns:
        Dict mapping file path -> yaml case data
    """
    yaml_cases = {}

    for yaml_file in directory.rglob("*.yml"):
        try:
            with open(yaml_file, 'r') as f:
                case = yaml.safe_load(f)
                if case and "metadata" in case:
                    case["_source_file"] = str(yaml_file)
                    yaml_cases[yaml_file] = case
        except Exception as e:
            console.print(f"[yellow]Warning: Could not load {yaml_file}: {e}[/yellow]")

    return yaml_cases


@click.command()
@click.option("--project-id", type=int, help="Testmo project ID", envvar="TESTMO_PROJECT_ID")
@click.option("--input-dir", type=Path, default="test-cases", help="Input directory with YAML files")
@click.option("--folder-name", type=str, help="Target folder name in Testmo (will be created if needed)")
@click.option("--preserve-folders", is_flag=True, default=True, help="Preserve folder structure from local export (default: True)")
@click.option("--dry-run", is_flag=True, help="Show what would be imported without actually importing")
@click.option("--update-existing", is_flag=True, help="Update existing cases (match by testmo_id)")
def import_to_testmo(project_id: int, input_dir: Path, folder_name: str, preserve_folders: bool, dry_run: bool, update_existing: bool):
    """Import test cases from YAML files to Testmo"""
    
    console.print("\n[bold blue]Testmo Import Tool[/bold blue]")
    console.print("=" * 50)
    
    if dry_run:
        console.print("[yellow]DRY RUN MODE - No changes will be made[/yellow]\n")
    
    try:
        # Initialize client
        client = TestmoClient()
        converter = YAMLConverter()
        
        # Get project info
        with console.status("[bold green]Fetching project info..."):
            project = client.get_project(project_id)
            console.print(f"[green]✓[/green] Connected to project: {project.get('name')}")
        
        # Get or create target folder
        folder_id = None
        if folder_name:
            with console.status(f"[bold green]Finding folder '{folder_name}'..."):
                folder = client.get_folder_by_name(project_id, folder_name)
                if folder:
                    folder_id = folder["id"]
                    console.print(f"[green]✓[/green] Using existing folder: {folder_name} (ID: {folder_id})")
                elif not dry_run:
                    folder = client.create_folder(project_id, folder_name)
                    folder_id = folder["id"]
                    console.print(f"[green]✓[/green] Created new folder: {folder_name} (ID: {folder_id})")
                else:
                    console.print(f"[yellow]Would create folder: {folder_name}[/yellow]")
        
        # Load YAML files
        with console.status("[bold green]Loading YAML files..."):
            yaml_cases_map = load_yaml_files(input_dir)
            console.print(f"[green]✓[/green] Loaded {len(yaml_cases_map)} YAML files")

        if not yaml_cases_map:
            console.print("[yellow]No YAML test cases found[/yellow]")
            return

        # Group cases by folder path (if preserve_folders is enabled)
        if preserve_folders and not folder_name:
            console.print("[cyan]Grouping cases by folder structure...")
            cases_by_folder = {}

            for filepath, yaml_case in yaml_cases_map.items():
                # Get folder path from filepath
                rel_path = filepath.relative_to(input_dir)
                folder_path = str(rel_path.parent)

                if folder_path == ".":
                    folder_path = None

                if folder_path not in cases_by_folder:
                    cases_by_folder[folder_path] = []

                cases_by_folder[folder_path].append((filepath, yaml_case))

            console.print(f"[green]✓[/green] Cases organized into {len(cases_by_folder)} folders")
        else:
            # No folder preservation - treat as flat list
            cases_by_folder = {folder_name: list(yaml_cases_map.items())}

        # Convert to Testmo format
        testmo_cases = []

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Converting to Testmo format...", total=len(yaml_cases_map))

            for folder_path, folder_cases in cases_by_folder.items():
                for filepath, yaml_case in folder_cases:
                    testmo_case = converter.yaml_to_testmo(yaml_case)

                    # Store folder path for later
                    testmo_case["_folder_path"] = folder_path

                    # Store metadata for tracking
                    testmo_case["_yaml_metadata"] = yaml_case.get("metadata", {})
                    testmo_case["_source_file"] = yaml_case.get("_source_file")

                    testmo_cases.append(testmo_case)
                    progress.advance(task)

        console.print(f"[green]✓[/green] Converted {len(testmo_cases)} test cases")
        
        if dry_run:
            if update_existing:
                # UPDATE MODE: Only update existing cases, skip those without testmo_id
                cases_to_update = []
                cases_skipped = []

                for case in testmo_cases:
                    metadata = case.get("_yaml_metadata", {})
                    testmo_id = metadata.get("testmo_id")
                    if testmo_id:
                        cases_to_update.append(case)
                    else:
                        cases_skipped.append(case)

                console.print("\n[cyan]UPDATE MODE[/cyan] - Will only update existing cases with testmo_id")

                # Show UPDATE table
                if cases_to_update:
                    update_table = Table(title=f"Would UPDATE ({len(cases_to_update)} cases)")
                    update_table.add_column("Testmo ID", style="cyan")
                    update_table.add_column("Name", style="magenta")
                    update_table.add_column("Priority", style="yellow")

                    for case in cases_to_update[:10]:
                        metadata = case.get("_yaml_metadata", {})
                        update_table.add_row(
                            str(metadata.get("testmo_id", "N/A")),
                            case.get("name", "Untitled")[:50],
                            metadata.get("priority", "medium")
                        )

                    console.print("\n")
                    console.print(update_table)

                    if len(cases_to_update) > 10:
                        console.print(f"[dim]... and {len(cases_to_update) - 10} more to update[/dim]")

                # Show SKIP table
                if cases_skipped:
                    skip_table = Table(title=f"Would SKIP ({len(cases_skipped)} cases - no testmo_id)")
                    skip_table.add_column("Test ID", style="yellow")
                    skip_table.add_column("Name", style="magenta")
                    skip_table.add_column("Reason", style="dim")

                    for case in cases_skipped[:10]:
                        metadata = case.get("_yaml_metadata", {})
                        skip_table.add_row(
                            metadata.get("id", "N/A"),
                            case.get("name", "Untitled")[:50],
                            "No testmo_id"
                        )

                    console.print("\n")
                    console.print(skip_table)

                    if len(cases_skipped) > 10:
                        console.print(f"[dim]... and {len(cases_skipped) - 10} more skipped[/dim]")

                # Summary
                console.print(f"\n[bold]Summary:[/bold]")
                console.print(f"  UPDATE: {len(cases_to_update)} existing cases")
                console.print(f"  SKIP: {len(cases_skipped)} cases (no testmo_id)")
                console.print(f"  Total: {len(testmo_cases)} cases")

                if cases_skipped:
                    console.print(f"\n[yellow]⚠️  Note: {len(cases_skipped)} case(s) will be skipped - use regular import mode (without --update-existing) to create new cases[/yellow]")

            else:
                # CREATE mode - show single table
                table = Table(title=f"Would CREATE ({len(testmo_cases)} cases)")
                table.add_column("Test ID", style="cyan")
                table.add_column("Name", style="magenta")
                table.add_column("Priority", style="yellow")
                table.add_column("Feature", style="green")

                for case in testmo_cases[:10]:
                    metadata = case.get("_yaml_metadata", {})
                    table.add_row(
                        metadata.get("id", "N/A"),
                        case.get("name", "Untitled")[:50],
                        metadata.get("priority", "medium"),
                        metadata.get("feature", "general")
                    )

                console.print("\n")
                console.print(table)

                if len(testmo_cases) > 10:
                    console.print(f"\n[dim]... and {len(testmo_cases) - 10} more cases[/dim]")

            console.print(f"\n[yellow]Dry run complete. Run without --dry-run to import.[/yellow]")
            return
        
        # Import to Testmo
        created = 0
        updated = 0
        failed = 0
        skipped = 0
        files_updated = 0

        if update_existing:
            console.print("\n[cyan]UPDATE MODE[/cyan] - Will only update existing cases with testmo_id")

            # Separate cases into update vs skip
            cases_to_update = []
            cases_skipped = []
            skipped = 0

            for case in testmo_cases:
                metadata = case.get("_yaml_metadata", {})
                testmo_id = metadata.get("testmo_id")
                if testmo_id:
                    cases_to_update.append((testmo_id, case))
                else:
                    test_id = metadata.get("id", "Unknown")
                    name = metadata.get("name", "Untitled")
                    cases_skipped.append((test_id, name))
                    skipped += 1

            console.print(f"  Will update: {len(cases_to_update)} cases")
            console.print(f"  Will skip: {len(cases_skipped)} cases (no testmo_id)\n")

            if cases_skipped:
                console.print("[yellow]Skipped cases (no testmo_id):[/yellow]")
                for test_id, name in cases_skipped[:5]:
                    console.print(f"  [dim]- {test_id}: {name[:40]}[/dim]")
                if len(cases_skipped) > 5:
                    console.print(f"  [dim]... and {len(cases_skipped) - 5} more[/dim]")
                console.print("")

            # Update existing cases only
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                if cases_to_update:
                    task = progress.add_task("Updating existing cases...", total=len(cases_to_update))
                    for testmo_id, case in cases_to_update:
                        try:
                            metadata = case.get("_yaml_metadata", {})
                            # Remove internal fields before sending to API
                            case.pop("_yaml_metadata", None)
                            case.pop("_source_file", None)
                            # Remove id field (it's in the URL, not the body)
                            case.pop("id", None)

                            client.update_case(project_id, testmo_id, case)
                            updated += 1
                        except Exception as e:
                            console.print(f"[red]Failed to update {testmo_id}: {e}[/red]")
                            failed += 1
                        progress.advance(task)
                else:
                    console.print("[yellow]No cases to update (all cases are missing testmo_id)[/yellow]")
        else:
            # CREATE mode - create all cases as new
            console.print("\n[cyan]CREATE MODE[/cyan] - Creating all cases as new\n")

            if preserve_folders and not folder_name:
                console.print("[cyan]Creating folder structure...")

            created_mapping = []  # Track: [(yaml_file_path, testmo_id), ...]
            folder_cache = {}  # Cache folder_path -> folder_id

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Creating cases in Testmo...", total=len(testmo_cases))

                for case in testmo_cases:
                    try:
                        metadata = case.get("_yaml_metadata", {})
                        source_file = case.get("_source_file")
                        folder_path = case.get("_folder_path")

                        # Create or get folder if needed
                        target_folder_id = None
                        if preserve_folders and folder_path and not folder_name:
                            if folder_path in folder_cache:
                                target_folder_id = folder_cache[folder_path]
                            else:
                                # Create folder hierarchy
                                target_folder_id = client.get_or_create_folder_hierarchy(
                                    project_id=project_id,
                                    folder_path=folder_path,
                                    verbose=True
                                )
                                folder_cache[folder_path] = target_folder_id
                        elif folder_id:
                            # Use the single folder specified by --folder-name
                            target_folder_id = folder_id

                        # Add folder_id to case
                        if target_folder_id:
                            case["folder_id"] = target_folder_id

                        # Remove internal fields before sending to API
                        case.pop("_yaml_metadata", None)
                        case.pop("_source_file", None)
                        case.pop("_folder_path", None)
                        # Remove testmo_id if present (we're creating new)
                        case.pop("id", None)

                        result = client.create_case(project_id, case, folder_id)
                        created += 1

                        # Track source file and assigned testmo_id
                        if result and result.get('id') and source_file:
                            created_mapping.append((source_file, result['id']))

                    except Exception as e:
                        console.print(f"[red]Failed to create {metadata.get('id', 'unknown')}: {e}[/red]")
                        failed += 1

                    progress.advance(task)

            # Update YAML files with assigned testmo_ids
            if created_mapping:
                console.print("\n[blue]Updating YAML files with testmo_ids...[/blue]")

                for yaml_file, testmo_id in created_mapping:
                    try:
                        # Read YAML
                        with open(yaml_file, 'r') as f:
                            data = yaml.safe_load(f)

                        # Update testmo_id
                        if 'metadata' not in data:
                            data['metadata'] = {}
                        data['metadata']['testmo_id'] = testmo_id

                        # Write back
                        with open(yaml_file, 'w') as f:
                            yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

                        files_updated += 1
                    except Exception as e:
                        console.print(f"[yellow]Warning: Could not update {yaml_file}: {e}[/yellow]")

                console.print(f"[green]✓[/green] Updated {files_updated} YAML files with testmo_ids")
        
        # Summary
        console.print(f"\n[bold green]Import Complete![/bold green]")
        console.print(f"  Created: {created}")
        console.print(f"  Updated: {updated}")
        console.print(f"  Failed: {failed}")
        if files_updated > 0:
            console.print(f"  YAML Files Updated: {files_updated}")
        if update_existing and skipped > 0:
            console.print(f"  Skipped: {skipped} (no testmo_id)")
            console.print(f"\n[yellow]⚠️  Use regular import mode (without --update-existing) to create new cases[/yellow]")

        # Export sync readiness message
        if files_updated > 0:
            console.print(f"\n[blue]✓ YAML files updated with testmo_ids - ready for export sync[/blue]")
        
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    import_to_testmo()
