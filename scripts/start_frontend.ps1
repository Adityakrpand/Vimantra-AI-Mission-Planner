$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
$frontendRoot = Join-Path $repoRoot "frontend"

if (-not $env:VITE_API_BASE_URL) {
  $env:VITE_API_BASE_URL = "http://127.0.0.1:8000"
}

Set-Location $frontendRoot
npm run dev
