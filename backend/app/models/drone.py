from pydantic import BaseModel, ConfigDict, Field


class DroneConnectionRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    system_address: str | None = Field(default=None, min_length=1, max_length=200)
    timeout_seconds: float | None = Field(default=None, gt=0, le=60)


class DroneConnectionStatus(BaseModel):
    model_config = ConfigDict(frozen=True)

    connected: bool
    system_address: str | None = None
    message: str


class DroneActionStatus(BaseModel):
    model_config = ConfigDict(frozen=True)

    completed: bool
    action: str
    message: str


class DroneTelemetrySnapshot(BaseModel):
    model_config = ConfigDict(frozen=True)

    connected: bool
    latitude: float | None = None
    longitude: float | None = None
    altitude_meters: float | None = None
    speed_meters_per_second: float | None = None
    heading_degrees: float | None = None
    battery_percent: float | None = None
    gps_satellites: int | None = None
    gps_fix_type: str | None = None
    flight_mode: str | None = None
    mission_current: int | None = None
    mission_total: int | None = None
    home_position_available: bool = False
    message: str
