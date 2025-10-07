"""
mklndir - Directory Hardlinking Tool

A Python utility that creates hardlinks for all files within a directory structure.
Since directories themselves cannot be hardlinked in Unix-like systems, this tool
recursively hardlinks individual files while preserving the directory structure.
"""

__version__ = "1.0.0"
__author__ = "JasonDoug"
__description__ = "Directory hardlinking tool for space-efficient file organization"

from .core import DirectoryHardlinker

__all__ = ["DirectoryHardlinker", "__version__"]
