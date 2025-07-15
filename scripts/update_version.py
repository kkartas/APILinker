#!/usr/bin/env python3
"""
Version updater script for APILinker

This script updates the version number across all relevant files in the project.
Usage: python scripts/update_version.py <new_version>
Example: python scripts/update_version.py 0.2.0
"""

import sys
import re
import os
from datetime import datetime
from pathlib import Path

def update_version(new_version):
    """Update version number across all files."""
    if not re.match(r'^\d+\.\d+\.\d+$', new_version):
        print(f"Error: Version '{new_version}' does not match format X.Y.Z")
        sys.exit(1)
    
    # Get the project root directory
    root_dir = Path(__file__).parent.parent.absolute()
    
    # Dictionary of files to update with their version patterns
    files_to_update = {
        "pyproject.toml": {
            "pattern": r'version\s*=\s*"[0-9]+\.[0-9]+\.[0-9]+"',
            "replacement": f'version = "{new_version}"'
        },
        "apilinker/__init__.py": {
            "pattern": r'__version__\s*=\s*"[0-9]+\.[0-9]+\.[0-9]+"',
            "replacement": f'__version__ = "{new_version}"'
        },
        "docs/sphinx_setup/conf.py": {
            "pattern": r"version\s*=\s*'[0-9]+\.[0-9]+\.[0-9]+'",
            "replacement": f"version = '{new_version}'  # Update this with your actual version"
        },
        "CITATION.cff": {
            "pattern": r"version:\s*[0-9]+\.[0-9]+\.[0-9]+",
            "replacement": f"version: {new_version}"
        },
        "README.md": {
            "pattern": r"version\s*=\s*\{[0-9]+\.[0-9]+\.[0-9]+\}",
            "replacement": f"version = {{{new_version}}}"
        },
        "tests/test_plugins.py": {
            "pattern": r'assert info\["version"\] == "[0-9]+\.[0-9]+\.[0-9]+"',
            "replacement": f'assert info["version"] == "{new_version}"'
        },
        "apilinker/core/plugins.py": {
            "pattern": r'"version":\s*getattr\(cls,\s*"version",\s*"[0-9]+\.[0-9]+\.[0-9]+"\)',
            "replacement": f'"version": getattr(cls, "version", "{new_version}"),'
        },
    }
    
    # Special handling for CHANGELOG.md
    today = datetime.now().strftime("%Y-%m-%d")
    changelog_file = os.path.join(root_dir, "CHANGELOG.md")
    if os.path.exists(changelog_file):
        with open(changelog_file, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Check if version entry already exists
        if f"## [{new_version}]" in content:
            print(f"Warning: Version {new_version} already exists in CHANGELOG.md")
        else:
            # Add new version entry at the top of the changelog
            content = re.sub(
                r'# Changelog\n+',
                f'# Changelog\n\n## [{new_version}] - {today}\n\n- Update version to {new_version}\n\n',
                content
            )
            
            with open(changelog_file, 'w', encoding='utf-8') as file:
                file.write(content)
            print(f"Updated CHANGELOG.md with version {new_version}")
    
    # Update all other files
    for file_path, update_info in files_to_update.items():
        full_path = os.path.join(root_dir, file_path)
        if os.path.exists(full_path):
            with open(full_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            updated_content = re.sub(
                update_info["pattern"],
                update_info["replacement"],
                content
            )
            
            if content != updated_content:
                with open(full_path, 'w', encoding='utf-8') as file:
                    file.write(updated_content)
                print(f"Updated {file_path}")
            else:
                print(f"No changes needed in {file_path}")
        else:
            print(f"Warning: File {file_path} not found, skipping")

def main():
    if len(sys.argv) != 2 or sys.argv[1] in ['--help', '-h', 'help']:
        print("Usage: python scripts/update_version.py <new_version>")
        print("Example: python scripts/update_version.py 0.2.0")
        sys.exit(0)
    
    new_version = sys.argv[1]
    update_version(new_version)
    print(f"\nVersion updated successfully to {new_version}")

if __name__ == "__main__":
    main()
