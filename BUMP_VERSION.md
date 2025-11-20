# bump-my-version Quick Reference

## Bump Version

```powershell
# Windows - Use the wrapper script
.\bump.ps1 patch
.\bump.ps1 minor
.\bump.ps1 major
```

```bash
# Linux/Mac
./bump.sh patch
./bump.sh minor
./bump.sh major
```

## What Gets Updated

When you bump the version, these **14 files** are automatically updated:

1. `pyproject.toml`
2. `apilinker/__init__.py`
3. `setup.py`
4. `CITATION.cff`
5. `ROADMAP.md`
6. `TECHNICAL_DOCUMENTATION.md`
7. `docs/sphinx_setup/conf.py`
8. `apilinker/core/plugins.py`
9. `apilinker/connectors/scientific/crossref.py`
10. `apilinker/connectors/scientific/semantic_scholar.py`
11. `apilinker/connectors/scientific/orcid.py`
12. `apilinker/connectors/general/github.py`
13. `tests/test_plugins.py`
14. **Manual**: `README.md` and `paper/paper.md` (update changelog/release notes)

## After Bumping

```bash
# Push changes and tags
git push origin main --tags
```

## Troubleshooting

**"Working directory is not clean"**
```bash
# Commit your changes first
git add .
git commit -m "Your changes"

# Then bump
.\bump.ps1 patch
```

**Check current version**
```powershell
$env:PYTHONIOENCODING='utf-8'
.\.venv\Scripts\bump-my-version show current_version
```

**Dry run (preview changes)**
```powershell
$env:PYTHONIOENCODING='utf-8'
.\.venv\Scripts\bump-my-version bump patch --dry-run --allow-dirty
```

## Configuration

The configuration is in `.bumpversion.toml`. You shouldn't need to edit it unless adding new files to track.

---

📖 **Full Documentation**: [VERSION_MANAGEMENT.md](VERSION_MANAGEMENT.md)
