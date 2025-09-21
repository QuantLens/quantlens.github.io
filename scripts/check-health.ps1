param(
  [string]$Url = 'http://127.0.0.1:8080/healthz',
  [int]$TimeoutSeconds = 2,
  [int]$Retries = 10,
  [int]$DelaySeconds = 1,
  [switch]$Quiet
)

$ErrorActionPreference = 'Stop'

function Write-Info($msg){ if(-not $Quiet){ Write-Host $msg } }

for($i=1; $i -le $Retries; $i++){
  try {
    $resp = Invoke-WebRequest -UseBasicParsing -TimeoutSec $TimeoutSeconds -Uri $Url
    if($resp.Content -match 'ok'){
      Write-Info ("Healthy after attempt {0}" -f $i)
      exit 0
    } else {
      $snippet = $resp.Content.Substring(0, [Math]::Min(80,$resp.Content.Length))
      Write-Info ("Attempt {0}: unhealthy content: {1}" -f $i, $snippet)
    }
  } catch {
    Write-Info ("Attempt {0}: {1}" -f $i, $_)
  }
  Start-Sleep -Seconds $DelaySeconds
}
Write-Info "Unhealthy after $Retries attempts"
exit 1
