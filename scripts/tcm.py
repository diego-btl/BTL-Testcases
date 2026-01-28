#!/usr/bin/env python3
"""
Test Case Management CLI
Main entry point for all operations
"""
import sys
from pathlib import Path
import click
from rich.console import Console

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from testmo_export import export_from_testmo
from testmo_import import import_to_testmo
from validate_yaml import validate_yaml

console = Console()

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version='1.0.0', prog_name='tcm')
def cli():
    """
    Test Case Management (TCM) CLI
    
    Git-first test case management with Testmo sync.
    
    Examples:
      tcm export --project-id 1 --feature remote-services
      tcm import --project-id 1 --folder-name "Remote Services"
      tcm validate
    """
    pass


# Register subcommands
cli.add_command(export_from_testmo, name='export')
cli.add_command(import_to_testmo, name='import')
cli.add_command(validate_yaml, name='validate')


@cli.command()
def info():
    """Show system information"""
    console.print("\n[bold blue]Test Case Management System[/bold blue]")
    console.print("=" * 50)
    
    # Check environment
    from dotenv import load_dotenv
    import os
    
    load_dotenv()
    
    testmo_url = os.getenv("TESTMO_URL")
    testmo_project = os.getenv("TESTMO_PROJECT_ID")
    
    console.print(f"\n[bold]Configuration:[/bold]")
    console.print(f"  Testmo URL: {testmo_url or '[red]Not set[/red]'}")
    console.print(f"  Project ID: {testmo_project or '[red]Not set[/red]'}")
    
    # Check Git
    import subprocess
    try:
        result = subprocess.run(['git', 'rev-parse', '--show-toplevel'], 
                              capture_output=True, text=True, check=True)
        git_root = result.stdout.strip()
        console.print(f"  Git Root: [green]{git_root}[/green]")
        
        # Current branch
        result = subprocess.run(['git', 'branch', '--show-current'],
                              capture_output=True, text=True, check=True)
        branch = result.stdout.strip()
        console.print(f"  Current Branch: [cyan]{branch}[/cyan]")
    except:
        console.print(f"  Git: [yellow]Not a git repository[/yellow]")
    
    # Count test cases
    test_dir = Path("test-cases")
    if test_dir.exists():
        yaml_files = list(test_dir.rglob("*.yml")) + list(test_dir.rglob("*.yaml"))
        console.print(f"  Test Cases: [green]{len(yaml_files)}[/green]")
    else:
        console.print(f"  Test Cases: [yellow]test-cases/ not found[/yellow]")
    
    console.print("\n[bold]Commands:[/bold]")
    console.print("  tcm export   - Export from Testmo to YAML")
    console.print("  tcm import   - Import from YAML to Testmo")
    console.print("  tcm validate - Validate YAML format")
    console.print("  tcm info     - Show this information")
    
    console.print("\n[dim]Run 'tcm COMMAND --help' for more information[/dim]\n")


@cli.command()
def init():
    """Initialize a new test case repository"""
    console.print("\n[bold blue]Initialize Test Case Repository[/bold blue]")
    console.print("=" * 50)
    
    # Check if already initialized
    if Path(".git").exists():
        console.print("[yellow]Git repository already initialized[/yellow]")
    else:
        import subprocess
        subprocess.run(['git', 'init'], check=True)
        console.print("[green]✓[/green] Git repository initialized")
    
    # Create directories
    dirs = ["test-cases", "scripts", "docs", ".github/workflows"]
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    console.print("[green]✓[/green] Created directory structure")
    
    # Create .gitignore if not exists
    gitignore = Path(".gitignore")
    if not gitignore.exists():
        gitignore.write_text("""
# Environment
.env
.env.local

# Python
__pycache__/
*.pyc
venv/

# IDE
.vscode/
.idea/

# OS
.DS_Store
""")
        console.print("[green]✓[/green] Created .gitignore")
    
    console.print("\n[bold green]Repository initialized![/bold green]")
    console.print("\n[bold]Next steps:[/bold]")
    console.print("1. Configure .env file with Testmo credentials")
    console.print("2. Run: [cyan]tcm export --project-id YOUR_PROJECT_ID[/cyan]")
    console.print("3. Commit: [cyan]git add . && git commit -m 'Initial export'[/cyan]")


if __name__ == "__main__":
    cli()
