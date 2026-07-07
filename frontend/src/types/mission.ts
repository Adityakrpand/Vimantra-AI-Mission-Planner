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

export type PreFlightCheckStatus = "PASS" | "WARNING" | "FAIL";

export type PreFlightCheck = {
  name: string;
  status: PreFlightCheckStatus;
  mandatory: boolean;
  message: string;
};

export type PreFlightResult = {
  ready: boolean;
  score: number;
  checks: PreFlightCheck[];
  warnings: PreFlightCheck[];
};

export type MissionAnalyticsWarning = {
  code: string;
  message: string;
};

export type MissionAnalyticsResult = {
  summary: {
    distance_meters: number;
    estimated_flight_time_seconds: number;
    estimated_battery_usage_percent: number;
    estimated_battery_remaining_percent: number;
    waypoint_count: number;
  };
  statistics: {
    maximum_altitude_meters: number;
    minimum_altitude_meters: number;
    average_altitude_meters: number;
    average_speed_meters_per_second: number;
    maximum_speed_meters_per_second: number;
    total_climb_meters: number;
    total_descent_meters: number;
    turn_count: number;
    longest_leg_distance_meters: number;
    shortest_leg_distance_meters: number;
  };
  warnings: MissionAnalyticsWarning[];
};

export type MissionValidationEngineStatus = "ready" | "warning" | "unsafe";
export type MissionValidationCheckStatus = "PASS" | "WARNING" | "FAIL";

export type MissionValidationEngineIssue = {
  code: string;
  message: string;
  category: string;
  waypoint: number | null;
};

export type MissionValidationEngineCheck = {
  name: string;
  category: string;
  status: MissionValidationCheckStatus;
  message: string;
};

export type MissionValidationEngineResult = {
  status: MissionValidationEngineStatus;
  score: number;
  errors: MissionValidationEngineIssue[];
  warnings: MissionValidationEngineIssue[];
  checks: MissionValidationEngineCheck[];
  summary: {
    errors: number;
    warnings: number;
    passed: boolean;
    passed_checks: number;
    failed_checks: number;
  };
};
