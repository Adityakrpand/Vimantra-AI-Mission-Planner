export type Waypoint = {
  id: string;
  sequence: number;
  latitude: number;
  longitude: number;
  altitudeMeters: number;
  speedMetersPerSecond: number;
};

export type MissionRecord = {
  id: number;
  name: string;
  waypoints: Waypoint[];
  createdAt: string;
  updatedAt: string;
};

export type MissionUploadStatus = {
  missionId: number;
  uploaded: boolean;
  waypointCount: number;
  message: string;
};
