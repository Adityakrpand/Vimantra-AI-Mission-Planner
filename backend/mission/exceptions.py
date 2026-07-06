from __future__ import annotations

from mission.validation_models import MissionValidationResult


class MissionValidationError(Exception):
    def __init__(self, result: MissionValidationResult) -> None:
        super().__init__("Mission validation failed.")
        self.result = result

