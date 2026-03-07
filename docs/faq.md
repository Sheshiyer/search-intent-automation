# FAQ

## Why not Make.com?

The source workflow used Make.com, but the implemented package targets coding-agent execution and deterministic local verification. Playwright MCP handles browser capture, and the Python CLI handles normalization, checkpoints, and resumes.

## How do blocked states work?

Blocked states emit `checkpoint.json` and print:

- `taxonomy`
- `recommended option 1`
- `recommended option 2`
- `custom direction`

## How do I resume?

Use:

```bash
search-intent-automation resume \
  --resume-from-checkpoint /path/to/checkpoint.json \
  --capture-status-json /path/to/capture-status.json \
  --direction recommended-2
```

## How are artifact paths resolved?

If `capture-status.json` contains relative artifact paths, they are resolved relative to that manifest file. Absolute paths still work as-is.
