# Todo

## In Progress: Public Package Launch

- [x] Scaffold the Python package and move the pipeline code into `src/search_intent_automation`.
- [x] Add console entrypoints and keep `Tools/OpportunityPipeline.py` as a compatibility shim.
- [x] Add packaging metadata, Apache-2.0 licensing, governance docs, and public-facing README/docs.
- [x] Add unit, integration, and build verification tests.
- [x] Add GitHub Actions CI and release workflows with PyPI trusted publishing configuration.
- [x] Add examples, contract docs, architecture/FAQ docs, sample outputs, and smoke scripts.
- [x] Create GitHub label taxonomy and wave/epic issues in `Sheshiyer/search-intent-automation`.
- [x] Make the repo public and push the implementation changes.
- [x] Update `System-MOC.md` and `Enneagram-Orchestration-MOC.md` with the new project link.
- [x] Cut `v0.1.0` and verify the GitHub Release / PyPI publish path.

## Current Slice: Release Completion

- [x] Push the final follow-up commit with doc/package hygiene fixes.
- [x] Create and push tag `v0.1.0`.
- [x] Inspect the `release.yml` run for GitHub Release artifact creation.
- [x] Confirm that GitHub Release artifacts were created and PyPI trusted publishing is blocked on publisher registration.

## Current Slice: Patch Release v0.1.1

- [x] Bump version metadata to `0.1.1`.
- [x] Update changelog, README positioning, and release notes for the CLI hardening pass.
- [x] Rebuild and verify release artifacts locally.
- [x] Push `main`, create tag `v0.1.1`, and publish the GitHub release.
- [x] Update GitHub repo description to match the hardened CLI surface.

## Next Slice: CLI Hardening Pass

- [x] Add manifest-relative artifact path resolution so `capture-status.json` can use relative file paths safely.
- [x] Add JSON contract validation for capture manifests, checkpoints, and opportunity maps.
- [x] Refactor the flat CLI into explicit `run`, `resume`, `validate`, and `init` subcommands.
- [x] Preserve compatibility behavior for `python Tools/OpportunityPipeline.py ...` and sensible default invocation.
- [x] Update tests to cover subcommands, schema validation failures, and relative artifact resolution.
- [x] Update examples and docs to match the new command surface.
- [x] Re-run lint, typecheck, tests, build, twine, smoke, and wheel-install checks.

## Review

- Repo implementation is public and verified locally.
- GitHub wave issues created: `#1` through `#11`.
- `main` CI is green on commit `dd08fba`.
- GitHub Release `v0.1.0` exists with wheel and sdist assets.
- Remaining launch risk is external: PyPI trusted publisher is not registered and returns `invalid-publisher`.
- Next implementation target is product hardening, not release plumbing.
- CLI hardening pass completed: subcommands, contract validation, manifest-relative artifact resolution, docs/examples refresh, and clean-wheel install smoke all passed locally.
- `v0.1.1` is published on GitHub with wheel and sdist assets, and the repo description now matches the hardened CLI surface.
- The `Release` workflow still concludes with failure because the PyPI trusted publisher is not registered, but the GitHub Release step succeeds.
