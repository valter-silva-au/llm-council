# Restart the LLM Council frontend server
$ErrorActionPreference = "Stop"

$ScriptDir = $PSScriptRoot

Write-Host "Restarting LLM Council frontend..." -ForegroundColor Cyan
Write-Host ""

# Stop if running
& "$ScriptDir\stop-frontend.ps1"

# Wait a moment
Start-Sleep -Seconds 1

# Start again
& "$ScriptDir\start-frontend.ps1"

Write-Host ""
Write-Host "Frontend restarted!" -ForegroundColor Green
