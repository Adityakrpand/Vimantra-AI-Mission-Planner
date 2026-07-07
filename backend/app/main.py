import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.routes.drone import router as drone_router
from app.routes.health import router as health_router
from app.routes.missions import api_router as mission_validation_router
from app.routes.missions import router as missions_router
from config.settings import get_settings
from logging.audit import audit_event, audit_exception
from logging.constants import AuditEvent
from logging.logger import configure_logging, get_logger
from logging.middleware import RequestLoggingMiddleware

logger = get_logger(__name__)


def create_app() -> FastAPI:
    try:
        settings = get_settings()
    except Exception:
        logging.basicConfig(level=logging.ERROR)
        audit_exception(
            AuditEvent.CONFIGURATION_VALIDATION_FAILED,
            "Configuration validation failed during application startup.",
        )
        raise

    configure_logging(settings)
    audit_event(AuditEvent.CONFIGURATION_LOADED, "Configuration loaded.")
    audit_event(AuditEvent.APPLICATION_STARTUP, "Application startup initiated.")
    application = FastAPI(
        title="Vimantra AI Mission Planner API",
        version="1.0.0-rc1",
        debug=settings.debug,
    )
    application.add_middleware(RequestLoggingMiddleware)
    application.add_middleware(
        CORSMiddleware,
        allow_credentials=False,
        allow_headers=["*"],
        allow_methods=["*"],
        allow_origins=settings.cors_origins,
    )
    application.include_router(drone_router)
    application.include_router(health_router)
    application.include_router(mission_validation_router)
    application.include_router(missions_router)

    @application.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        logger.exception(
            "Unhandled exception path=%s method=%s",
            request.url.path,
            request.method,
        )
        audit_exception(
            AuditEvent.UNHANDLED_EXCEPTION,
            "Unhandled exception returned as API error.",
        )
        return JSONResponse(
            status_code=500,
            content={"detail": "An unexpected server error occurred."},
        )

    @application.on_event("shutdown")
    async def audit_shutdown() -> None:
        audit_event(AuditEvent.APPLICATION_SHUTDOWN, "Application shutdown completed.")

    return application


app = create_app()
