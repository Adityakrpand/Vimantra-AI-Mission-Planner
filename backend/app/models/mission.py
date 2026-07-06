from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class Waypoint(BaseModel):
    model_config = ConfigDict(frozen=True)

    sequence: int = Field(gt=0)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    altitude_meters: float = Field(gt=0, le=10000)
    speed_meters_per_second: float = Field(gt=0, le=100)


class MissionCreate(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str = Field(min_length=1, max_length=120)
    waypoints: list[Waypoint] = Field(min_length=1)


class MissionRecord(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: int
    name: str
    waypoints: list[Waypoint]
    created_at: datetime
    updated_at: datetime


class MissionUploadStatus(BaseModel):
    model_config = ConfigDict(frozen=True)

    mission_id: int
    uploaded: bool
    waypoint_count: int
    message: str
