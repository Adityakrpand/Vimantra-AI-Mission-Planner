# ADR-002: Use React For The Frontend

## Status

Accepted

## Context

The frontend must support an interactive map, waypoint editing, mission state, drone controls, telemetry display, and future operator workflows. It should be familiar to frontend engineers and compatible with a strong TypeScript toolchain.

## Decision

Use React with TypeScript and Vite.

## Consequences

Positive:

- React component state fits mission editing and telemetry UI updates.
- TypeScript improves API integration correctness.
- Vite provides fast local development and simple production builds.
- The ecosystem supports map libraries, testing, and future UI expansion.

Tradeoffs:

- More complex state management may be needed as fleet, AI, or collaboration features are introduced.
- UI performance must be monitored if telemetry rate, map overlays, or mission scale grows.
