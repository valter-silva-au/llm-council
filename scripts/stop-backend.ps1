# Stop the LLM Council backend server
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$PidFile = "$ProjectRoot\scripts\.backend.pid"

if (-not (Test-Path $PidFile)) {
    Write-Host "Backend is not running (no PID file found)" -ForegroundColor Yellow
    exit 0
}

$ProcessId = Get-Content $PidFile
$Process = Get-Process -Id $ProcessId -ErrorAction SilentlyContinue

if (-not $Process) {
    Write-Host "Backend process (PID: $ProcessId) is not running" -ForegroundColor Yellow
    Remove-Item $PidFile
    exit 0
}

Write-Host "Stopping backend (PID: $ProcessId)..." -ForegroundColor Cyan

try {
    # Stop the process and its children (uvicorn workers)
    Stop-Process -Id $ProcessId -Force -ErrorAction SilentlyContinue

    # Also kill any python processes on port 8001
    $PortProcess = Get-NetTCPConnection -LocalPort 8001 -ErrorAction SilentlyContinue |
        Select-Object -ExpandProperty OwningProcess -Unique
    foreach ($p in $PortProcess) {
        Stop-Process -Id $p -Force -ErrorAction SilentlyContinue
    }

    Remove-Item $PidFile -ErrorAction SilentlyContinue
    Write-Host "Backend stopped successfully!" -ForegroundColor Green
}
catch {
    Write-Host "Error stopping backend: $_" -ForegroundColor Red
    exit 1
}
