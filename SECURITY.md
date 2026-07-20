# Security Policy

## Supported Versions

| Version | Status |
| --- | --- |
| `v1.0.0` | Supported, security reports accepted |

## Reporting a Vulnerability

Do not open public issues for security vulnerabilities.

Report security concerns privately to the maintainers with:

- Affected component.
- Steps to reproduce.
- Expected impact.
- Logs, screenshots, or proof of concept if available.
- Suggested mitigation if known.

Maintainer profile: [Aditya K. R. Pand](https://github.com/Adityakrpand).

## Scope

Security reports may include:

- API vulnerabilities.
- Unsafe file handling.
- Dependency vulnerabilities.
- Authentication or authorization concerns once those features exist.
- Unsafe mission upload or drone action behavior.
- Exposure of logs, secrets, or local mission data.

## Out of Scope

- Social engineering.
- Denial-of-service testing against systems you do not own.
- Physical vehicle testing without explicit authorization.
- Reports requiring unsafe flight operations.

## Response Process

1. Maintainers acknowledge receipt.
2. The issue is triaged for impact and exploitability.
3. A fix is prepared on a private branch or limited-access issue.
4. Tests and release notes are updated.
5. A patched release is published when appropriate.

## Safety Note

This repository is currently intended for local development and PX4 SITL validation. Do not use this software for physical flight operations without independent safety review, test planning, and operator approval.
