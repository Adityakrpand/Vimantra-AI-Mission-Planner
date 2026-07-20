# Release Process

Vimantra AI Mission Planner follows Semantic Versioning and Conventional Commits.

## Version Policy

Version format:

```text
MAJOR.MINOR.PATCH[-PRERELEASE]
```

Current release candidate:

```text
v1.0.0
```

### Major

Increment `MAJOR` for breaking API changes, mission format changes that require migration, major architecture changes, or safety-relevant workflow changes.

### Minor

Increment `MINOR` for backward-compatible features, new supported workflows, additional APIs, or substantial non-breaking improvements.

### Patch

Increment `PATCH` for backward-compatible bug fixes, documentation corrections, dependency patching, and small quality improvements.

### Pre-release

Use suffixes such as `-alpha.1`, `-beta.1`, or `-rc1` for builds that should be validated before a stable release.

## Release Branching

1. Create `release/vX.Y.Z` from `develop`.
2. Freeze feature work on the release branch.
3. Update version numbers.
4. Update `CHANGELOG.md`.
5. Run backend tests, frontend tests, frontend build, and workflow verification.
6. Fix only release-blocking defects.
7. Merge release branch into `main`.
8. Tag the release.
9. Merge `main` back into `develop`.

## Release Checklist

- Backend tests passing.
- Frontend tests passing.
- Frontend production build passing.
- Backend-only workflow verifier passing.
- PX4 SITL workflow result recorded when PX4 is available.
- Version updated in package metadata.
- `CHANGELOG.md` updated.
- `README.md` and relevant docs updated.
- Security notes reviewed.
- Git tag created.
- GitHub Release created.

## GitHub Release Notes

Release notes should include:

- Summary.
- New features.
- Fixes.
- Known limitations.
- Upgrade notes.
- Test evidence.
- PX4 SITL validation status.

## Rollback

For local release candidates, rollback by checking out the previous tag. For future deployed releases, rollback instructions must include database migration handling and configuration rollback.
