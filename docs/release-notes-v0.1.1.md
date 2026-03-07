# Release Notes: v0.1.1

## Summary

`v0.1.1` hardens the public CLI contract after the initial package launch.

## Highlights

- explicit `run`, `resume`, `validate`, and `init` subcommands
- validated JSON contracts for `capture-status.json`, `checkpoint.json`, and `opportunity-map.json`
- artifact paths in `capture-status.json` resolve relative to the manifest file
- refreshed examples, smoke flow, and workflow docs for the new command surface
- repo-checkout-friendly CLI tests plus clean wheel-install smoke verification

## Verification

- `ruff check .`
- `mypy src`
- `pytest`
- `.venv/bin/python -m build`
- `.venv/bin/twine check dist/*`
- `./scripts/smoke-examples.sh`
- clean venv wheel-install smoke
