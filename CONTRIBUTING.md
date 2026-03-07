# Contributing

## Workflow

1. Create a focused branch.
2. Run the local quality loop:
   - `python -m pip install -e .[dev]`
   - `ruff check .`
   - `mypy src`
   - `pytest`
   - `python -m build`
3. Keep JSON contracts stable unless the change explicitly revises the contract docs.
4. Update docs when behavior changes.

## Pull request expectations

- Explain the behavior change, not just the file diff.
- Include verification output.
- Call out any compatibility impact on `Tools/OpportunityPipeline.py`.
