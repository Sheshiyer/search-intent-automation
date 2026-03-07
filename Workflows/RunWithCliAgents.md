# RunWithCliAgents

Use this workflow when a coding agent should execute the pipeline end to end.

## Prepare

- Create a run directory.
- Save browser outputs locally.
- Write `capture-status.json` following `Tools/CaptureStatusContract.md`.
- Use `search-intent-automation init --workdir /path/to/run` if you want a scaffolded manifest and sample artifact names.
- Use `search-intent-automation validate --kind capture-status /path/to/run/capture-status.json` before running if the manifest was produced by another tool.

## Run

```bash
search-intent-automation run \
  --seed "SEED" \
  --goal "GOAL" \
  --workdir /path/to/run \
  --capture-status-json /path/to/run/capture-status.json
```

Compatibility path:

```bash
python Tools/OpportunityPipeline.py run --help
```

## Resume

```bash
search-intent-automation resume \
  --resume-from-checkpoint /path/to/run/checkpoint.json \
  --capture-status-json /path/to/run/capture-status.json \
  --direction recommended-2
```

Relative artifact paths inside `capture-status.json` are resolved from the manifest file location.

## Blocked-state contract

When the pipeline is blocked, present:

- `taxonomy`
- `recommended option 1`
- `recommended option 2`
- `custom direction`
