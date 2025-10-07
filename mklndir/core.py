"""
Core functionality for directory hardlinking.

This module contains the DirectoryHardlinker class that handles the actual
hardlinking operations.
"""

import os
import fnmatch
from pathlib import Path
from typing import List, Optional


class DirectoryHardlinker:
    """Handles hardlinking of directory contents."""

    def __init__(self, verbose: bool = False, dry_run: bool = False):
        self.verbose = verbose
        self.dry_run = dry_run
        self.stats = {"files_linked": 0, "dirs_created": 0, "errors": 0, "skipped": 0}

    def log(self, message: str, level: str = "INFO") -> None:
        """Log messages if verbose mode is enabled."""
        if self.verbose:
            print(f"[{level}] {message}")

    def hardlink_directory(
        self,
        source: Path,
        target: Path,
        overwrite: bool = False,
        exclude_patterns: Optional[List[str]] = None,
    ) -> bool:
        """
        Hardlink all files from source directory to target directory.

        Args:
            source: Source directory path
            target: Target directory path
            overwrite: Whether to overwrite existing files
            exclude_patterns: List of patterns to exclude (glob-style)

        Returns:
            True if successful, False otherwise
        """
        if not source.exists():
            self.log(f"Source directory does not exist: {source}", "ERROR")
            return False

        if not source.is_dir():
            self.log(f"Source is not a directory: {source}", "ERROR")
            return False

        # Create target directory if it doesn't exist
        if not target.exists():
            if not self.dry_run:
                target.mkdir(parents=True, exist_ok=True)
            self.log(f"Created target directory: {target}")
            self.stats["dirs_created"] += 1

        try:
            return self._hardlink_recursive(source, target, overwrite, exclude_patterns)
        except Exception as e:
            self.log(f"Error during hardlinking: {e}", "ERROR")
            return False

    def _should_exclude(
        self, path: Path, exclude_patterns: Optional[List[str]]
    ) -> bool:
        """Check if a path should be excluded based on patterns."""
        if not exclude_patterns:
            return False

        path_str = str(path)
        for pattern in exclude_patterns:
            if fnmatch.fnmatch(path_str, pattern) or fnmatch.fnmatch(
                path.name, pattern
            ):
                return True
        return False

    def _hardlink_recursive(
        self,
        source: Path,
        target: Path,
        overwrite: bool,
        exclude_patterns: Optional[List[str]],
    ) -> bool:
        """Recursively hardlink files from source to target."""
        success = True

        try:
            for item in source.iterdir():
                if self._should_exclude(item, exclude_patterns):
                    self.log(f"Excluding: {item}")
                    self.stats["skipped"] += 1
                    continue

                target_item = target / item.name

                if item.is_file():
                    success &= self._hardlink_file(item, target_item, overwrite)
                elif item.is_dir():
                    # Create directory structure and recurse
                    if not target_item.exists():
                        if not self.dry_run:
                            target_item.mkdir(parents=True, exist_ok=True)
                        self.log(f"Created directory: {target_item}")
                        self.stats["dirs_created"] += 1

                    success &= self._hardlink_recursive(
                        item, target_item, overwrite, exclude_patterns
                    )
                else:
                    self.log(f"Skipping special file: {item}", "WARN")
                    self.stats["skipped"] += 1

        except PermissionError as e:
            self.log(f"Permission denied: {e}", "ERROR")
            self.stats["errors"] += 1
            success = False
        except Exception as e:
            self.log(f"Unexpected error: {e}", "ERROR")
            self.stats["errors"] += 1
            success = False

        return success

    def _hardlink_file(
        self, source_file: Path, target_file: Path, overwrite: bool
    ) -> bool:
        """Create a hardlink for a single file."""
        try:
            # Check if target already exists
            if target_file.exists():
                if not overwrite:
                    self.log(f"Target exists, skipping: {target_file}", "WARN")
                    self.stats["skipped"] += 1
                    return True
                else:
                    # Check if they're already hardlinked
                    if source_file.samefile(target_file):
                        self.log(f"Already hardlinked: {target_file}")
                        self.stats["skipped"] += 1
                        return True

                    if not self.dry_run:
                        target_file.unlink()  # Remove existing file
                    self.log(f"Removed existing file: {target_file}")

            # Create the hardlink
            if not self.dry_run:
                os.link(str(source_file), str(target_file))

            self.log(f"Hardlinked: {source_file} -> {target_file}")
            self.stats["files_linked"] += 1
            return True

        except OSError as e:
            if e.errno == 18:  # EXDEV - Cross-device link
                self.log(
                    f"Cannot hardlink across filesystems: {source_file} -> {target_file}",
                    "ERROR",
                )
            else:
                self.log(f"Error hardlinking {source_file}: {e}", "ERROR")
            self.stats["errors"] += 1
            return False
        except Exception as e:
            self.log(f"Unexpected error hardlinking {source_file}: {e}", "ERROR")
            self.stats["errors"] += 1
            return False

    def print_stats(self) -> None:
        """Print statistics about the hardlinking operation."""
        print("\nOperation Summary:")
        print(f"  Files hardlinked: {self.stats['files_linked']}")
        print(f"  Directories created: {self.stats['dirs_created']}")
        print(f"  Files skipped: {self.stats['skipped']}")
        print(f"  Errors: {self.stats['errors']}")
