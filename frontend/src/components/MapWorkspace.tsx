import { divIcon } from "leaflet";
import { MapContainer, Marker, Polyline, TileLayer, Tooltip } from "react-leaflet";

import type { Waypoint } from "../types/mission";

const defaultCenter: [number, number] = [19.076, 72.8777];
const defaultZoom = 12;

const waypointIcon = divIcon({
  className: "",
  html: '<div class="waypoint-marker"></div>',
  iconAnchor: [8, 8],
  iconSize: [16, 16]
});

export function MapWorkspace({ waypoints }: { waypoints: Waypoint[] }) {
  const routePositions = waypoints.map((waypoint) => [
    waypoint.latitude,
    waypoint.longitude
  ]) satisfies [number, number][];

  return (
    <section
      aria-label="Map workspace"
      className="relative min-h-0 bg-zinc-950"
    >
      <MapContainer
        center={defaultCenter}
        className="h-full w-full"
        scrollWheelZoom
        zoom={defaultZoom}
        zoomControl
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {routePositions.length > 1 ? (
          <Polyline color="#10b981" positions={routePositions} weight={4} />
        ) : null}
        {waypoints.map((waypoint) => (
          <Marker
            icon={waypointIcon}
            key={waypoint.id}
            position={[waypoint.latitude, waypoint.longitude]}
          >
            <Tooltip direction="top" offset={[0, -8]} permanent>
              WP{waypoint.sequence}
            </Tooltip>
          </Marker>
        ))}
      </MapContainer>

      <div className="pointer-events-none absolute left-4 top-4 z-[500] rounded-md border border-zinc-800 bg-zinc-900 px-3 py-2 shadow-lg">
        <p className="text-xs font-medium uppercase text-zinc-400">Map</p>
        <p className="text-sm font-semibold text-white">Mumbai, India</p>
      </div>
      <div className="pointer-events-none absolute bottom-4 left-4 right-4 z-[500] flex items-center justify-between rounded-md border border-zinc-800 bg-zinc-900 px-4 py-3 text-sm">
        <span className="text-zinc-300">Mission Progress</span>
        <span className="font-medium text-emerald-300">0%</span>
      </div>
    </section>
  );
}
