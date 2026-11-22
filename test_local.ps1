# Same steps as the GitHub Action, locally.
# Usage: .\test_local.ps1 [N]  (first N products)   or   .\test_local.ps1 -Only "zoete aardappel,roodbaars"
param([int]$Limit = 0, [string]$Only = "")
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
if (-not (Test-Path .venv)) { & .\setup.ps1 }
$env:LIMIT = $Limit
$env:ONLY = $Only
$env:DEBUG = "1"
& .\.venv\Scripts\python.exe checker\check_promos.py
Write-Host "Preview: http://localhost:8000  (Ctrl+C to stop)"
Set-Location docs
& ..\.venv\Scripts\python.exe -m http.server 8000
