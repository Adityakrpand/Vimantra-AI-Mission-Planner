from __future__ import annotations

from datetime import datetime, timezone
from logging import Formatter, LogRecord

from logging.constants import DRONE_ID_KEY, MISSION_ID_KEY, REQUEST_ID_KEY


class StructuredLogFormatter(Formatter):
    def formatTime(self, record: LogRecord, datefmt: str | None = None) -> str:
        return datetime.fromtimestamp(record.created, timezone.utc).isoformat(
            timespec="seconds"
        ).replace("+00:00", "Z")

    def format(self, record: LogRecord) -> str:
        timestamp = self.formatTime(record)
        message = record.getMessage()
        base = (
            f"{timestamp} {record.levelname} {record.module} {record.funcName} "
            f"request_id={getattr(record, REQUEST_ID_KEY)} "
            f"mission_id={getattr(record, MISSION_ID_KEY)} "
            f"drone_id={getattr(record, DRONE_ID_KEY)} {message}"
        )
        if record.exc_info:
            base = f"{base}\n{self.formatException(record.exc_info)}"

        return base
