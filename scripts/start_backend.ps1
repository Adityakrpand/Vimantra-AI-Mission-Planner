param(
  [string]$HostAddress = "",
  [int]$Port = 0
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
$backendRoot = Join-Path $repoRoot "backend"
$python = Join-Path $backendRoot ".venv\Scripts\python.exe"

if (-not $HostAddress) {
  $HostAddress = if ($env:VIMANTRA_API_HOST) { $env:VIMANTRA_API_HOST } else { "127.0.0.1" }
}
if ($Port -eq 0) {
  $Port = if ($env:VIMANTRA_API_PORT) { [int]$env:VIMANTRA_API_PORT } else { 8000 }
}

if (-not (Test-Path $python)) {
  Write-Host "Backend virtual environment not found at $python"
  Write-Host "Create it and install backend dependencies before starting the API."
  exit 1
}

Set-Location $backendRoot
& $python -m uvicorn app.main:create_app --factory --host $HostAddress --port $Port
