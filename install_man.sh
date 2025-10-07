#!/bin/bash
# Script to install and test the mklndir man page locally

set -e  # Exit on any error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

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
if [ ! -f "man/mklndir.1" ]; then
    print_error "This script must be run from the mklndir project root directory"
    print_error "Expected to find man/mklndir.1"
    exit 1
fi

print_status "Installing mklndir man page..."

# Determine installation directory
if [ -w "/usr/local/share/man/man1" ]; then
    MAN_DIR="/usr/local/share/man/man1"
    INSTALL_METHOD="system"
elif [ -d "$HOME/.local/share/man/man1" ] || mkdir -p "$HOME/.local/share/man/man1" 2>/dev/null; then
    MAN_DIR="$HOME/.local/share/man/man1"
    INSTALL_METHOD="user"
else
    print_error "Cannot find suitable man page directory"
    print_error "Try creating ~/.local/share/man/man1 manually:"
    echo "  mkdir -p ~/.local/share/man/man1"
    exit 1
fi

print_status "Installing to: $MAN_DIR"

# Install the man page
if [ "$INSTALL_METHOD" = "system" ]; then
    print_warning "Installing system-wide (may require sudo)"
    if sudo cp man/mklndir.1 "$MAN_DIR/"; then
        print_status "Man page installed successfully"
    else
        print_error "Failed to install man page system-wide"
        exit 1
    fi
else
    cp man/mklndir.1 "$MAN_DIR/"
    print_status "Man page installed to user directory"
fi

# Update man database
print_status "Updating man database..."
if [ "$INSTALL_METHOD" = "system" ]; then
    if command -v mandb >/dev/null 2>&1; then
        sudo mandb -q 2>/dev/null || print_warning "Could not update man database"
    elif command -v makewhatis >/dev/null 2>&1; then
        sudo makewhatis "$MAN_DIR" 2>/dev/null || print_warning "Could not update man database"
    fi
else
    if command -v mandb >/dev/null 2>&1; then
        mandb -u -q ~/.local/share/man 2>/dev/null || print_warning "Could not update user man database"
    elif command -v makewhatis >/dev/null 2>&1; then
        makewhatis "$HOME/.local/share/man" 2>/dev/null || print_warning "Could not update user man database"
    fi

    # Add to MANPATH if needed
    if [[ ":$MANPATH:" != *":$HOME/.local/share/man:"* ]]; then
        print_warning "~/.local/share/man is not in your MANPATH"
        echo
        echo "Add this line to your ~/.bashrc or ~/.zshrc:"
        echo "export MANPATH=\"\$HOME/.local/share/man:\$MANPATH\""
        echo
        echo "Or run: export MANPATH=\"\$HOME/.local/share/man:\$MANPATH\""
    fi
fi

# Test the installation
echo
print_status "Testing man page installation..."

# Test different ways to access the man page
if man mklndir >/dev/null 2>&1; then
    print_status "✓ Man page accessible via 'man mklndir'"
elif man 1 mklndir >/dev/null 2>&1; then
    print_status "✓ Man page accessible via 'man 1 mklndir'"
elif [ "$INSTALL_METHOD" = "user" ] && MANPATH="$HOME/.local/share/man:$MANPATH" man mklndir >/dev/null 2>&1; then
    print_status "✓ Man page accessible with MANPATH set"
    print_warning "Run: export MANPATH=\"\$HOME/.local/share/man:\$MANPATH\""
else
    print_warning "Man page installed but may not be immediately accessible"
    print_warning "Try: MANPATH=\"$MAN_DIR:$MANPATH\" man mklndir"
fi

# Test man page formatting
echo
print_status "Testing man page formatting..."
if command -v groff >/dev/null 2>&1; then
    if groff -man -Tascii "$MAN_DIR/mklndir.1" >/dev/null 2>&1; then
        print_status "✓ Man page format is valid"
    else
        print_warning "Man page format may have issues"
    fi
else
    print_warning "groff not available, cannot validate man page format"
fi

# Show quick preview
echo
print_status "Man page preview (first few lines):"
echo "----------------------------------------"
if command -v man >/dev/null 2>&1; then
    # Try to show just the header
    MANPATH="$MAN_DIR:$MANPATH" man mklndir 2>/dev/null | head -20 | cat || {
        # Fallback to raw groff output
        groff -man -Tascii "$MAN_DIR/mklndir.1" 2>/dev/null | head -20 | cat || {
            print_warning "Could not generate preview"
        }
    }
else
    print_warning "man command not available for preview"
fi

echo
print_status "Man page installation complete!"
echo
echo "Usage:"
echo "  man mklndir          # View the manual page"
echo "  man -k mklndir       # Search for mklndir in man pages"
echo "  whatis mklndir       # Show brief description"
echo
echo "If the man page is not accessible, try:"
echo "  export MANPATH=\"$MAN_DIR:\$MANPATH\""
echo "  man mklndir"

# Optional: Show installation info
echo
echo "Installation details:"
echo "  Man page: $MAN_DIR/mklndir.1"
echo "  Method: $INSTALL_METHOD"
echo "  Size: $(du -h "$MAN_DIR/mklndir.1" 2>/dev/null | cut -f1 || echo "unknown")"
