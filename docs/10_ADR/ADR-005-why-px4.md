# ADR-005: Use PX4 SITL As The Primary Simulation Target

## Status

Accepted

## Context

The application needs a realistic autopilot simulation target for mission upload, execution, and telemetry verification. Version 1.0 should validate workflows without requiring physical aircraft.

## Decision

Use PX4 SITL as the primary Version 1.0 simulation target.

## Consequences

Positive:

- PX4 SITL is widely used for UAV software validation.
- Supports MAVSDK workflows required by the project.
- Allows mission upload and telemetry validation without physical flight risk.
- Provides a practical path toward future hardware validation.

Tradeoffs:

- SITL does not replace physical flight testing.
- Local developer setup may vary by operating system.
- Real vehicle support will require hardware configuration, safety procedures, and additional validation.
