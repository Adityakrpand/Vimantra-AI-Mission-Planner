from __future__ import annotations

import logging
from typing import Protocol

from logging.constants import LOGGER_NAME
from logging.filters import ContextFilter
from logging.handlers import build_console_handler, build_file_handlers


class LoggingSettings(Protocol):
    log_level: str
    log_console_enabled: bool
    log_file_enabled: bool
    log_max_file_size_bytes: int
    log_retention_days: int

    @property
    def resolved_log_directory(self): ...


_configured = False


def configure_logging(settings: LoggingSettings, *, force: bool = False) -> None:
    global _configured
    if _configured and not force:
        return

    level = logging.getLevelName(settings.log_level)
    root_logger = logging.getLogger()
    application_logger = logging.getLogger(LOGGER_NAME)

    for target_logger in (root_logger, application_logger):
        target_logger.handlers.clear()
        target_logger.setLevel(level)
        target_logger.addFilter(ContextFilter())

    handlers = []
    if settings.log_console_enabled:
        handlers.append(build_console_handler(level))
    if settings.log_file_enabled:
        handlers.extend(
            build_file_handlers(
                log_directory=settings.resolved_log_directory,
                level=level,
                max_file_size_bytes=settings.log_max_file_size_bytes,
                retention_days=settings.log_retention_days,
            )
        )

    for handler in handlers:
        root_logger.addHandler(handler)

    application_logger.propagate = True
    _configured = True


def get_logger(name: str) -> logging.Logger:
    if name.startswith(LOGGER_NAME):
        return logging.getLogger(name)

    return logging.getLogger(f"{LOGGER_NAME}.{name}")


def reset_logging_for_tests() -> None:
    global _configured
    logging.getLogger().handlers.clear()
    logging.getLogger(LOGGER_NAME).handlers.clear()
    _configured = False
