# Release Process

This guide covers version management and releasing new versions of APILinker.

## Version Bumping

APILinker uses `bump-my-version` for version management.

### Bump Patch Version (0.5.3 → 0.5.4)

```bash
bump-my-version bump patch
```

### Bump Minor Version (0.5.3 → 0.6.0)

```bash
bump-my-version bump minor
```

### Bump Major Version (0.5.3 → 1.0.0)

```bash
bump-my-version bump major
```

## Release Workflow

1. **Update CHANGELOG.md** with new version details
2. **Bump version**: `bump-my-version bump <patch|minor|major>`
3. **Commit changes**: `git commit -am "Bump version to X.Y.Z"`
4. **Create tag**: `git tag vX.Y.Z`
5. **Push**: `git push && git push --tags`
6. GitHub Actions will automatically publish to PyPI

## Configuration

Version bumping is configured in `.bumpversion.toml`.
