# Release

## Versioning

- Start at `0.1.0`
- Use `0.1.x` for patch releases until the CLI contract stabilizes further

## Local release checklist

```bash
ruff check .
mypy src
pytest
python -m build
python -m twine check dist/*
```

## GitHub release

1. Update `CHANGELOG.md`.
2. Commit and push `main`.
3. Create and push tag `vX.Y.Z`.
4. Let `release.yml` build artifacts, create the GitHub Release, and publish to PyPI.

## PyPI trusted publishing

The workflow expects GitHub OIDC trusted publishing for the `pypi` environment. If that is not configured yet, the release job should remain in place and the publish step will be blocked until the publisher is registered.
