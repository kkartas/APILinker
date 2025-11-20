# PyPI Publishing Setup

## Overview

APILinker uses GitHub Actions to automatically publish to PyPI when version tags are pushed.

## ⚠️ Current Issue

```
ERROR HTTPError: 403 Forbidden from https://upload.pypi.org/legacy/
Invalid or non-existent authentication information.
```

This means the `PYPI_API_TOKEN` secret is either missing or invalid.

## Setup Steps

### 1. Create PyPI Account

1. Go to https://pypi.org/account/register/
2. Create an account (if you don't have one)
3. Verify your email address

### 2. Generate PyPI API Token

1. Go to https://pypi.org/manage/account/token/
2. Click **"Add API token"**
3. Token name: `GitHub Actions - APILinker`
4. Scope: 
   - If `apilinker` package exists: Select **"Project: apilinker"**
   - If first time publishing: Select **"Entire account"** (you can narrow scope later)
5. Click **"Add token"**
6. **⚠️ COPY THE TOKEN IMMEDIATELY** - it starts with `pypi-` and you can't see it again!

### 3. Add Token to GitHub Secrets

1. Go to your repository: https://github.com/kkartas/APILinker
2. Click **Settings** (top menu)
3. In left sidebar: **Secrets and variables** → **Actions**
4. Click **"New repository secret"**
5. Fill in:
   - **Name:** `PYPI_API_TOKEN`
   - **Secret:** Paste the token from step 2 (starts with `pypi-`)
6. Click **"Add secret"**

### 4. Verify Workflow Configuration

The `release.yml` workflow handles both scenarios:

```yaml
on:
  push:
    tags:
      - 'v*.*.*'        # Triggers on version tags (from bump.ps1)
  release:
    types: [created]    # Triggers on GitHub releases
```

Both trigger the same job that builds and publishes to PyPI.

## Publishing Process

### Automatic (Recommended)

```bash
# 1. Bump version (creates tag)
.\bump.ps1 patch   # or minor/major

# 2. Push (triggers release.yml)
git push origin main --tags
```

The GitHub Actions workflow will:
1. ✅ **Tag pushed** → Create GitHub release (with auto-generated notes)
2. ✅ **Release published** → Build package (sdist + wheel)
3. ✅ **Build complete** → Publish to PyPI
4. ✅ **PyPI published** → Attach distribution files to GitHub release

### Manual (for testing)

```bash
# 1. Set environment variables
$env:TWINE_USERNAME = "__token__"
$env:TWINE_PASSWORD = "pypi-YOUR-TOKEN-HERE"

# 2. Build and upload
python -m pip install build twine
python -m build
python -m twine upload dist/*
```

## Troubleshooting

### 403 Forbidden Error

**Cause:** Missing or invalid `PYPI_API_TOKEN` secret

**Fix:**
1. Generate new token at https://pypi.org/manage/account/token/
2. Add to GitHub Secrets as `PYPI_API_TOKEN`
3. Re-run the workflow

### 400 Bad Request - File Already Exists

**Cause:** Version already published to PyPI

**Fix:**
```bash
# Bump version to new number
.\bump.ps1 patch
git push origin main --tags
```

### Package Name Conflict

**Cause:** Package name `apilinker` already exists (owned by someone else)

**Fix:**
1. Check package ownership at https://pypi.org/project/apilinker/
2. If you own it: Add your PyPI username to package maintainers
3. If you don't own it: Rename package in `pyproject.toml`

### First Time Publishing

**Issue:** Can't use project-scoped token before package exists

**Fix:**
1. Create token with **"Entire account"** scope
2. Publish first version
3. Generate new project-scoped token
4. Update GitHub secret

## Workflow Files

- **`release.yml`**: Two-stage release process ✅ ACTIVE
  - **Stage 1 (Tag Push):** Tag `v*.*.*` → Create GitHub Release
  - **Stage 2 (Release Published):** Build → Publish to PyPI → Attach artifacts

## Security Best Practices

✅ **DO:**
- Use API tokens (not passwords)
- Use project-scoped tokens (after first publish)
- Store tokens in GitHub Secrets
- Rotate tokens periodically

❌ **DON'T:**
- Commit tokens to repository
- Share tokens publicly
- Use account-level tokens long-term
- Hard-code credentials

## Testing Before Publishing

```bash
# Test build locally
python -m build

# Check built package
python -m twine check dist/*

# Upload to TestPyPI first (optional)
python -m twine upload --repository testpypi dist/*
```

## After Successful Publishing

1. Verify on PyPI: https://pypi.org/project/apilinker/
2. Test installation:
   ```bash
   pip install --upgrade apilinker
   python -c "import apilinker; print(apilinker.__version__)"
   ```
3. Update CHANGELOG.md and README.md if needed

## References

- [PyPI Token Help](https://pypi.org/help/#apitoken)
- [Twine Documentation](https://twine.readthedocs.io/)
- [GitHub Encrypted Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
