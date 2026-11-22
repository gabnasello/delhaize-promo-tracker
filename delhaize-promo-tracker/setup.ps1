# Isolated environment in .\.venv (system Python untouched)
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
python -m venv .venv
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt
& .\.venv\Scripts\python.exe -m playwright install chromium
Write-Host "Done."
