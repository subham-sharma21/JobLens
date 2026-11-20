$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location (Join-Path $scriptDir "frontend")
Write-Host "Starting JobLens Next.js Frontend on http://localhost:3000..." -ForegroundColor Cyan
npm run dev
