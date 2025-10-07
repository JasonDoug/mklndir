"""
Command-line interface for mklndir.

This module contains the CLI argument parsing and main entry point for the
mklndir command-line tool.
"""

import sys
import argparse
from pathlib import Path
from typing import Optional

from .core import DirectoryHardlinker
from . import __version__


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        prog="mklndir",
        description="Hardlink all files from source directory to target directory",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  mklndir /path/to/source /path/to/target
  mklndir source_dir target_dir --verbose --dry-run
  mklndir src dst --overwrite --exclude "*.tmp" "*.log"

Note: Hardlinks can only be created within the same filesystem.
        """,
    )

    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )

    parser.add_argument("source", type=Path, help="Source directory path")
    parser.add_argument("target", type=Path, help="Target directory path")
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose output"
    )
    parser.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        help="Show what would be done without actually doing it",
    )
    parser.add_argument(
        "-o",
        "--overwrite",
        action="store_true",
        help="Overwrite existing files in target",
    )
    parser.add_argument(
        "-e",
        "--exclude",
        nargs="*",
        metavar="PATTERN",
        help="Exclude files/directories matching these patterns",
    )
    parser.add_argument(
        "--stats", action="store_true", help="Show operation statistics"
    )

    return parser


def validate_arguments(args) -> Optional[str]:
    """Validate command-line arguments and return error message if invalid."""
    if not args.source.exists():
        return f"Source directory does not exist: {args.source}"

    if not args.source.is_dir():
        return f"Source is not a directory: {args.source}"

    if args.target.exists() and not args.target.is_dir():
        return f"Target exists but is not a directory: {args.target}"

    return None


def check_filesystem_compatibility(source: Path, target: Path) -> None:
    """Check and warn if source and target are on different filesystems."""
    try:
        source_stat = source.stat()
        if target.exists():
            target_stat = target.stat()
            if source_stat.st_dev != target_stat.st_dev:
                print(
                    "Warning: Source and target appear to be on different filesystems.",
                    file=sys.stderr,
                )
                print(
                    "Hardlinks cannot be created across filesystems.", file=sys.stderr
                )
        else:
            # Check parent directory
            parent_stat = target.parent.stat()
            if source_stat.st_dev != parent_stat.st_dev:
                print(
                    "Warning: Source and target appear to be on different filesystems.",
                    file=sys.stderr,
                )
                print(
                    "Hardlinks cannot be created across filesystems.", file=sys.stderr
                )
    except (OSError, AttributeError):
        pass  # Can't check, proceed anyway


def main() -> int:
    """Main entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args()

    # Validate arguments
    error_msg = validate_arguments(args)
    if error_msg:
        print(f"Error: {error_msg}", file=sys.stderr)
        return 1

    # Check filesystem compatibility
    check_filesystem_compatibility(args.source, args.target)

    # Initialize hardlinker
    hardlinker = DirectoryHardlinker(verbose=args.verbose, dry_run=args.dry_run)

    if args.dry_run:
        print("DRY RUN MODE - No actual changes will be made\n")

    # Perform the hardlinking
    success = hardlinker.hardlink_directory(
        source=args.source,
        target=args.target,
        overwrite=args.overwrite,
        exclude_patterns=args.exclude,
    )

    # Show statistics if requested or in verbose mode
    if args.stats or args.verbose:
        hardlinker.print_stats()

    # Determine exit code
    if not success:
        print("Operation completed with errors.", file=sys.stderr)
        return 1
    elif hardlinker.stats["errors"] > 0:
        print("Operation completed but some errors occurred.", file=sys.stderr)
        return 1
    else:
        if not args.dry_run:
            print("Directory hardlinking completed successfully!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
