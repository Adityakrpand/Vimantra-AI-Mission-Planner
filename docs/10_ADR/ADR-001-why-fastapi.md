# ADR-001: Use FastAPI For The Backend API

## Status

Accepted

## Context

The backend must expose typed HTTP APIs for mission storage, drone connection, mission upload, drone actions, and telemetry. It must integrate with Python MAVSDK, support async operations, provide good validation, and remain approachable for aerospace engineers and backend contributors.

## Decision

Use FastAPI as the backend framework.

## Consequences

Positive:

- Native async support for MAVSDK workflows.
- Pydantic models provide explicit request and response contracts.
- OpenAPI documentation is generated automatically.
- pytest and FastAPI TestClient support a strong testing workflow.
- Python keeps backend integration close to MAVSDK.

Tradeoffs:

- Long-running real-time telemetry may eventually require streaming patterns beyond simple request/response endpoints.
- Production deployment will require explicit configuration, logging, process management, and security hardening.
