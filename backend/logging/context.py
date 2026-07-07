from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar, Token
from collections.abc import Iterator

from logging.constants import (
    DRONE_ID_KEY,
    MISSION_ID_KEY,
    MISSING_CONTEXT_VALUE,
    REQUEST_ID_KEY,
)

_request_id: ContextVar[str | None] = ContextVar(REQUEST_ID_KEY, default=None)
_mission_id: ContextVar[str | None] = ContextVar(MISSION_ID_KEY, default=None)
_drone_id: ContextVar[str | None] = ContextVar(DRONE_ID_KEY, default=None)


def get_context() -> dict[str, str]:
    return {
        REQUEST_ID_KEY: _request_id.get() or MISSING_CONTEXT_VALUE,
        MISSION_ID_KEY: _mission_id.get() or MISSING_CONTEXT_VALUE,
        DRONE_ID_KEY: _drone_id.get() or MISSING_CONTEXT_VALUE,
    }


@contextmanager
def log_context(
    *,
    request_id: str | None = None,
    mission_id: int | str | None = None,
    drone_id: int | str | None = None,
) -> Iterator[None]:
    tokens: list[tuple[ContextVar[str | None], Token[str | None]]] = []
    if request_id is not None:
        tokens.append((_request_id, _request_id.set(str(request_id))))
    if mission_id is not None:
        tokens.append((_mission_id, _mission_id.set(str(mission_id))))
    if drone_id is not None:
        tokens.append((_drone_id, _drone_id.set(str(drone_id))))

    try:
        yield
    finally:
        for variable, token in reversed(tokens):
            variable.reset(token)
