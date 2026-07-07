from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.dependencies import (
    get_app_settings,
    get_mission_analytics_service,
    get_mission_storage,
    get_mission_validator,
    get_preflight_service,
)
from analytics.models import MissionAnalyticsResult
from analytics.service import MissionAnalyticsService
from app.dependencies import get_drone_connection_service
from app.models.api import ApiResponse, DeleteResult, api_success
from app.models.mission import MissionCreate, MissionRecord, MissionUploadStatus
from app.services.drone_connection import DroneConnectionService, DroneNotConnectedError
from app.services.mission_storage import MissionNotFoundError, MissionStorage
from app.services.mission_upload import MissionUploadService
from app.services.telemetry import TelemetryService
from config.settings import AppSettings
from mission.exceptions import MissionValidationError
from mission.validation_models import MissionValidationRequest, MissionValidationResult
from mission.validator import MissionValidator
from preflight.exceptions import PreFlightCheckFailedError
from preflight.models import PreFlightResult
from preflight.service import PreFlightService

router = APIRouter(prefix="/missions", tags=["missions"])
api_router = APIRouter(prefix="/api/missions", tags=["mission validation"])


@router.post("", response_model=ApiResponse[MissionRecord], status_code=status.HTTP_201_CREATED)
def create_mission(
    request: Request,
    mission: MissionCreate,
    storage: MissionStorage = Depends(get_mission_storage),
) -> ApiResponse[MissionRecord]:
    return api_success(request, storage.save_mission(mission))


@router.get("", response_model=ApiResponse[list[MissionRecord]])
def list_missions(
    request: Request,
    storage: MissionStorage = Depends(get_mission_storage),
) -> ApiResponse[list[MissionRecord]]:
    return api_success(request, storage.list_missions())


@router.get("/{mission_id}", response_model=ApiResponse[MissionRecord])
def get_mission(
    request: Request,
    mission_id: int,
    storage: MissionStorage = Depends(get_mission_storage),
) -> ApiResponse[MissionRecord]:
    try:
        return api_success(request, storage.get_mission(mission_id))
    except MissionNotFoundError as error:
        raise _mission_not_found(error.mission_id) from error


@router.delete("/{mission_id}", response_model=ApiResponse[DeleteResult])
def delete_mission(
    request: Request,
    mission_id: int,
    storage: MissionStorage = Depends(get_mission_storage),
) -> ApiResponse[DeleteResult]:
    try:
        storage.delete_mission(mission_id)
    except MissionNotFoundError as error:
        raise _mission_not_found(error.mission_id) from error

    return api_success(request, DeleteResult())


@router.post("/{mission_id}/upload", response_model=ApiResponse[MissionUploadStatus])
async def upload_mission(
    request: Request,
    mission_id: int,
    storage: MissionStorage = Depends(get_mission_storage),
    drone_connection: DroneConnectionService = Depends(get_drone_connection_service),
    mission_validator: MissionValidator = Depends(get_mission_validator),
    preflight_service: PreFlightService = Depends(get_preflight_service),
    settings: AppSettings = Depends(get_app_settings),
) -> ApiResponse[MissionUploadStatus]:
    upload_service = MissionUploadService(
        storage,
        drone_connection,
        mission_validator,
        preflight_service,
        upload_timeout_seconds=settings.mission_upload_timeout_seconds,
        telemetry_timeout_seconds=settings.telemetry_read_timeout_seconds,
    )

    try:
        return api_success(request, await upload_service.upload_mission(mission_id))
    except MissionNotFoundError as error:
        raise _mission_not_found(error.mission_id) from error
    except DroneNotConnectedError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Connect to PX4 SITL before uploading a mission.",
        ) from error
    except MissionValidationError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error.result.model_dump(),
        ) from error
    except PreFlightCheckFailedError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=error.result.model_dump(mode="json"),
        ) from error


@router.post("/{mission_id}/preflight", response_model=ApiResponse[PreFlightResult])
async def run_preflight(
    request: Request,
    mission_id: int,
    storage: MissionStorage = Depends(get_mission_storage),
    drone_connection: DroneConnectionService = Depends(get_drone_connection_service),
    mission_validator: MissionValidator = Depends(get_mission_validator),
    preflight_service: PreFlightService = Depends(get_preflight_service),
    settings: AppSettings = Depends(get_app_settings),
) -> ApiResponse[PreFlightResult]:
    try:
        mission = storage.get_mission(mission_id)
    except MissionNotFoundError as error:
        raise _mission_not_found(error.mission_id) from error

    validation_result = mission_validator.validate(mission)
    telemetry = await TelemetryService(
        drone_connection,
        timeout_seconds=settings.telemetry_read_timeout_seconds,
    ).get_snapshot()
    result = preflight_service.run(
        mission=mission,
        mission_validation=validation_result,
        drone_status=drone_connection.status(),
        telemetry=telemetry,
        mission_loaded=True,
    )
    return api_success(request, result)


@router.get("/{mission_id}/analytics", response_model=ApiResponse[MissionAnalyticsResult])
def get_mission_analytics(
    request: Request,
    mission_id: int,
    storage: MissionStorage = Depends(get_mission_storage),
    analytics_service: MissionAnalyticsService = Depends(get_mission_analytics_service),
) -> ApiResponse[MissionAnalyticsResult]:
    try:
        mission = storage.get_mission(mission_id)
    except MissionNotFoundError as error:
        raise _mission_not_found(error.mission_id) from error

    return api_success(request, analytics_service.generate(mission))


@api_router.post("/validate", response_model=ApiResponse[MissionValidationResult])
def validate_mission(
    request: Request,
    mission: MissionValidationRequest,
    mission_validator: MissionValidator = Depends(get_mission_validator),
) -> ApiResponse[MissionValidationResult]:
    return api_success(request, mission_validator.validate(mission))


def _mission_not_found(mission_id: int) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Mission {mission_id} was not found.",
    )
