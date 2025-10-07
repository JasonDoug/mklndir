# Directory Hardlinking Tool (mklndir)

A Python utility that creates hardlinks for all files within a directory structure. Since directories themselves cannot be hardlinked in Unix-like systems, this tool recursively hardlinks individual files while preserving the directory structure.

## Features

- **Recursive hardlinking**: Links all files in nested directory structures
- **Preserve directory structure**: Creates target directories as needed
- **Cross-filesystem detection**: Warns when source and target are on different filesystems
- **File exclusion**: Support for glob-pattern based file exclusion
- **Dry run mode**: Preview operations without making changes
- **Overwrite control**: Choose whether to overwrite existing files
- **Verbose logging**: Detailed operation reporting
- **Statistics**: Summary of operations performed
- **Error handling**: Comprehensive error reporting and recovery

## Installation

### Option 1: Install with pipx (Recommended)
```bash
git clone <repository-url>
cd mklndir
pipx install -e .
```

### Option 2: Install with pip
```bash
git clone <repository-url>
cd mklndir
pip install --user -e .
```

### Option 3: Quick Setup Script
```bash
git clone <repository-url>
cd mklndir
./install.sh
```

### Option 4: Direct Usage (No Installation)
```bash
git clone <repository-url>
cd mklndir
python3 -m mklndir.cli --help
```

## Usage

### Basic Usage

```bash
mklndir /path/to/source /path/to/target
```

Or if not installed globally:
```bash
python3 -m mklndir.cli /path/to/source /path/to/target
```

### Command Line Options

```bash
mklndir [OPTIONS] SOURCE TARGET

Arguments:
  SOURCE              Source directory path
  TARGET              Target directory path

Options:
  -h, --help          Show help message and exit
  -v, --verbose       Enable verbose output
  -n, --dry-run       Show what would be done without actually doing it
  -o, --overwrite     Overwrite existing files in target
  -e, --exclude       Exclude files/directories matching these patterns
  --stats             Show operation statistics
```

### Examples

1. **Basic directory hardlinking:**
   ```bash
   mklndir /home/user/documents /backup/documents
   ```

2. **Dry run to preview operations:**
   ```bash
   mklndir /source /target --dry-run --verbose
   ```

3. **Exclude temporary and log files:**
   ```bash
   mklndir /source /target --exclude "*.tmp" "*.log" "__pycache__"
   ```

4. **Overwrite existing files with verbose output:**
   ```bash
   mklndir /source /target --overwrite --verbose --stats
   ```

5. **Check version:**
   ```bash
   mklndir --version
   ```

## How It Works

1. **Directory Structure**: The tool recursively walks through the source directory
2. **Directory Creation**: Creates corresponding directories in the target location
3. **File Hardlinking**: Uses `os.link()` to create hardlinks for each file
4. **Link Verification**: Checks if files are already hardlinked to avoid duplicates
5. **Error Handling**: Reports and continues on individual file failures

### Hardlink Benefits

- **Space Efficiency**: Hardlinked files share the same inode, using no additional disk space
- **Instant Updates**: Changes to one hardlinked file appear in all linked locations
- **Performance**: No data copying required, only metadata operations
- **Atomic**: File linking is an atomic operation

### Limitations

- **Same Filesystem**: Hardlinks can only be created within the same filesystem
- **File Types**: Only regular files can be hardlinked (not directories, symlinks, or special files)
- **Permissions**: Requires appropriate permissions for both source and target locations

## Manual Page

A comprehensive Unix manual page is included with the package:

```bash
# Install man page locally
./install_man.sh

# Or using Make
make install-man

# View the manual
man mklndir
```

The man page includes:
- Complete command reference
- Detailed examples and use cases
- Technical information about hardlinks
- Troubleshooting guide
- Cross-references to related commands

## Testing

Run the included test suite to verify functionality:

```bash
python3 -m pytest tests/ -v
```

Or using the Makefile:
```bash
make test
make test-man    # Test man page formatting
```

The test suite includes:
- Basic hardlinking functionality
- CLI argument parsing and validation
- File exclusion patterns
- Dry run mode verification
- Overwrite behavior testing
- Error condition handling
- Integration tests

## Use Cases

### Backup Systems
Create space-efficient backups where files are hardlinked rather than copied:
```bash
mklndir /home/user/project /backups/project-$(date +%Y%m%d)
```

### Development Environments
Link source code to multiple build directories:
```bash
mklndir /src/myproject /build/debug/src --exclude "*.o" "*.pyc"
```

### Content Distribution
Distribute files to multiple locations without using additional storage:
```bash
mklndir /content/shared /var/www/site1/shared
mklndir /content/shared /var/www/site2/shared
```

### Media Organization
Organize media files in multiple directory structures:
```bash
mklndir /media/by-date/2023 /media/by-genre/music --exclude "*.tmp"
```

## Error Handling

The tool handles various error conditions gracefully:

- **Cross-device links**: Detects and reports when trying to link across filesystems
- **Permission errors**: Reports permission issues and continues with other files
- **Existing files**: Options to skip or overwrite existing target files
- **Special files**: Safely skips non-regular files (symlinks, devices, etc.)

## Performance Considerations

- **Large directories**: The tool processes files sequentially; very large directories may take time
- **Network filesystems**: Performance may vary on network-mounted filesystems
- **Filesystem limits**: Some filesystems have limits on the number of hardlinks per file

## Security Notes

- The tool preserves file permissions and ownership of the source files
- Hardlinked files share the same permissions; changes affect all links
- Use caution with setuid/setgid files as hardlinks preserve these attributes

## Troubleshooting

### Common Issues

1. **"Invalid cross-device link" error**:
   - Source and target are on different filesystems
   - Use `df` command to check filesystem boundaries

2. **Permission denied errors**:
   - Ensure read permissions on source files
   - Ensure write permissions on target directory

3. **"Operation not supported" errors**:
   - Some filesystems don't support hardlinks (e.g., FAT32, some network filesystems)

4. **Files not linking**:
   - Check if files already exist in target (use `--overwrite` if needed)
   - Verify source files are regular files, not symlinks

### Debug Mode

Use verbose mode to troubleshoot issues:
```bash
mklndir /source /target --verbose --dry-run
```

## Development

### Setup Development Environment
```bash
git clone <repository-url>
cd mklndir
make setup-dev
```

### Running Tests
```bash
make test          # Run all tests
make test-verbose  # Run tests with verbose output
make check         # Run all quality checks
```

### Code Quality
```bash
make format        # Format code with black
make lint          # Run flake8 linter
make type-check    # Run mypy type checker
```

### Building and Distribution
```bash
make build         # Build distribution packages
make clean         # Clean build artifacts
make install-man   # Install man page locally
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Set up development environment: `make setup-dev`
4. Add tests for new functionality
5. Ensure all checks pass: `make check`
6. Submit a pull request

## License

This tool is released under the MIT License. See LICENSE file for details.

## Author

Created as a utility for efficient directory operations and backup systems.