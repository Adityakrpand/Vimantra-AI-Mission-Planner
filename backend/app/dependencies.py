from functools import lru_cache
from pathlib import Path

from app.services.drone_connection import DroneConnectionService
from app.services.mission_storage import MissionStorage


@lru_cache
def get_mission_storage() -> MissionStorage:
    storage = MissionStorage(_default_database_path())
    storage.initialize()
    return storage


@lru_cache
def get_drone_connection_service() -> DroneConnectionService:
    return DroneConnectionService()


def _default_database_path() -> Path:
    return Path(__file__).resolve().parents[2] / "database" / "missions.sqlite"
