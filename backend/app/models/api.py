from __future__ import annotations

from typing import Any, Generic, TypeVar

from fastapi import Request
from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class ApiError(BaseModel):
    model_config = ConfigDict(frozen=True)

    code: str
    message: str
    details: Any | None = None


class ApiResponse(BaseModel, Generic[T]):
    model_config = ConfigDict(frozen=True)

    success: bool
    request_id: str
    data: T | None = None
    error: ApiError | None = None


class DeleteResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    deleted: bool = Field(default=True)


def api_success(request: Request, data: T) -> ApiResponse[T]:
    return ApiResponse(
        success=True,
        request_id=request_id_from_request(request),
        data=data,
        error=None,
    )


def api_error(
    request: Request,
    *,
    code: str,
    message: str,
    details: Any | None = None,
) -> ApiResponse[None]:
    return ApiResponse(
        success=False,
        request_id=request_id_from_request(request),
        data=None,
        error=ApiError(code=code, message=message, details=details),
    )


def request_id_from_request(request: Request) -> str:
    return str(getattr(request.state, "request_id", "unknown"))
