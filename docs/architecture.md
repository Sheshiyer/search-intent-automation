# Architecture

## Flow

1. Playwright MCP writes `capture-status.json` and any exported artifacts.
2. The CLI reads the manifest and resolves artifact paths.
3. The pipeline normalizes JSON or CSV exports into row sets.
4. If the run is blocked, the CLI emits `checkpoint.json` plus the three-way decision contract.
5. If the user resumes with `recommended-2` or `custom:...`, the CLI can continue as a partial run.
6. Success writes `opportunity-map.json`.

## Components

- Package CLI: `src/search_intent_automation/cli.py`
- Pipeline engine: `src/search_intent_automation/pipeline.py`
- Compatibility shim: `Tools/OpportunityPipeline.py`
- Browser-to-Python contract: `Tools/CaptureStatusContract.md`
