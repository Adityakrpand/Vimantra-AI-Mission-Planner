from pathlib import Path

import pytest
from pydantic import ValidationError

from app.models.mission import MissionCreate, Waypoint
from app.services.mission_storage import MissionNotFoundError, MissionStorage


def test_save_and_load_mission(tmp_path: Path) -> None:
    storage = create_storage(tmp_path)
    mission = MissionCreate(
        name="Survey Block A",
        waypoints=[
            Waypoint(
                sequence=4,
                latitude=19.076,
                longitude=72.8777,
                altitude_meters=80,
                speed_meters_per_second=8,
            ),
            Waypoint(
                sequence=9,
                latitude=19.0821,
                longitude=72.8903,
                altitude_meters=90,
                speed_meters_per_second=9,
            ),
        ],
    )

    saved_mission = storage.save_mission(mission)
    loaded_mission = storage.get_mission(saved_mission.id)

    assert loaded_mission.name == "Survey Block A"
    assert [waypoint.sequence for waypoint in loaded_mission.waypoints] == [1, 2]
    assert loaded_mission.waypoints[0].latitude == 19.076


def test_list_missions_returns_saved_missions(tmp_path: Path) -> None:
    storage = create_storage(tmp_path)
    first_mission = storage.save_mission(create_mission("First Mission"))
    second_mission = storage.save_mission(create_mission("Second Mission"))

    missions = storage.list_missions()

    assert [mission.id for mission in missions] == [second_mission.id, first_mission.id]


def test_delete_mission_removes_waypoints(tmp_path: Path) -> None:
    storage = create_storage(tmp_path)
    mission = storage.save_mission(create_mission("Temporary Mission"))

    storage.delete_mission(mission.id)

    with pytest.raises(MissionNotFoundError):
        storage.get_mission(mission.id)


def test_delete_missing_mission_raises_not_found(tmp_path: Path) -> None:
    storage = create_storage(tmp_path)

    with pytest.raises(MissionNotFoundError):
        storage.delete_mission(404)


def test_mission_validation_rejects_invalid_waypoint() -> None:
    with pytest.raises(ValidationError):
        MissionCreate(
            name="Invalid Mission",
            waypoints=[
                Waypoint(
                    sequence=1,
                    latitude=95,
                    longitude=72.8777,
                    altitude_meters=80,
                    speed_meters_per_second=8,
                )
            ],
        )


def create_storage(tmp_path: Path) -> MissionStorage:
    storage = MissionStorage(tmp_path / "missions.sqlite")
    storage.initialize()
    return storage


def create_mission(name: str) -> MissionCreate:
    return MissionCreate(
        name=name,
        waypoints=[
            Waypoint(
                sequence=1,
                latitude=19.076,
                longitude=72.8777,
                altitude_meters=80,
                speed_meters_per_second=8,
            )
        ],
    )
