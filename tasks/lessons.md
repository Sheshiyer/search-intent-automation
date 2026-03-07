# Lessons

## 2026-03-07

- Public-package work in a new standalone repo should keep old skill entrypoints working through compatibility shims instead of breaking existing automation paths.
- When a release is blocked by an external registry or account login, stop forcing the publish path and pivot to the highest-value repo improvements instead of spending more turns on unavailable credentials.
- CLI tests for a public package must not assume a globally installed console script or preinstalled distribution metadata; keep repo-checkout tests self-contained and use build plus wheel-install smoke to verify packaging.
