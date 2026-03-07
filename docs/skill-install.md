# Skill-Install Mode

Use this document only when the repository is installed as a skill bundle for an agent runtime.

## Entry Points

- `../SKILL.md`: skill metadata and workflow router
- `../Workflows/BuildOpportunityMap.md`: research and opportunity-map workflow
- `../Workflows/RunWithCliAgents.md`: execution workflow for coding agents
- `../FailureTaxonomy.md`: shared blocked-state taxonomy

## Path Policy

- Resolve references relative to `$SKILL_ROOT`.
- Use repo-relative paths such as `Tools/OpportunityPipeline.py` and `Workflows/RunWithCliAgents.md`.
- Do not publish runtime-specific absolute paths in public docs, prompts, or issue templates.

## Command Form

From the installed skill root, use the compatibility script directly:

```bash
python3 Tools/OpportunityPipeline.py run --help
```

Run example:

```bash
python3 Tools/OpportunityPipeline.py run \
  --seed "local seo" \
  --goal "rank service pages" \
  --workdir /tmp/search-intent-run \
  --capture-status-json /tmp/search-intent-run/capture-status.json
```

Relative artifact paths inside `capture-status.json` resolve from the manifest file location, so skill runtimes do not need to `cd` into the run directory before execution.

## What Stays Skill-Specific

- customization lookup under `<runtime-customization-dir>/SearchIntentAutomation/`
- workflow routing from `SKILL.md`
- agent-runtime conventions for loading local context files

Everything else should match the public package docs as closely as possible.
