param(
  [string]$Api = "http://127.0.0.1:8080",
  [string]$Ptsm = "http://127.0.0.1:8081",
  [string]$Key = "dev123"
)
$ErrorActionPreference = 'Stop'

function Section($t){ Write-Host "== $t ==" -ForegroundColor Cyan }

Section "Health"
Invoke-WebRequest "$Api/healthz" | Out-Null
Invoke-WebRequest "$Ptsm/healthz" | Out-Null
Write-Host "OK" -ForegroundColor Green

Section "Version"
(Invoke-WebRequest "$Api/version").Content
(Invoke-WebRequest "$Ptsm/version").Content

Section "Fetch BTC/USDT (15m head_only)"
Invoke-WebRequest "$Api/v1/fetch?symbol=BTC/USDT&tf=15m&limit=5&head_only=true" -Headers @{"x-api-key"=$Key} | Out-Null
Write-Host "OK" -ForegroundColor Green

Section "Infer AAPL (1h)"
$body = @{ symbol="AAPL"; tf="1h"; limit=50 } | ConvertTo-Json
(Invoke-WebRequest "$Ptsm/v1/infer" -Method POST -Headers @{"x-api-key"=$Key; "Content-Type"="application/json" } -Body $body).Content
