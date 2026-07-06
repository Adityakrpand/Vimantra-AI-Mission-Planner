import { useEffect, useMemo, useState } from "react";

import { MapWorkspace } from "./components/MapWorkspace";
import {
  armDrone,
  connectDrone,
  disconnectDrone,
  disarmDrone,
  getDroneTelemetry,
  getDroneStatus,
  startMission,
  type DroneConnectionStatus,
  type DroneTelemetrySnapshot
} from "./services/droneApi";
import {
  listMissions,
  loadMission,
  saveMission,
  uploadMission,
  validateMission
} from "./services/missionApi";
import type {
  MissionRecord,
  MissionValidationResult,
  Waypoint
} from "./types/mission";

type TelemetryMetric = {
  label: string;
  value: string;
};

type MissionSummary = {
  distanceKilometers: number;
  estimatedMinutes: number | null;
};

const initialWaypointPositions = [
  [19.076, 72.8777],
  [19.0821, 72.8903],
  [19.0664, 72.9008],
  [19.0587, 72.8722],
  [19.0727, 72.8588]
];

const defaultAltitudeMeters = 80;
const defaultSpeedMetersPerSecond = 8;
const emptyTelemetrySnapshot: DroneTelemetrySnapshot = {
  connected: false,
  latitude: null,
  longitude: null,
  altitudeMeters: null,
  speedMetersPerSecond: null,
  headingDegrees: null,
  batteryPercent: null,
  gpsFixType: null,
  flightMode: null,
  missionCurrent: null,
  missionTotal: null,
  message: "Drone disconnected."
};

const formatCoordinate = (coordinate: number) => coordinate.toFixed(5);
const formatTelemetryNumber = (
  value: number | null,
  fractionDigits: number,
  suffix = ""
) => (value === null ? "--" : `${value.toFixed(fractionDigits)}${suffix}`);
const formatBattery = (batteryPercent: number | null) =>
  batteryPercent === null ? "--" : `${Math.round(batteryPercent)}%`;
const formatMissionProgress = (snapshot: DroneTelemetrySnapshot) =>
  snapshot.missionCurrent === null || snapshot.missionTotal === null
    ? "--"
    : `${snapshot.missionCurrent}/${snapshot.missionTotal}`;
const formatDistance = (distanceKilometers: number) =>
  `${distanceKilometers.toFixed(2)} km`;
const formatEstimatedTime = (minutes: number | null) =>
  minutes === null ? "--" : `${Math.ceil(minutes)} min`;

const createWaypoint = (index: number): Waypoint => {
  const position =
    initialWaypointPositions[index % initialWaypointPositions.length];
  const loopOffset = Math.floor(index / initialWaypointPositions.length) * 0.006;

  return {
    id: crypto.randomUUID(),
    sequence: index + 1,
    latitude: position[0] + loopOffset,
    longitude: position[1] + loopOffset,
    altitudeMeters: defaultAltitudeMeters,
    speedMetersPerSecond: defaultSpeedMetersPerSecond
  };
};

const calculateMissionSummary = (waypoints: Waypoint[]): MissionSummary => {
  if (waypoints.length < 2) {
    return {
      distanceKilometers: 0,
      estimatedMinutes: null
    };
  }

  const distanceKilometers = waypoints
    .slice(1)
    .reduce(
      (totalDistance, waypoint, index) =>
        totalDistance + getDistanceKilometers(waypoints[index], waypoint),
      0
    );
  const averageSpeed =
    waypoints.reduce(
      (totalSpeed, waypoint) => totalSpeed + waypoint.speedMetersPerSecond,
      0
    ) / waypoints.length;
  const estimatedMinutes = (distanceKilometers * 1000) / averageSpeed / 60;

  return {
    distanceKilometers,
    estimatedMinutes
  };
};

