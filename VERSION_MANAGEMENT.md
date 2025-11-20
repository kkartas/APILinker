# Version Management

APILinker uses **bump-my-version** for automated version management.

## Quick Start

```powershell
# Windows
.\bump.ps1 patch   # 0.5.0 -> 0.5.1
.\bump.ps1 minor   # 0.5.0 -> 0.6.0
.\bump.ps1 major   # 0.5.0 -> 1.0.0
```

```bash
# Linux/Mac
./bump.sh patch
./bump.sh minor
./bump.sh major
```

## What It Does

When you run a bump command, it automatically:
1. ✅ Updates version in **14 files**
2. ✅ Creates a **git commit** with message: `Bump version: X.Y.Z -> X.Y.Z+1`
3. ✅ Creates a **git tag**: `vX.Y.Z`
4. ✅ Ready to push!

## Installation

```bash
pip install bump-my-version
```

Or add to development dependencies:
```bash
pip install -e ".[dev]"
```

## Usage

### Using the Wrapper Scripts (Easiest)

```powershell
# Windows PowerShell
.\bump.ps1 patch
```

```bash
# Linux/Mac
chmod +x bump.sh
./bump.sh minor
```

### Using bump-my-version Directly

```powershell
# Windows - Set UTF-8 encoding first
$env:PYTHONIOENCODING='utf-8'
.\.venv\Scripts\bump-my-version bump patch
```

```bash
# Linux/Mac
export PYTHONIOENCODING=utf-8
./.venv/bin/bump-my-version bump minor
```

### Bump Version

```bash
# Patch release (0.5.0 -> 0.5.1) - Bug fixes
bump-my-version bump patch

# Minor release (0.5.0 -> 0.6.0) - New features, backward compatible
bump-my-version bump minor

# Major release (0.5.0 -> 1.0.0) - Breaking changes
bump-my-version bump major
```

### What It Does

When you run a bump command, it automatically:
1. ✅ Updates version in **14 files**:
   - `pyproject.toml`
   - `apilinker/__init__.py`
   - `setup.py`
   - `CITATION.cff`
   - `ROADMAP.md`
   - `TECHNICAL_DOCUMENTATION.md`
   - `docs/sphinx_setup/conf.py`
   - `apilinker/core/plugins.py`
   - `apilinker/connectors/scientific/crossref.py`
   - `apilinker/connectors/scientific/semantic_scholar.py`
   - `apilinker/connectors/scientific/orcid.py`
   - `apilinker/connectors/general/github.py`
   - `tests/test_plugins.py`
   - `README.md` (manually update changelog)
   - `paper/paper.md` (manually update when publishing)

2. ✅ Creates a **git commit** with message: `Bump version: X.Y.Z → X.Y.Z+1`
3. ✅ Creates a **git tag**: `vX.Y.Z`

### Options

### Options

```powershell
# Dry run (see what would change without making changes)
$env:PYTHONIOENCODING='utf-8'
.\.venv\Scripts\bump-my-version bump patch --dry-run --allow-dirty

# Skip git commit
.\.venv\Scripts\bump-my-version bump patch --no-commit

# Skip git tag
.\.venv\Scripts\bump-my-version bump patch --no-tag

# Allow uncommitted changes
.\.venv\Scripts\bump-my-version bump patch --allow-dirty

# Show current version
.\.venv\Scripts\bump-my-version show current_version
```

## Configuration

The configuration is in `.bumpversion.toml` which specifies:
- Current version
- Files to update and their search/replace patterns
- Git commit/tag settings

## Versioning Strategy

APILinker follows [Semantic Versioning](https://semver.org/):

- **MAJOR** (X.0.0): Breaking changes, incompatible API changes
- **MINOR** (0.X.0): New features, backward compatible
- **PATCH** (0.0.X): Bug fixes, backward compatible

## Manual Updates

If you need to manually update version:
1. Edit `apilinker/__init__.py` to change `__version__`
2. Run: `bump-my-version bump patch --no-tag --no-commit --new-version X.Y.Z`
3. This will update all files without creating commit/tag

## Examples

### Release Workflow

```bash
# 1. Make your changes and test
pytest --cov=apilinker --cov-fail-under=80

# 2. Bump version (creates commit and tag)
.\bump.ps1 minor   # Windows
# ./bump.sh minor  # Linux/Mac

# 3. Update CHANGELOG.md manually
# Add release notes for the new version

# 4. Amend the bump commit to include changelog
git add CHANGELOG.md README.md
git commit --amend --no-edit

# 5. Push with tags (triggers PyPI release via release.yml workflow)
git push origin main --tags
```
**Note:** Pushing tags triggers the GitHub Actions `release.yml` workflow which automatically publishes to PyPI (requires `PYPI_API_TOKEN` secret in GitHub repository settings).

### Hotfix Release

```bash
# On main branch with version 0.5.0
# Found critical bug, need 0.5.1

# 1. Fix the bug
# 2. Bump patch version
bump-my-version bump patch

# 3. Push
git push origin main --tags
```

## Troubleshooting

### "Working directory is not clean"
```bash
# Commit or stash your changes first
git status
git commit -am "Your changes"
# Then bump
bump-my-version bump patch
```

### "File not found"
Check that all files listed in `.bumpversion.toml` exist.

### Version mismatch
```bash
# Check current version in config
bump-my-version show current_version

# Check actual version in code
python -c "import apilinker; print(apilinker.__version__)"

# If they differ, update .bumpversion.toml manually
```

## CI/CD Integration

In your GitHub Actions workflow:

```yaml
- name: Bump version and push tag
  run: |
    pip install bump-my-version
    bump-my-version bump patch
    git push origin main --tags
```

## Alternative: Manual Version Update

If you prefer not to use bump-my-version, update version in:
1. `apilinker/__init__.py` - This is the **source of truth**
2. Run script to sync to other files (or update manually)
