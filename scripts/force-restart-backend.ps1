# Force restart backend by killing all python processes and starting fresh
$ErrorActionPreference = "Continue"

$ScriptDir = $PSScriptRoot

Write-Host "=" * 60 -ForegroundColor Red
Write-Host "FORCE RESTART - Killing all backend processes" -ForegroundColor Red
Write-Host "=" * 60 -ForegroundColor Red
Write-Host ""

# Use the aggressive kill script
& "$ScriptDir\kill-backend.ps1"

# Check if port is really free
$StillUsed = Get-NetTCPConnection -LocalPort 8001 -ErrorAction SilentlyContinue
if ($StillUsed) {
    Write-Host ""
    Write-Host "ERROR: Port 8001 is still in use after cleanup!" -ForegroundColor Red
    Write-Host "Please manually close the process or restart your computer." -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Starting fresh backend..." -ForegroundColor Green
& "$ScriptDir\start-backend.ps1"

Write-Host ""
Write-Host "=" * 60 -ForegroundColor Green
Write-Host "Backend force restarted with fresh credentials!" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Green
