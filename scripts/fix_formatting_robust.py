#!/usr/bin/env python3
"""
Robust formatting fixer that handles all edge cases.
Removes trailing whitespace, fixes line endings, and ensures proper EOF.
"""

import re
import sys
from pathlib import Path


def fix_file(file_path: Path) -> bool:
    """Fix all formatting issues in a file. Returns True if file was modified."""
    try:
        # Read as binary first to preserve exact content
        content_bytes = file_path.read_bytes()
        original_bytes = content_bytes

        # Convert to text, normalizing line endings to LF
        try:
            content = content_bytes.decode('utf-8')
        except UnicodeDecodeError:
            print(f"Warning: {file_path} is not UTF-8, skipping", file=sys.stderr)
            return False

        # Normalize line endings to LF (Unix style)
        content = content.replace('\r\n', '\n').replace('\r', '\n')

        # Remove trailing whitespace from all lines (spaces and tabs)
        lines = content.split('\n')
        fixed_lines = []
        for line in lines:
            # Remove trailing spaces and tabs
            fixed_line = line.rstrip(' \t')
            fixed_lines.append(fixed_line)

        # Join lines and ensure file ends with exactly one newline
        content = '\n'.join(fixed_lines)
        if content and not content.endswith('\n'):
            content += '\n'
        elif content.endswith('\n\n'):
            # Remove extra trailing newlines
            content = content.rstrip('\n') + '\n'

        # Convert back to bytes with LF line endings
        new_content_bytes = content.encode('utf-8')

        if new_content_bytes != original_bytes:
            file_path.write_bytes(new_content_bytes)
            return True
        return False
    except Exception as e:
        print(f"Error fixing {file_path}: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return False


def main():
    """Fix formatting in specified files."""
    if len(sys.argv) > 1:
        files = [Path(f) for f in sys.argv[1:]]
    else:
        # Default files
        repo_root = Path(__file__).parent.parent
        files = [
            repo_root / 'ROADMAP.md',
            repo_root / 'README.md',
            repo_root / 'CHANGELOG.md',
        ]

    fixed_count = 0
    for file_path in files:
        if file_path.exists():
            if fix_file(file_path):
                print(f"Fixed: {file_path}")
                fixed_count += 1
            else:
                print(f"OK: {file_path} (no changes needed)")
        else:
            print(f"File not found: {file_path}", file=sys.stderr)

    if fixed_count > 0:
        print(f"\nFixed {fixed_count} file(s)")
        sys.exit(0)
    else:
        print("All files are properly formatted")
        sys.exit(0)


if __name__ == '__main__':
    main()
