#!/usr/bin/env python3
"""
Test suite for the CLI module of mklndir.

This module tests the command-line interface functionality including
argument parsing, validation, and integration with the core module.
"""

import os
import sys
import tempfile
import subprocess
from pathlib import Path
from unittest.mock import patch
import pytest

# Add the parent directory to the path so we can import mklndir
sys.path.insert(0, str(Path(__file__).parent.parent))

from mklndir.cli import (
    main,
    create_parser,
    validate_arguments,
    check_filesystem_compatibility,
)
from mklndir.core import DirectoryHardlinker


class TestCLIArgumentParsing:
    """Test command-line argument parsing."""

    def test_parser_creation(self):
        """Test that parser is created correctly."""
        parser = create_parser()
        assert parser.prog == "mklndir"

    def test_required_arguments(self):
        """Test that required arguments are parsed correctly."""
        parser = create_parser()
        args = parser.parse_args(["source", "target"])
        assert args.source == Path("source")
        assert args.target == Path("target")

    def test_optional_arguments(self):
        """Test that optional arguments are parsed correctly."""
        parser = create_parser()
        args = parser.parse_args(
            [
                "source",
                "target",
                "--verbose",
                "--dry-run",
                "--overwrite",
                "--exclude",
                "*.tmp",
                "*.log",
                "--stats",
            ]
        )
        assert args.verbose is True
        assert args.dry_run is True
        assert args.overwrite is True
        assert args.exclude == ["*.tmp", "*.log"]
        assert args.stats is True

    def test_version_argument(self):
        """Test version argument."""
        parser = create_parser()
        with pytest.raises(SystemExit) as exc_info:
            parser.parse_args(["--version"])
        assert exc_info.value.code == 0


class TestCLIValidation:
    """Test CLI argument validation."""

    def test_validate_nonexistent_source(self):
        """Test validation with non-existent source."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            nonexistent = temp_path / "nonexistent"
            target = temp_path / "target"

            class Args:
                def __init__(self):
                    self.source = nonexistent
                    self.target = target

            error = validate_arguments(Args())
            assert "does not exist" in error

    def test_validate_source_not_directory(self):
        """Test validation when source is not a directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            source_file = temp_path / "source.txt"
            source_file.write_text("not a directory")
            target = temp_path / "target"

            class Args:
                def __init__(self):
                    self.source = source_file
                    self.target = target

            error = validate_arguments(Args())
            assert "not a directory" in error

    def test_validate_target_exists_not_directory(self):
        """Test validation when target exists but is not a directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            source = temp_path / "source"
            source.mkdir()
            target_file = temp_path / "target.txt"
            target_file.write_text("not a directory")

            class Args:
                def __init__(self):
                    self.source = source
                    self.target = target_file

            error = validate_arguments(Args())
            assert "not a directory" in error

    def test_validate_valid_arguments(self):
        """Test validation with valid arguments."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            source = temp_path / "source"
            source.mkdir()
            target = temp_path / "target"

            class Args:
                def __init__(self):
                    self.source = source
                    self.target = target

            error = validate_arguments(Args())
            assert error is None


