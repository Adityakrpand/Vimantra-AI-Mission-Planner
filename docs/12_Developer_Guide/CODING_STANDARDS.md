# Coding Standards

This document defines engineering standards for Vimantra AI Mission Planner.

## Python

- Follow PEP 8 style.
- Use type hints for public functions, service methods, and test fixtures.
- Prefer small service classes with clear dependencies.
- Use Pydantic models for API input and output boundaries.
- Raise domain-specific exceptions from services and translate them to HTTP errors in route modules.
- Keep route handlers thin.
- Avoid hidden global state except explicit cached dependencies.
- Use docstrings for non-obvious public functions or safety-relevant behavior.

## Backend Tests

- Use pytest.
- Add tests for route behavior and service behavior.
- Cover success and failure paths.
- Use fakes for MAVSDK interactions.
- Do not require real PX4 SITL for normal unit tests.

## TypeScript And React

- Use TypeScript for component props, API types, and domain data.
- Keep API serialization logic in service modules.
- Keep UI components focused on rendering and user interaction.
- Prefer explicit state names over compressed abbreviations.
- Avoid adding UI controls for behavior that is not implemented.
- Use React Testing Library for user-facing behavior.

## Frontend Tests

- Cover primary operator workflows.
- Mock backend API services at component boundaries.
- Verify disabled states for unsafe or unavailable actions.
- Run production builds before release.

## Naming

- Python modules: `snake_case`.
- Python classes: `PascalCase`.
- Python functions and variables: `snake_case`.
- TypeScript files: existing project convention, currently component files in `PascalCase` and service files in `camelCase`.
- TypeScript types: `PascalCase`.
- TypeScript variables and functions: `camelCase`.

## Folder Conventions

- Backend route modules live in `backend/app/routes`.
- Backend service modules live in `backend/app/services`.
- Backend Pydantic models live in `backend/app/models`.
- Frontend API clients live in `frontend/src/services`.
- Shared frontend domain types live in `frontend/src/types`.
- Documentation belongs in the most specific folder under `docs/`.

## Review Requirements

Before merge:

- Scope is clear.
- Tests are added or updated.
- Documentation is updated when behavior changes.
- No unrelated refactors are mixed into feature or fix pull requests.
- Safety-relevant behavior has explicit review notes.
