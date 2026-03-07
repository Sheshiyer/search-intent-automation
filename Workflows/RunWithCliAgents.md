# RunWithCliAgents

Use this workflow when a CLI coding agent should execute the pipeline end to end with minimal interaction.

## Goal

Split the workflow into:
- browser capture via Playwright MCP
- deterministic orchestration via Python

This keeps the pipeline scriptable and recoverable.

## Flow

### 1. Prepare the run directory

Create a focused workspace containing:
- the seed and goal
- target output paths
- capture artifact paths
- checkpoint path
- `/path/to/run/capture-status.json` following `Tools/CaptureStatusContract.md`

### 2. Capture Ubersuggest with Playwright MCP

Use Playwright MCP to:
- open Ubersuggest
- run the target query
- export or save the relevant keyword artifact

Save the result as:
- `ubersuggest.json` or `ubersuggest.csv`

If the capture step fails before an artifact exists, write that status into `capture-status.json`.

### 3. Capture AnswerThePublic with Playwright MCP

Use Playwright MCP to:
- open AnswerThePublic
- run the same seed
- export or save question, comparison, and preposition outputs

Save the result as:
- `answer-the-public.json` or `answer-the-public.csv`

If the capture step fails before an artifact exists, write that status into `capture-status.json`.

### 4. Run the Python orchestrator

Run:

```bash
python3 ~/.claude/skills/SearchIntentAutomation/Tools/OpportunityPipeline.py \
  --seed "SEED" \
  --goal "GOAL" \
  --workdir /path/to/run \
  --capture-status-json /path/to/run/capture-status.json
```

Optional override form:

```bash
python3 ~/.claude/skills/SearchIntentAutomation/Tools/OpportunityPipeline.py \
  --seed "SEED" \
  --goal "GOAL" \
  --workdir /path/to/run \
  --ubersuggest-input /path/to/run/ubersuggest.json \
  --answer-input /path/to/run/answer-the-public.json \
  --ubersuggest-status ok \
  --answer-status ok
```

### 5. If blocked, stop cleanly

The pipeline should not guess through broken states.

If it exits with a checkpoint:
- read the taxonomy first
- then present exactly three direction choices:
  1. recommended option 1
  2. recommended option 2
  3. custom direction

Then resume with:
- `--direction recommended-1`
- `--direction recommended-2`
- `--direction "custom:..."`

Resume example:

```bash
python3 ~/.claude/skills/SearchIntentAutomation/Tools/OpportunityPipeline.py \
  --resume-from-checkpoint /path/to/run/checkpoint.json \
  --capture-status-json /path/to/run/capture-status.json \
  --direction recommended-2
```

### 6. Ask the user in the right mode

If the agent is running with a structured user-input tool, use it and put the recommended option first, the second-best option second, and let the client provide the custom branch.

If the agent is running without that tool, ask one concise plain-text question in this shape:

- taxonomy: `[issue]`
- option 1: `[recommended option 1]`
- option 2: `[recommended option 2]`
- custom: `Provide a different direction to change the flow`

## Output Contract

The run should produce:
- `opportunity-map.json`
- `checkpoint.json` if blocked
- `capture-status.json` from the Playwright layer
- normalized source copies if needed

Success payload fields should include:
- `status`
- `source_statuses`
- `deferred_sources`
- `review_required`
- `direction`

## Guardrails

- Prefer non-interactive CLI arguments over prompts
- Fail with structured checkpoint files, not silent partial state
- Keep Playwright responsible for capture and Python responsible for logic
- Only continue partial runs when the user explicitly selects option 2 or provides a custom direction
