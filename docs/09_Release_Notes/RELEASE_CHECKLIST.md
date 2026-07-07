# Release Checklist

Use this checklist for every tagged release.

## Code And Tests

- Backend tests pass.
- Frontend tests pass.
- Frontend production build passes.
- Backend-only workflow verifier passes.
- PX4 SITL workflow is run or explicitly marked unavailable.

## Documentation

- `README.md` reflects the release.
- `CHANGELOG.md` is updated.
- API, testing, deployment, and user docs are updated if behavior changed.
- ADRs are added for new significant architecture decisions.

## Versioning

- Backend package version updated.
- Frontend package version updated.
- API version updated.
- Git tag created using Semantic Versioning.

## Release Publication

- GitHub Release created.
- Release notes include known limitations.
- Security notes reviewed.
- Rollback path documented when applicable.

## v1.0.0-rc1 QA Snapshot

- Backend tests: `108 passed`.
- Frontend tests: `15 passed`.
- Frontend production build: passed.
- CHANGELOG created.
- Mission Analytics and Mission Validation panels reviewed for consistent states.
- PX4 SITL workflow remains an external manual check when PX4 is available.
