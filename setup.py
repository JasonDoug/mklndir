#!/usr/bin/env python3
"""Setup script for mklndir package."""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file for long description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

# Read version from package
version = "1.0.0"

setup(
    name="mklndir",
    version=version,
    author="JasonDoug",
    author_email="jason@potterlabs.xyz",
    description="Directory hardlinking tool for space-efficient file organization",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JasonDoug/mklndir",
    packages=find_packages(),
    data_files=[
        ("share/man/man1", ["man/mklndir.1"]),
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Topic :: System :: Archiving :: Backup",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: Unix",
        "Operating System :: POSIX",
        "Operating System :: MacOS",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires=">=3.7",
    install_requires=[
        # No external dependencies - uses only standard library
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
        "test": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "mklndir=mklndir.cli:main",
        ],
    },
    keywords="hardlink directory backup filesystem storage space-efficient",
    project_urls={
        "Bug Reports": "https://github.com/JasonDoug/mklndir/issues",
        "Source": "https://github.com/JasonDoug/mklndir",
        "Documentation": "https://github.com/JasonDoug/mklndir#readme",
    },
    include_package_data=True,
    zip_safe=False,
)
