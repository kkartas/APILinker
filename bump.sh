#!/bin/bash
# Version Bump Script for Unix/Linux/Mac
# Usage: ./bump.sh [patch|minor|major]

if [ $# -eq 0 ]; then
    echo "Usage: ./bump.sh [patch|minor|major]"
    exit 1
fi

PART=$1

# Set UTF-8 encoding
export PYTHONIOENCODING=utf-8

echo "Bumping $PART version..."

# Run bump-my-version
./.venv/bin/bump-my-version bump $PART

if [ $? -eq 0 ]; then
    echo ""
    echo "Version bumped successfully!"
    echo "Remember to push with tags: git push origin main --tags"
else
    echo ""
    echo "Version bump failed!"
    exit 1
fi