const getDistanceKilometers = (start: Waypoint, end: Waypoint) => {
  const earthRadiusKilometers = 6371;
  const startLatitude = toRadians(start.latitude);
  const endLatitude = toRadians(end.latitude);
  const latitudeDelta = toRadians(end.latitude - start.latitude);
  const longitudeDelta = toRadians(end.longitude - start.longitude);
  const haversine =
    Math.sin(latitudeDelta / 2) * Math.sin(latitudeDelta / 2) +
    Math.cos(startLatitude) *
      Math.cos(endLatitude) *
      Math.sin(longitudeDelta / 2) *
      Math.sin(longitudeDelta / 2);

  return (
    earthRadiusKilometers *
    2 *
    Math.atan2(Math.sqrt(haversine), Math.sqrt(1 - haversine))
  );
};

const toRadians = (degrees: number) => (degrees * Math.PI) / 180;

const resequenceWaypoints = (waypoints: Waypoint[]) =>
  waypoints.map((waypoint, index) => ({
    ...waypoint,
    sequence: index + 1
  }));

const clampNumericValue = (value: number, minimum: number, maximum: number) =>
  Math.min(Math.max(value, minimum), maximum);

export function App() {
  const [waypoints, setWaypoints] = useState<Waypoint[]>([]);
  const [missionName, setMissionName] = useState("Untitled");
  const [savedMissions, setSavedMissions] = useState<MissionRecord[]>([]);
  const [selectedMissionId, setSelectedMissionId] = useState<number | null>(
    null
  );
  const [statusMessage, setStatusMessage] = useState(
    "Mission storage ready"
  );
  const [validationResult, setValidationResult] =
    useState<MissionValidationResult | null>(null);
  const [droneStatus, setDroneStatus] = useState<DroneConnectionStatus>({
    connected: false,
    systemAddress: null,
    message: "Drone disconnected."
  });
  const [telemetrySnapshot, setTelemetrySnapshot] =
    useState<DroneTelemetrySnapshot>(emptyTelemetrySnapshot);
  const [isConnectingDrone, setIsConnectingDrone] = useState(false);
  const [isDroneArmed, setIsDroneArmed] = useState(false);
  const [isMissionStarted, setIsMissionStarted] = useState(false);
  const [isSendingDroneAction, setIsSendingDroneAction] = useState(false);
  const [isStartingMission, setIsStartingMission] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [isLoadingMission, setIsLoadingMission] = useState(false);
  const [isUploadingMission, setIsUploadingMission] = useState(false);
  const [isValidatingMission, setIsValidatingMission] = useState(false);
  const missionSummary = useMemo(
    () => calculateMissionSummary(waypoints),
    [waypoints]
  );
  const missionRows = [
    { label: "Mission", value: missionName },
    { label: "Waypoints", value: String(waypoints.length) },
    {
      label: "Distance",
      value: formatDistance(missionSummary.distanceKilometers)
    },
    {
      label: "Estimated Time",
      value: formatEstimatedTime(missionSummary.estimatedMinutes)
    }
  ];
  const telemetryMetrics: TelemetryMetric[] = [
    {
      label: "Latitude",
      value: formatTelemetryNumber(telemetrySnapshot.latitude, 5)
    },
    {
      label: "Longitude",
      value: formatTelemetryNumber(telemetrySnapshot.longitude, 5)
    },
    {
      label: "Altitude",
      value: formatTelemetryNumber(telemetrySnapshot.altitudeMeters, 1, " m")
    },
    {
      label: "Ground Speed",
      value: formatTelemetryNumber(
        telemetrySnapshot.speedMetersPerSecond,
        1,
        " m/s"
      )
    },
    {
      label: "Heading",
      value: formatTelemetryNumber(
        telemetrySnapshot.headingDegrees,
        0,
        " deg"
      )
    },
    {
      label: "Battery",
      value: formatBattery(telemetrySnapshot.batteryPercent)
    },
    { label: "GPS Fix", value: telemetrySnapshot.gpsFixType ?? "--" },
    { label: "Flight Mode", value: telemetrySnapshot.flightMode ?? "--" },
    {
      label: "Mission Progress",
      value: formatMissionProgress(telemetrySnapshot)
    }
  ];
  const telemetryStatus = telemetrySnapshot.connected ? "Live" : "Idle";

  useEffect(() => {
    void refreshSavedMissions();
    void refreshDroneStatus();
    void refreshTelemetry();

    const telemetryInterval = window.setInterval(() => {
      void refreshTelemetry();
    }, 2000);

    return () => window.clearInterval(telemetryInterval);
  }, []);

  const refreshSavedMissions = async () => {
    try {
      setSavedMissions(await listMissions());
    } catch {
      setStatusMessage("Backend unavailable. Start the API to save or load.");
    }
  };

  const refreshDroneStatus = async () => {
    try {
      setDroneStatus(await getDroneStatus());
    } catch {
      setDroneStatus({
        connected: false,
        systemAddress: null,
        message: "Drone API unavailable."
      });
    }
  };

  const refreshTelemetry = async () => {
    try {
      setTelemetrySnapshot(await getDroneTelemetry());
    } catch {
      setTelemetrySnapshot({
        ...emptyTelemetrySnapshot,
        message: "Telemetry API unavailable."
      });
    }
  };

  const addWaypoint = () => {
    setValidationResult(null);
    setWaypoints((currentWaypoints) => [
      ...currentWaypoints,
      createWaypoint(currentWaypoints.length)
    ]);
  };

  const handleSaveMission = async () => {
    if (waypoints.length === 0) {
      setStatusMessage("Add at least one waypoint before saving.");
      return;
    }

    setIsSaving(true);
    try {
      const savedMission = await saveMission(missionName, waypoints);
      setMissionName(savedMission.name);
      setSelectedMissionId(savedMission.id);
      setStatusMessage(`Saved mission ${savedMission.name}.`);
      await refreshSavedMissions();
    } catch {
      setStatusMessage("Mission save failed. Check backend connection.");
    } finally {
      setIsSaving(false);
    }
  };

  const handleLoadMission = async () => {
    if (selectedMissionId === null) {
      setStatusMessage("Select a saved mission before loading.");
      return;
    }

    setIsLoadingMission(true);
    try {
      const loadedMission = await loadMission(selectedMissionId);
      setMissionName(loadedMission.name);
      setWaypoints(loadedMission.waypoints);
      setSelectedMissionId(loadedMission.id);
      setValidationResult(null);
      setStatusMessage(`Loaded mission ${loadedMission.name}.`);
    } catch {
      setStatusMessage("Mission load failed. Check backend connection.");
    } finally {
      setIsLoadingMission(false);
    }
  };

  const handleUploadMission = async () => {
    if (selectedMissionId === null) {
      setStatusMessage("Save or load a mission before uploading.");
      return;
    }

    if (!droneStatus.connected) {
      setStatusMessage("Connect to PX4 SITL before uploading.");
      return;
    }

    setIsUploadingMission(true);
    try {
      const uploadStatus = await uploadMission(selectedMissionId);
      setStatusMessage(uploadStatus.message);
    } catch {
      setStatusMessage("Mission upload failed. Check drone connection.");
    } finally {
      setIsUploadingMission(false);
    }
  };

  const handleValidateMission = async () => {
    setIsValidatingMission(true);
    try {
      const result = await validateMission(missionName, waypoints);
      setValidationResult(result);
      setStatusMessage(result.valid ? "Mission valid." : "Mission invalid.");
    } catch {
      setStatusMessage("Mission validation failed. Check backend connection.");
    } finally {
      setIsValidatingMission(false);
    }
  };

  const handleDroneConnection = async () => {
    setIsConnectingDrone(true);
    try {
      const updatedStatus = droneStatus.connected
        ? await disconnectDrone()
        : await connectDrone();
      setDroneStatus(updatedStatus);
      if (!updatedStatus.connected) {
        setIsDroneArmed(false);
        setIsMissionStarted(false);
      }
      setStatusMessage(updatedStatus.message);
      void refreshTelemetry();
    } catch {
      const failureMessage = droneStatus.connected
        ? "Drone disconnect failed."
        : "Drone connection failed. Start PX4 SITL and try again.";
      setDroneStatus({
        connected: false,
        systemAddress: null,
        message: failureMessage
      });
      setStatusMessage(failureMessage);
    } finally {
      setIsConnectingDrone(false);
    }
  };

  const handleArmDisarm = async () => {
    if (!droneStatus.connected) {
      setStatusMessage("Connect to PX4 SITL before arming.");
      return;
    }

    setIsSendingDroneAction(true);
    try {
      const actionStatus = isDroneArmed ? await disarmDrone() : await armDrone();
      setIsDroneArmed(actionStatus.action === "arm");
      if (actionStatus.action === "disarm") {
        setIsMissionStarted(false);
      }
      setStatusMessage(actionStatus.message);
    } catch {
      setStatusMessage("Drone action failed. Check PX4 state.");
    } finally {
      setIsSendingDroneAction(false);
    }
  };

  const handleStartMission = async () => {
    if (!droneStatus.connected || !isDroneArmed) {
      setStatusMessage("Connect and arm the drone before starting mission.");
      return;
    }

    setIsStartingMission(true);
    try {
      const actionStatus = await startMission();
      setIsMissionStarted(true);
      setStatusMessage(actionStatus.message);
      void refreshTelemetry();
    } catch {
      setStatusMessage("Mission start failed. Check upload and drone state.");
    } finally {
      setIsStartingMission(false);
    }
  };

  const deleteWaypoint = (waypointId: string) => {
    setValidationResult(null);
    setWaypoints((currentWaypoints) =>
      resequenceWaypoints(
        currentWaypoints.filter((waypoint) => waypoint.id !== waypointId)
      )
    );
  };

  const updateWaypointNumber = (
    waypointId: string,
    field: "altitudeMeters" | "speedMetersPerSecond",
    value: number
  ) => {
    setValidationResult(null);
    const limits = {
      altitudeMeters: { minimum: 1, maximum: 500 },
      speedMetersPerSecond: { minimum: 1, maximum: 40 }
    }[field];

    setWaypoints((currentWaypoints) =>
      currentWaypoints.map((waypoint) =>
        waypoint.id === waypointId
          ? {
              ...waypoint,
              [field]: clampNumericValue(value, limits.minimum, limits.maximum)
            }
          : waypoint
      )
    );
  };

  return (
    <main className="min-h-screen bg-zinc-950 text-zinc-100">
      <div className="flex min-h-screen flex-col">
        <header className="flex h-14 items-center justify-between border-b border-zinc-800 bg-zinc-900 px-4">
          <div className="flex items-center gap-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-md bg-emerald-500 text-sm font-bold text-zinc-950">
              V
            </div>
            <div>
              <h1 className="text-base font-semibold tracking-normal text-white">
                Vimantra AI Mission Planner
              </h1>
              <p className="text-xs text-zinc-400">Ground Control Station</p>
            </div>
          </div>
          <div className="flex items-center gap-3 text-xs">
            <StatusPill
              label="PX4 SITL"
              value={droneStatus.connected ? "Connected" : "Disconnected"}
              tone={droneStatus.connected ? "emerald" : "amber"}
            />
            <StatusPill
              label="Telemetry"
              value={telemetryStatus}
              tone={telemetrySnapshot.connected ? "emerald" : "zinc"}
            />
          </div>
        </header>

        <section className="grid min-h-0 flex-1 grid-cols-[280px_minmax(420px,1fr)_320px] grid-rows-[1fr_auto] gap-px bg-zinc-800">
          <aside
            aria-label="Mission planner"
            className="min-h-0 bg-zinc-925 p-4"
          >
            <PanelTitle title="Mission Planner" />
            <label className="mt-4 block">
              <span className="text-xs text-zinc-400">Mission name</span>
              <input
                aria-label="Mission name"
                className="mt-1 h-9 w-full rounded-md border border-zinc-800 bg-zinc-950 px-3 text-sm text-zinc-100 outline-none"
                maxLength={120}
                onChange={(event) => {
                  setMissionName(event.target.value);
                  setValidationResult(null);
                }}
                value={missionName}
              />
            </label>
            <div className="mt-4 space-y-2">
              {missionRows.map((row) => (
                <DataRow key={row.label} label={row.label} value={row.value} />
              ))}
            </div>

            <div className="mt-6">
              <PanelTitle title="Mission List" />
              <MissionList
                onSelectMission={setSelectedMissionId}
                selectedMissionId={selectedMissionId}
                savedMissions={savedMissions}
              />
            </div>

            <div className="mt-6">
              <div className="flex items-center justify-between gap-3">
                <PanelTitle title="Waypoint Editor" />
                <ControlButton label="Add WP" onClick={addWaypoint} />
              </div>
              <WaypointEditor
                onDeleteWaypoint={deleteWaypoint}
                onUpdateWaypoint={updateWaypointNumber}
                waypoints={waypoints}
              />
            </div>
          </aside>

          <MapWorkspace waypoints={waypoints} />

          <aside aria-label="Drone status" className="min-h-0 bg-zinc-925 p-4">
            <PanelTitle title="Drone Status" />
            <div className="mt-4 grid grid-cols-2 gap-2">
              {telemetryMetrics.map((metric) => (
                <MetricCard
                  key={metric.label}
                  label={metric.label}
                  value={metric.value}
                />
              ))}
            </div>
          </aside>

          <section
            aria-label="Mission controls"
            className="col-span-3 flex items-center justify-between bg-zinc-900 px-4 py-3"
          >
            <div className="flex gap-2">
              <ControlButton
                label={
                  isConnectingDrone
                    ? droneStatus.connected
                      ? "Disconnecting"
                      : "Connecting"
                    : droneStatus.connected
                      ? "Disconnect"
                      : "Connect"
                }
                disabled={isConnectingDrone}
                onClick={handleDroneConnection}
              />
              <ControlButton
                label={isSaving ? "Saving" : "Save"}
                disabled={isSaving || waypoints.length === 0}
                onClick={handleSaveMission}
              />
              <ControlButton
                label={isLoadingMission ? "Loading" : "Load"}
                disabled={isLoadingMission || savedMissions.length === 0}
                onClick={handleLoadMission}
              />
              <ControlButton
                label="Clear"
                disabled={waypoints.length === 0}
                onClick={() => {
                  setWaypoints([]);
                  setSelectedMissionId(null);
                  setValidationResult(null);
                  setStatusMessage("Mission cleared.");
                }}
              />
            </div>
            <div aria-live="polite" className="max-w-xl text-sm">
              <p className="truncate text-zinc-400">{statusMessage}</p>
              <ValidationSummary result={validationResult} />
            </div>
            <div className="flex gap-2">
              <ControlButton
                label={isValidatingMission ? "Validating" : "Validate Mission"}
                disabled={isValidatingMission}
                onClick={handleValidateMission}
              />
              <ControlButton
                label={isUploadingMission ? "Uploading" : "Upload"}
                disabled={
                  isUploadingMission ||
                  selectedMissionId === null ||
                  !droneStatus.connected
                }
                onClick={handleUploadMission}
              />
              <ControlButton
                label={
                  isSendingDroneAction
                    ? isDroneArmed
                      ? "Disarming"
                      : "Arming"
                    : isDroneArmed
                      ? "Disarm"
                      : "Arm"
                }
                disabled={isSendingDroneAction || !droneStatus.connected}
                onClick={handleArmDisarm}
              />
              <ControlButton
                label={
                  isStartingMission
                    ? "Starting"
                    : isMissionStarted
                      ? "Started"
                      : "Start"
                }
                disabled={
                  isStartingMission ||
                  isMissionStarted ||
                  !droneStatus.connected ||
                  !isDroneArmed
                }
                intent="primary"
                onClick={handleStartMission}
              />
            </div>
          </section>
        </section>
      </div>
    </main>
  );
}

