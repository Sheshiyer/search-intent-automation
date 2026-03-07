---
name: SearchIntentAutomation
description: Use when turning a niche, offer, product, or topic into a keyword map, audience question map, and an agent-executable workflow using Ubersuggest, AnswerThePublic, Playwright MCP browser capture, and Python orchestration.
---

# SearchIntentAutomation

This repo is the canonical public source for the Search Intent Automation skill.

## Public package mode

Install the package and run the CLI described in `README.md` and `docs/`.

## Skill mode

If your runtime loads local skill folders directly, use this file as the entrypoint and load:

- `Workflows/BuildOpportunityMap.md`
- `Workflows/ExtractFromSource.md`
- `Workflows/RunWithCliAgents.md`
- `FailureTaxonomy.md`
- `Tools/CaptureStatusContract.md`

## Quick reference

- Capture browser-only research data with Playwright MCP.
- Hand off results through `capture-status.json`.
- Use `search-intent-automation init`, `validate`, `run`, and `resume` as the primary command surface.
- Use `python Tools/OpportunityPipeline.py run ...` only as the compatibility path for skill-style installs.
- If blocked, present `taxonomy`, `recommended option 1`, `recommended option 2`, and `custom direction`.
