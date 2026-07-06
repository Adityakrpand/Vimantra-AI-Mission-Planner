# ADR-003: Use SQLite For Local Mission Storage

## Status

Accepted

## Context

Version 1.0 needs reliable local mission persistence without requiring operators or developers to install and administer a database server. The data model is relational: missions have ordered waypoints.

## Decision

Use SQLite for Version 1.0 mission storage.

## Consequences

Positive:

- Zero external database service required.
- Simple local development and testing.
- Relational constraints fit missions and waypoints.
- Easy backup and inspection for local simulation workflows.

Tradeoffs:

- SQLite is not a multi-user cloud database.
- Future fleet, collaboration, or cloud features may require PostgreSQL or another server database.
- Migration tooling will be needed if schema changes become frequent.
