import { apiBaseUrl } from "./apiConfig";

export type DroneConnectionStatus = {
  connected: boolean;
  systemAddress: string | null;
  message: string;
};

export type DroneActionStatus = {
  completed: boolean;
  action: "arm" | "disarm" | "start_mission";
  message: string;
};

export type DroneTelemetrySnapshot = {
  connected: boolean;
  latitude: number | null;
  longitude: number | null;
  altitudeMeters: number | null;
  speedMetersPerSecond: number | null;
  headingDegrees: number | null;
  batteryPercent: number | null;
  gpsFixType: string | null;
  flightMode: string | null;
  missionCurrent: number | null;
  missionTotal: number | null;
  message: string;
};

type ApiDroneConnectionStatus = {
  connected: boolean;
  system_address: string | null;
  message: string;
};

type ApiDroneActionStatus = {
  completed: boolean;
  action: "arm" | "disarm" | "start_mission";
  message: string;
};

type ApiDroneTelemetrySnapshot = {
  connected: boolean;
  latitude: number | null;
  longitude: number | null;
  altitude_meters: number | null;
  speed_meters_per_second: number | null;
  heading_degrees: number | null;
  battery_percent: number | null;
  gps_fix_type: string | null;
  flight_mode: string | null;
  mission_current: number | null;
  mission_total: number | null;
  message: string;
};

export async function getDroneStatus(): Promise<DroneConnectionStatus> {
  const response = await fetch(`${apiBaseUrl}/drone/status`);

  return parseDroneStatusResponse(response);
}

export async function connectDrone(
  systemAddress?: string
): Promise<DroneConnectionStatus> {
  const response = await fetch(`${apiBaseUrl}/drone/connect`, {
    body: JSON.stringify({
      system_address: systemAddress
    }),
    headers: {
      "Content-Type": "application/json"
    },
    method: "POST"
  });

  return parseDroneStatusResponse(response);
}

export async function disconnectDrone(): Promise<DroneConnectionStatus> {
  const response = await fetch(`${apiBaseUrl}/drone/disconnect`, {
    method: "POST"
  });

  return parseDroneStatusResponse(response);
}

export async function armDrone(): Promise<DroneActionStatus> {
  const response = await fetch(`${apiBaseUrl}/drone/arm`, {
    method: "POST"
  });

  return parseDroneActionResponse(response);
}

export async function disarmDrone(): Promise<DroneActionStatus> {
  const response = await fetch(`${apiBaseUrl}/drone/disarm`, {
    method: "POST"
  });

  return parseDroneActionResponse(response);
}

export async function startMission(): Promise<DroneActionStatus> {
  const response = await fetch(`${apiBaseUrl}/drone/start-mission`, {
    method: "POST"
  });

  return parseDroneActionResponse(response);
}

export async function getDroneTelemetry(): Promise<DroneTelemetrySnapshot> {
  const response = await fetch(`${apiBaseUrl}/drone/telemetry`);

  if (!response.ok) {
    throw new Error("Drone telemetry request failed.");
  }

  const snapshot = (await response.json()) as ApiDroneTelemetrySnapshot;
  return {
    connected: snapshot.connected,
    latitude: snapshot.latitude,
    longitude: snapshot.longitude,
    altitudeMeters: snapshot.altitude_meters,
    speedMetersPerSecond: snapshot.speed_meters_per_second,
    headingDegrees: snapshot.heading_degrees,
    batteryPercent: snapshot.battery_percent,
    gpsFixType: snapshot.gps_fix_type,
    flightMode: snapshot.flight_mode,
    missionCurrent: snapshot.mission_current,
    missionTotal: snapshot.mission_total,
    message: snapshot.message
  };
}

async function parseDroneStatusResponse(
  response: Response
): Promise<DroneConnectionStatus> {
  if (!response.ok) {
    throw new Error("Drone connection request failed.");
  }

  const status = (await response.json()) as ApiDroneConnectionStatus;
  return {
    connected: status.connected,
    systemAddress: status.system_address,
    message: status.message
  };
}

async function parseDroneActionResponse(
  response: Response
): Promise<DroneActionStatus> {
  if (!response.ok) {
    throw new Error("Drone action request failed.");
  }

  const status = (await response.json()) as ApiDroneActionStatus;
  return {
    completed: status.completed,
    action: status.action,
    message: status.message
  };
}
