# FailureTaxonomy

Use this taxonomy when the workflow cannot continue non-interactively.

## Categories

### `auth-expired`

Meaning:
- login session expired
- gated report requires fresh authentication

Recommended option 1:
- refresh auth and retry the same Playwright capture step

Recommended option 2:
- continue from cached artifacts if they are recent enough

### `selector-drift`

Meaning:
- target UI changed
- element selector no longer matches

Recommended option 1:
- retry with fallback selectors and the same capture target

Recommended option 2:
- switch to screenshot/manual-export mode for the blocked step

### `rate-limited`

Meaning:
- upstream site is throttling requests or blocking repeated actions

Recommended option 1:
- back off and retry after a cooling interval

Recommended option 2:
- continue with partial data and mark the missing source as deferred

### `missing-export`

Meaning:
- expected capture file was not written
- Playwright step finished but produced no usable artifact

Recommended option 1:
- retry the capture step with an explicit export/save path

Recommended option 2:
- continue with the remaining source and mark the output partial

### `schema-mismatch`

Meaning:
- exported files exist but do not match the expected JSON/CSV shape

Recommended option 1:
- run a normalization patch for the current schema and continue

Recommended option 2:
- re-run capture with a simpler export format

### `low-signal-data`

Meaning:
- both sources ran, but the results are too thin or noisy to trust

Recommended option 1:
- change the seed term and retry with a narrower or clearer topic

Recommended option 2:
- proceed with manual review instead of full automation

## Required User-Direction Prompt

When blocked, state the taxonomy first and then present exactly three direction inputs:

1. `Recommended option 1`
2. `Recommended option 2`
3. `Custom direction`

Prompt shape:

- `taxonomy`: the issue category
- `option 1`: the best next action
- `option 2`: the second-best action
- `custom`: user can provide a new direction to change the flow
