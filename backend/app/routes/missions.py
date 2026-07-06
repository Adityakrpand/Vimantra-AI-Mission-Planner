from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.dependencies import get_mission_storage
from app.dependencies import get_drone_connection_service
from app.models.mission import MissionCreate, MissionRecord, MissionUploadStatus
from app.services.drone_connection import DroneConnectionService, DroneNotConnectedError
from app.services.mission_storage import MissionNotFoundError, MissionStorage
from app.services.mission_upload import MissionUploadService
from mission.exceptions import MissionValidationError
from mission.validation_models import MissionValidationRequest, MissionValidationResult
from mission.validator import MissionValidator

router = APIRouter(prefix="/missions", tags=["missions"])
api_router = APIRouter(prefix="/api/missions", tags=["mission validation"])


@router.post("", response_model=MissionRecord, status_code=status.HTTP_201_CREATED)
def create_mission(
    mission: MissionCreate,
    storage: MissionStorage = Depends(get_mission_storage),
) -> MissionRecord:
    return storage.save_mission(mission)


@router.get("", response_model=list[MissionRecord])
def list_missions(
    storage: MissionStorage = Depends(get_mission_storage),
) -> list[MissionRecord]:
    return storage.list_missions()


@router.get("/{mission_id}", response_model=MissionRecord)
def get_mission(
    mission_id: int,
    storage: MissionStorage = Depends(get_mission_storage),
) -> MissionRecord:
    try:
        return storage.get_mission(mission_id)
    except MissionNotFoundError as error:
        raise _mission_not_found(error.mission_id) from error


@router.delete("/{mission_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_mission(
    mission_id: int,
    storage: MissionStorage = Depends(get_mission_storage),
) -> Response:
    try:
        storage.delete_mission(mission_id)
    except MissionNotFoundError as error:
        raise _mission_not_found(error.mission_id) from error

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{mission_id}/upload", response_model=MissionUploadStatus)
async def upload_mission(
    mission_id: int,
    storage: MissionStorage = Depends(get_mission_storage),
    drone_connection: DroneConnectionService = Depends(get_drone_connection_service),
) -> MissionUploadStatus:
    upload_service = MissionUploadService(storage, drone_connection)

    try:
        return await upload_service.upload_mission(mission_id)
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


@api_router.post("/validate", response_model=MissionValidationResult)
def validate_mission(
    mission: MissionValidationRequest,
) -> MissionValidationResult:
    return MissionValidator().validate(mission)


def _mission_not_found(mission_id: int) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Mission {mission_id} was not found.",
    )
