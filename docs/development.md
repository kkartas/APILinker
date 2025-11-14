# Development Guide

## Pre-commit Hooks

This project uses pre-commit hooks to ensure code quality and formatting consistency. The hooks automatically check and fix common issues like trailing whitespace and end-of-file formatting.

### Common Issues and Solutions

#### Formatting Errors on Commit

If you encounter errors like:
```
trim trailing whitespace.................................................Failed
fix end of files.........................................................Failed
```

**Solution 1: Run the formatting fix script (Recommended)**
```bash
# Windows PowerShell
.\scripts\pre_commit_helper.ps1

# Unix/Linux/Mac
./scripts/pre_commit_helper.sh

# Or manually
python scripts/fix_formatting.py ROADMAP.md README.md CHANGELOG.md
```

**Solution 2: Stage all changes before committing**
The pre-commit hooks work best when all changes are staged:
```bash
git add .
git commit -m "Your commit message"
```

**Solution 3: Let hooks auto-fix and re-commit**
If hooks modify files, they will be auto-fixed. Simply add the fixed files and commit again:
```bash
git add .
git commit -m "Your commit message"
```

### Manual Formatting Fix

To fix formatting issues in specific files:
```bash
python scripts/fix_formatting.py <file1> <file2> ...
```

To fix all common markdown files:
```bash
python scripts/fix_formatting.py
```

### Pre-commit Hook Configuration

The pre-commit hooks are configured in `.pre-commit-config.yaml`. The hooks check:
- Trailing whitespace removal
- End-of-file formatting (single newline)
- YAML syntax validation
- JSON syntax validation
- Large file detection

### Troubleshooting

**Issue: "Stashed changes conflicted with hook auto-fixes"**

This happens when you have unstaged changes. Solutions:
1. Stage all changes: `git add .`
2. Or commit only staged files: `git commit` (without `-a`)
3. Or run the formatting fix script first

**Issue: Pre-commit hooks are slow**

You can skip hooks for a single commit (not recommended):
```bash
git commit --no-verify -m "Your message"
```

However, this bypasses quality checks and should only be used in emergencies.

### Best Practices

1. **Always stage files before committing** - This prevents conflicts with pre-commit hooks
2. **Run formatting fixes before committing** - Use the helper scripts
3. **Review auto-fixes** - Pre-commit hooks may modify files; review changes before committing
4. **Keep hooks updated** - Run `pre-commit autoupdate` periodically
