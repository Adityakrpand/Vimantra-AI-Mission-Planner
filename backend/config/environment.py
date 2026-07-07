from __future__ import annotations

from enum import StrEnum


class RuntimeEnvironment(StrEnum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"

