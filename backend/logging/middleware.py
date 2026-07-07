from __future__ import annotations

import time
from uuid import uuid4

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from logging.context import log_context
from logging.logger import get_logger

logger = get_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        request_id = request.headers.get("x-request-id", str(uuid4()))
        request.state.request_id = request_id
        start_time = time.perf_counter()
        with log_context(request_id=request_id):
            logger.info(
                "Incoming request method=%s path=%s",
                request.method,
                request.url.path,
            )
            try:
                response = await call_next(request)
            except Exception:
                elapsed_ms = _elapsed_ms(start_time)
                logger.exception(
                    "Request failed method=%s path=%s duration_ms=%.2f",
                    request.method,
                    request.url.path,
                    elapsed_ms,
                )
                raise

            elapsed_ms = _elapsed_ms(start_time)
            if response.status_code >= 400:
                logger.warning(
                    "Request returned failure method=%s path=%s status_code=%s duration_ms=%.2f",
                    request.method,
                    request.url.path,
                    response.status_code,
                    elapsed_ms,
                )
            else:
                logger.info(
                    "Request completed method=%s path=%s status_code=%s duration_ms=%.2f",
                    request.method,
                    request.url.path,
                    response.status_code,
                    elapsed_ms,
                )
            response.headers["x-request-id"] = request_id
            return response


def _elapsed_ms(start_time: float) -> float:
    return (time.perf_counter() - start_time) * 1000
