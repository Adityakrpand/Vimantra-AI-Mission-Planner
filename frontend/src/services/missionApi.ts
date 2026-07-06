import type {
  MissionRecord,
  MissionUploadStatus,
  Waypoint
} from "../types/mission";
import { apiBaseUrl } from "./apiConfig";

type ApiWaypoint = {
  sequence: number;
  latitude: number;
  longitude: number;
  altitude_meters: number;
  speed_meters_per_second: number;
};

type ApiMissionRecord = {
  id: number;
  name: string;
  waypoints: ApiWaypoint[];
  created_at: string;
  updated_at: string;
};

type ApiMissionUploadStatus = {
  mission_id: number;
  uploaded: boolean;
  waypoint_count: number;
  message: string;
};

export async function saveMission(
  name: string,
  waypoints: Waypoint[]
): Promise<MissionRecord> {
  const response = await fetch(`${apiBaseUrl}/missions`, {
    body: JSON.stringify({
      name,
      waypoints: waypoints.map(toApiWaypoint)
    }),
    headers: {
      "Content-Type": "application/json"
    },
    method: "POST"
  });

  return parseMissionResponse(response);
}

export async function listMissions(): Promise<MissionRecord[]> {
  const response = await fetch(`${apiBaseUrl}/missions`);

  if (!response.ok) {
    throw new Error("Unable to load saved missions.");
  }

  const missions = (await response.json()) as ApiMissionRecord[];
  return missions.map(fromApiMission);
}

export async function loadMission(missionId: number): Promise<MissionRecord> {
  const response = await fetch(`${apiBaseUrl}/missions/${missionId}`);

  return parseMissionResponse(response);
}

export async function uploadMission(
  missionId: number
): Promise<MissionUploadStatus> {
  const response = await fetch(`${apiBaseUrl}/missions/${missionId}/upload`, {
    method: "POST"
  });

  if (!response.ok) {
    throw new Error("Mission upload failed.");
  }

  const status = (await response.json()) as ApiMissionUploadStatus;
  return {
    missionId: status.mission_id,
    uploaded: status.uploaded,
    waypointCount: status.waypoint_count,
    message: status.message
  };
}

async function parseMissionResponse(response: Response): Promise<MissionRecord> {
  if (!response.ok) {
    throw new Error("Mission request failed.");
  }

  return fromApiMission((await response.json()) as ApiMissionRecord);
}

function toApiWaypoint(waypoint: Waypoint): ApiWaypoint {
  return {
    sequence: waypoint.sequence,
    latitude: waypoint.latitude,
    longitude: waypoint.longitude,
    altitude_meters: waypoint.altitudeMeters,
    speed_meters_per_second: waypoint.speedMetersPerSecond
  };
}

function fromApiMission(mission: ApiMissionRecord): MissionRecord {
  return {
    id: mission.id,
    name: mission.name,
    createdAt: mission.created_at,
    updatedAt: mission.updated_at,
    waypoints: mission.waypoints.map((waypoint) => ({
      id: `${mission.id}-${waypoint.sequence}`,
      sequence: waypoint.sequence,
      latitude: waypoint.latitude,
      longitude: waypoint.longitude,
      altitudeMeters: waypoint.altitude_meters,
      speedMetersPerSecond: waypoint.speed_meters_per_second
    }))
  };
}