function MissionList({
  onSelectMission,
  savedMissions,
  selectedMissionId
}: {
  onSelectMission: (missionId: number) => void;
  savedMissions: MissionRecord[];
  selectedMissionId: number | null;
}) {
  if (savedMissions.length === 0) {
    return (
      <div className="mt-3 rounded-md border border-zinc-800 bg-zinc-900 p-4 text-sm text-zinc-400">
        No saved missions
      </div>
    );
  }

  return (
    <div className="mt-3 max-h-36 space-y-2 overflow-y-auto pr-1">
      {savedMissions.map((mission) => (
        <button
          className={`w-full rounded-md border px-3 py-2 text-left text-sm transition ${
            selectedMissionId === mission.id
              ? "border-emerald-500 bg-emerald-500/10 text-emerald-200"
              : "border-zinc-800 bg-zinc-900 text-zinc-300 hover:bg-zinc-800"
          }`}
          key={mission.id}
          onClick={() => onSelectMission(mission.id)}
          type="button"
        >
          <span className="block font-medium">{mission.name}</span>
          <span className="mt-1 block text-xs text-zinc-500">
            {mission.waypoints.length} waypoint
            {mission.waypoints.length === 1 ? "" : "s"}
          </span>
        </button>
      ))}
    </div>
  );
}

