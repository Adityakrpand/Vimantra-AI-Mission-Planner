from __future__ import annotations

from typing import Any

from logging.constants import AUDIT_LOGGER_NAME, AuditEvent
from logging.context import log_context
from logging.logger import get_logger

_audit_logger = get_logger(AUDIT_LOGGER_NAME)


def audit_event(
    event: AuditEvent,
    message: str,
    *,
    mission_id: int | str | None = None,
    drone_id: int | str | None = None,
    level: str = "INFO",
    details: dict[str, Any] | None = None,
) -> None:
    safe_details = _sanitize_details(details or {})
    suffix = ""
    if safe_details:
        suffix = " " + " ".join(
            f"{key}={value}" for key, value in sorted(safe_details.items())
        )

    with log_context(mission_id=mission_id, drone_id=drone_id):
        _audit_logger.log(
            _level_number(level),
            "audit_event=%s %s%s",
            event.value,
            message,
            suffix,
        )


def audit_exception(
    event: AuditEvent,
    message: str,
    *,
    mission_id: int | str | None = None,
    drone_id: int | str | None = None,
) -> None:
    with log_context(mission_id=mission_id, drone_id=drone_id):
        _audit_logger.exception("audit_event=%s %s", event.value, message)


def _sanitize_details(details: dict[str, Any]) -> dict[str, str]:
    sensitive_tokens = ("password", "secret", "token", "key", "credential")
    sanitized: dict[str, str] = {}
    for key, value in details.items():
        key_text = str(key)
        if any(token in key_text.lower() for token in sensitive_tokens):
            sanitized[key_text] = "[redacted]"
        else:
            sanitized[key_text] = str(value)

    return sanitized


def _level_number(level: str) -> int:
    import logging

    return int(logging.getLevelName(level.upper()))
