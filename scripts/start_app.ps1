$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
$backendRoot = Join-Path $repoRoot "backend"
$frontendRoot = Join-Path $repoRoot "frontend"
$backendScript = Join-Path $PSScriptRoot "start_backend.ps1"
$frontendScript = Join-Path $PSScriptRoot "start_frontend.ps1"
$backendHost = if ($env:VIMANTRA_API_HOST) { $env:VIMANTRA_API_HOST } else { "127.0.0.1" }
$backendPort = if ($env:VIMANTRA_API_PORT) { $env:VIMANTRA_API_PORT } else { "8000" }

Start-Process `
  -FilePath "powershell.exe" `
  -ArgumentList @("-NoExit", "-ExecutionPolicy", "Bypass", "-File", $backendScript) `
  -WorkingDirectory $backendRoot `
  -WindowStyle Normal

Start-Process `
  -FilePath "powershell.exe" `
  -ArgumentList @("-NoExit", "-ExecutionPolicy", "Bypass", "-File", $frontendScript) `
  -WorkingDirectory $frontendRoot `
  -WindowStyle Normal

Write-Host "Vimantra services are starting."
Write-Host "Frontend: http://127.0.0.1:5173"
Write-Host "Backend:  http://$($backendHost):$($backendPort)"
