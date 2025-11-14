#!/bin/bash
# Pre-commit helper script for Unix/Linux/Mac
# Run this before committing to fix formatting issues

echo "Running formatting fixes..."

# Fix formatting in common files
python scripts/fix_formatting.py ROADMAP.md README.md CHANGELOG.md

if [ $? -eq 0 ]; then
    echo "Formatting fixes complete!"
    echo "You can now commit your changes."
else
    echo "Error running formatting fixes."
    exit 1
fi
