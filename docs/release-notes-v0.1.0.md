# Release Notes Draft: v0.1.0

## Summary

`v0.1.0` turns the original search-intent workflow into a public Python package with a stable CLI, deterministic checkpoint/resume behavior, and Playwright MCP handoff contracts.

## Highlights

- packaged CLI: `search-intent-automation`
- module entrypoint: `python -m search_intent_automation`
- compatibility shim: `Tools/OpportunityPipeline.py`
- checkpoint taxonomy for blocked browser states
- sample manifests, sample outputs, and smoke script
- CI, release workflow, and PyPI trusted publishing scaffolding

## Included Docs

- installation and quickstart
- development and release operations
- architecture and contracts
- FAQ and skill-install guidance

## Verification

- `ruff check .`
- `mypy src`
- `pytest`
- `python -m build`
- `python -m twine check dist/*`
- `./scripts/smoke-examples.sh`
