# Search Intent Automation

Turn a seed topic into a repeatable search-intent research pipeline using:

- Ubersuggest
- AnswerThePublic
- Playwright MCP
- Python CLI orchestration

This project extracts the workflow logic from a source reel and rewrites the automation layer so coding agents can execute it non-interactively.

## Why this exists

The original reel used `Make.com` as the automation layer. This project preserves the research sequence but replaces the implementation layer with:

- `Playwright MCP` for browser capture
- `OpportunityPipeline.py` for deterministic normalization, merge, resume, and checkpoint handling

## Project layout

- `SKILL.md`: reusable skill entry point
- `ReelEvidence.md`: source trace from the reel
- `FailureTaxonomy.md`: blocked-state taxonomy and branch contract
- `Workflows/`: workflow docs for extraction, opportunity mapping, and CLI-agent runs
- `Tools/OpportunityPipeline.py`: Python CLI orchestrator
- `Tools/CaptureStatusContract.md`: Playwright-to-Python handoff contract

## Run the pipeline

```bash
python3 Tools/OpportunityPipeline.py \
  --seed "local seo" \
  --goal "rank service pages" \
  --workdir /tmp/search-intent-run \
  --capture-status-json /tmp/search-intent-run/capture-status.json
```

Resume after a checkpoint:

```bash
python3 Tools/OpportunityPipeline.py \
  --resume-from-checkpoint /tmp/search-intent-run/checkpoint.json \
  --capture-status-json /tmp/search-intent-run/capture-status.json \
  --direction recommended-2
```

## Blocked-state contract

When blocked, the pipeline stops and emits:

- `taxonomy`
- `recommended option 1`
- `recommended option 2`
- `custom direction`

Only `recommended-2` or `custom:...` should allow a partial continuation.
