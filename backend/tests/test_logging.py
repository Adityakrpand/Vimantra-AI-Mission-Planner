from __future__ import annotations

from pathlib import Path

from config.settings import AppSettings
from logging.audit import audit_event, audit_exception
from logging.constants import AuditEvent
from logging.logger import configure_logging, get_logger, reset_logging_for_tests


def teardown_function() -> None:
    reset_logging_for_tests()


def test_logger_initialization_creates_configured_file_handlers(tmp_path: Path) -> None:
    settings = AppSettings(
        _env_file=None,
        log_directory=tmp_path,
        log_console_enabled=False,
        log_file_enabled=True,
    )

    configure_logging(settings, force=True)
    get_logger(__name__).info("Logger initialized.")

    assert (tmp_path / "vimantra.log").exists()
    assert (tmp_path / "vimantra-daily.log").exists()


def test_log_level_filtering_respects_configuration(
    tmp_path: Path,
) -> None:
    settings = AppSettings(
        _env_file=None,
        log_directory=tmp_path,
        log_level="WARNING",
        log_console_enabled=False,
        log_file_enabled=True,
    )
    configure_logging(settings, force=True)

    logger = get_logger(__name__)
    logger.info("Filtered info message.")
    logger.warning("Visible warning message.")

    log_text = (tmp_path / "vimantra.log").read_text(encoding="utf-8")
    assert "Filtered info message." not in log_text
    assert "Visible warning message." in log_text


def test_rotating_file_handler_rolls_over(tmp_path: Path) -> None:
    settings = AppSettings(
        _env_file=None,
        log_directory=tmp_path,
        log_console_enabled=False,
        log_file_enabled=True,
        log_max_file_size_bytes=128,
        log_retention_days=2,
    )
    configure_logging(settings, force=True)
    logger = get_logger(__name__)

    for index in range(20):
        logger.info("Rotating log line %s with enough text to force rollover.", index)

    assert (tmp_path / "vimantra.log").exists()
    assert any(path.name.startswith("vimantra.log.") for path in tmp_path.iterdir())


def test_audit_event_generation_includes_event_name(tmp_path: Path) -> None:
    settings = AppSettings(
        _env_file=None,
        log_directory=tmp_path,
        log_console_enabled=False,
        log_file_enabled=True,
    )
    configure_logging(settings, force=True)

    audit_event(AuditEvent.MISSION_CREATED, "Mission created.", mission_id=42)

    log_text = (tmp_path / "vimantra.log").read_text(encoding="utf-8")
    assert "audit_event=mission_created" in log_text
    assert "mission_id=42" in log_text


def test_exception_logging_includes_stack_trace(tmp_path: Path) -> None:
    settings = AppSettings(
        _env_file=None,
        log_directory=tmp_path,
        log_console_enabled=False,
        log_file_enabled=True,
    )
    configure_logging(settings, force=True)

    try:
        raise RuntimeError("simulated failure")
    except RuntimeError:
        audit_exception(AuditEvent.UNHANDLED_EXCEPTION, "Unhandled exception.")

    log_text = (tmp_path / "vimantra.log").read_text(encoding="utf-8")
    assert "RuntimeError: simulated failure" in log_text
    assert "audit_event=unhandled_exception" in log_text


def test_logging_settings_load_from_environment_file(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "VIMANTRA_LOG_LEVEL=DEBUG",
                f"VIMANTRA_LOG_DIRECTORY={tmp_path.as_posix()}",
                "VIMANTRA_LOG_MAX_FILE_SIZE_BYTES=2048",
                "VIMANTRA_LOG_RETENTION_DAYS=7",
                "VIMANTRA_LOG_CONSOLE_ENABLED=false",
                "VIMANTRA_LOG_FILE_ENABLED=true",
            ]
        ),
        encoding="utf-8",
    )

    settings = AppSettings(_env_file=env_file)

    assert settings.log_level == "DEBUG"
    assert settings.resolved_log_directory == tmp_path
    assert settings.log_max_file_size_bytes == 2048
    assert settings.log_retention_days == 7
    assert settings.log_console_enabled is False
    assert settings.log_file_enabled is True
