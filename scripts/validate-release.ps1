param(
  [string]$Api = "http://127.0.0.1:8080",
  [string]$Ptsm = "http://127.0.0.1:8081",
  [string]$Key = "dev123"
)
$ErrorActionPreference = "Stop"
function Assert($cond,$msg){ if(-not $cond){ throw $msg } }

Write-Host "== QuantLens Release Validation ==" -ForegroundColor Cyan

# Health & Version
$h1 = Invoke-WebRequest "$Api/healthz"
$h2 = Invoke-WebRequest "$Ptsm/healthz"
Assert ($h1.StatusCode -eq 200 -and $h2.StatusCode -eq 200) "Health check failed"
$v1 = (Invoke-WebRequest "$Api/version").Content | ConvertFrom-Json
$v2 = (Invoke-WebRequest "$Ptsm/version").Content | ConvertFrom-Json
Assert ($v1.version -and $v1.git_sha -and $v1.built_at) "API version metadata missing"
Assert ($v2.version -and $v2.git_sha -and $v2.built_at) "PTSM version metadata missing"

# OpenAPI security present
$open = (Invoke-WebRequest "$Api/openapi.json").Content
Assert ($open -match "ApiKeyAuth") "OpenAPI missing ApiKeyAuth"

# Metrics gating
$rA = (Invoke-WebRequest "$Api/metrics" -ErrorAction SilentlyContinue).StatusCode
$rP = (Invoke-WebRequest "$Ptsm/metrics" -ErrorAction SilentlyContinue).StatusCode
Assert ($rA -eq 401 -and $rP -eq 401) "Metrics should be gated (401)"
$okA = Invoke-WebRequest "$Api/metrics" -Headers @{ 'x-api-key' = $Key }
$okP = Invoke-WebRequest "$Ptsm/metrics" -Headers @{ 'x-api-key' = $Key }
Assert ($okA.Content -match '# HELP' -and $okP.Content -match '# HELP') "Metrics not exposed after auth"

# Fetch + rate limit headers (accept 200 or 400; only assert headers on 200)
$resp = Invoke-WebRequest "$Api/v1/fetch?symbol=AAPL&tf=1d&limit=1" -Headers @{ 'x-api-key' = $Key } -ErrorAction SilentlyContinue
if ($resp.StatusCode -eq 200) {
  Assert $resp.Headers['X-RateLimit-Limit'] "Missing X-RateLimit-Limit"
  Assert $resp.Headers['X-RateLimit-Remaining'] "Missing X-RateLimit-Remaining"
  Assert $resp.Headers['X-RateLimit-Reset'] "Missing X-RateLimit-Reset"
}

Write-Host "✅ Release validation passed." -ForegroundColor Green
