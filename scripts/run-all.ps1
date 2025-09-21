# Starts both API and PTSM services concurrently and tails their health.
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

$env:PYTHONPATH = "$Root\tools\python_indicator_clone\src;$Root"
if (-not $env:QL_API_KEYS) { $env:QL_API_KEYS = "dev123" }

Write-Host "Launching QuantLens services..."

$api = Start-Process -PassThru powershell -ArgumentList "-NoLogo","-NoProfile","-Command","uvicorn services.api.data_api:app --host 127.0.0.1 --port 8080" 
$ptsm = Start-Process -PassThru powershell -ArgumentList "-NoLogo","-NoProfile","-Command","uvicorn services.ptsm.app:app --host 127.0.0.1 --port 8081" 

Write-Host "API PID: $($api.Id)  PTSM PID: $($ptsm.Id)"

Write-Host "Waiting for health ... (Ctrl+C to abort)"

$healthOk = $false
$attempt = 0
while (-not $healthOk -and $attempt -lt 30) {
  Start-Sleep -Seconds 1
  $attempt++
  $aStatus = '...'
  $pStatus = '...'
  try {
    $h1 = (Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8080/healthz -TimeoutSec 2).Content
    if ($h1 -match 'ok') { $aStatus = 'up' }
  } catch {}
  try {
    $h2 = (Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8081/healthz -TimeoutSec 2).Content
    if ($h2 -match 'ok') { $pStatus = 'up' }
  } catch {}
  if ($aStatus -eq 'up' -and $pStatus -eq 'up') { $healthOk = $true }
  Write-Host ("Attempt {0}: API={1} PTSM={2}" -f $attempt, $aStatus, $pStatus)
}

if ($healthOk) {
  Write-Host "Both services healthy." -ForegroundColor Green
} else {
  Write-Host "Services not healthy after $attempt attempts." -ForegroundColor Yellow
}

Write-Host "Press Enter to terminate both..."
[void][System.Console]::ReadLine()
try { Stop-Process -Id $api.Id -Force } catch {}
try { Stop-Process -Id $ptsm.Id -Force } catch {}
Write-Host "Stopped." -ForegroundColor Cyan
