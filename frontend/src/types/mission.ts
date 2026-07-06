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

export type MissionValidationIssue = {
  code: string;
  waypoint: number | null;
  message: string;
};

export type MissionValidationStatistics = {
  waypoints: number;
  distance: number;
};

export type MissionValidationResult = {
  valid: boolean;
  errors: MissionValidationIssue[];
  warnings: MissionValidationIssue[];
  statistics: MissionValidationStatistics;
};
