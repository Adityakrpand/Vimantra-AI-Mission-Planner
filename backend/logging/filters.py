from __future__ import annotations

from logging import Filter, LogRecord

from logging.constants import DRONE_ID_KEY, MISSION_ID_KEY, REQUEST_ID_KEY
from logging.context import get_context


class ContextFilter(Filter):
    def filter(self, record: LogRecord) -> bool:
        context = get_context()
        for key in (REQUEST_ID_KEY, MISSION_ID_KEY, DRONE_ID_KEY):
            if not hasattr(record, key):
                setattr(record, key, context[key])

        return True
