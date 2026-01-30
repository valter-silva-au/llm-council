# Restart both backend and frontend
$ErrorActionPreference = "Stop"

$ScriptDir = $PSScriptRoot

Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "Restarting LLM Council (Backend + Frontend)" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""

# Restart backend
Write-Host "[1/2] Backend..." -ForegroundColor Yellow
& "$ScriptDir\restart-backend.ps1"

Write-Host ""
Write-Host "[2/2] Frontend..." -ForegroundColor Yellow
& "$ScriptDir\restart-frontend.ps1"

Write-Host ""
Write-Host "=" * 60 -ForegroundColor Green
Write-Host "All services restarted successfully!" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Green
Write-Host ""
Write-Host "Backend:  http://localhost:8001" -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:5173" -ForegroundColor Cyan
Write-Host ""
Write-Host "Logs are in: scripts\.backend.log and scripts\.frontend.log"
