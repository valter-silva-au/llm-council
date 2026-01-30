# Check status of LLM Council services
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$BackendPidFile = "$ProjectRoot\scripts\.backend.pid"
$FrontendPidFile = "$ProjectRoot\scripts\.frontend.pid"

Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "LLM Council Status" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""

# Check backend
Write-Host "Backend:" -ForegroundColor Yellow
if (Test-Path $BackendPidFile) {
    $BackendPid = Get-Content $BackendPidFile
    $BackendProcess = Get-Process -Id $BackendPid -ErrorAction SilentlyContinue
    if ($BackendProcess) {
        Write-Host "  Status: Running" -ForegroundColor Green
        Write-Host "  PID: $BackendPid"
        Write-Host "  URL: http://localhost:8001"
        Write-Host "  Started: $($BackendProcess.StartTime)"
    } else {
        Write-Host "  Status: Not running (stale PID file)" -ForegroundColor Red
        Write-Host "  Run: .\scripts\stop-backend.ps1 to clean up"
    }
} else {
    Write-Host "  Status: Not running" -ForegroundColor Red
    Write-Host "  Run: .\scripts\start-backend.ps1 to start"
}

Write-Host ""

# Check frontend
Write-Host "Frontend:" -ForegroundColor Yellow
if (Test-Path $FrontendPidFile) {
    $FrontendPid = Get-Content $FrontendPidFile
    $FrontendProcess = Get-Process -Id $FrontendPid -ErrorAction SilentlyContinue
    if ($FrontendProcess) {
        Write-Host "  Status: Running" -ForegroundColor Green
        Write-Host "  PID: $FrontendPid"
        Write-Host "  URL: http://localhost:5173"
        Write-Host "  Started: $($FrontendProcess.StartTime)"
    } else {
        Write-Host "  Status: Not running (stale PID file)" -ForegroundColor Red
        Write-Host "  Run: .\scripts\stop-frontend.ps1 to clean up"
    }
} else {
    Write-Host "  Status: Not running" -ForegroundColor Red
    Write-Host "  Run: .\scripts\start-frontend.ps1 to start"
}

Write-Host ""
Write-Host "=" * 60 -ForegroundColor Cyan

# Show quick commands
Write-Host ""
Write-Host "Quick Commands:" -ForegroundColor Cyan
Write-Host "  Start all:   .\scripts\start-backend.ps1 ; .\scripts\start-frontend.ps1"
Write-Host "  Stop all:    .\scripts\stop-backend.ps1 ; .\scripts\stop-frontend.ps1"
Write-Host "  Restart all: .\scripts\restart-all.ps1"
Write-Host "  View logs:   Get-Content scripts\.backend.log -Tail 50 -Wait"
