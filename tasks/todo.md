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
- [ ] Cut `v0.1.0` and verify the GitHub Release / PyPI publish path.

## Current Slice: Release Completion

- [x] Push the final follow-up commit with doc/package hygiene fixes.
- [x] Create and push tag `v0.1.0`.
- [x] Inspect the `release.yml` run for GitHub Release artifact creation.
- [x] Confirm that GitHub Release artifacts were created and PyPI trusted publishing is blocked on publisher registration.

## Review

- Repo implementation is public and verified locally.
- GitHub wave issues created: `#1` through `#11`.
- `main` CI is green on commit `dd08fba`.
- GitHub Release `v0.1.0` exists with wheel and sdist assets.
- Remaining launch risk is external: PyPI trusted publisher is not registered and returns `invalid-publisher`.
