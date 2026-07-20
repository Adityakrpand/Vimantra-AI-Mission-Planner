param(
  [string]$BackendUrl = "",
  [string]$SystemAddress = "",
  [int]$ConnectTimeoutSeconds = 10,
  [int]$ApiTimeoutSeconds = 30,
  [int]$MissionTimeoutSeconds = 300,
  [int]$TelemetryPollSeconds = 2,
  [switch]$SkipDroneActions
)

$ErrorActionPreference = "Stop"

if (-not $BackendUrl) {
  $backendHost = if ($env:VIMANTRA_API_HOST) { $env:VIMANTRA_API_HOST } else { "127.0.0.1" }
  $backendPort = if ($env:VIMANTRA_API_PORT) { $env:VIMANTRA_API_PORT } else { "8000" }
  $BackendUrl = "http://$($backendHost):$($backendPort)"
}
if (-not $SystemAddress) {
  $SystemAddress = if ($env:VIMANTRA_MAVSDK_ADDRESS) { $env:VIMANTRA_MAVSDK_ADDRESS } else { "udp://:14540" }
}

function Write-Step {
  param([string]$Message)
  Write-Host ""
  Write-Host "== $Message =="
}

function Invoke-VimantraApi {
  param(
    [string]$Method,
    [string]$Path,
    [object]$Body = $null
  )

  $uri = "$BackendUrl$Path"
  if ($null -eq $Body) {
    try {
      return Invoke-RestMethod -Method $Method -TimeoutSec $ApiTimeoutSeconds -Uri $uri
    } catch {
      if ($_.ErrorDetails.Message) {
        Write-Host $_.ErrorDetails.Message
        exit 1
      }
      Write-Host $_.Exception.Message
      exit 1
    }
  }

  $json = $Body | ConvertTo-Json -Depth 12
  try {
    return Invoke-RestMethod `
      -Body $json `
      -ContentType "application/json" `
      -Method $Method `
      -TimeoutSec $ApiTimeoutSeconds `
      -Uri $uri
  } catch {
    if ($_.ErrorDetails.Message) {
      Write-Host $_.ErrorDetails.Message
      exit 1
    }
    Write-Host $_.Exception.Message
    exit 1
  }
}

function Assert-Truthy {
  param(
    [bool]$Condition,
    [string]$Message
  )

  if (-not $Condition) {
    throw $Message
  }
}

function Get-ApiData {
  param(
    [object]$Response,
    [string]$Operation
  )

  Assert-Truthy ($null -ne $Response) "$Operation returned no response."
  Assert-Truthy ($Response.success -eq $true) "$Operation failed."
  Assert-Truthy ($null -ne $Response.data) "$Operation returned no data."
  return $Response.data
}

$BackendUrl = $BackendUrl.TrimEnd("/")

Write-Step "Backend health"
$health = Get-ApiData (Invoke-VimantraApi -Method "GET" -Path "/health") "Backend health check"
Assert-Truthy ($health.status -eq "ok") "Backend health check failed."
Write-Host "Backend is healthy: $($health.service)"

Write-Step "Create verification mission"
$mission = Get-ApiData (Invoke-VimantraApi -Method "POST" -Path "/missions" -Body @{
  name = "PX4 SITL Verification"
  waypoints = @(
    @{
      sequence = 1
      latitude = 19.076
      longitude = 72.8777
      altitude_meters = 80
      speed_meters_per_second = 8
    },
    @{
      sequence = 2
      latitude = 19.0821
      longitude = 72.8903
      altitude_meters = 90
      speed_meters_per_second = 8
    }
  )
}) "Mission creation"
Write-Host "Mission created: id=$($mission.id), waypoints=$($mission.waypoints.Count)"

Write-Step "Load verification mission"
$loadedMission = Get-ApiData (Invoke-VimantraApi -Method "GET" -Path "/missions/$($mission.id)") "Mission load"
Assert-Truthy ($loadedMission.id -eq $mission.id) "Mission load check failed."
Write-Host "Mission loaded: $($loadedMission.name)"

Write-Step "Initial drone status"
$initialStatus = Get-ApiData (Invoke-VimantraApi -Method "GET" -Path "/drone/status") "Initial drone status"
Write-Host "Connected: $($initialStatus.connected)"

Write-Step "Initial telemetry"
$initialTelemetry = Get-ApiData (Invoke-VimantraApi -Method "GET" -Path "/drone/telemetry") "Initial telemetry"
Write-Host "Telemetry message: $($initialTelemetry.message)"

if ($SkipDroneActions) {
  Write-Step "PX4 actions skipped"
  Write-Host "Backend, mission storage, drone status, and telemetry endpoints are reachable."
  Get-ApiData (Invoke-VimantraApi -Method "DELETE" -Path "/missions/$($mission.id)") "Verification mission cleanup" | Out-Null
  Write-Host "Verification mission removed."
  exit 0
}

Write-Step "Connect to PX4 SITL"
$connectedStatus = Get-ApiData (Invoke-VimantraApi -Method "POST" -Path "/drone/connect" -Body @{
  system_address = $SystemAddress
  timeout_seconds = $ConnectTimeoutSeconds
}) "PX4 connection"
Assert-Truthy ($connectedStatus.connected -eq $true) "PX4 connection failed."
Write-Host "Connected to $($connectedStatus.system_address)"

Write-Step "Telemetry readiness"
$connectedTelemetry = Get-ApiData (Invoke-VimantraApi -Method "GET" -Path "/drone/telemetry") "Connected telemetry"
Assert-Truthy ($connectedTelemetry.connected -eq $true) "Telemetry did not report a connected drone."
Assert-Truthy ($null -ne $connectedTelemetry.latitude) "Position telemetry is unavailable."
Assert-Truthy ($null -ne $connectedTelemetry.battery_percent) "Battery telemetry is unavailable."
Write-Host "Telemetry ready: GPS=$($connectedTelemetry.gps_fix_type), battery=$($connectedTelemetry.battery_percent)%"

Write-Step "Pre-flight checks"
$preflight = Get-ApiData (Invoke-VimantraApi -Method "POST" -Path "/missions/$($mission.id)/preflight") "Pre-flight checks"
Assert-Truthy ($preflight.ready -eq $true) "Pre-flight checks failed."
Write-Host "Pre-flight passed: score=$($preflight.score)"

Write-Step "Upload mission"
$uploadStatus = Get-ApiData (Invoke-VimantraApi -Method "POST" -Path "/missions/$($mission.id)/upload") "Mission upload"
Assert-Truthy ($uploadStatus.uploaded -eq $true) "Mission upload failed."
Write-Host $uploadStatus.message

Write-Step "Arm drone"
$armStatus = Get-ApiData (Invoke-VimantraApi -Method "POST" -Path "/drone/arm") "Arm command"
Assert-Truthy ($armStatus.completed -eq $true) "Arm command failed."
Write-Host $armStatus.message

Write-Step "Start mission"
$startStatus = Get-ApiData (Invoke-VimantraApi -Method "POST" -Path "/drone/start-mission") "Mission start"
Assert-Truthy ($startStatus.completed -eq $true) "Start mission command failed."
Write-Host $startStatus.message

Write-Step "Monitor mission"
$deadline = (Get-Date).AddSeconds($MissionTimeoutSeconds)
$missionComplete = $false
while ((Get-Date) -lt $deadline) {
  $telemetry = Get-ApiData (Invoke-VimantraApi -Method "GET" -Path "/drone/telemetry") "Mission telemetry"
  Assert-Truthy ($telemetry.connected -eq $true) "Telemetry lost the drone connection."
  Write-Host "Progress: $($telemetry.mission_current)/$($telemetry.mission_total), altitude=$($telemetry.altitude_meters)m, mode=$($telemetry.flight_mode)"
  if (
    $null -ne $telemetry.mission_total -and
    $telemetry.mission_total -gt 0 -and
    $telemetry.mission_current -ge $telemetry.mission_total
  ) {
    $missionComplete = $true
    break
  }
  Start-Sleep -Seconds $TelemetryPollSeconds
}
Assert-Truthy $missionComplete "Mission did not complete within $MissionTimeoutSeconds seconds."

Write-Step "Disarm drone"
$disarmStatus = Get-ApiData (Invoke-VimantraApi -Method "POST" -Path "/drone/disarm") "Disarm command"
Assert-Truthy ($disarmStatus.completed -eq $true) "Disarm command failed."
Write-Host $disarmStatus.message

Write-Step "Clean verification data"
Get-ApiData (Invoke-VimantraApi -Method "DELETE" -Path "/missions/$($mission.id)") "Verification mission cleanup" | Out-Null
Write-Host "Verification mission removed."

Write-Step "Workflow complete"
Write-Host "Connect, telemetry, pre-flight, upload, arm, start, mission completion, and disarm checks passed."
