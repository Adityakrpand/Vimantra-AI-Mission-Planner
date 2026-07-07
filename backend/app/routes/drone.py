from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.dependencies import (
    get_app_settings,
    get_drone_connection_service,
    get_mission_storage,
    get_mission_validator,
    get_preflight_service,
)
from app.models.api import ApiResponse, api_success
from app.models.drone import (
    DroneActionStatus,
    DroneConnectionRequest,
    DroneConnectionStatus,
    DroneTelemetrySnapshot,
)
from app.services.drone_action import DroneActionService
from app.services.drone_connection import (
    DroneConnectionService,
    DroneConnectionTimeoutError,
    DroneNotConnectedError,
)
from app.services.mission_storage import MissionNotFoundError, MissionStorage
from app.services.telemetry import TelemetryService
from config.settings import AppSettings
from mission.validator import MissionValidator
from preflight.exceptions import PreFlightCheckFailedError
from preflight.service import PreFlightService

router = APIRouter(prefix="/drone", tags=["drone"])


@router.post("/connect", response_model=ApiResponse[DroneConnectionStatus])
async def connect_drone(
    http_request: Request,
    request: DroneConnectionRequest,
    service: DroneConnectionService = Depends(get_drone_connection_service),
    settings: AppSettings = Depends(get_app_settings),
) -> ApiResponse[DroneConnectionStatus]:
    try:
        return api_success(
            http_request,
            await service.connect(
                system_address=request.system_address or settings.mavsdk_address,
                timeout_seconds=(
                    request.timeout_seconds or settings.drone_connection_timeout_seconds
                ),
            ),
        )
    except DroneConnectionTimeoutError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(error),
        ) from error


@router.post("/disconnect", response_model=ApiResponse[DroneConnectionStatus])
async def disconnect_drone(
    request: Request,
    service: DroneConnectionService = Depends(get_drone_connection_service),
) -> ApiResponse[DroneConnectionStatus]:
    return api_success(request, await service.disconnect())


@router.get("/status", response_model=ApiResponse[DroneConnectionStatus])
def get_drone_status(
    request: Request,
    service: DroneConnectionService = Depends(get_drone_connection_service),
) -> ApiResponse[DroneConnectionStatus]:
    return api_success(request, service.status())


@router.get("/telemetry", response_model=ApiResponse[DroneTelemetrySnapshot])
async def get_drone_telemetry(
    request: Request,
    service: DroneConnectionService = Depends(get_drone_connection_service),
    settings: AppSettings = Depends(get_app_settings),
) -> ApiResponse[DroneTelemetrySnapshot]:
    return api_success(
        request,
        await TelemetryService(
            service,
            timeout_seconds=settings.telemetry_read_timeout_seconds,
        ).get_snapshot(),
    )


@router.post("/arm", response_model=ApiResponse[DroneActionStatus])
async def arm_drone(
    request: Request,
    service: DroneConnectionService = Depends(get_drone_connection_service),
) -> ApiResponse[DroneActionStatus]:
    try:
        return api_success(request, await DroneActionService(service).arm())
    except DroneNotConnectedError as error:
        raise _drone_not_connected() from error


@router.post("/disarm", response_model=ApiResponse[DroneActionStatus])
async def disarm_drone(
    request: Request,
    service: DroneConnectionService = Depends(get_drone_connection_service),
) -> ApiResponse[DroneActionStatus]:
    try:
        return api_success(request, await DroneActionService(service).disarm())
    except DroneNotConnectedError as error:
        raise _drone_not_connected() from error


@router.post("/start-mission", response_model=ApiResponse[DroneActionStatus])
async def start_mission(
    request: Request,
    service: DroneConnectionService = Depends(get_drone_connection_service),
    storage: MissionStorage = Depends(get_mission_storage),
    mission_validator: MissionValidator = Depends(get_mission_validator),
    preflight_service: PreFlightService = Depends(get_preflight_service),
    settings: AppSettings = Depends(get_app_settings),
) -> ApiResponse[DroneActionStatus]:
    try:
        mission_id = service.loaded_mission_id()
        if mission_id is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Upload a mission before starting.",
            )
        try:
            mission = storage.get_mission(mission_id)
        except MissionNotFoundError as error:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Loaded mission {error.mission_id} is no longer available.",
            ) from error

        validation_result = mission_validator.validate(mission)
        telemetry = await TelemetryService(
            service,
            timeout_seconds=settings.telemetry_read_timeout_seconds,
        ).get_snapshot()
        preflight_result = preflight_service.run(
            mission=mission,
            mission_validation=validation_result,
            drone_status=service.status(),
            telemetry=telemetry,
            mission_loaded=True,
        )
        if not preflight_result.ready:
            raise PreFlightCheckFailedError(preflight_result)

        return api_success(request, await DroneActionService(service).start_mission())
    except DroneNotConnectedError as error:
        raise _drone_not_connected() from error
    except PreFlightCheckFailedError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=error.result.model_dump(mode="json"),
        ) from error


def _drone_not_connected() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="Connect to PX4 SITL before sending drone actions.",
    )
