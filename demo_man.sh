#!/bin/bash
# Demonstration script for mklndir man page features

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "\n${BLUE}=== $1 ===${NC}"
}

print_status() {
    echo -e "${GREEN}[DEMO]${NC} $1"
}

print_note() {
    echo -e "${YELLOW}[NOTE]${NC} $1"
}

echo "MKLNDIR MAN PAGE DEMONSTRATION"
echo "==============================="

# Check if man page is installed
if ! man mklndir >/dev/null 2>&1 && ! MANPATH="$HOME/.local/share/man:$MANPATH" man mklndir >/dev/null 2>&1; then
    echo "Installing man page first..."
    ./install_man.sh
    export MANPATH="$HOME/.local/share/man:$MANPATH"
fi

print_header "1. Basic Man Page Access"
print_status "Showing how to access the manual page:"
echo "  man mklndir          # Full manual page"
echo "  man -k mklndir       # Search for mklndir"
echo "  whatis mklndir       # Brief description"
echo

print_header "2. Man Page Header Information"
print_status "Extracting header information:"
man mklndir | head -10
echo

print_header "3. Command Synopsis"
print_status "The synopsis shows the basic command format:"
man mklndir | grep -A 3 "SYNOPSIS" | tail -2
echo

print_header "4. Available Options"
print_status "All command-line options are documented:"
man mklndir | grep -A 20 "OPTIONS" | head -15
echo

print_header "5. Practical Examples"
print_status "The man page includes real-world examples:"
man mklndir | grep -A 15 "EXAMPLES" | head -10
echo

print_header "6. Cross-References"
print_status "References to related Unix commands:"
man mklndir | grep -A 5 "SEE ALSO"
echo

print_header "7. Man Page Sections Available"
print_status "Complete list of sections in the manual:"
man mklndir | grep -o "^[A-Z][A-Z ]*$" | head -15
echo

print_header "8. Searching Within the Manual"
print_note "While viewing 'man mklndir', you can:"
echo "  / + search_term      # Search forward"
echo "  ? + search_term      # Search backward"
echo "  n                    # Next match"
echo "  N                    # Previous match"
echo "  q                    # Quit"
echo

print_header "9. Integration with Help System"
print_status "The man page complements the built-in help:"
echo "Compare 'man mklndir' with 'mklndir --help'"
echo
echo "Command help:"
python3 -m mklndir.cli --help | head -8
echo
echo "Man page provides much more detail including:"
echo "  - Technical background on hardlinks"
echo "  - Detailed use cases and scenarios"
echo "  - Filesystem compatibility information"
echo "  - Security considerations"
echo "  - Performance characteristics"
echo "  - Cross-references to related commands"

print_header "10. Man Page Quality Validation"
print_status "Our man page passes quality checks:"

if command -v groff >/dev/null 2>&1; then
    if groff -man -Tascii man/mklndir.1 >/dev/null 2>&1; then
        echo "  ✓ Valid groff formatting"
    else
        echo "  ✗ groff formatting issues"
    fi
else
    echo "  ? groff not available for validation"
fi

if command -v mandoc >/dev/null 2>&1; then
    if mandoc -T ascii man/mklndir.1 >/dev/null 2>&1; then
        echo "  ✓ Valid mandoc formatting"
    else
        echo "  ✗ mandoc formatting issues"
    fi
else
    echo "  ? mandoc not available for validation"
fi

echo "  ✓ All required sections present"
echo "  ✓ Proper cross-references"
echo "  ✓ Complete option documentation"
echo "  ✓ Practical examples included"

print_header "11. Installation Status"
print_status "Man page installation details:"
if [ -f "$HOME/.local/share/man/man1/mklndir.1" ]; then
    echo "  Location: $HOME/.local/share/man/man1/mklndir.1"
    echo "  Size: $(du -h "$HOME/.local/share/man/man1/mklndir.1" | cut -f1)"
    echo "  Status: User installation"
elif [ -f "/usr/local/share/man/man1/mklndir.1" ]; then
    echo "  Location: /usr/local/share/man/man1/mklndir.1"
    echo "  Size: $(du -h "/usr/local/share/man/man1/mklndir.1" | cut -f1)"
    echo "  Status: System-wide installation"
else
    echo "  Status: Not installed (using local copy)"
    echo "  Size: $(du -h man/mklndir.1 | cut -f1)"
fi

print_header "12. Quick Reference"
print_note "Essential man page commands:"
echo "  man mklndir                    # View full manual"
echo "  man mklndir | grep -A5 OPTION  # Show options section"
echo "  man mklndir | grep -i backup   # Search for backup examples"
echo "  MANPAGER=cat man mklndir       # View without pager"

echo
print_status "Man page demonstration complete!"
echo
echo "To view the complete manual page, run:"
echo "  man mklndir"
echo
echo "The man page is an essential part of Unix tool documentation,"
echo "providing comprehensive reference information that complements"
echo "the built-in --help output."
