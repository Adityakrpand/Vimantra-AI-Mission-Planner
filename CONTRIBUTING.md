# Contributing

Thank you for contributing to Vimantra AI Mission Planner. This repository is maintained as an aerospace-oriented engineering project, so contributions should be traceable, tested, and reviewable.

## Development Workflow

1. Create an issue or link your work to an existing issue.
2. Create a branch from `develop`.
3. Use a focused branch name such as `feature/mission-import`, `fix/telemetry-timeout`, or `docs/api-errors`.
4. Keep changes scoped to one purpose.
5. Add or update tests when behavior changes.
6. Update documentation when public behavior, setup, APIs, or workflows change.
7. Open a pull request into `develop`.

## Branching Strategy

- `main`: stable released code only.
- `develop`: integration branch for the next release.
- `feature/*`: new work planned for a future release.
- `release/*`: release stabilization and final documentation updates.
- `hotfix/*`: urgent fixes based on `main`.

## Merge Strategy

- Pull requests require passing CI before merge.
- Prefer squash merge for feature branches to keep history readable.
- Release branches merge into both `main` and `develop`.
- Hotfix branches merge into both `main` and `develop`.

## Commit Standard

Use Conventional Commits:

```text
feat: add mission import validation
fix: handle telemetry timeout response
docs: document PX4 SITL setup
refactor: isolate mission serialization
test: cover mission upload conflict
perf: reduce telemetry polling overhead
chore: update CI workflow
```

## Coding Standards

See [docs/12_Developer_Guide/CODING_STANDARDS.md](docs/12_Developer_Guide/CODING_STANDARDS.md).

## Testing

Backend:

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest --basetemp=pytest-tmp-run
```

Frontend:

```powershell
cd frontend
npx vitest run
npm run build
```

## Pull Request Expectations

A pull request should include:

- A short summary of the change.
- Related issue references.
- Test evidence.
- Documentation updates, when applicable.
- Notes about risk, migration, or validation limits.

## Safety Expectations

Do not merge changes that bypass operator control for flight actions, weaken validation around mission execution, or introduce autonomous behavior without explicit roadmap approval and safety review.
