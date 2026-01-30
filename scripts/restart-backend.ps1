# Restart the LLM Council backend server
$ErrorActionPreference = "Stop"

$ScriptDir = $PSScriptRoot

Write-Host "Restarting LLM Council backend..." -ForegroundColor Cyan
Write-Host ""

# Stop if running
& "$ScriptDir\stop-backend.ps1"

# Wait a moment
Start-Sleep -Seconds 1

# Start again
& "$ScriptDir\start-backend.ps1"

Write-Host ""
Write-Host "Backend restarted!" -ForegroundColor Green
Write-Host "Updated code is now active."
