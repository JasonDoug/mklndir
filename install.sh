#!/bin/bash
# Installation script for mklndir development

set -e  # Exit on any error

echo "Installing mklndir development environment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "setup.py" ] || [ ! -f "pyproject.toml" ]; then
    print_error "This script must be run from the mklndir project root directory"
    exit 1
fi

# Check Python version
python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
required_version="3.7"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 7) else 1)"; then
    print_error "Python 3.7+ is required. Current version: $python_version"
    exit 1
fi

print_status "Python version check passed: $python_version"

# Check if we can create a virtual environment
if ! command -v python3 -m venv &> /dev/null; then
    print_warning "python3-venv is not available. Attempting system-wide installation..."
    USE_SYSTEM=true
else
    USE_SYSTEM=false
fi

# Option 1: Try pipx (recommended)
if command -v pipx &> /dev/null; then
    print_status "pipx found. Installing with pipx (recommended)..."

    # Remove existing installation if present
    pipx uninstall mklndir 2>/dev/null || true

    if pipx install -e .; then
        print_status "Successfully installed mklndir with pipx!"
        print_status "You can now use the 'mklndir' command from anywhere"

        echo
        echo "Testing installation..."
        if mklndir --version; then
            print_status "Installation test passed!"
        else
            print_error "Installation test failed"
            exit 1
        fi

        echo
        print_status "Installation complete! Usage examples:"
        echo "  mklndir source_dir target_dir"
        echo "  mklndir /path/to/source /path/to/target --verbose"
        echo "  mklndir src dst --dry-run --exclude '*.tmp'"
        exit 0
    else
        print_warning "pipx installation failed. Trying alternative methods..."
    fi
fi

# Option 2: Try pip with --user flag
print_status "Attempting pip install with --user flag..."
if pip3 install --user -e .; then
    print_status "Successfully installed mklndir with pip --user!"

    # Add ~/.local/bin to PATH if not already there
    if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
        print_warning "~/.local/bin is not in your PATH"
        echo "Add this line to your ~/.bashrc or ~/.zshrc:"
        echo "export PATH=\"\$HOME/.local/bin:\$PATH\""
        echo
        echo "Then run: source ~/.bashrc (or restart your terminal)"
    fi

    echo
    echo "Testing installation..."
    if python3 -m mklndir.cli --version; then
        print_status "Installation test passed!"
        print_status "You can use: python3 -m mklndir.cli [options]"
        if command -v mklndir &> /dev/null; then
            print_status "Or simply: mklndir [options]"
        fi
    else
        print_error "Installation test failed"
        exit 1
    fi
    exit 0
fi

# Option 3: Try with --break-system-packages (if user confirms)
if [ "$USE_SYSTEM" = true ]; then
    echo
    print_warning "Standard installation methods failed."
    echo "This system has an externally managed Python environment."
    echo
    read -p "Do you want to install with --break-system-packages? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Installing with --break-system-packages..."
        if pip3 install --break-system-packages -e .; then
            print_status "Successfully installed mklndir!"

            echo
            echo "Testing installation..."
            if python3 -m mklndir.cli --version; then
                print_status "Installation test passed!"
            else
                print_error "Installation test failed"
                exit 1
            fi
        else
            print_error "Installation failed"
            exit 1
        fi
    else
        print_status "Installation cancelled by user"
        exit 0
    fi
fi

# Final fallback: Direct usage instructions
echo
print_status "Installation methods completed. You can still use mklndir directly:"
echo "  python3 -m mklndir.cli source_dir target_dir"
echo "  python3 -m mklndir.cli --help"

# Run a quick test to make sure everything works
echo
echo "Testing direct usage..."
if python3 -m mklndir.cli --version; then
    print_status "Direct usage test passed!"
else
    print_error "Something is wrong with the package structure"
    exit 1
fi

echo
print_status "Setup complete! mklndir is ready to use."
