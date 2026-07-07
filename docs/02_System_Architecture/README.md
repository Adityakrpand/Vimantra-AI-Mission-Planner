# System Architecture

This folder contains system architecture documentation, context diagrams, component boundaries, runtime flows, interface boundaries, and architecture tradeoffs.

The root [ARCHITECTURE.md](../../ARCHITECTURE.md) is the current high-level architecture reference. More detailed diagrams and subsystem notes should be added here as the project grows.

Sprint 17 adds an independent `backend/validation` package for V1 mission
readiness checks. It is separate from `backend/analytics`, which computes
statistics, and from `backend/preflight`, which checks live vehicle readiness.
