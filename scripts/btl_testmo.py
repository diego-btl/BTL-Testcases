#!/usr/bin/env python3
"""
BTL Testmo CLI - Main Entry Point

Unified command-line interface for all Testmo operations.

Usage:
    btl_testmo export --project-id 2 --output testmo/oneapp
    btl_testmo import --project-id 9 --source testmo/oneapp
    btl_testmo update testmo/oneapp/test-cases/folder/TC535-test.yml
    btl_testmo create testmo/oneapp/test-cases/folder/TC-NEW-test.yml
    btl_testmo sync --project testmo/oneapp
    btl_testmo status testmo/oneapp
    btl_testmo validate testmo/oneapp

For detailed help:
    btl_testmo --help
    btl_testmo <command> --help

Version: 1.0.0
Based on validation: TESTING_LOG.md (5/5 tests passed, 100% success rate)
"""

import sys
import argparse
from pathlib import Path
from typing import List, Optional

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from testmo_sync.hasher import ContentHasher
from testmo_sync.mapper import FolderMapper
from testmo_sync.validator import YAMLValidator
from testmo_sync.converter import TestmoConverter
from testmo_sync.writer import TestmoWriter
from testmo_sync.sync_engine import SyncEngine


VERSION = "1.0.0"


class CLI:
    """BTL Testmo CLI application."""

    def __init__(self):
        self.parser = self._create_parser()

    def _create_parser(self) -> argparse.ArgumentParser:
        """Create argument parser with all commands."""
        parser = argparse.ArgumentParser(
            description="BTL TestCases Framework - Testmo Sync CLI",
            epilog="For more information, see docs/ directory"
        )

        parser.add_argument('--version', action='version', version=f'%(prog)s {VERSION}')

        subparsers = parser.add_subparsers(dest='command', help='Available commands')

        # Export command
        export_parser = subparsers.add_parser('export', help='Export test cases from Testmo')
        export_parser.add_argument('--project-id', type=int, required=True, help='Testmo project ID')
        export_parser.add_argument('--output', type=Path, required=True, help='Output directory')
        export_parser.add_argument('--incremental', action='store_true', help='Only export new/modified cases')

        # Import command
        import_parser = subparsers.add_parser('import', help='Import test cases to Testmo')
        import_parser.add_argument('--project-id', type=int, required=True, help='Testmo project ID')
        import_parser.add_argument('--source', type=Path, required=True, help='Source directory')
        import_parser.add_argument('--new-only', action='store_true', help='Only import TC-NEW-* files')

        # Update command
        update_parser = subparsers.add_parser('update', help='Update test cases in Testmo')
        update_parser.add_argument('files', nargs='*', type=Path, help='YAML files to update')
        update_parser.add_argument('--case-id', type=int, help='Update specific case by ID')
        update_parser.add_argument('--folder', type=Path, help='Update all changed files in folder')
        update_parser.add_argument('--project', type=Path, help='Update all changed files in project')
        update_parser.add_argument('--project-id', type=int, help='Project ID (required with --case-id)')

        # Create command
        create_parser = subparsers.add_parser('create', help='Create new test cases in Testmo')
        create_parser.add_argument('files', nargs='*', type=Path, help='YAML files to create')
        create_parser.add_argument('--folder', type=Path, help='Create all TC-NEW-* files in folder')
        create_parser.add_argument('--project', type=Path, help='Create all TC-NEW-* files in project')
        create_parser.add_argument('--new-only', action='store_true', help='Only create TC-NEW-* files')

        # Sync command
        sync_parser = subparsers.add_parser('sync', help='Bidirectional sync')
        sync_parser.add_argument('--project', type=Path, required=True, help='Project directory')
        sync_parser.add_argument('--direction', choices=['push', 'pull', 'bidirectional'],
                                default='bidirectional', help='Sync direction')
        sync_parser.add_argument('--dry-run', action='store_true', help='Show changes without applying')
        sync_parser.add_argument('--auto-resolve', action='store_true', help='Auto-resolve conflicts (newer wins)')

        # Status command
        status_parser = subparsers.add_parser('status', help='Show sync status')
        status_parser.add_argument('project', type=Path, help='Project directory')

        # Validate command
        validate_parser = subparsers.add_parser('validate', help='Validate YAML files')
        validate_parser.add_argument('files', nargs='+', type=Path, help='Files or directories to validate')
        validate_parser.add_argument('--fix', action='store_true', help='Auto-fix common issues')

        # Info command
        info_parser = subparsers.add_parser('info', help='Show project information')
        info_parser.add_argument('--project-id', type=int, required=True, help='Testmo project ID')

        # Folders command
        folders_parser = subparsers.add_parser('folders', help='List project folders')
        folders_parser.add_argument('--project-id', type=int, required=True, help='Testmo project ID')

        # Stats command
        stats_parser = subparsers.add_parser('stats', help='Show project statistics')
        stats_parser.add_argument('project', type=Path, help='Project directory')

        return parser

    def run(self, args: Optional[List[str]] = None):
        """Run CLI with given arguments."""
        parsed_args = self.parser.parse_args(args)

        if not parsed_args.command:
            self.parser.print_help()
            return 1

        # Route to appropriate handler
        handler = getattr(self, f'cmd_{parsed_args.command}', None)
        if not handler:
            print(f"Error: Command '{parsed_args.command}' not implemented yet")
            return 1

        try:
            return handler(parsed_args)
        except Exception as e:
            print(f"Error: {e}")
            return 1

    def cmd_export(self, args):
        """Handle export command."""
        print(f"BTL Testmo Export")
        print(f"Project ID: {args.project_id}")
        print(f"Output: {args.output}")
        print()

        print("⚠️  Export command requires MCP integration")
        print("This should be executed by Claude/Claude Code with MCP access")
        print()
        print("Expected workflow:")
        print("1. Call MCP: testmo.list_folders(project_id)")
        print("2. Build folder hierarchy and save to .sync/folder-map.json")
        print("3. Call MCP: testmo.get_all_cases(project_id)")
        print("4. Convert each case to YAML format")
        print("5. Compute hashes")
        print("6. Write files to output directory")
        print("7. Save metadata to .sync/ directory")
        print()
        print("See: scripts/legacy/testmo_export.py for reference")
        print("See: TESTING_LOG.md for validated performance (1334 cases in ~1 min)")

        return 0

    def cmd_import(self, args):
        """Handle import command."""
        print(f"BTL Testmo Import")
        print(f"Project ID: {args.project_id}")
        print(f"Source: {args.source}")
        print()

        print("⚠️  Import command requires MCP integration")
        print("This should be executed by Claude/Claude Code with MCP access")
        print()
        print("Expected workflow:")
        print("1. Load folder mappings from .sync/folder-map.json")
        print("2. Find all YAML files in source directory")
        print("3. Convert each YAML to Testmo format")
        print("4. Use batch create for efficiency (5 cases = ~393ms)")
        print("5. Update files with new case_ids")
        print("6. Rename TC-NEW-* files to TC{id}-*")
        print("7. Update metadata")
        print()
        print("See: scripts/legacy/testmo_import.py for reference")
        print("See: TESTING_LOG.md for validated performance (1334 cases in ~1 min)")

        return 0

    def cmd_update(self, args):
        """Handle update command."""
        print(f"BTL Testmo Update")

        if args.files:
            print(f"Files: {len(args.files)}")
            for file in args.files:
                print(f"  - {file}")
        elif args.folder:
            print(f"Folder: {args.folder}")
        elif args.project:
            print(f"Project: {args.project}")
        elif args.case_id:
            print(f"Case ID: {args.case_id}")

        print()
        print("⚠️  Update implementation in progress")
        print()
        print("Expected workflow:")
        print("1. Detect changed files (hash comparison)")
        print("2. Validate files")
        print("3. Convert to Testmo format")
        print("4. Use batch update for efficiency (hybrid approach)")
        print("5. Update hashes and timestamps")
        print()
        print("Performance: ~223ms per case (individual), ~1.5s for 5 cases (batch)")

        return 0

    def cmd_create(self, args):
        """Handle create command."""
        print(f"BTL Testmo Create")

        if args.files:
            print(f"Files: {len(args.files)}")
        elif args.folder:
            print(f"Folder: {args.folder}")
        elif args.project:
            print(f"Project: {args.project}")

        print()
        print("⚠️  Create implementation in progress")
        print()
        print("Expected workflow:")
        print("1. Find all TC-NEW-* files")
        print("2. Validate files")
        print("3. Convert to Testmo format")
        print("4. Use batch create (3.3x faster than individual)")
        print("5. Rename files: TC-NEW-* → TC{id}-*")
        print("6. Add testmo metadata")
        print("7. Compute and save hashes")
        print()
        print("Performance: ~150ms per case (individual), ~393ms for 5 cases (batch)")

        return 0

    def cmd_sync(self, args):
        """Handle sync command."""
        print(f"BTL Testmo Sync")
        print(f"Project: {args.project}")
        print(f"Direction: {args.direction}")
        print(f"Dry run: {args.dry_run}")
        print()

        if args.dry_run:
            print("⚠️  Dry run mode - no changes will be made")
            print()

        print("⚠️  Sync implementation in progress")
        print()
        print("Expected workflow:")
        print("1. Detect local changes (hash comparison)")
        print("2. Detect remote changes (timestamp comparison)")
        print("3. Detect conflicts")
        print("4. Push local changes (if direction allows)")
        print("5. Pull remote changes (if direction allows)")
        print("6. Update all metadata")

        return 0

    def cmd_status(self, args):
        """Handle status command."""
        print(f"BTL Testmo Status")
        print(f"Project: {args.project}")
        print()

        if not args.project.exists():
            print(f"Error: Project directory not found: {args.project}")
            return 1

        # Load sync metadata
        sync_dir = args.project / ".sync"
        if not sync_dir.exists():
            print("⚠️  No sync metadata found (.sync/ directory missing)")
            print("Run 'btl_testmo export' first")
            return 1

        # Show basic stats
        test_cases_dir = args.project / "test-cases"
        if test_cases_dir.exists():
            yaml_files = list(test_cases_dir.rglob("*.yml"))
            print(f"Total test cases: {len(yaml_files)}")

            # Check for changes
            hasher = ContentHasher()
            changed_files = hasher.batch_check(test_cases_dir)

            if changed_files:
                print(f"⚠️  {len(changed_files)} files changed locally (need push)")
                for file in changed_files[:5]:  # Show first 5
                    print(f"  - {file.name}")
                if len(changed_files) > 5:
                    print(f"  ... and {len(changed_files) - 5} more")
            else:
                print("✓ All files synced (no local changes)")

        return 0

    def cmd_validate(self, args):
        """Handle validate command."""
        print(f"BTL Testmo Validate")
        print(f"Files: {len(args.files)}")
        print()

        validator = YAMLValidator()
        total_files = 0
        total_errors = 0
        total_warnings = 0

        for path in args.files:
            if path.is_dir():
                # Validate all YAML files in directory
                for yaml_file in path.rglob("*.yml"):
                    total_files += 1
                    is_valid, errors = validator.validate_file(yaml_file)

                    if not is_valid:
                        print(f"✗ {yaml_file}")
                        for error in errors:
                            if error.severity == "error":
                                total_errors += 1
                            else:
                                total_warnings += 1
                            print(f"  {error}")

                        if args.fix:
                            if validator.auto_fix(yaml_file):
                                print(f"  ✓ Auto-fixed")
                    else:
                        print(f"✓ {yaml_file}")
            else:
                # Validate single file
                total_files += 1
                is_valid, errors = validator.validate_file(path)

                if not is_valid:
                    print(f"✗ {path}")
                    for error in errors:
                        if error.severity == "error":
                            total_errors += 1
                        else:
                            total_warnings += 1
                        print(f"  {error}")

                    if args.fix:
                        if validator.auto_fix(path):
                            print(f"  ✓ Auto-fixed")
                else:
                    print(f"✓ {path}")

        print()
        print(f"Summary: {total_files} files, {total_errors} errors, {total_warnings} warnings")

        return 0 if total_errors == 0 else 1

    def cmd_info(self, args):
        """Handle info command."""
        print(f"BTL Testmo Info")
        print(f"Project ID: {args.project_id}")
        print()
        print("⚠️  Info command requires MCP/API access")
        print("This should be executed by Claude/Claude Code")

        return 0

    def cmd_folders(self, args):
        """Handle folders command."""
        print(f"BTL Testmo Folders")
        print(f"Project ID: {args.project_id}")
        print()
        print("⚠️  Folders command requires MCP access")
        print("This should be executed by Claude/Claude Code")
        print()
        print("Expected: Call MCP testmo.list_folders(project_id)")

        return 0

    def cmd_stats(self, args):
        """Handle stats command."""
        print(f"BTL Testmo Statistics")
        print(f"Project: {args.project}")
        print()

        if not args.project.exists():
            print(f"Error: Project directory not found: {args.project}")
            return 1

        test_cases_dir = args.project / "test-cases"
        if not test_cases_dir.exists():
            print("No test cases found")
            return 1

        # Count files
        yaml_files = list(test_cases_dir.rglob("*.yml"))
        print(f"Total test cases: {len(yaml_files)}")

        # Count by folder (top-level only)
        folders = {}
        for yaml_file in yaml_files:
            folder = yaml_file.parent.relative_to(test_cases_dir)
            top_folder = str(folder).split('/')[0] if '/' in str(folder) else str(folder)
            folders[top_folder] = folders.get(top_folder, 0) + 1

        print(f"\nBy top-level folder:")
        for folder, count in sorted(folders.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {folder}: {count}")

        # Count TC-NEW-* files
        new_files = [f for f in yaml_files if 'TC-NEW-' in f.name]
        if new_files:
            print(f"\nNew cases (TC-NEW-*): {len(new_files)}")

        return 0


def main():
    """Main entry point."""
    cli = CLI()
    return cli.run()


if __name__ == "__main__":
    sys.exit(main())
