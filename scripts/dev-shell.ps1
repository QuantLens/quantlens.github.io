$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root
$env:PYTHONPATH = "$Root\tools\python_indicator_clone\src;$Root"
Write-Host "Dev shell ready. PYTHONPATH set to: $($env:PYTHONPATH)"
powershell
