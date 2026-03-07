# CaptureStatusContract

Use this contract when Playwright MCP hands browser-capture results to the Python CLI.

## Goal

Make browser success and browser failure explicit so coding agents do not invent hidden fallback behavior.

## File

Write a JSON file such as:

- `/path/to/run/capture-status.json`

## Required shape

```json
{
  "ubersuggest": {
    "status": "ok",
    "artifact": "/path/to/run/ubersuggest.csv"
  },
  "answer_the_public": {
    "status": "rate-limited",
    "artifact": null
  }
}
```

## Allowed `status` values

- `ok`
- `auth-expired`
- `selector-drift`
- `rate-limited`
- `missing-export`
- `schema-mismatch`
- `low-signal-data`

## Source naming

Use these exact source keys:

- `ubersuggest`
- `answer_the_public`

## Artifact rules

- If `status` is `ok`, `artifact` should point to the file Playwright saved.
- If `status` is not `ok`, `artifact` can be omitted or set to `null`.
- Preferred filenames:
  - `ubersuggest.json` or `ubersuggest.csv`
  - `answer-the-public.json` or `answer-the-public.csv`

## Failure mapping

- login wall or expired session -> `auth-expired`
- selector broke because UI changed -> `selector-drift`
- throttled, blocked, or delayed by the upstream site -> `rate-limited`
- export/save path never produced a file -> `missing-export`
- file exists but cannot be parsed downstream -> `schema-mismatch`
- file exists but signal is too thin to trust -> `low-signal-data`

## Python handoff

Run:

```bash
python3 ~/.claude/skills/SearchIntentAutomation/Tools/OpportunityPipeline.py \
  --seed "SEED" \
  --goal "GOAL" \
  --workdir /path/to/run \
  --capture-status-json /path/to/run/capture-status.json
```

If blocked, the Python tool emits:

- `taxonomy`
- `recommended option 1`
- `recommended option 2`
- `custom direction`
