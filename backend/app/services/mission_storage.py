from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable

from app.models.mission import MissionCreate, MissionRecord, Waypoint


class MissionNotFoundError(Exception):
    def __init__(self, mission_id: int) -> None:
        super().__init__(f"Mission {mission_id} was not found.")
        self.mission_id = mission_id


class MissionStorage:
    def __init__(self, database_path: Path, schema_path: Path | None = None) -> None:
        self.database_path = database_path
        self.schema_path = schema_path or _default_schema_path()

    def initialize(self) -> None:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.executescript(self.schema_path.read_text(encoding="utf-8"))

    def save_mission(self, mission: MissionCreate) -> MissionRecord:
        ordered_waypoints = _normalize_waypoint_sequence(mission.waypoints)

        with self._connect() as connection:
            cursor = connection.execute(
                "INSERT INTO missions (name) VALUES (?)",
                (mission.name.strip(),),
            )
            mission_id = int(cursor.lastrowid)
            connection.executemany(
                """
                INSERT INTO mission_waypoints (
                    mission_id,
                    sequence,
                    latitude,
                    longitude,
                    altitude_meters,
                    speed_meters_per_second
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        mission_id,
                        waypoint.sequence,
                        waypoint.latitude,
                        waypoint.longitude,
                        waypoint.altitude_meters,
                        waypoint.speed_meters_per_second,
                    )
                    for waypoint in ordered_waypoints
                ],
            )

        return self.get_mission(mission_id)

    def list_missions(self) -> list[MissionRecord]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT id
                FROM missions
                ORDER BY updated_at DESC, id DESC
                """
            ).fetchall()

        return [self.get_mission(int(row["id"])) for row in rows]

    def get_mission(self, mission_id: int) -> MissionRecord:
        with self._connect() as connection:
            mission_row = connection.execute(
                """
                SELECT id, name, created_at, updated_at
                FROM missions
                WHERE id = ?
                """,
                (mission_id,),
            ).fetchone()

            if mission_row is None:
                raise MissionNotFoundError(mission_id)

            waypoint_rows = connection.execute(
                """
                SELECT
                    sequence,
                    latitude,
                    longitude,
                    altitude_meters,
                    speed_meters_per_second
                FROM mission_waypoints
                WHERE mission_id = ?
                ORDER BY sequence ASC
                """,
                (mission_id,),
            ).fetchall()

        return MissionRecord(
            id=int(mission_row["id"]),
            name=str(mission_row["name"]),
            created_at=mission_row["created_at"],
            updated_at=mission_row["updated_at"],
            waypoints=[
                Waypoint(
                    sequence=int(row["sequence"]),
                    latitude=float(row["latitude"]),
                    longitude=float(row["longitude"]),
                    altitude_meters=float(row["altitude_meters"]),
                    speed_meters_per_second=float(row["speed_meters_per_second"]),
                )
                for row in waypoint_rows
            ],
        )

    def delete_mission(self, mission_id: int) -> None:
        with self._connect() as connection:
            cursor = connection.execute(
                "DELETE FROM missions WHERE id = ?",
                (mission_id,),
            )

        if cursor.rowcount == 0:
            raise MissionNotFoundError(mission_id)

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection


def _normalize_waypoint_sequence(waypoints: Iterable[Waypoint]) -> list[Waypoint]:
    return [
        waypoint.model_copy(update={"sequence": index + 1})
        for index, waypoint in enumerate(waypoints)
    ]


def _default_schema_path() -> Path:
    return Path(__file__).resolve().parents[3] / "database" / "schema.sql"
