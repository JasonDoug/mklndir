# Makefile for mklndir development

.PHONY: help install install-dev test test-verbose clean build upload check format lint type-check docs examples install-man test-man all

# Default target
help:
	@echo "Available targets:"
	@echo "  install      - Install the package"
	@echo "  install-dev  - Install in development mode with dev dependencies"
	@echo "  test         - Run tests"
	@echo "  test-verbose - Run tests with verbose output"
	@echo "  clean        - Clean build artifacts"
	@echo "  build        - Build distribution packages"
	@echo "  upload       - Upload to PyPI (requires credentials)"
	@echo "  check        - Run all checks (format, lint, type-check, test)"
	@echo "  format       - Format code with black"
	@echo "  lint         - Run flake8 linter"
	@echo "  type-check   - Run mypy type checker"
	@echo "  examples     - Run example usage script"
	@echo "  install-man  - Install man page locally"
	@echo "  test-man     - Test man page formatting and accessibility"
	@echo "  all          - Run check and build"

# Installation targets
install:
	pip install .

install-dev:
	pip install -e ".[dev]"

# Testing targets
test:
	python -m pytest tests/ -v

test-verbose:
	python -m pytest tests/ -v -s

test-coverage:
	python -m pytest tests/ --cov=mklndir --cov-report=html --cov-report=term

# Quality checks
format:
	python -m black mklndir/ tests/ examples/

lint:
	python -m flake8 mklndir/ tests/ examples/

type-check:
	python -m mypy mklndir/

check: format lint type-check test
	@echo "All checks passed!"

# Build and distribution
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean
	python -m build

upload: build
	python -m twine upload dist/*

upload-test: build
	python -m twine upload --repository testpypi dist/*

# Development utilities
examples:
	cd examples && python example_usage.py

# Man page targets
install-man:
	./install_man.sh

test-man:
	@echo "Testing man page format..."
	@if command -v groff >/dev/null 2>&1; then \
		groff -man -Tascii man/mklndir.1 >/dev/null && echo "✅ Man page format is valid"; \
	else \
		echo "⚠️  groff not available, cannot validate format"; \
	fi
	@echo "Man page file: man/mklndir.1"
	@echo "Size: $$(du -h man/mklndir.1 | cut -f1)"

cli-test:
	python -m mklndir.cli --help
	python -m mklndir.cli --version

install-tools:
	pip install build twine pytest pytest-cov black flake8 mypy

# Complete workflow
all: check build
	@echo "Package is ready for distribution!"

# Local installation test
test-install: build
	pip install --force-reinstall dist/*.whl
	mklndir --version
	mklndir --help

# Development setup
setup-dev: install-tools install-dev
	@echo "Development environment ready!"
