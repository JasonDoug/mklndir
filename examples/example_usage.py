#!/usr/bin/env python3
"""
Example usage script for the directory hardlinking tool.

This script demonstrates practical use cases for hardlinking directories,
including backup scenarios, development workflows, and content organization.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add the parent directory to the path so we can import mklndir
sys.path.insert(0, str(Path(__file__).parent.parent))

from mklndir.core import DirectoryHardlinker


def example_backup_system():
    """
    Example: Creating space-efficient backups using hardlinks.

    This simulates a backup system where each backup is a full copy
    but unchanged files are hardlinked to save space.
    """
    print("=" * 60)
    print("EXAMPLE 1: Space-Efficient Backup System")
    print("=" * 60)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create a "project" directory with some files
        project_dir = temp_path / "my_project"
        project_dir.mkdir()

        (project_dir / "main.py").write_text("""
def main():
    print("Hello, World!")

if __name__ == "__main__":
    main()
""")
        (project_dir / "README.md").write_text(
            "# My Project\n\nA simple Python project."
        )
        (project_dir / "requirements.txt").write_text("requests>=2.25.0\nclick>=7.0")

        src_dir = project_dir / "src"
        src_dir.mkdir()
        (src_dir / "utils.py").write_text("def helper_function():\n    return 'Helper'")

        print(f"Created project at: {project_dir}")
        print("Project structure:")
        for root, dirs, files in os.walk(project_dir):
            level = root.replace(str(project_dir), "").count(os.sep)
            indent = "  " * level
            print(f"{indent}{os.path.basename(root)}/")
            subindent = "  " * (level + 1)
            for file in files:
                print(f"{subindent}{file}")

        # Create first backup
        backup1_dir = temp_path / "backups" / "backup_001"
        hardlinker = DirectoryHardlinker(verbose=False)

        print(f"\nCreating first backup at: {backup1_dir}")
        success = hardlinker.hardlink_directory(project_dir, backup1_dir)

        if success:
            print("✅ First backup created successfully!")
            hardlinker.print_stats()

        # Modify one file in the project
        (project_dir / "main.py").write_text("""
def main():
    print("Hello, World! Updated version")
    print("Added new functionality")

if __name__ == "__main__":
    main()
""")

        # Create second backup (most files will be hardlinked, only changed file copied)
        backup2_dir = temp_path / "backups" / "backup_002"
        hardlinker2 = DirectoryHardlinker(verbose=False)

        print(f"\nCreating second backup at: {backup2_dir}")
        success2 = hardlinker2.hardlink_directory(project_dir, backup2_dir)

        if success2:
            print("✅ Second backup created successfully!")
            hardlinker2.print_stats()

        # Show space savings
        print("\nSpace usage demonstration:")
        print("- In a traditional backup: each file would be copied")
        print("- With hardlinks: unchanged files share storage")

        # Check if files are hardlinked
        readme1 = backup1_dir / "README.md"
        readme2 = backup2_dir / "README.md"
        main1 = backup1_dir / "main.py"
        main2 = backup2_dir / "main.py"

        print(
            f"\nREADME.md (unchanged) - Same inode in both backups: {readme1.samefile(readme2)}"
        )
        print(f"main.py (changed) - Different files: {not main1.samefile(main2)}")


def example_development_workflow():
    """
    Example: Development workflow with multiple build directories.

    Link source code to different build directories for debug/release builds.
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Development Build Workflow")
    print("=" * 60)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create source directory
        src_dir = temp_path / "project" / "src"
        src_dir.mkdir(parents=True)

        # Add source files
        (src_dir / "main.cpp").write_text("""
#include <iostream>

int main() {
    std::cout << "Hello, World!" << std::endl;
    return 0;
}
""")
        (src_dir / "utils.cpp").write_text("""
#include "utils.h"

void utility_function() {
    // Implementation here
}
""")
        (src_dir / "utils.h").write_text("""
#ifndef UTILS_H
#define UTILS_H

void utility_function();

#endif
""")

        print(f"Created source directory: {src_dir}")

        # Create debug and release build directories
        debug_dir = temp_path / "builds" / "debug" / "src"
        release_dir = temp_path / "builds" / "release" / "src"

        hardlinker = DirectoryHardlinker(verbose=True)

        print(f"\nLinking source to debug build: {debug_dir}")
        hardlinker.hardlink_directory(
            src_dir, debug_dir, exclude_patterns=["*.o", "*.obj", "*.exe", "*.out"]
        )

        print(f"\nLinking source to release build: {release_dir}")
        hardlinker.hardlink_directory(
            src_dir, release_dir, exclude_patterns=["*.o", "*.obj", "*.exe", "*.out"]
        )

        print("\n✅ Source code linked to both build directories!")
        print("Benefits:")
        print("- No storage duplication for source files")
        print("- Changes in source immediately reflect in all builds")
        print("- Build artifacts are kept separate")

        # Verify hardlinks
        main_src = src_dir / "main.cpp"
        main_debug = debug_dir / "main.cpp"
        main_release = release_dir / "main.cpp"

        print(f"\nVerification - All main.cpp files are hardlinked:")
        print(f"  Source ↔ Debug: {main_src.samefile(main_debug)}")
        print(f"  Source ↔ Release: {main_src.samefile(main_release)}")
        print(f"  Debug ↔ Release: {main_debug.samefile(main_release)}")


