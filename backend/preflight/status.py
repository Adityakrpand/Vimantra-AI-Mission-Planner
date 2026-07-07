from __future__ import annotations

from enum import StrEnum


class PreFlightCheckStatus(StrEnum):
    PASS = "PASS"
    WARNING = "WARNING"
    FAIL = "FAIL"
