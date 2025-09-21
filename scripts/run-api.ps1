# Run the Data API from anywhere with correct PYTHONPATH + .env
$ErrorActionPreference = "Stop"

# Repo root = parent of this script
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

# Ensure ql_indicator and services are importable
$env:PYTHONPATH = "$Root\tools\python_indicator_clone\src;$Root"

# Load .env if present (KEY=VALUE lines)
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

# Sensible defaults
if (-not $env:QL_API_KEYS) { $env:QL_API_KEYS = "dev123" }
if (-not $env:QL_RPM) { $env:QL_RPM = "120" }

# Inject build metadata if not already set so /version is rich in local dev
if (-not $env:GIT_SHA) {
  try { $env:GIT_SHA = (git rev-parse --short HEAD) } catch { $env:GIT_SHA = "dev" }
}
if (-not $env:BUILT_AT) { $env:BUILT_AT = (Get-Date -AsUTC -Format o) }
if (-not $env:QL_VERSION) { $env:QL_VERSION = "0.1.1" }

Write-Host "PYTHONPATH = $($env:PYTHONPATH)"
Write-Host "Starting Data API on http://localhost:8080 ..."
uvicorn services.api.data_api:app --reload --port 8080
