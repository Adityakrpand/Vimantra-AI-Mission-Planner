# Roadmap

This roadmap describes the planned product direction for Vimantra AI Mission Planner. Dates are intentionally omitted until release planning has assigned owners, validation environments, and acceptance criteria.

## Version 1.0: Local PX4 SITL Mission Planner

Status: `v1.0.0-rc1`

Scope:

- React mission planner UI.
- FastAPI backend.
- SQLite mission storage.
- MAVSDK integration.
- PX4 SITL connection, mission upload, arm, disarm, start mission, and telemetry.
- Local verification scripts and test suites.

## Version 1.1: Production Hardening

Planned scope:

- Structured logging and log correlation.
- Configuration files and environment-specific settings.
- Stronger API error models.
- Expanded telemetry status diagnostics.
- Installer and environment bootstrap documentation.
- Continuous integration enforcement for backend and frontend checks.
- Expanded safety validation around mission upload and execution.

## Version 2.0: AI Mission Planning

Planned scope:

- Human-reviewed AI-assisted route generation.
- Constraint-aware mission proposals.
- Mission risk scoring.
- Operator approval workflow before upload.
- Audit trail for AI-generated recommendations.

## Version 3.0: Computer Vision

Planned scope:

- Camera feed integration.
- Object detection and target annotation.
- Vision-assisted waypoint recommendations.
- Dataset management and model evaluation workflows.

## Version 4.0: Fleet Management

Planned scope:

- Multiple vehicle sessions.
- Fleet status dashboard.
- Per-vehicle mission assignment.
- Operator roles and permission boundaries.
- Fleet telemetry aggregation.

## Version 5.0: Cloud Platform

Planned scope:

- Cloud-hosted mission management.
- Organization accounts and access control.
- Remote collaboration.
- Cloud mission archive.
- Enterprise deployment, monitoring, and support processes.

## Roadmap Principles

- Flight-critical actions must remain operator-controlled.
- AI output must be reviewable, explainable, and auditable.
- Simulation validation must precede physical vehicle deployment.
- Backward compatibility is preferred for saved mission formats and public APIs.
