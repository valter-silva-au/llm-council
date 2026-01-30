# Aggressively kill all backend processes
$ErrorActionPreference = "Continue"

Write-Host "Killing all backend processes..." -ForegroundColor Yellow

# Method 1: Kill by port 8001
Write-Host "Checking port 8001..." -ForegroundColor Cyan
try {
    $Connections = Get-NetTCPConnection -LocalPort 8001 -ErrorAction SilentlyContinue
    foreach ($conn in $Connections) {
        $ProcessId = $conn.OwningProcess
        $proc = Get-Process -Id $ProcessId -ErrorAction SilentlyContinue
        if ($proc) {
            Write-Host "  Killing $($proc.Name) (PID: $ProcessId)" -ForegroundColor Red
            Stop-Process -Id $ProcessId -Force -ErrorAction SilentlyContinue
        }
    }
} catch {
    Write-Host "  No active connections on port 8001"
}

# Method 2: Kill by PID file
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$PidFile = "$ProjectRoot\scripts\.backend.pid"
if (Test-Path $PidFile) {
    $ProcessId = Get-Content $PidFile
    Write-Host "  Killing PID from file: $ProcessId" -ForegroundColor Red
    Stop-Process -Id $ProcessId -Force -ErrorAction SilentlyContinue
    Remove-Item $PidFile -ErrorAction SilentlyContinue
}

# Method 3: Kill all python processes running backend.main
Write-Host "Checking for backend.main processes..." -ForegroundColor Cyan
$PythonProcesses = Get-Process python* -ErrorAction SilentlyContinue
foreach ($proc in $PythonProcesses) {
    try {
        $cmdline = (Get-CimInstance Win32_Process -Filter "ProcessId = $($proc.Id)").CommandLine
        if ($cmdline -and ($cmdline -like "*backend.main*" -or $cmdline -like "*uvicorn*")) {
            Write-Host "  Killing $($proc.Name) (PID: $($proc.Id))" -ForegroundColor Red
            Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
        }
    } catch {
        # Ignore errors
    }
}

Write-Host ""
Write-Host "Waiting 5 seconds for ports to release..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Verify port is free
Write-Host "Verifying port 8001 is free..." -ForegroundColor Cyan
$StillUsed = Get-NetTCPConnection -LocalPort 8001 -ErrorAction SilentlyContinue
if ($StillUsed) {
    Write-Host "  WARNING: Port 8001 is still in use!" -ForegroundColor Red
    foreach ($conn in $StillUsed) {
        $ProcessId = $conn.OwningProcess
        $proc = Get-Process -Id $ProcessId -ErrorAction SilentlyContinue
        Write-Host "  Still held by: $($proc.Name) (PID: $ProcessId)" -ForegroundColor Yellow
    }
} else {
    Write-Host "  Port 8001 is free!" -ForegroundColor Green
}
