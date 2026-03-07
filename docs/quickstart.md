# Quickstart

Use the package with a local capture-status manifest, or use the bundled examples from a source checkout.

## Package-only quickstart

Create a manifest at `/tmp/search-intent-demo-success/capture-status.json`:

```json
{
  "ubersuggest": {
    "status": "ok",
    "artifact": "/tmp/search-intent-demo-success/ubersuggest.json"
  },
  "answer_the_public": {
    "status": "ok",
    "artifact": "/tmp/search-intent-demo-success/answer-the-public.json"
  }
}
```

Then point the CLI at that file:

```bash
search-intent-automation \
  --seed "search intent automation" \
  --goal "build opportunity map" \
  --workdir /tmp/search-intent-demo-success \
  --capture-status-json /tmp/search-intent-demo-success/capture-status.json
```

The artifact files referenced by that manifest must already exist.

## Source checkout quickstart

If you have the repository checked out, you can use the bundled example manifests directly.

### Success path

```bash
search-intent-automation \
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
search-intent-automation \
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
search-intent-automation \
  --resume-from-checkpoint /tmp/search-intent-demo-blocked/checkpoint.json \
  --capture-status-json examples/capture-status.blocked.json \
  --direction recommended-2
```

Expected output:

- `/tmp/search-intent-demo-blocked/opportunity-map.json`
- status `partial`
- deferred source `ubersuggest`
