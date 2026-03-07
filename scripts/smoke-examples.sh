#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
success_dir="${TMPDIR:-/tmp}/search-intent-demo-success"
blocked_dir="${TMPDIR:-/tmp}/search-intent-demo-blocked"
python_bin="python3"

if [[ -x "$repo_root/.venv/bin/python" ]]; then
  python_bin="$repo_root/.venv/bin/python"
fi

rm -rf "$success_dir" "$blocked_dir"

"$python_bin" -m search_intent_automation \
  run \
  --seed "search intent automation" \
  --goal "build opportunity map" \
  --workdir "$success_dir" \
  --capture-status-json "$repo_root/examples/capture-status.success.json"

set +e
"$python_bin" -m search_intent_automation \
  run \
  --seed "search intent automation" \
  --goal "build opportunity map" \
  --workdir "$blocked_dir" \
  --capture-status-json "$repo_root/examples/capture-status.blocked.json"
blocked_exit="$?"
set -e

if [[ "$blocked_exit" -ne 32 ]]; then
  echo "Expected blocked run to exit 32, got $blocked_exit" >&2
  exit 1
fi

"$python_bin" -m search_intent_automation \
  resume \
  --resume-from-checkpoint "$blocked_dir/checkpoint.json" \
  --capture-status-json "$repo_root/examples/capture-status.blocked.json" \
  --direction recommended-2

test -f "$success_dir/opportunity-map.json"
test -f "$blocked_dir/checkpoint.json"
test -f "$blocked_dir/opportunity-map.json"

echo "Smoke examples passed"
