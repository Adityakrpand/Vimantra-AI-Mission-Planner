import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { App } from "./App";
import {
  armDrone,
  connectDrone,
  disconnectDrone,
  disarmDrone,
  getDroneTelemetry,
  getDroneStatus,
  startMission
} from "./services/droneApi";
import {
  listMissions,
  loadMission,
  runPreFlight,
  saveMission,
  uploadMission,
  validateMission
} from "./services/missionApi";

vi.mock("./services/droneApi", () => ({
  armDrone: vi.fn(),
  connectDrone: vi.fn(),
  disconnectDrone: vi.fn(),
  disarmDrone: vi.fn(),
  getDroneTelemetry: vi.fn(),
  getDroneStatus: vi.fn(),
  startMission: vi.fn()
}));

vi.mock("./services/missionApi", () => ({
  listMissions: vi.fn(),
  loadMission: vi.fn(),
  runPreFlight: vi.fn(),
  saveMission: vi.fn(),
  uploadMission: vi.fn(),
  validateMission: vi.fn()
}));

const mockedArmDrone = vi.mocked(armDrone);
const mockedConnectDrone = vi.mocked(connectDrone);
const mockedDisconnectDrone = vi.mocked(disconnectDrone);
const mockedDisarmDrone = vi.mocked(disarmDrone);
const mockedGetDroneTelemetry = vi.mocked(getDroneTelemetry);
const mockedGetDroneStatus = vi.mocked(getDroneStatus);
const mockedStartMission = vi.mocked(startMission);
const mockedListMissions = vi.mocked(listMissions);
const mockedLoadMission = vi.mocked(loadMission);
const mockedRunPreFlight = vi.mocked(runPreFlight);
const mockedSaveMission = vi.mocked(saveMission);
const mockedUploadMission = vi.mocked(uploadMission);
const mockedValidateMission = vi.mocked(validateMission);

