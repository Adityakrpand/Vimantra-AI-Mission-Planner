# Git Strategy

## Branches

- `main`: stable releases only.
- `develop`: integrated work for the next release.
- `feature/*`: new planned work.
- `release/*`: release stabilization.
- `hotfix/*`: urgent fixes from `main`.

## Pull Requests

- Pull requests target `develop` by default.
- Release pull requests target `main`.
- Hotfix pull requests target `main` and are then merged back to `develop`.

## Merge Strategy

- Squash merge feature branches.
- Use merge commits for release branches when preserving release context is useful.
- Do not merge without passing CI.

## Commit Messages

Use Conventional Commits:

- `feat:` for features.
- `fix:` for defects.
- `docs:` for documentation.
- `refactor:` for internal restructuring.
- `test:` for test changes.
- `perf:` for performance improvements.
- `chore:` for build, tooling, or maintenance.
