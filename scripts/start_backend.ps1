param(
  [string]$HostAddress = "127.0.0.1",
  [int]$Port = 8000
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
$backendRoot = Join-Path $repoRoot "backend"
$python = Join-Path $backendRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $python)) {
  Write-Host "Backend virtual environment not found at $python"
  Write-Host "Create it and install backend dependencies before starting the API."
  exit 1
}

Set-Location $backendRoot
& $python -m uvicorn app.main:create_app --factory --host $HostAddress --port $Port
