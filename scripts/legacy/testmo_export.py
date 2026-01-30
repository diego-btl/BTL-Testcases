#!/usr/bin/env python3
"""
Export test cases from Testmo to Git YAML format with CSV folder mapping support
"""
import os
import sys
import yaml
import csv
from pathlib import Path
from typing import List, Dict, Any, Optional
import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from testmo_client import TestmoClient
from yaml_converter import YAMLConverter

console = Console()


def safe_filename(name: str) -> str:
    """Convert test case name to safe filename"""
    # Remove special characters, replace spaces with hyphens
    safe = "".join(c if c.isalnum() or c in (' ', '-', '_') else '' for c in name)
    safe = safe.replace(' ', '-').lower()
    # Limit length
    return safe[:100]


def safe_folder_name(name: str) -> str:
    """Sanitize folder name for filesystem (same as TestmoClient._safe_folder_name)"""
    # Remove special characters, replace spaces with hyphens
    safe = "".join(c if c.isalnum() or c in (' ', '-', '_') else '-' for c in name)
    safe = safe.replace(' ', '-').lower()
    # Remove consecutive dashes
    while '--' in safe:
        safe = safe.replace('--', '-')
    # Strip leading/trailing dashes
    return safe.strip('-')


def build_csv_folder_map(csv_path: Path) -> Dict[int, str]:
    """
    Build folder mapping from Testmo CSV export.
    Returns: {testmo_id: folder_path, ...}

    Testmo CSV structure:
    Line 1-3: Metadata ("Project ID","2" / "Project","OneApp" / "Exported at","...")
    Line 4: Empty line
    Line 5: Column headers ("Case","Description","Folder",...,"Case ID",...)
    Line 6+: Data rows
    """
    folder_map = {}

    console.print(f"[blue]Reading CSV file: {csv_path}[/blue]")

    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        # Skip first 4 lines (3 metadata rows + 1 empty line)
        for _ in range(4):
            next(f)

        # Now line 5 has the real column headers
        reader = csv.DictReader(f)

        # Debug: show columns from first row
        first_row = next(reader, None)
        if first_row:
            console.print(f"[dim]CSV columns found: Case ID, Folder, and {len(first_row) - 2} others[/dim]")

            # Process first row
            case_id_str = first_row.get("Case ID", "").strip()
            folder_name = first_row.get("Folder", "").strip()

            if case_id_str and folder_name:
                try:
                    case_id = int(case_id_str)
                    folder_path = safe_folder_name(folder_name)
                    folder_map[case_id] = folder_path
                except (ValueError, KeyError):
                    pass

        # Process remaining rows
        for row in reader:
            case_id_str = row.get("Case ID", "").strip()
            folder_name = row.get("Folder", "").strip()

            if not case_id_str or not folder_name:
                continue

            try:
                case_id = int(case_id_str)
                folder_path = safe_folder_name(folder_name)
                folder_map[case_id] = folder_path
            except (ValueError, KeyError):
                continue

    console.print(f"[green]✓[/green] Loaded folder mappings for {len(folder_map)} test cases from CSV")
    
    # Show sample mappings
    if folder_map:
        console.print("[dim]Sample mappings:[/dim]")
        for testmo_id in list(folder_map.keys())[:5]:
            console.print(f"[dim]  TC{testmo_id} → {folder_map[testmo_id]}/[/dim]")
    
    return folder_map


