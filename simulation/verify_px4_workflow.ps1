param(
  [string]$BackendUrl = "http://127.0.0.1:8000",
  [string]$SystemAddress = "udp://:14540",
  [int]$ConnectTimeoutSeconds = 10,
  [int]$ApiTimeoutSeconds = 30,
  [switch]$SkipDroneActions
)

$ErrorActionPreference = "Stop"

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

$BackendUrl = $BackendUrl.TrimEnd("/")

Write-Step "Backend health"
$health = Invoke-VimantraApi -Method "GET" -Path "/health"
Assert-Truthy ($health.status -eq "ok") "Backend health check failed."
Write-Host "Backend is healthy: $($health.service)"

Write-Step "Create verification mission"
$mission = Invoke-VimantraApi -Method "POST" -Path "/missions" -Body @{
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
}
Write-Host "Mission created: id=$($mission.id), waypoints=$($mission.waypoints.Count)"

Write-Step "Load verification mission"
$loadedMission = Invoke-VimantraApi -Method "GET" -Path "/missions/$($mission.id)"
Assert-Truthy ($loadedMission.id -eq $mission.id) "Mission load check failed."
Write-Host "Mission loaded: $($loadedMission.name)"

Write-Step "Initial drone status"
$initialStatus = Invoke-VimantraApi -Method "GET" -Path "/drone/status"
Write-Host "Connected: $($initialStatus.connected)"

Write-Step "Initial telemetry"
$initialTelemetry = Invoke-VimantraApi -Method "GET" -Path "/drone/telemetry"
Write-Host "Telemetry message: $($initialTelemetry.message)"

if ($SkipDroneActions) {
  Write-Step "PX4 actions skipped"
  Write-Host "Backend, mission storage, drone status, and telemetry endpoints are reachable."
  exit 0
}

Write-Step "Connect to PX4 SITL"
$connectedStatus = Invoke-VimantraApi -Method "POST" -Path "/drone/connect" -Body @{
  system_address = $SystemAddress
  timeout_seconds = $ConnectTimeoutSeconds
}
Assert-Truthy ($connectedStatus.connected -eq $true) "PX4 connection failed."
Write-Host "Connected to $($connectedStatus.system_address)"

Write-Step "Upload mission"
$uploadStatus = Invoke-VimantraApi -Method "POST" -Path "/missions/$($mission.id)/upload"
Assert-Truthy ($uploadStatus.uploaded -eq $true) "Mission upload failed."
Write-Host $uploadStatus.message

Write-Step "Arm drone"
$armStatus = Invoke-VimantraApi -Method "POST" -Path "/drone/arm"
Assert-Truthy ($armStatus.completed -eq $true) "Arm command failed."
Write-Host $armStatus.message

Write-Step "Start mission"
$startStatus = Invoke-VimantraApi -Method "POST" -Path "/drone/start-mission"
Assert-Truthy ($startStatus.completed -eq $true) "Start mission command failed."
Write-Host $startStatus.message

Write-Step "Telemetry snapshot"
$telemetry = Invoke-VimantraApi -Method "GET" -Path "/drone/telemetry"
Assert-Truthy ($telemetry.connected -eq $true) "Telemetry did not report a connected drone."
Write-Host "Position: $($telemetry.latitude), $($telemetry.longitude)"
Write-Host "Altitude: $($telemetry.altitude_meters) m"
Write-Host "Speed: $($telemetry.speed_meters_per_second) m/s"
Write-Host "Mode: $($telemetry.flight_mode)"
Write-Host "Mission progress: $($telemetry.mission_current)/$($telemetry.mission_total)"

Write-Step "Workflow complete"
Write-Host "Connect, upload, arm, start, and telemetry checks passed."
