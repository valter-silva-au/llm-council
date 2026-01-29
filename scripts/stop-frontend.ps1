# Stop the LLM Council frontend server
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$PidFile = "$ProjectRoot\scripts\.frontend.pid"

if (-not (Test-Path $PidFile)) {
    Write-Host "Frontend is not running (no PID file found)" -ForegroundColor Yellow
    exit 0
}

$ProcessId = Get-Content $PidFile
$Process = Get-Process -Id $ProcessId -ErrorAction SilentlyContinue

if (-not $Process) {
    Write-Host "Frontend process (PID: $ProcessId) is not running" -ForegroundColor Yellow
    Remove-Item $PidFile
    exit 0
}

Write-Host "Stopping frontend (PID: $ProcessId)..." -ForegroundColor Cyan

try {
    # Stop the npm process and its children (node/vite)
    Stop-Process -Id $ProcessId -Force -ErrorAction SilentlyContinue

    # Also kill any node processes on common Vite ports
    foreach ($Port in @(5173, 5174, 5175)) {
        $PortProcess = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue |
            Select-Object -ExpandProperty OwningProcess -Unique
        foreach ($p in $PortProcess) {
            Stop-Process -Id $p -Force -ErrorAction SilentlyContinue
        }
    }

    Remove-Item $PidFile -ErrorAction SilentlyContinue
    Write-Host "Frontend stopped successfully!" -ForegroundColor Green
}
catch {
    Write-Host "Error stopping frontend: $_" -ForegroundColor Red
    exit 1
}
