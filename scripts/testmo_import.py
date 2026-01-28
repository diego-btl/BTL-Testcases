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


def load_yaml_files(directory: Path) -> List[Dict[str, Any]]:
    """Load all YAML test case files from directory"""
    yaml_cases = []
    
    for yaml_file in directory.rglob("*.yml"):
        try:
            with open(yaml_file, 'r') as f:
                case = yaml.safe_load(f)
                if case and "metadata" in case:
                    case["_source_file"] = str(yaml_file)
                    yaml_cases.append(case)
        except Exception as e:
            console.print(f"[yellow]Warning: Could not load {yaml_file}: {e}[/yellow]")
    
    return yaml_cases


@click.command()
@click.option("--project-id", type=int, help="Testmo project ID", envvar="TESTMO_PROJECT_ID")
@click.option("--input-dir", type=Path, default="test-cases", help="Input directory with YAML files")
@click.option("--folder-name", type=str, help="Target folder name in Testmo (will be created if needed)")
@click.option("--dry-run", is_flag=True, help="Show what would be imported without actually importing")
@click.option("--update-existing", is_flag=True, help="Update existing cases (match by testmo_id)")
def import_to_testmo(project_id: int, input_dir: Path, folder_name: str, dry_run: bool, update_existing: bool):
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
            yaml_cases = load_yaml_files(input_dir)
            console.print(f"[green]✓[/green] Loaded {len(yaml_cases)} YAML files")
        
        if not yaml_cases:
            console.print("[yellow]No YAML test cases found[/yellow]")
            return
        
        # Convert to Testmo format
        testmo_cases = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Converting to Testmo format...", total=len(yaml_cases))
            
            for yaml_case in yaml_cases:
                testmo_case = converter.yaml_to_testmo(yaml_case)
                
                # Add folder_id if specified
                if folder_id:
                    testmo_case["folder_id"] = folder_id
                
                # Store metadata for tracking
                testmo_case["_yaml_metadata"] = yaml_case.get("metadata", {})
                testmo_case["_source_file"] = yaml_case.get("_source_file")
                
                testmo_cases.append(testmo_case)
                progress.advance(task)
        
        console.print(f"[green]✓[/green] Converted {len(testmo_cases)} test cases")
        
        if dry_run:
            # Show what would be imported
            table = Table(title="Would Import")
            table.add_column("ID", style="cyan")
            table.add_column("Name", style="magenta")
            table.add_column("Priority", style="yellow")
            table.add_column("Feature", style="green")
            
            for case in testmo_cases[:10]:  # Show first 10
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
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Importing to Testmo...", total=len(testmo_cases))
            
            for case in testmo_cases:
                try:
                    metadata = case.get("_yaml_metadata", {})
                    testmo_id = metadata.get("testmo_id")
                    
                    # Remove internal fields before sending to API
                    case.pop("_yaml_metadata", None)
                    case.pop("_source_file", None)
                    
                    if testmo_id and update_existing:
                        # Update existing case
                        client.update_case(testmo_id, case)
                        updated += 1
                    else:
                        # Create new case
                        result = client.create_case(project_id, case)
                        created += 1
                        
                        # TODO: Update YAML file with testmo_id
                        # This would require updating the source file
                        
                except Exception as e:
                    console.print(f"[red]Failed to import {metadata.get('id', 'unknown')}: {e}[/red]")
                    failed += 1
                
                progress.advance(task)
        
        # Summary
        console.print(f"\n[bold green]Import Complete![/bold green]")
        console.print(f"  Created: {created}")
        console.print(f"  Updated: {updated}")
        console.print(f"  Failed: {failed}")
        
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    import_to_testmo()
