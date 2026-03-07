# Contracts

## Capture manifest

See `Tools/CaptureStatusContract.md`.

## Blocked checkpoint

`checkpoint.json` contains:

- `taxonomy`
- `recommended_option_1`
- `recommended_option_2`
- `custom_direction`
- `source_statuses`
- `resume_hints`

Sample artifact: `examples/checkpoint.sample.json`

## Success output

`opportunity-map.json` contains:

- `status`
- `seed`
- `goal`
- `direction`
- `source_counts`
- `source_statuses`
- `deferred_sources`
- `review_required`
- `opportunity_map`

Sample artifacts:

- `examples/opportunity-map.sample.json`
- `examples/opportunity-map.partial.sample.json`
