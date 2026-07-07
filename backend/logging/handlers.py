from __future__ import annotations

import importlib.util
import sys
import sysconfig
from logging import Handler, StreamHandler
from pathlib import Path

from logging.filters import ContextFilter
from logging.formatter import StructuredLogFormatter

_STDLIB_HANDLERS_PATH = Path(sysconfig.get_path("stdlib")) / "logging" / "handlers.py"
_SPEC = importlib.util.spec_from_file_location(
    "_vimantra_stdlib_logging_handlers",
    _STDLIB_HANDLERS_PATH,
)
if _SPEC is None or _SPEC.loader is None:
    raise ImportError("Unable to load Python standard logging handlers.")

_stdlib_handlers = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_stdlib_handlers)

for _name in dir(_stdlib_handlers):
    if _name.startswith("__"):
        continue
    globals()[_name] = getattr(_stdlib_handlers, _name)

RotatingFileHandler = _stdlib_handlers.RotatingFileHandler
TimedRotatingFileHandler = _stdlib_handlers.TimedRotatingFileHandler


def build_console_handler(level: int) -> Handler:
    handler = StreamHandler(sys.stdout)
    _configure_handler(handler, level)
    return handler


def build_file_handlers(
    *,
    log_directory: Path,
    level: int,
    max_file_size_bytes: int,
    retention_days: int,
) -> list[Handler]:
    log_directory.mkdir(parents=True, exist_ok=True)
    rotating_handler = RotatingFileHandler(
        log_directory / "vimantra.log",
        maxBytes=max_file_size_bytes,
        backupCount=retention_days,
        encoding="utf-8",
    )
    daily_handler = TimedRotatingFileHandler(
        log_directory / "vimantra-daily.log",
        when="midnight",
        backupCount=retention_days,
        encoding="utf-8",
        utc=True,
    )
    for handler in (rotating_handler, daily_handler):
        _configure_handler(handler, level)

    return [rotating_handler, daily_handler]


def _configure_handler(handler: Handler, level: int) -> None:
    handler.setLevel(level)
    handler.addFilter(ContextFilter())
    handler.setFormatter(StructuredLogFormatter())
