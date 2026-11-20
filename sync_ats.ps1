$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir
$env:PYTHONPATH = $scriptDir
Write-Host "Running JobLens ATS Ingestion Engine (Greenhouse + Lever)..." -ForegroundColor Green
& ".\venv\Scripts\python.exe" -m backend.trackers.engine
