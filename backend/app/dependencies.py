from functools import lru_cache

from analytics.service import MissionAnalyticsService
from app.services.drone_connection import DroneConnectionService
from app.services.mission_storage import MissionStorage
from config.settings import AppSettings, get_settings
from mission.validator import MissionValidator
from preflight.service import PreFlightService


@lru_cache
def get_mission_storage() -> MissionStorage:
    storage = MissionStorage(get_settings().resolved_database_path)
    storage.initialize()
    return storage


@lru_cache
def get_drone_connection_service() -> DroneConnectionService:
    return DroneConnectionService()


@lru_cache
def get_mission_validator() -> MissionValidator:
    return MissionValidator(get_settings().mission_validation_config())


@lru_cache
def get_preflight_service() -> PreFlightService:
    return PreFlightService(get_settings().preflight_config())


@lru_cache
def get_mission_analytics_service() -> MissionAnalyticsService:
    return MissionAnalyticsService(get_settings().mission_analytics_config())


def get_app_settings() -> AppSettings:
    return get_settings()
