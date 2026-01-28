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
        
        # Convert to YAML format
        yaml_cases = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Converting to YAML format...", total=len(cases))
            
            for case in cases:
                yaml_case = converter.testmo_to_yaml(case, feature=feature or "general")
                yaml_cases.append(yaml_case)
                progress.advance(task)
        
        console.print(f"[green]✓[/green] Converted {len(yaml_cases)} test cases")
        
        # Organize by feature
        organized = organize_by_feature(yaml_cases)
        
        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Write YAML files
        total_written = 0
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Writing YAML files...", total=len(yaml_cases))
            
            for feature_name, feature_cases in organized.items():
                # Create feature directory
                feature_dir = output_dir / feature_name
                feature_dir.mkdir(parents=True, exist_ok=True)
                
                for case in feature_cases:
                    metadata = case.get("metadata", {})
                    test_id = metadata.get("id", "TC00000")
                    test_name = metadata.get("name", "untitled")
                    
                    # Generate filename
                    filename = f"{test_id}-{safe_filename(test_name)}.yml"
                    filepath = feature_dir / filename
                    
                    # Write YAML file
                    with open(filepath, 'w') as f:
                        yaml.dump(case, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
                    
                    total_written += 1
                    progress.advance(task)
        
        console.print(f"[green]✓[/green] Written {total_written} YAML files to {output_dir}")
        
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
