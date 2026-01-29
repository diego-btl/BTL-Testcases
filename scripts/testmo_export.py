#!/usr/bin/env python3
"""
Export test cases from Testmo to Git YAML format
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


def safe_filename(name: str) -> str:
    """Convert test case name to safe filename"""
    # Remove special characters, replace spaces with hyphens
    safe = "".join(c if c.isalnum() or c in (' ', '-', '_') else '' for c in name)
    safe = safe.replace(' ', '-').lower()
    # Limit length
    return safe[:100]


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

    # Find all YAML files in output_dir (not in subdirectories)
    for yaml_file in output_dir.glob("TC*.yml"):
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
@click.option("--output-dir", type=Path, default="test-cases", help="Output directory for YAML files")
@click.option("--limit", type=int, help="Limit number of cases to export (for testing)")
@click.option("--feature", type=str, help="Feature name for categorization")
def export_from_testmo(project_id: int, folder_id: int, output_dir: Path, limit: int, feature: str):
    """Export test cases from Testmo to YAML files"""
    
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
        
        # Fetch test cases
        with console.status("[bold green]Fetching test cases..."):
            if folder_id:
                cases = client.get_all_cases(project_id, folder_id=folder_id)
            else:
                cases = client.get_all_cases(project_id)
            
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

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Writing YAML files...", total=len(yaml_cases))
            
            for feature_name, feature_cases in organized.items():
                # Determine target directory
                # If output_dir already ends with the feature name, write directly to it
                # Otherwise, create a subdirectory
                if Path(output_dir).name == feature_name:
                    feature_dir = output_dir  # Write directly to test-cases/tesla-pricing/
                else:
                    feature_dir = output_dir / feature_name  # Write to test-cases/general/

                feature_dir.mkdir(parents=True, exist_ok=True)

                for case in feature_cases:
                    metadata = case.get("metadata", {})
                    testmo_id = metadata.get("testmo_id")
                    test_id = metadata.get("id", "TC00000")
                    test_name = metadata.get("name", "untitled")

                    # Generate expected filename based on Testmo ID
                    expected_filename = f"{test_id}-{safe_filename(test_name)}.yml"
                    expected_filepath = feature_dir / expected_filename

                    # Check if we're updating an existing file
                    existing_file = existing_files.get(testmo_id) if testmo_id else None

                    if existing_file and existing_file.exists():
                        # File exists with this testmo_id
                        # Check if it needs to be renamed
                        if existing_file.name != expected_filename:
                            # RENAME: Testmo ID changed or name changed
                            console.print(f"[yellow]Renaming:[/yellow] {existing_file.name} → {expected_filename}")
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

                    # Remove old file if we renamed
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
        console.print("\n[bold]Next steps:[/bold]")
        console.print("1. Review the exported YAML files")
        console.print("2. Initialize git repository: [cyan]git init && git add . && git commit -m 'Initial export'[/cyan]")
        console.print("3. Create a feature branch: [cyan]git checkout -b improve-tests[/cyan]")
        console.print("4. Make improvements and commit changes")
        
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    export_from_testmo()
