# Search Intent Automation

[![CI](https://github.com/Sheshiyer/search-intent-automation/actions/workflows/ci.yml/badge.svg)](https://github.com/Sheshiyer/search-intent-automation/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/search-intent-automation.svg)](https://pypi.org/project/search-intent-automation/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)

Deterministic search-intent automation for coding agents.

This project turns a seed topic into a repeatable research pipeline using:

- Ubersuggest
- AnswerThePublic
- Playwright MCP
- Python CLI orchestration

The original source workflow used `Make.com` as the automation layer. This repo preserves the research sequence but replaces the implementation layer with Playwright MCP capture plus a Python package that handles normalization, checkpoints, and resumable flows.

## Install

```bash
pip install search-intent-automation
```

For local development:

```bash
python -m pip install -e .[dev]
```

More setup options live in [docs/installation.md](docs/installation.md).

## Public package mode

Run the installed CLI:

```bash
# create /tmp/search-intent-run/capture-status.json first
search-intent-automation \
  --seed "local seo" \
  --goal "rank service pages" \
  --workdir /tmp/search-intent-run \
  --capture-status-json /tmp/search-intent-run/capture-status.json
```

Module invocation is also supported:

```bash
python -m search_intent_automation --help
```

## Skill mode

If you want to use this repo as a skill source, keep the public package docs as the source of truth and use `SKILL.md` plus `Workflows/` as the adaptation layer for your local skill runtime.

## Compatibility path

If you are running from a source checkout or installed skill bundle, existing automation can continue using:

```bash
python Tools/OpportunityPipeline.py --help
```

That file is a compatibility shim and is not part of the PyPI wheel.

## Blocked-state contract

When the pipeline is blocked, it stops and emits:

- `taxonomy`
- `recommended option 1`
- `recommended option 2`
- `custom direction`

Only `recommended-2` or `custom:...` may continue as a partial run.

## Repo structure

- `src/search_intent_automation/`: packaged CLI and pipeline logic
- `Tools/OpportunityPipeline.py`: compatibility shim for prior script-based callers
- `Tools/CaptureStatusContract.md`: Playwright-to-Python handoff contract
- `Workflows/`: skill-oriented workflow docs
- `docs/`: public package documentation
- `examples/`: runnable manifests and fixture artifacts

## Documentation

- [Installation](docs/installation.md)
- [Quickstart](docs/quickstart.md)
- [Development](docs/development.md)
- [Release](docs/release.md)
- [Architecture](docs/architecture.md)
- [Contracts](docs/contracts.md)
- [FAQ](docs/faq.md)

## Source trace

The reel-derived source evidence remains available in [ReelEvidence.md](ReelEvidence.md). It is treated as provenance, not as the package usage guide.
