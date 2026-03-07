# Quickstart

Use the package with a local capture-status manifest, or use the bundled examples from a source checkout.

## Package-only quickstart

Initialize a runnable workdir:

```bash
search-intent-automation init --workdir /tmp/search-intent-demo-success
```

Validate the generated manifest:

```bash
search-intent-automation validate \
  --kind capture-status \
  /tmp/search-intent-demo-success/capture-status.json
```

Run the pipeline:

```bash
search-intent-automation run \
  --seed "search intent automation" \
  --goal "build opportunity map" \
  --workdir /tmp/search-intent-demo-success \
  --capture-status-json /tmp/search-intent-demo-success/capture-status.json
```

The artifact files referenced by that manifest must already exist. Relative artifact paths are resolved from the manifest directory, not from your shell working directory.

## Source checkout quickstart

If you have the repository checked out, you can use the bundled example manifests directly.

### Success path

```bash
search-intent-automation run \
  --seed "search intent automation" \
  --goal "build opportunity map" \
  --workdir /tmp/search-intent-demo-success \
  --capture-status-json examples/capture-status.success.json
```

Expected output:

- `/tmp/search-intent-demo-success/opportunity-map.json`
- status `ok`

### Blocked path

```bash
search-intent-automation run \
  --seed "search intent automation" \
  --goal "build opportunity map" \
  --workdir /tmp/search-intent-demo-blocked \
  --capture-status-json examples/capture-status.blocked.json
```

Expected output:

- `/tmp/search-intent-demo-blocked/checkpoint.json`
- exit code `32`
- taxonomy `rate-limited`

### Resume with partial continuation

```bash
search-intent-automation resume \
  --resume-from-checkpoint /tmp/search-intent-demo-blocked/checkpoint.json \
  --capture-status-json examples/capture-status.blocked.json \
  --direction recommended-2
```

Expected output:

- `/tmp/search-intent-demo-blocked/opportunity-map.json`
- status `partial`
- deferred source `ubersuggest`