function WaypointEditor({
  onDeleteWaypoint,
  onUpdateWaypoint,
  waypoints
}: {
  onDeleteWaypoint: (waypointId: string) => void;
  onUpdateWaypoint: (
    waypointId: string,
    field: "altitudeMeters" | "speedMetersPerSecond",
    value: number
  ) => void;
  waypoints: Waypoint[];
}) {
  if (waypoints.length === 0) {
    return (
      <div className="mt-3 rounded-md border border-zinc-800 bg-zinc-900 p-4 text-sm text-zinc-400">
        No waypoints
      </div>
    );
  }

  return (
    <div className="mt-3 max-h-[calc(100vh-22rem)] space-y-3 overflow-y-auto pr-1">
      {waypoints.map((waypoint) => (
        <article
          className="rounded-md border border-zinc-800 bg-zinc-900 p-3"
          key={waypoint.id}
        >
          <div className="flex items-start justify-between gap-3">
            <div>
              <h3 className="text-sm font-semibold text-zinc-100">
                WP{waypoint.sequence}
              </h3>
              <p className="mt-1 text-xs text-zinc-400">
                {formatCoordinate(waypoint.latitude)},{" "}
                {formatCoordinate(waypoint.longitude)}
              </p>
            </div>
            <button
              className="h-8 rounded-md border border-zinc-700 px-2 text-xs font-medium text-zinc-300 transition hover:bg-zinc-800"
              onClick={() => onDeleteWaypoint(waypoint.id)}
              type="button"
            >
              Delete
            </button>
          </div>

          <div className="mt-3 grid grid-cols-2 gap-2">
            <NumberField
              label={`WP${waypoint.sequence} altitude`}
              max={500}
              min={1}
              onChange={(value) =>
                onUpdateWaypoint(waypoint.id, "altitudeMeters", value)
              }
              suffix="m"
              value={waypoint.altitudeMeters}
            />
            <NumberField
              label={`WP${waypoint.sequence} speed`}
              max={40}
              min={1}
              onChange={(value) =>
                onUpdateWaypoint(waypoint.id, "speedMetersPerSecond", value)
              }
              suffix="m/s"
              value={waypoint.speedMetersPerSecond}
            />
          </div>
        </article>
      ))}
    </div>
  );
}