def example_content_organization():
    """
    Example: Organizing media files in multiple directory structures.
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Content Organization")
    print("=" * 60)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create original media library
        media_dir = temp_path / "media_library"

        # Create directories by date
        (media_dir / "2023" / "01_January").mkdir(parents=True)
        (media_dir / "2023" / "02_February").mkdir(parents=True)

        # Add sample media files
        (media_dir / "2023" / "01_January" / "vacation_photo1.jpg").write_text(
            "fake image data 1"
        )
        (media_dir / "2023" / "01_January" / "vacation_photo2.jpg").write_text(
            "fake image data 2"
        )
        (media_dir / "2023" / "02_February" / "family_dinner.jpg").write_text(
            "fake image data 3"
        )
        (media_dir / "2023" / "02_February" / "concert_video.mp4").write_text(
            "fake video data"
        )

        print(f"Created media library organized by date: {media_dir}")

        # Create alternative organization by type
        by_type_dir = temp_path / "by_type"
        photos_dir = by_type_dir / "photos"
        videos_dir = by_type_dir / "videos"

        hardlinker = DirectoryHardlinker(verbose=True)

        print(f"\nCreating photos collection: {photos_dir}")
        # Link only photo files to photos directory
        hardlinker.hardlink_directory(
            media_dir,
            photos_dir,
            exclude_patterns=["*.mp4", "*.avi", "*.mov"],  # Exclude videos
        )

        print(f"\nCreating videos collection: {videos_dir}")
        # Link only video files to videos directory
        hardlinker.hardlink_directory(
            media_dir,
            videos_dir,
            exclude_patterns=["*.jpg", "*.png", "*.gif"],  # Exclude images
        )

        print("\n✅ Media organized by both date and type!")
        print("Benefits:")
        print("- Same files accessible through different organizational schemes")
        print("- No storage duplication")
        print("- Changes propagate across all organizations")

        # Show the different organizations
        print(f"\nBy Date structure:")
        for root, dirs, files in os.walk(media_dir):
            level = root.replace(str(media_dir), "").count(os.sep)
            indent = "  " * level
            print(f"{indent}{os.path.basename(root)}/")
            subindent = "  " * (level + 1)
            for file in files:
                print(f"{subindent}{file}")

        print(f"\nBy Type structure:")
        for root, dirs, files in os.walk(by_type_dir):
            level = root.replace(str(by_type_dir), "").count(os.sep)
            indent = "  " * level
            print(f"{indent}{os.path.basename(root)}/")
            subindent = "  " * (level + 1)
            for file in files:
                print(f"{subindent}{file}")


def example_dry_run_preview():
    """
    Example: Using dry run to preview operations before execution.
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Preview Operations with Dry Run")
    print("=" * 60)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create a complex directory structure
        source_dir = temp_path / "complex_source"

        # Create nested structure with various file types
        (source_dir / "documents").mkdir(parents=True)
        (source_dir / "images" / "2023").mkdir(parents=True)
        (source_dir / "temp").mkdir(parents=True)

        # Add files
        (source_dir / "documents" / "report.pdf").write_text("PDF content")
        (source_dir / "documents" / "notes.txt").write_text("Text notes")
        (source_dir / "images" / "2023" / "photo.jpg").write_text("Image data")
        (source_dir / "temp" / "cache.tmp").write_text("Temp data")
        (source_dir / "temp" / "log.log").write_text("Log entries")
        (source_dir / "config.json").write_text('{"setting": "value"}')

        print(f"Created complex source directory: {source_dir}")

        target_dir = temp_path / "target_preview"

        # First, show what would happen with no exclusions
        print(f"\n--- DRY RUN: All files ---")
        hardlinker1 = DirectoryHardlinker(verbose=True, dry_run=True)
        hardlinker1.hardlink_directory(source_dir, target_dir)
        hardlinker1.print_stats()

        # Then show what would happen with exclusions
        print(f"\n--- DRY RUN: Excluding temp files ---")
        hardlinker2 = DirectoryHardlinker(verbose=True, dry_run=True)
        hardlinker2.hardlink_directory(
            source_dir, target_dir, exclude_patterns=["*.tmp", "*.log", "temp"]
        )
        hardlinker2.print_stats()

        print("\n✅ Dry run shows exactly what will happen!")
        print("Benefits:")
        print("- Preview operations before execution")
        print("- Test exclusion patterns")
        print("- Estimate time and space requirements")
        print("- Verify directory structures")


def main():
    """Run all example scenarios."""
    print("DIRECTORY HARDLINKING TOOL - USAGE EXAMPLES")
    print(
        "This script demonstrates practical applications of hardlinking directories.\n"
    )

    try:
        example_backup_system()
        example_development_workflow()
        example_content_organization()
        example_dry_run_preview()

        print("\n" + "=" * 60)
        print("ALL EXAMPLES COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("\nKey takeaways:")
        print("• Hardlinks save storage space by sharing file data")
        print("• Changes propagate across all hardlinked locations")
        print("• Useful for backups, build systems, and content organization")
        print("• Always test with --dry-run first")
        print("• Use exclusion patterns to filter unwanted files")

    except Exception as e:
        print(f"Example failed with error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
