# Run the PTSM service with correct PYTHONPATH + .env
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

$env:PYTHONPATH = "$Root\tools\python_indicator_clone\src;$Root"

$EnvFile = Join-Path $Root ".env"
if (Test-Path $EnvFile) {
  Get-Content $EnvFile | ForEach-Object {
    if ($_ -match '^\s*#') { return }
    if ($_ -match '^\s*$') { return }
    $kv = $_.Split('=',2)
    if ($kv.Count -eq 2) {
      $k = $kv[0].Trim()
      $v = $kv[1].Trim()
      if (-not [string]::IsNullOrEmpty($k)) { Set-Item -Path Env:$k -Value $v }
    }
  }
}

if (-not $env:QL_API_KEYS) { $env:QL_API_KEYS = "dev123" }
if (-not $env:QL_MODEL_PATH) {
  $env:QL_MODEL_PATH = "$Root\models\ptsm"
  New-Item -ItemType Directory -Force -Path $env:QL_MODEL_PATH | Out-Null
}

# Inject build metadata if not already present
if (-not $env:GIT_SHA) {
  try { $env:GIT_SHA = (git rev-parse --short HEAD) } catch { $env:GIT_SHA = "dev" }
}
if (-not $env:BUILT_AT) { $env:BUILT_AT = (Get-Date -AsUTC -Format o) }
if (-not $env:QL_VERSION) { $env:QL_VERSION = "0.1.1" }

Write-Host "PYTHONPATH = $($env:PYTHONPATH)"
Write-Host "Starting PTSM on http://localhost:8081 ..."
uvicorn services.ptsm.app:app --reload --port 8081
