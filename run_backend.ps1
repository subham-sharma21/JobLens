$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir
$env:PYTHONPATH = $scriptDir
Write-Host "Starting JobLens FastAPI Backend on http://127.0.0.1:8000..." -ForegroundColor Cyan
& ".\venv\Scripts\python.exe" -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