def organize_by_feature(cases: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Organize test cases by feature"""
    features = {}
    
    for case in cases:
        feature = case.get("metadata", {}).get("feature", "general")
        if feature not in features:
            features[feature] = []
        features[feature].append(case)
    
    return features


def build_existing_file_map(output_dir: Path) -> Dict[int, Path]:
    """
    Build mapping of testmo_id → filepath for existing files.
    Returns: {64860: Path("TC001-max-charge-limit-banner.yml"), ...}
    """
    file_map = {}

    # Find all YAML files in output_dir (including subdirectories)
    for yaml_file in output_dir.rglob("TC*.yml"):
        try:
            with open(yaml_file, 'r') as f:
                data = yaml.safe_load(f)
                testmo_id = data.get("metadata", {}).get("testmo_id")

                if testmo_id and testmo_id != "null" and testmo_id is not None:
                    file_map[int(testmo_id)] = yaml_file
        except Exception:
            continue  # Skip malformed files

    return file_map


@click.command()
@click.option("--project-id", type=int, help="Testmo project ID", envvar="TESTMO_PROJECT_ID")
@click.option("--folder-id", type=int, help="Specific folder ID to export (optional)")
@click.option("--csv-map", type=Path, help="CSV file with Case ID → Folder mappings (from Testmo export)")
@click.option("--output-dir", type=Path, default="test-cases", help="Output directory for YAML files")
@click.option("--limit", type=int, help="Limit number of cases to export (for testing)")
@click.option("--feature", type=str, help="Feature name for categorization")
def export_from_testmo(
    project_id: int,
    folder_id: Optional[int],
    csv_map: Optional[Path],
    output_dir: Path,
    limit: Optional[int],
    feature: Optional[str]
):
    """Export test cases from Testmo to YAML files
    
    Use --csv-map to provide folder structure from Testmo CSV export:
    
        python scripts/testmo_export.py \\
          --project-id 2 \\
          --csv-map data/oneapp-repo-export.csv \\
          --output-dir testmo/oneapp/test-cases
    """
    
    console.print("\n[bold blue]Testmo Export Tool[/bold blue]")
    console.print("=" * 50)
    
    try:
        # Initialize client
        client = TestmoClient()
        converter = YAMLConverter()
        
        # Get project info
        with console.status("[bold green]Fetching project info..."):
            project = client.get_project(project_id)
            console.print(f"[green]✓[/green] Connected to project: {project.get('name')}")

        # Build folder map
        csv_folder_map = None
        folders_map = None
        
        if csv_map:
            # Use CSV for folder mapping (RECOMMENDED)
            if not csv_map.exists():
                console.print(f"[red]Error: CSV file not found: {csv_map}[/red]")
                sys.exit(1)
            
            csv_folder_map = build_csv_folder_map(csv_map)
            console.print(f"[cyan]Using CSV-based folder mapping ({len(csv_folder_map)} mappings)[/cyan]")
        else:
            # Fallback to API folder hierarchy (may have missing folders)
            with console.status("[bold green]Fetching folder structure from API..."):
                folders_map = client.get_folders_map(project_id)
                console.print(f"[yellow]⚠ Using API folder hierarchy ({len(folders_map)} folders)[/yellow]")
                console.print(f"[yellow]  Note: Some folders may be missing. Use --csv-map for accurate structure.[/yellow]")

        # Fetch test cases (with pagination)
        console.print("[bold green]Fetching test cases (paginating through all pages)...")
        if folder_id:
            cases = client.get_all_cases(project_id, folder_id=folder_id, debug=True)
        else:
            cases = client.get_all_cases(project_id, debug=True)

        if limit:
            cases = cases[:limit]

        console.print(f"[green]✓[/green] Found {len(cases)} test cases")
        
        if not cases:
            console.print("[yellow]No test cases found[/yellow]")
            return

        # Infer feature from output_dir if not explicitly provided
        if not feature:
            # Extract feature from output path like "test-cases/tesla-pricing" → "tesla-pricing"
            output_path_str = str(output_dir)

            if output_path_str != "test-cases" and output_path_str != ".":
                # Use the last part of the path as feature name
                feature = Path(output_dir).name
            else:
                feature = "general"

        console.print(f"[blue]Using feature:[/blue] {feature}")

        # Build map of existing files
        console.print("[blue]Scanning existing files...[/blue]")
        existing_files = build_existing_file_map(output_dir)
        console.print(f"[blue]Found {len(existing_files)} existing test cases[/blue]")

        # Convert to YAML format
        yaml_cases = []

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Converting to YAML format...", total=len(cases))

            for case in cases:
                testmo_id = case.get("id")
                existing_file = existing_files.get(testmo_id)

                yaml_case = converter.testmo_to_yaml(case, feature=feature, existing_file=existing_file)
                yaml_cases.append(yaml_case)
                progress.advance(task)
        
        console.print(f"[green]✓[/green] Converted {len(yaml_cases)} test cases")
        
        # Organize by feature
        organized = organize_by_feature(yaml_cases)
        
        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Write YAML files
        total_written = 0
        files_created = 0
        files_updated = 0
        files_renamed = 0
        missing_folder_mapping = 0
        folder_distribution = {}

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Writing YAML files...", total=len(yaml_cases))

            for case in yaml_cases:
                metadata = case.get("metadata", {})
                testmo_id = metadata.get("testmo_id")
                test_id = metadata.get("id", "TC00000")
                test_name = metadata.get("name", "untitled")
                folder_id = metadata.get("folder_id")

                # Determine folder path
                folder_path = None
                
                if csv_folder_map and testmo_id in csv_folder_map:
                    # PRIMARY: Use CSV mapping (most reliable)
                    folder_path = csv_folder_map[testmo_id]
                elif folders_map and folder_id and folder_id in folders_map:
                    # FALLBACK: Use API folder hierarchy
                    folder_path = folders_map[folder_id]['path']
                else:
                    # NO MAPPING FOUND
                    if csv_folder_map:
                        console.print(f"[yellow]Warning: TC{testmo_id} not in CSV map - using 'uncategorized'[/yellow]")
                    elif folder_id:
                        console.print(f"[yellow]Warning: TC{testmo_id} has folder_id={folder_id} not in API - using 'uncategorized'[/yellow]")
                    folder_path = "uncategorized"
                    missing_folder_mapping += 1

                # Track folder distribution
                folder_distribution[folder_path] = folder_distribution.get(folder_path, 0) + 1

                # Build target directory: output_dir / folder_path
                target_dir = output_dir / folder_path
                target_dir.mkdir(parents=True, exist_ok=True)

                # Generate expected filename based on Testmo ID
                expected_filename = f"{test_id}-{safe_filename(test_name)}.yml"
                expected_filepath = target_dir / expected_filename

                # Check if we're updating an existing file
                existing_file = existing_files.get(testmo_id) if testmo_id else None

                if existing_file and existing_file.exists():
                    # File exists with this testmo_id
                    # Check if it needs to be renamed or moved
                    if existing_file != expected_filepath:
                        # RENAME/MOVE: Testmo ID changed, name changed, or folder changed
                        console.print(f"[yellow]Moving:[/yellow] {existing_file.relative_to(output_dir)} → {expected_filepath.relative_to(output_dir)}")
                        # Delete old file after we write the new one
                        old_file_to_delete = existing_file
                        filepath = expected_filepath
                        files_renamed += 1
                    else:
                        # UPDATE in place
                        filepath = existing_file
                        old_file_to_delete = None
                        files_updated += 1
                else:
                    # CREATE new file
                    filepath = expected_filepath
                    old_file_to_delete = None
                    files_created += 1

                # Write YAML file
                with open(filepath, 'w') as f:
                    yaml.dump(case, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

                # Remove old file if we renamed/moved
                if old_file_to_delete and old_file_to_delete != filepath:
                    old_file_to_delete.unlink()

                total_written += 1
                progress.advance(task)

        console.print(f"[green]✓[/green] Written {total_written} YAML files to {output_dir}")

        # File operation summary
        console.print("\n[bold]File Operations:[/bold]")
        console.print(f"  [green]Created:[/green] {files_created}")
        console.print(f"  [blue]Updated:[/blue] {files_updated}")
        console.print(f"  [yellow]Renamed:[/yellow] {files_renamed}")
        console.print(f"  [cyan]Total:[/cyan] {total_written}")

        if missing_folder_mapping > 0:
            console.print(f"\n[yellow]⚠ Warning: {missing_folder_mapping} cases had no folder mapping (moved to 'uncategorized')[/yellow]")

        # Folder distribution
        console.print("\n[bold]Folder Distribution:[/bold]")
        for folder, count in sorted(folder_distribution.items(), key=lambda x: -x[1])[:15]:
            console.print(f"  {folder}: {count} cases")
        
        if len(folder_distribution) > 15:
            console.print(f"  ... and {len(folder_distribution) - 15} more folders")

        # Summary table
        table = Table(title="Export Summary")
        table.add_column("Feature", style="cyan")
        table.add_column("Test Cases", style="magenta", justify="right")

        for feature_name, feature_cases in sorted(organized.items()):
            table.add_row(feature_name, str(len(feature_cases)))

        console.print("\n")
        console.print(table)

        # Next steps
        console.print("\n[bold green]Export Complete![/bold green]")
        console.print("\n[bold]Validation:[/bold]")
        console.print(f"  Verify folder structure: [cyan]find {output_dir} -name '*.yml' | head -20[/cyan]")
        console.print(f"  Check for root files: [cyan]ls {output_dir}/*.yml 2>/dev/null | wc -l[/cyan] (should be 0)")
        
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    export_from_testmo()
