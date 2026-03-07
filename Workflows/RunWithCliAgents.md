# RunWithCliAgents

Use this workflow when a coding agent should execute the pipeline end to end.

## Prepare

- Create a run directory.
- Save browser outputs locally.
- Write `capture-status.json` following `Tools/CaptureStatusContract.md`.

## Run

```bash
search-intent-automation \
  --seed "SEED" \
  --goal "GOAL" \
  --workdir /path/to/run \
  --capture-status-json /path/to/run/capture-status.json
```

Compatibility path:

```bash
python Tools/OpportunityPipeline.py --help
```

## Resume

```bash
search-intent-automation \
  --resume-from-checkpoint /path/to/run/checkpoint.json \
  --capture-status-json /path/to/run/capture-status.json \
  --direction recommended-2
```

## Blocked-state contract

When the pipeline is blocked, present:

- `taxonomy`
- `recommended option 1`
- `recommended option 2`
- `custom direction`
