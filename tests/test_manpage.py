#!/usr/bin/env python3
"""
Test suite for the man page of mklndir.

This module tests that the man page is properly included in the package
and has correct formatting.
"""

import os
import sys
import subprocess
from pathlib import Path
import pytest

# Add the parent directory to the path so we can import mklndir
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestManPage:
    """Test man page inclusion and formatting."""

    def test_man_page_exists(self):
        """Test that the man page file exists."""
        man_page = Path(__file__).parent.parent / "man" / "mklndir.1"
        assert man_page.exists(), "Man page file should exist at man/mklndir.1"
        assert man_page.is_file(), "Man page should be a regular file"

    def test_man_page_not_empty(self):
        """Test that the man page has content."""
        man_page = Path(__file__).parent.parent / "man" / "mklndir.1"
        content = man_page.read_text()
        assert len(content.strip()) > 0, "Man page should not be empty"
        assert len(content) > 1000, "Man page should have substantial content"

    def test_man_page_has_required_sections(self):
        """Test that the man page has all required sections."""
        man_page = Path(__file__).parent.parent / "man" / "mklndir.1"
        content = man_page.read_text()

        required_sections = [
            ".SH NAME",
            ".SH SYNOPSIS",
            ".SH DESCRIPTION",
            ".SH OPTIONS",
            ".SH ARGUMENTS",
            ".SH EXAMPLES",
            ".SH EXIT STATUS",
            ".SH SEE ALSO",
        ]

        for section in required_sections:
            assert section in content, f"Man page should contain {section} section"

    def test_man_page_has_correct_title(self):
        """Test that the man page has the correct title line."""
        man_page = Path(__file__).parent.parent / "man" / "mklndir.1"
        content = man_page.read_text()

        # Should have proper .TH line
        assert ".TH MKLNDIR 1" in content, "Man page should have correct .TH line"
        assert "mklndir 1.0.0" in content, "Man page should reference correct version"
        assert "User Commands" in content, (
            "Man page should be categorized as User Commands"
        )

    def test_man_page_has_name_section(self):
        """Test that the NAME section is properly formatted."""
        man_page = Path(__file__).parent.parent / "man" / "mklndir.1"
        content = man_page.read_text()

        # NAME section should contain the command name and brief description
        assert "mklndir \\- create hardlinks" in content, (
            "NAME section should have brief description"
        )

    def test_man_page_has_synopsis(self):
        """Test that the SYNOPSIS section is properly formatted."""
        man_page = Path(__file__).parent.parent / "man" / "mklndir.1"
        content = man_page.read_text()

        # SYNOPSIS should show the basic command format
        lines = content.split("\n")
        synopsis_found = False
        for i, line in enumerate(lines):
            if line.strip() == ".SH SYNOPSIS":
                synopsis_found = True
                # Should have the basic command format nearby
                nearby_text = " ".join(lines[i : i + 5])
                assert "mklndir" in nearby_text, "SYNOPSIS should show command name"
                assert "SOURCE" in nearby_text, "SYNOPSIS should show SOURCE argument"
                assert "TARGET" in nearby_text, "SYNOPSIS should show TARGET argument"
                break

        assert synopsis_found, "Should find SYNOPSIS section"

    def test_man_page_has_examples(self):
        """Test that the EXAMPLES section contains practical examples."""
        man_page = Path(__file__).parent.parent / "man" / "mklndir.1"
        content = man_page.read_text()

        # Should have multiple examples
        assert "mklndir /home/user/documents" in content, "Should have basic example"
        assert "--dry-run" in content, "Should have dry-run example"
        assert "--exclude" in content, "Should have exclusion example"

    def test_man_page_references_related_commands(self):
        """Test that the man page references related Unix commands."""
        man_page = Path(__file__).parent.parent / "man" / "mklndir.1"
        content = man_page.read_text()

        # SEE ALSO section should reference related commands
        related_commands = ["ln (1)", "cp (1)", "rsync (1)", "link (2)"]
        for cmd in related_commands:
            assert cmd in content, f"Man page should reference {cmd}"

    @pytest.mark.skipif(
        not subprocess.run(["which", "groff"], capture_output=True).returncode == 0,
        reason="groff not available",
    )
    def test_man_page_format_validation(self):
        """Test that the man page has valid groff formatting."""
        man_page = Path(__file__).parent.parent / "man" / "mklndir.1"

        # Try to render the man page with groff
        result = subprocess.run(
            ["groff", "-man", "-Tascii", str(man_page)], capture_output=True, text=True
        )

        assert result.returncode == 0, (
            f"groff should successfully render man page: {result.stderr}"
        )
        assert len(result.stdout) > 1000, (
            "Rendered man page should have substantial content"
        )
        assert "MKLNDIR(1)" in result.stdout, (
            "Rendered page should show command name and section"
        )

    @pytest.mark.skipif(
        not subprocess.run(["which", "man"], capture_output=True).returncode == 0,
        reason="man command not available",
    )
    def test_man_page_lint(self):
        """Test man page with man command if available."""
        man_page = Path(__file__).parent.parent / "man" / "mklndir.1"

        # Use man to check the format (some versions support -l for local files)
        result = subprocess.run(
            ["man", "-l", str(man_page)],
            capture_output=True,
            text=True,
            input="\n",  # Immediately quit
        )

        # man command should not report format errors (exit code varies by system)
        # We mainly check that it doesn't crash
        assert "mklndir" in result.stdout or result.returncode in [0, 1], (
            "man command should handle the page"
        )

    def test_man_page_includes_all_cli_options(self):
        """Test that man page documents all CLI options."""
        man_page = Path(__file__).parent.parent / "man" / "mklndir.1"
        content = man_page.read_text()

        # Should document all the CLI options from our CLI module
        # Note: groff uses escape sequences, so -- becomes \-\-
        cli_options = [
            "\\-\\-help",  # --help in groff format
            "\\-h",  # -h in groff format
            "\\-\\-version",
            "\\-\\-verbose",
            "\\-v",
            "\\-\\-dry\\-run",  # --dry-run in groff format
            "\\-n",
            "\\-\\-overwrite",
            "\\-o",
            "\\-\\-exclude",
            "\\-e",
            "\\-\\-stats",
        ]

        for option in cli_options:
            assert option in content, f"Man page should document {option} option"

    def test_man_page_mentions_hardlink_limitations(self):
        """Test that man page explains hardlink limitations."""
        man_page = Path(__file__).parent.parent / "man" / "mklndir.1"
        content = man_page.read_text()

        # Should explain key limitations
        limitations = [
            "same filesystem",
            "cross-device",
            "regular files",
            "network filesystems",
        ]

        for limitation in limitations:
            assert limitation in content.lower(), (
                f"Man page should mention {limitation} limitation"
            )

    def test_man_page_exit_status(self):
        """Test that man page documents exit status codes."""
        man_page = Path(__file__).parent.parent / "man" / "mklndir.1"
        content = man_page.read_text()

        # Should document exit codes
        assert "EXIT STATUS" in content, "Man page should have EXIT STATUS section"
        assert ".B 0" in content, "Should document success exit code"
        assert ".B 1" in content, "Should document error exit code"


if __name__ == "__main__":
    pytest.main([__file__])