function NumberField({
  label,
  max,
  min,
  onChange,
  suffix,
  value
}: {
  label: string;
  max: number;
  min: number;
  onChange: (value: number) => void;
  suffix: string;
  value: number;
}) {
  return (
    <label className="block">
      <span className="text-xs text-zinc-400">{label}</span>
      <div className="mt-1 flex h-9 items-center rounded-md border border-zinc-800 bg-zinc-950">
        <input
          aria-label={label}
          className="h-full min-w-0 flex-1 bg-transparent px-2 text-sm text-zinc-100 outline-none"
          max={max}
          min={min}
          onChange={(event) => onChange(Number(event.target.value))}
          type="number"
          value={value}
        />
        <span className="border-l border-zinc-800 px-2 text-xs text-zinc-500">
          {suffix}
        </span>
      </div>
    </label>
  );
}

function PanelTitle({ title }: { title: string }) {
  return <h2 className="text-sm font-semibold text-zinc-100">{title}</h2>;
}

function ValidationSummary({
  result
}: {
  result: MissionValidationResult | null;
}) {
  if (result === null) {
    return null;
  }

  const toneClass = result.valid ? "text-emerald-300" : "text-red-300";
  const label = result.valid ? "Mission Valid" : "Mission Invalid";

  return (
    <div className="mt-1 max-h-24 overflow-y-auto">
      <p className={`text-xs font-semibold ${toneClass}`}>{label}</p>
      {result.errors.length > 0 && (
        <ul className="mt-1 space-y-1 text-xs text-red-300">
          {result.errors.map((error) => (
            <li key={`${error.code}-${error.waypoint ?? "mission"}`}>
              {error.waypoint === null ? "" : `WP${error.waypoint}: `}
              {error.message}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

function DataRow({ label, value }: TelemetryMetric) {
  return (
    <div className="flex items-center justify-between border-b border-zinc-800 py-2 text-sm">
      <span className="text-zinc-400">{label}</span>
      <span className="font-medium text-zinc-100">{value}</span>
    </div>
  );
}

function MetricCard({ label, value }: TelemetryMetric) {
  return (
    <div className="rounded-md border border-zinc-800 bg-zinc-900 p-3">
      <p className="text-xs text-zinc-400">{label}</p>
      <p className="mt-1 text-sm font-semibold text-zinc-100">{value}</p>
    </div>
  );
}

function StatusPill({
  label,
  value,
  tone
}: {
  label: string;
  value: string;
  tone: "amber" | "emerald" | "zinc";
}) {
  const valueColor = {
    amber: "text-amber-300",
    emerald: "text-emerald-300",
    zinc: "text-zinc-300"
  }[tone];

  return (
    <div className="rounded-md border border-zinc-800 bg-zinc-950 px-3 py-1.5">
      <span className="text-zinc-500">{label}: </span>
      <span className={valueColor}>{value}</span>
    </div>
  );
}

function ControlButton({
  label,
  disabled = false,
  intent = "default",
  onClick
}: {
  label: string;
  disabled?: boolean;
  intent?: "default" | "primary" | "danger";
  onClick?: () => void;
}) {
  const intentClass = {
    default: "border-zinc-700 bg-zinc-800 text-zinc-100 enabled:hover:bg-zinc-700",
    primary:
      "border-emerald-500 bg-emerald-500 text-zinc-950 enabled:hover:bg-emerald-400",
    danger: "border-red-500 bg-red-500 text-white enabled:hover:bg-red-400"
  }[intent];

  return (
    <button
      className={`h-9 min-w-20 rounded-md border px-3 text-sm font-medium transition disabled:cursor-not-allowed disabled:border-zinc-800 disabled:bg-zinc-950 disabled:text-zinc-600 ${intentClass}`}
      disabled={disabled}
      onClick={onClick}
      type="button"
    >
      {label}
    </button>
  );
}
