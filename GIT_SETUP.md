# Git Setup Documentation for mklndir

This document explains the Git configuration and best practices for the mklndir project.

## Repository Structure

```
mklndir/
├── .git/                   # Git repository metadata
├── .gitignore             # Files and patterns to ignore
├── .gitattributes         # File attribute configuration
├── mklndir/               # Main Python package
├── tests/                 # Test suite
├── man/                   # Manual page
├── examples/              # Usage examples
├── setup.py               # Package setup
├── pyproject.toml         # Modern Python packaging
├── README.md              # Project documentation
├── LICENSE                # MIT License
├── Makefile               # Development tasks
└── ...                    # Other project files
```

## Git Configuration Files

### .gitignore

The `.gitignore` file is comprehensive and organized into sections:

- **Python specific**: `__pycache__/`, `*.pyc`, `*.pyo`, `build/`, `dist/`, etc.
- **Development environments**: `.venv/`, `.idea/`, `.vscode/`, etc.
- **Operating system files**: `.DS_Store`, `Thumbs.db`, etc.
- **Testing artifacts**: `.pytest_cache/`, `htmlcov/`, `.coverage`, etc.
- **mklndir specific**: `test_source/`, `demo_target/`, `*.log`, etc.

Key patterns for this project:
```gitignore
# Test directories created during development
test_source/
test_target/
demo_source/
demo_target/
temp_test*/

# Build artifacts
build/
dist/
*.egg-info/

# Development files
*.log
debug.txt
```

### .gitattributes

Ensures consistent handling across platforms:

- **Line endings**: All text files use LF (`eol=lf`)
- **Binary files**: Images, archives marked as `binary`
- **Language detection**: Proper GitHub language detection
- **Export ignore**: Development files excluded from archives

Key attributes:
```gitattributes
# Consistent line endings
*.py text eol=lf
*.sh text eol=lf
*.md text eol=lf

# Man pages
*.1 text eol=lf linguist-language=Roff

# Binary files
*.whl binary
*.tar.gz binary
```

## Initial Setup

1. **Initialize repository**:
   ```bash
   git init
   git config user.name "Your Name"
   git config user.email "your.email@example.com"
   ```

2. **Add all files**:
   ```bash
   git add .
   git status  # Verify only intended files are staged
   ```

3. **Initial commit**:
   ```bash
   git commit -m "Initial commit: Complete mklndir package"
   ```

## Development Workflow

### Branch Strategy

- **main/master**: Stable releases
- **develop**: Development integration
- **feature/***: Feature branches
- **hotfix/***: Critical fixes

### Commit Message Format

Use conventional commits:
```
type(scope): description

[optional body]

[optional footer]
```

Examples:
- `feat(cli): add --exclude option for file patterns`
- `fix(core): handle permission errors gracefully`
- `docs(man): update examples section`
- `test(cli): add integration tests for dry-run mode`

### Pre-commit Checks

Before committing:
```bash
make check          # Run all quality checks
make test           # Run test suite
make lint           # Check code style
make type-check     # Run mypy
```

## File Handling Best Practices

### What to Track

✅ **Always track**:
- Source code (`*.py`)
- Configuration (`setup.py`, `pyproject.toml`)
- Documentation (`README.md`, `*.1`)
- Tests (`tests/*.py`)
- Build scripts (`Makefile`, `*.sh`)
- License and legal files

### What to Ignore

❌ **Never track**:
- Build artifacts (`build/`, `dist/`)
- Python bytecode (`__pycache__/`, `*.pyc`)
- IDE files (`.vscode/`, `.idea/`)
- OS files (`.DS_Store`, `Thumbs.db`)
- Test artifacts (`test_source/`, `*.log`)
- Virtual environments (`venv/`, `.venv/`)

### Special Cases

⚠️ **Consider carefully**:
- `requirements.txt` - Track if used
- `poetry.lock` - Track for applications, consider for libraries
- Configuration files - Track templates, ignore local configs

## Remote Repository Setup

### Adding Remote

```bash
# GitHub
git remote add origin https://github.com/username/mklndir.git

# GitLab
git remote add origin https://gitlab.com/username/mklndir.git
```

### Push Initial Commit

```bash
git branch -M main  # Rename to main branch
git push -u origin main
```

## Release Workflow

### Version Tagging

```bash
# Tag release
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0

# List tags
git tag -l
```

### Release Preparation

1. Update version in `mklndir/__init__.py`
2. Update `CHANGELOG.md`
3. Run full test suite
4. Build and test package
5. Tag and push

## Maintenance

### Clean Working Directory

```bash
# Remove ignored files (be careful!)
git clean -fdX

# Show what would be removed
git clean -fdX --dry-run
```

### Update .gitignore

When adding new ignore patterns:
```bash
# Remove already tracked files that should be ignored
git rm --cached filename
git commit -m "Remove file from tracking"
```

### Check Repository Health

```bash
# Check what's ignored
git status --ignored

# Verify attributes
git check-attr --all -- filename

# Check line endings
git ls-files --eol
```

## Integration with Development Tools

### IDE Integration

Most IDEs respect `.gitignore` and `.gitattributes`:
- **VSCode**: Install GitLens extension
- **PyCharm**: Built-in Git support
- **Vim**: Use fugitive plugin

### Continuous Integration

Example GitHub Actions workflow:
```yaml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install -e ".[test]"
      - name: Run tests
        run: make test
```

## Troubleshooting

### Common Issues

1. **Files still tracked after adding to .gitignore**:
   ```bash
   git rm --cached filename
   ```

2. **Line ending issues**:
   ```bash
   git add --renormalize .
   ```

3. **Large files accidentally committed**:
   ```bash
   git filter-branch --force --index-filter \
     'git rm --cached --ignore-unmatch filename' \
     --prune-empty --tag-name-filter cat -- --all
   ```

### Verification Commands

```bash
# Check what Git sees
git ls-files                    # All tracked files
git status --ignored           # Show ignored files
git check-ignore -v filename   # Why is file ignored
git check-attr --all filename  # File attributes
```

## Security Considerations

- Never commit secrets (API keys, passwords)
- Use `.gitignore` to prevent accidental commits
- Review commits before pushing
- Use signed commits for releases:
  ```bash
  git config --global user.signingkey YOUR_GPG_KEY
  git config --global commit.gpgsign true
  ```

## Best Practices Summary

1. **Commit early, commit often** - Small, focused commits
2. **Use descriptive messages** - Follow conventional format
3. **Review before committing** - Use `git status` and `git diff`
4. **Keep repository clean** - Proper `.gitignore` configuration
5. **Test before pushing** - Run test suite locally
6. **Use branches** - Don't work directly on main
7. **Tag releases** - Use semantic versioning
8. **Document changes** - Update CHANGELOG.md

## References

- [Git Documentation](https://git-scm.com/doc)
- [gitignore templates](https://github.com/github/gitignore)
- [Conventional Commits](https://conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)