from __future__ import annotations

from preflight.models import PreFlightResult


class PreFlightCheckFailedError(Exception):
    def __init__(self, result: PreFlightResult) -> None:
        super().__init__("Pre-flight checks failed.")
        self.result = result
