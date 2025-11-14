#!/usr/bin/env python3
"""
Fix common formatting issues in markdown files.
Removes trailing whitespace and ensures proper end-of-file formatting.
"""

import re
import sys
from pathlib import Path


def fix_file(file_path: Path) -> bool:
    """Fix formatting issues in a file. Returns True if file was modified."""
    try:
        content = file_path.read_text(encoding='utf-8')
        original = content

        # Remove trailing whitespace from all lines
        content = re.sub(r'[ \t]+$', '', content, flags=re.MULTILINE)

        # Ensure file ends with exactly one newline
        content = content.rstrip() + '\n'

        if content != original:
            file_path.write_text(content, encoding='utf-8', newline='\n')
            return True
        return False
    except Exception as e:
        print(f"Error fixing {file_path}: {e}", file=sys.stderr)
        return False


def main():
    """Fix formatting in specified files or all markdown files in the repo."""
    if len(sys.argv) > 1:
        files = [Path(f) for f in sys.argv[1:]]
    else:
        # Fix common markdown files
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
            print(f"File not found: {file_path}", file=sys.stderr)

    if fixed_count > 0:
        print(f"\nFixed {fixed_count} file(s)")
        sys.exit(0)
    else:
        print("No files needed fixing")
        sys.exit(0)


if __name__ == '__main__':
    main()
