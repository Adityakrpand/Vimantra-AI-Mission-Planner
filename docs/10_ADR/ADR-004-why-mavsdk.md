# ADR-004: Use MAVSDK For Drone Integration

## Status

Accepted

## Context

The system must connect to PX4 SITL, upload missions, execute drone actions, and read telemetry. The integration should use a maintained SDK with typed APIs instead of manually constructing MAVLink messages.

## Decision

Use MAVSDK Python for drone communication.

## Consequences

Positive:

- Provides high-level mission, action, telemetry, and connection APIs.
- Reduces direct MAVLink protocol handling in application code.
- Aligns well with PX4 SITL workflows.
- Supports async Python integration with FastAPI services.

Tradeoffs:

- Application behavior depends on MAVSDK runtime behavior and compatibility.
- Connection and telemetry edge cases must be tested with fakes and real SITL.
- Physical vehicle support will require additional safety and configuration layers.
