# Changelog

All notable changes to this project will be documented in this file.

## [0.1.1] - 2026-03-07

### Added
- Explicit `run`, `resume`, `validate`, and `init` subcommands for the public CLI.
- JSON contract validation for capture manifests, checkpoints, and opportunity maps.
- Manifest-relative artifact resolution for `capture-status.json`.

### Changed
- Updated examples, smoke scripts, workflow docs, and README to reflect the subcommanded CLI.
- Hardened CLI tests so they pass from a clean source checkout without assuming a globally installed console script.

## [0.1.0] - 2026-03-07

### Added
- Initial public package scaffolding plan implementation.
- Packaged CLI entrypoint and compatibility shim.
- Public documentation, CI, and release workflow scaffolding.
