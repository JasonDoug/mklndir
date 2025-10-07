#!/usr/bin/env python3
"""
Test script for the directory hardlinking tool.

This script creates test directories and files, then demonstrates
the hardlink_dir.py functionality.
"""

import os
import tempfile
import shutil
from pathlib import Path
from mklndir.core import DirectoryHardlinker


def create_test_structure(base_dir: Path) -> None:
    """Create a test directory structure with various files."""
    # Create directories
    (base_dir / "subdir1").mkdir(parents=True)
    (base_dir / "subdir2" / "nested").mkdir(parents=True)

    # Create test files
    (base_dir / "file1.txt").write_text("Content of file1")
    (base_dir / "file2.py").write_text("print('Hello from file2')")
    (base_dir / "subdir1" / "nested_file.txt").write_text("Nested file content")
    (base_dir / "subdir2" / "another_file.md").write_text("# Markdown file")
    (base_dir / "subdir2" / "nested" / "deep_file.json").write_text('{"test": true}')
    (base_dir / "temp_file.tmp").write_text("Temporary file")
    (base_dir / "log_file.log").write_text("Log entry 1\nLog entry 2")


def test_basic_hardlinking():
    """Test basic directory hardlinking functionality."""
    print("=== Test: Basic Directory Hardlinking ===")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        source_dir = temp_path / "source"
        target_dir = temp_path / "target"

        # Create test structure
        source_dir.mkdir()
        create_test_structure(source_dir)

        print(f"Source directory: {source_dir}")
        print(f"Target directory: {target_dir}")

        # Initialize hardlinker
        hardlinker = DirectoryHardlinker(verbose=True)

        # Perform hardlinking
        success = hardlinker.hardlink_directory(source_dir, target_dir)

        if success:
            print("✅ Hardlinking successful!")

            # Verify structure
            print("\nVerifying directory structure:")
            for root, dirs, files in os.walk(target_dir):
                level = root.replace(str(target_dir), "").count(os.sep)
                indent = " " * 2 * level
                print(f"{indent}{os.path.basename(root)}/")
                subindent = " " * 2 * (level + 1)
                for file in files:
                    print(f"{subindent}{file}")

            # Verify hardlinks
            print("\nVerifying hardlinks:")
            source_file = source_dir / "file1.txt"
            target_file = target_dir / "file1.txt"

            if source_file.samefile(target_file):
                print("✅ Files are properly hardlinked")
                print(f"   Inode: {source_file.stat().st_ino}")
            else:
                print("❌ Files are not hardlinked")

        else:
            print("❌ Hardlinking failed!")

        hardlinker.print_stats()


def test_with_exclusions():
    """Test hardlinking with file exclusions."""
    print("\n=== Test: Hardlinking with Exclusions ===")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        source_dir = temp_path / "source"
        target_dir = temp_path / "target_exclude"

        # Create test structure
        source_dir.mkdir()
        create_test_structure(source_dir)

        # Initialize hardlinker with exclusions
        hardlinker = DirectoryHardlinker(verbose=True)

        # Exclude temporary and log files
        exclude_patterns = ["*.tmp", "*.log"]

        print(f"Excluding patterns: {exclude_patterns}")

        success = hardlinker.hardlink_directory(
            source_dir, target_dir, exclude_patterns=exclude_patterns
        )

        if success:
            print("✅ Hardlinking with exclusions successful!")

            # Check that excluded files are not present
            temp_file = target_dir / "temp_file.tmp"
            log_file = target_dir / "log_file.log"

            if not temp_file.exists() and not log_file.exists():
                print("✅ Excluded files properly filtered out")
            else:
                print("❌ Some excluded files were not filtered")

        hardlinker.print_stats()


def test_dry_run():
    """Test dry run functionality."""
    print("\n=== Test: Dry Run Mode ===")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        source_dir = temp_path / "source"
        target_dir = temp_path / "target_dryrun"

        # Create test structure
        source_dir.mkdir()
        create_test_structure(source_dir)

        # Initialize hardlinker in dry run mode
        hardlinker = DirectoryHardlinker(verbose=True, dry_run=True)

        print("Running in DRY RUN mode...")

        success = hardlinker.hardlink_directory(source_dir, target_dir)

        if success:
            print("✅ Dry run completed successfully!")

            # Verify that no actual files were created
            if not target_dir.exists():
                print("✅ No files actually created (as expected in dry run)")
            else:
                print("❌ Files were created despite dry run mode")

        hardlinker.print_stats()


def test_overwrite_behavior():
    """Test overwrite functionality."""
    print("\n=== Test: Overwrite Behavior ===")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        source_dir = temp_path / "source"
        target_dir = temp_path / "target_overwrite"

        # Create test structure
        source_dir.mkdir()
        target_dir.mkdir()
        create_test_structure(source_dir)

        # Create a conflicting file in target
        conflicting_file = target_dir / "file1.txt"
        conflicting_file.write_text("Different content")

        print(f"Created conflicting file: {conflicting_file}")

        # Test without overwrite (should skip)
        hardlinker1 = DirectoryHardlinker(verbose=True)
        print("\nTesting without overwrite flag...")
        hardlinker1.hardlink_directory(source_dir, target_dir, overwrite=False)

        # Test with overwrite
        hardlinker2 = DirectoryHardlinker(verbose=True)
        print("\nTesting with overwrite flag...")
        hardlinker2.hardlink_directory(source_dir, target_dir, overwrite=True)

        # Verify the file was overwritten and is now hardlinked
        source_file = source_dir / "file1.txt"
        target_file = target_dir / "file1.txt"

        if source_file.samefile(target_file):
            print("✅ File was successfully overwritten and hardlinked")
        else:
            print("❌ File was not properly overwritten")


def main():
    """Run all tests."""
    print("Starting Directory Hardlinking Tool Tests\n")

    try:
        test_basic_hardlinking()
        test_with_exclusions()
        test_dry_run()
        test_overwrite_behavior()

        print("\n" + "=" * 50)
        print("All tests completed!")

    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
