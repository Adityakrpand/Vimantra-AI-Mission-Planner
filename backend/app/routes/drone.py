from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_drone_connection_service
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
from app.services.telemetry import TelemetryService

router = APIRouter(prefix="/drone", tags=["drone"])


@router.post("/connect", response_model=DroneConnectionStatus)
async def connect_drone(
    request: DroneConnectionRequest,
    service: DroneConnectionService = Depends(get_drone_connection_service),
) -> DroneConnectionStatus:
    try:
        return await service.connect(
            system_address=request.system_address,
            timeout_seconds=request.timeout_seconds,
        )
    except DroneConnectionTimeoutError as error:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=str(error),
        ) from error


@router.post("/disconnect", response_model=DroneConnectionStatus)
async def disconnect_drone(
    service: DroneConnectionService = Depends(get_drone_connection_service),
) -> DroneConnectionStatus:
    return await service.disconnect()


@router.get("/status", response_model=DroneConnectionStatus)
def get_drone_status(
    service: DroneConnectionService = Depends(get_drone_connection_service),
) -> DroneConnectionStatus:
    return service.status()


@router.get("/telemetry", response_model=DroneTelemetrySnapshot)
async def get_drone_telemetry(
    service: DroneConnectionService = Depends(get_drone_connection_service),
) -> DroneTelemetrySnapshot:
    return await TelemetryService(service).get_snapshot()


@router.post("/arm", response_model=DroneActionStatus)
async def arm_drone(
    service: DroneConnectionService = Depends(get_drone_connection_service),
) -> DroneActionStatus:
    try:
        return await DroneActionService(service).arm()
    except DroneNotConnectedError as error:
        raise _drone_not_connected() from error


@router.post("/disarm", response_model=DroneActionStatus)
async def disarm_drone(
    service: DroneConnectionService = Depends(get_drone_connection_service),
) -> DroneActionStatus:
    try:
        return await DroneActionService(service).disarm()
    except DroneNotConnectedError as error:
        raise _drone_not_connected() from error


@router.post("/start-mission", response_model=DroneActionStatus)
async def start_mission(
    service: DroneConnectionService = Depends(get_drone_connection_service),
) -> DroneActionStatus:
    try:
        return await DroneActionService(service).start_mission()
    except DroneNotConnectedError as error:
        raise _drone_not_connected() from error


def _drone_not_connected() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="Connect to PX4 SITL before sending drone actions.",
    )
