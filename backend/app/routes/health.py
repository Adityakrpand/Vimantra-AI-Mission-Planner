from fastapi import APIRouter, Request
from pydantic import BaseModel

from app.models.api import ApiResponse, api_success


class HealthResponse(BaseModel):
    status: str
    service: str


router = APIRouter(tags=["health"])


@router.get("/health", response_model=ApiResponse[HealthResponse])
def health_check(request: Request) -> ApiResponse[HealthResponse]:
    return api_success(request, HealthResponse(status="ok", service="vimantra-backend"))