describe("App", () => {
  beforeEach(() => {
    mockedArmDrone.mockReset();
    mockedConnectDrone.mockReset();
    mockedDisconnectDrone.mockReset();
    mockedDisarmDrone.mockReset();
    mockedGetDroneTelemetry.mockReset();
    mockedGetDroneTelemetry.mockResolvedValue({
      connected: false,
      latitude: null,
      longitude: null,
      altitudeMeters: null,
      speedMetersPerSecond: null,
      headingDegrees: null,
      batteryPercent: null,
      gpsSatellites: null,
      gpsFixType: null,
      flightMode: null,
      missionCurrent: null,
      missionTotal: null,
      homePositionAvailable: false,
      message: "Drone disconnected."
    });
    mockedGetDroneStatus.mockResolvedValue({
      connected: false,
      systemAddress: null,
      message: "Drone disconnected."
    });
    mockedListMissions.mockResolvedValue([]);
    mockedLoadMission.mockReset();
    mockedRunPreFlight.mockReset();
    mockedSaveMission.mockReset();
    mockedStartMission.mockReset();
    mockedUploadMission.mockReset();
    mockedValidateMission.mockReset();
    mockedValidateMission.mockResolvedValue({
      valid: true,
      errors: [],
      warnings: [],
      statistics: {
        waypoints: 2,
        distance: 1280.5
      }
    });
  });

  it("renders the ground control station layout", async () => {
    render(<App />);

    expect(
      screen.getByRole("heading", { name: "Vimantra AI Mission Planner" })
    ).toBeInTheDocument();
    expect(screen.getByLabelText("Mission planner")).toBeInTheDocument();
    expect(screen.getByLabelText("Map workspace")).toBeInTheDocument();
    expect(screen.getByText("Mumbai, India")).toBeInTheDocument();
    expect(screen.getByLabelText("Drone status")).toBeInTheDocument();
    expect(screen.getByLabelText("Mission controls")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Connect" })).toBeEnabled();
    expect(screen.getByRole("button", { name: "Start" })).toBeDisabled();
    expect(screen.getByRole("button", { name: "Upload" })).toBeDisabled();
    expect(
      screen.getByRole("button", { name: "Validate Mission" })
    ).toBeEnabled();
    expect(screen.getByRole("button", { name: "Arm" })).toBeDisabled();
    expect(await screen.findByText("No saved missions")).toBeInTheDocument();
    expect(screen.getAllByText("Mission Progress").length).toBeGreaterThan(0);
  });

  it("validates the current mission through the mission API", async () => {
    render(<App />);
    await screen.findByText("No saved missions");

    fireEvent.click(screen.getByRole("button", { name: "Add WP" }));
    fireEvent.click(screen.getByRole("button", { name: "Validate Mission" }));

    expect(await screen.findByText("Mission Valid")).toBeInTheDocument();
    expect(mockedValidateMission).toHaveBeenCalledOnce();
  });

  it("shows mission validation errors", async () => {
    mockedValidateMission.mockResolvedValue({
      valid: false,
      errors: [
        {
          code: "ALTITUDE_TOO_LOW",
          waypoint: 1,
          message: "Altitude must be at least 5 meters."
        }
      ],
      warnings: [],
      statistics: {
        waypoints: 1,
        distance: 0
      }
    });

    render(<App />);
    await screen.findByText("No saved missions");

    fireEvent.click(screen.getByRole("button", { name: "Validate Mission" }));

    expect(await screen.findByText("Mission Invalid")).toBeInTheDocument();
    expect(
      screen.getByText("WP1: Altitude must be at least 5 meters.")
    ).toBeInTheDocument();
  });

  it("renders telemetry from the backend snapshot", async () => {
    mockedGetDroneTelemetry.mockResolvedValue({
      connected: true,
      latitude: 19.076,
      longitude: 72.8777,
      altitudeMeters: 80,
      speedMetersPerSecond: 5,
      headingDegrees: 125,
      batteryPercent: 76,
      gpsSatellites: 10,
      gpsFixType: "FIX_3D",
      flightMode: "HOLD",
      missionCurrent: 2,
      missionTotal: 5,
      homePositionAvailable: true,
      message: "Telemetry snapshot received."
    });

    render(<App />);

    expect(await screen.findByText("19.07600")).toBeInTheDocument();
    expect(screen.getByText("72.87770")).toBeInTheDocument();
    expect(screen.getByText("80.0 m")).toBeInTheDocument();
    expect(screen.getByText("5.0 m/s")).toBeInTheDocument();
    expect(screen.getByText("125 deg")).toBeInTheDocument();
    expect(screen.getByText("76%")).toBeInTheDocument();
    expect(screen.getByText("FIX_3D")).toBeInTheDocument();
    expect(screen.getByText("HOLD")).toBeInTheDocument();
    expect(screen.getByText("2/5")).toBeInTheDocument();
  });

  it("connects and disconnects through the drone API", async () => {
    mockedConnectDrone.mockResolvedValue({
      connected: true,
      systemAddress: "udp://:14540",
      message: "Connected to drone."
    });
    mockedDisconnectDrone.mockResolvedValue({
      connected: false,
      systemAddress: null,
      message: "Drone connection cleared."
    });

    render(<App />);
    await screen.findByText("No saved missions");

    fireEvent.click(screen.getByRole("button", { name: "Connect" }));

    expect(await screen.findByText("Connected to drone.")).toBeInTheDocument();
    expect(screen.getByText("Connected")).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Disconnect" }));

    expect(
      await screen.findByText("Drone connection cleared.")
    ).toBeInTheDocument();
    expect(mockedConnectDrone).toHaveBeenCalledOnce();
    expect(mockedDisconnectDrone).toHaveBeenCalledOnce();
  });

  it("arms and disarms through the drone API when connected", async () => {
    mockedConnectDrone.mockResolvedValue({
      connected: true,
      systemAddress: "udp://:14540",
      message: "Connected to drone."
    });
    mockedArmDrone.mockResolvedValue({
      completed: true,
      action: "arm",
      message: "Drone armed."
    });
    mockedDisarmDrone.mockResolvedValue({
      completed: true,
      action: "disarm",
      message: "Drone disarmed."
    });

    render(<App />);
    await screen.findByText("No saved missions");

    fireEvent.click(screen.getByRole("button", { name: "Connect" }));
    await screen.findByText("Connected to drone.");

    fireEvent.click(screen.getByRole("button", { name: "Arm" }));

    expect(await screen.findByText("Drone armed.")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Disarm" })).toBeEnabled();

    fireEvent.click(screen.getByRole("button", { name: "Disarm" }));

    expect(await screen.findByText("Drone disarmed.")).toBeInTheDocument();
    expect(mockedArmDrone).toHaveBeenCalledOnce();
    expect(mockedDisarmDrone).toHaveBeenCalledOnce();
  });

  it("starts the mission after the drone is connected and armed", async () => {
    mockedConnectDrone.mockResolvedValue({
      connected: true,
      systemAddress: "udp://:14540",
      message: "Connected to drone."
    });
    mockedArmDrone.mockResolvedValue({
      completed: true,
      action: "arm",
      message: "Drone armed."
    });
    mockedStartMission.mockResolvedValue({
      completed: true,
      action: "start_mission",
      message: "Mission started."
    });

    render(<App />);
    await screen.findByText("No saved missions");

    fireEvent.click(screen.getByRole("button", { name: "Connect" }));
    await screen.findByText("Connected to drone.");

    expect(screen.getByRole("button", { name: "Start" })).toBeDisabled();

    fireEvent.click(screen.getByRole("button", { name: "Arm" }));
    await screen.findByText("Drone armed.");

    fireEvent.click(screen.getByRole("button", { name: "Start" }));

    expect(await screen.findByText("Mission started.")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Started" })).toBeDisabled();
    expect(mockedStartMission).toHaveBeenCalledOnce();
  });

  it("adds, edits, and deletes waypoints", async () => {
    render(<App />);
    await screen.findByText("No saved missions");

    fireEvent.click(screen.getByRole("button", { name: "Add WP" }));

    expect(screen.getAllByText("WP1")).toHaveLength(2);
    expect(screen.getByText("Waypoints")).toBeInTheDocument();
    expect(screen.getByText("1")).toBeInTheDocument();

    fireEvent.change(screen.getByLabelText("WP1 altitude"), {
      target: { value: "120" }
    });
    fireEvent.change(screen.getByLabelText("WP1 speed"), {
      target: { value: "12" }
    });

    expect(screen.getByLabelText("WP1 altitude")).toHaveValue(120);
    expect(screen.getByLabelText("WP1 speed")).toHaveValue(12);

    fireEvent.click(screen.getByRole("button", { name: "Delete" }));

    expect(screen.getByText("No waypoints")).toBeInTheDocument();
  });

  it("saves the current mission through the mission API", async () => {
    mockedSaveMission.mockResolvedValue({
      id: 7,
      name: "Untitled",
      createdAt: "2026-07-06T00:00:00.000Z",
      updatedAt: "2026-07-06T00:00:00.000Z",
      waypoints: [
        {
          id: "7-1",
          sequence: 1,
          latitude: 19.076,
          longitude: 72.8777,
          altitudeMeters: 80,
          speedMetersPerSecond: 8
        }
      ]
    });
    mockedListMissions
      .mockResolvedValueOnce([])
      .mockResolvedValueOnce([
        {
          id: 7,
          name: "Untitled",
          createdAt: "2026-07-06T00:00:00.000Z",
          updatedAt: "2026-07-06T00:00:00.000Z",
          waypoints: [
            {
              id: "7-1",
              sequence: 1,
              latitude: 19.076,
              longitude: 72.8777,
              altitudeMeters: 80,
              speedMetersPerSecond: 8
            }
          ]
        }
      ]);

    render(<App />);
    fireEvent.click(screen.getByRole("button", { name: "Add WP" }));
    fireEvent.click(screen.getByRole("button", { name: "Save" }));

    expect(await screen.findByText("Saved mission Untitled.")).toBeInTheDocument();
    expect(mockedSaveMission).toHaveBeenCalledOnce();
  });

  it("loads a selected mission through the mission API", async () => {
    mockedListMissions.mockResolvedValue([
      {
        id: 8,
        name: "Loaded Mission",
        createdAt: "2026-07-06T00:00:00.000Z",
        updatedAt: "2026-07-06T00:00:00.000Z",
        waypoints: [
          {
            id: "8-1",
            sequence: 1,
            latitude: 19.0821,
            longitude: 72.8903,
            altitudeMeters: 90,
            speedMetersPerSecond: 9
          }
        ]
      }
    ]);
    mockedLoadMission.mockResolvedValue({
      id: 8,
      name: "Loaded Mission",
      createdAt: "2026-07-06T00:00:00.000Z",
      updatedAt: "2026-07-06T00:00:00.000Z",
      waypoints: [
        {
          id: "8-1",
          sequence: 1,
          latitude: 19.0821,
          longitude: 72.8903,
          altitudeMeters: 90,
          speedMetersPerSecond: 9
        }
      ]
    });

    render(<App />);
    fireEvent.click(await screen.findByRole("button", { name: /Loaded Mission/ }));
    fireEvent.click(screen.getByRole("button", { name: "Load" }));

    expect(
      await screen.findByText("Loaded mission Loaded Mission.")
    ).toBeInTheDocument();
    expect(screen.getByLabelText("Mission name")).toHaveValue("Loaded Mission");
  });

  it("uploads a saved mission when the drone is connected", async () => {
    mockedConnectDrone.mockResolvedValue({
      connected: true,
      systemAddress: "udp://:14540",
      message: "Connected to drone."
    });
    mockedSaveMission.mockResolvedValue({
      id: 12,
      name: "Upload Ready",
      createdAt: "2026-07-06T00:00:00.000Z",
      updatedAt: "2026-07-06T00:00:00.000Z",
      waypoints: [
        {
          id: "12-1",
          sequence: 1,
          latitude: 19.076,
          longitude: 72.8777,
          altitudeMeters: 80,
          speedMetersPerSecond: 8
        }
      ]
    });
    mockedUploadMission.mockResolvedValue({
      missionId: 12,
      uploaded: true,
      waypointCount: 1,
      message: "Uploaded mission Upload Ready."
    });

    render(<App />);
    await screen.findByText("No saved missions");

    fireEvent.click(screen.getByRole("button", { name: "Add WP" }));
    fireEvent.change(screen.getByLabelText("Mission name"), {
      target: { value: "Upload Ready" }
    });
    fireEvent.click(screen.getByRole("button", { name: "Save" }));
    await screen.findByText("Saved mission Upload Ready.");

    expect(screen.getByRole("button", { name: "Upload" })).toBeDisabled();

    fireEvent.click(screen.getByRole("button", { name: "Connect" }));
    await screen.findByText("Connected to drone.");

    fireEvent.click(screen.getByRole("button", { name: "Upload" }));

    expect(
      await screen.findByText("Uploaded mission Upload Ready.")
    ).toBeInTheDocument();
    expect(mockedUploadMission).toHaveBeenCalledWith(12);
  });

  it("runs pre-flight checks for a saved mission", async () => {
    mockedSaveMission.mockResolvedValue({
      id: 21,
      name: "Preflight Ready",
      createdAt: "2026-07-06T00:00:00.000Z",
      updatedAt: "2026-07-06T00:00:00.000Z",
      waypoints: [
        {
          id: "21-1",
          sequence: 1,
          latitude: 19.076,
          longitude: 72.8777,
          altitudeMeters: 80,
          speedMetersPerSecond: 8
        }
      ]
    });
    mockedRunPreFlight.mockResolvedValue({
      ready: true,
      score: 100,
      checks: [
        {
          name: "Vehicle Connected",
          status: "PASS",
          mandatory: true,
          message: "Vehicle connection is active."
        }
      ],
      warnings: []
    });

    render(<App />);
    await screen.findByText("No saved missions");

    fireEvent.click(screen.getByRole("button", { name: "Add WP" }));
    fireEvent.change(screen.getByLabelText("Mission name"), {
      target: { value: "Preflight Ready" }
    });
    fireEvent.click(screen.getByRole("button", { name: "Save" }));
    await screen.findByText("Saved mission Preflight Ready.");
    fireEvent.click(screen.getByRole("button", { name: "Pre-Flight Check" }));

    expect(await screen.findByText("Pre-flight checks passed.")).toBeInTheDocument();
    expect(screen.getByText("Pre-Flight Pass - Score 100")).toBeInTheDocument();
    expect(mockedRunPreFlight).toHaveBeenCalledWith(21);
  });
});