class TestCLIIntegration:
    """Test CLI integration with core functionality."""

    def test_main_help(self):
        """Test that help works."""
        with patch.object(sys, "argv", ["mklndir", "--help"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0

    def test_main_nonexistent_source(self):
        """Test main with nonexistent source."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            nonexistent = temp_path / "nonexistent"
            target = temp_path / "target"

            with patch.object(sys, "argv", ["mklndir", str(nonexistent), str(target)]):
                exit_code = main()
                assert exit_code == 1

    def test_main_dry_run(self):
        """Test main with dry run."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            source = temp_path / "source"
            source.mkdir()
            (source / "test.txt").write_text("test content")
            target = temp_path / "target"

            with patch.object(
                sys, "argv", ["mklndir", str(source), str(target), "--dry-run"]
            ):
                exit_code = main()
                assert exit_code == 0
                # Target should not exist in dry run
                assert not target.exists()

    def test_main_successful_operation(self):
        """Test successful hardlinking operation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            source = temp_path / "source"
            source.mkdir()
            (source / "test.txt").write_text("test content")
            (source / "subdir").mkdir()
            (source / "subdir" / "nested.txt").write_text("nested content")
            target = temp_path / "target"

            with patch.object(
                sys, "argv", ["mklndir", str(source), str(target), "--verbose"]
            ):
                exit_code = main()
                assert exit_code == 0

                # Verify files were hardlinked
                assert target.exists()
                assert (target / "test.txt").exists()
                assert (target / "subdir" / "nested.txt").exists()

                # Verify they are actually hardlinked
                source_file = source / "test.txt"
                target_file = target / "test.txt"
                assert source_file.samefile(target_file)

    def test_main_with_exclusions(self):
        """Test main with file exclusions."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            source = temp_path / "source"
            source.mkdir()
            (source / "keep.txt").write_text("keep this")
            (source / "exclude.tmp").write_text("exclude this")
            target = temp_path / "target"

            with patch.object(
                sys,
                "argv",
                [
                    "mklndir",
                    str(source),
                    str(target),
                    "--exclude",
                    "*.tmp",
                    "--verbose",
                ],
            ):
                exit_code = main()
                assert exit_code == 0

                # Verify kept file is there
                assert (target / "keep.txt").exists()
                # Verify excluded file is not there
                assert not (target / "exclude.tmp").exists()

    def test_main_overwrite_behavior(self):
        """Test main with overwrite flag."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            source = temp_path / "source"
            source.mkdir()
            (source / "file.txt").write_text("new content")

            target = temp_path / "target"
            target.mkdir()
            (target / "file.txt").write_text("old content")

            # First without overwrite - should skip
            with patch.object(sys, "argv", ["mklndir", str(source), str(target)]):
                exit_code = main()
                assert exit_code == 0
                # File should still have old content
                assert (target / "file.txt").read_text() == "old content"

            # Now with overwrite - should replace
            with patch.object(
                sys, "argv", ["mklndir", str(source), str(target), "--overwrite"]
            ):
                exit_code = main()
                assert exit_code == 0
                # Files should now be hardlinked
                source_file = source / "file.txt"
                target_file = target / "file.txt"
                assert source_file.samefile(target_file)


class TestFilesystemCompatibility:
    """Test filesystem compatibility checking."""

    def test_check_filesystem_compatibility(self):
        """Test filesystem compatibility check function."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            source = temp_path / "source"
            source.mkdir()
            target = temp_path / "target"

            # Should not raise an exception
            check_filesystem_compatibility(source, target)


class TestCLIExecutable:
    """Test CLI as executable command."""

    def test_cli_executable_help(self):
        """Test that the CLI can be executed with help."""
        # Test using python -m
        result = subprocess.run(
            [sys.executable, "-m", "mklndir.cli", "--help"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        assert result.returncode == 0
        assert "mklndir" in result.stdout
        assert "source" in result.stdout
        assert "target" in result.stdout

    def test_cli_executable_version(self):
        """Test that the CLI version works."""
        result = subprocess.run(
            [sys.executable, "-m", "mklndir.cli", "--version"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        assert result.returncode == 0
        assert "mklndir" in result.stdout
        assert "1.0.0" in result.stdout


def test_main_direct_call():
    """Test calling main directly without patching argv."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        source = temp_path / "source"
        source.mkdir()
        (source / "test.txt").write_text("test")
        target = temp_path / "target"

        # Mock sys.argv for direct call
        original_argv = sys.argv
        try:
            sys.argv = ["mklndir", str(source), str(target)]
            exit_code = main()
            assert exit_code == 0
            assert (target / "test.txt").exists()
        finally:
            sys.argv = original_argv


if __name__ == "__main__":
    import pytest

    pytest.main([__file__])
