import logging
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.models.api import api_error
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


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    audit_event(AuditEvent.APPLICATION_STARTUP, "Application startup initiated.")
    try:
        yield
    finally:
        audit_event(AuditEvent.APPLICATION_SHUTDOWN, "Application shutdown completed.")


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
    application = FastAPI(
        title="Vimantra AI Mission Planner API",
        version="1.0.0",
        debug=False,
        lifespan=lifespan,
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

    @application.exception_handler(HTTPException)
    async def http_exception_handler(
        request: Request,
        exc: HTTPException,
    ) -> JSONResponse:
        return _http_exception_response(request, exc)

    @application.exception_handler(StarletteHTTPException)
    async def starlette_http_exception_handler(
        request: Request,
        exc: StarletteHTTPException,
    ) -> JSONResponse:
        return _http_exception_response(request, exc)

    def _http_exception_response(
        request: Request,
        exc: HTTPException | StarletteHTTPException,
    ) -> JSONResponse:
        logger.warning(
            "API error status_code=%s path=%s method=%s",
            exc.status_code,
            request.url.path,
            request.method,
        )
        response = api_error(
            request,
            code=_http_error_code(exc),
            message=_http_error_message(exc),
            details=_http_error_details(exc),
        )
        return _json_response(request, exc.status_code, response.model_dump(mode="json"))

    @application.exception_handler(RequestValidationError)
    async def request_validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        logger.warning(
            "Request validation failed path=%s method=%s errors=%s",
            request.url.path,
            request.method,
            len(exc.errors()),
        )
        response = api_error(
            request,
            code="VALIDATION_ERROR",
            message="Request validation failed.",
            details=exc.errors(),
        )
        return _json_response(
            request,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            response.model_dump(mode="json"),
        )

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
        response = api_error(
            request,
            code="INTERNAL_SERVER_ERROR",
            message="An unexpected server error occurred.",
        )
        return _json_response(
            request,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            response.model_dump(mode="json"),
        )

    return application


app = create_app()


def _json_response(request: Request, status_code: int, content: dict) -> JSONResponse:
    response = JSONResponse(status_code=status_code, content=content)
    response.headers["x-request-id"] = str(getattr(request.state, "request_id", "unknown"))
    return response


def _http_error_code(exc: HTTPException) -> str:
    if isinstance(exc.detail, dict) and "valid" in exc.detail and "errors" in exc.detail:
        return "MISSION_INVALID"
    if isinstance(exc.detail, dict) and "ready" in exc.detail and "checks" in exc.detail:
        return "PREFLIGHT_FAILED"

    return {
        status.HTTP_400_BAD_REQUEST: "BAD_REQUEST",
        status.HTTP_404_NOT_FOUND: "NOT_FOUND",
        status.HTTP_409_CONFLICT: "CONFLICT",
        status.HTTP_422_UNPROCESSABLE_ENTITY: "VALIDATION_ERROR",
        status.HTTP_500_INTERNAL_SERVER_ERROR: "INTERNAL_SERVER_ERROR",
    }.get(exc.status_code, "API_ERROR")


def _http_error_message(exc: HTTPException) -> str:
    if isinstance(exc.detail, str):
        return exc.detail
    if isinstance(exc.detail, dict) and "valid" in exc.detail and "errors" in exc.detail:
        return "Mission validation failed."
    if isinstance(exc.detail, dict) and "ready" in exc.detail and "checks" in exc.detail:
        return "Pre-flight checks failed."

    return "API request failed."


def _http_error_details(exc: HTTPException) -> object | None:
    if isinstance(exc.detail, dict):
        return exc.detail

    return None
