# Nuclear restart - completely kills Python and starts fresh
$ErrorActionPreference = "Continue"

Write-Host "===============================================" -ForegroundColor Red
Write-Host "HARD RESTART - Killing ALL Python processes" -ForegroundColor Red
Write-Host "===============================================" -ForegroundColor Red
Write-Host ""

# Step 1: Kill ALL Python processes (not just backend)
Write-Host "Step 1: Killing ALL Python processes..." -ForegroundColor Yellow
$PythonProcesses = Get-Process python* -ErrorAction SilentlyContinue
if ($PythonProcesses) {
    foreach ($proc in $PythonProcesses) {
        Write-Host "  Killing Python PID: $($proc.Id)" -ForegroundColor Red
        Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
    }
    Write-Host "  Killed $($PythonProcesses.Count) Python process(es)" -ForegroundColor Green
} else {
    Write-Host "  No Python processes running" -ForegroundColor Gray
}

# Step 2: Clean up PID file
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$PidFile = "$ProjectRoot\scripts\.backend.pid"
if (Test-Path $PidFile) {
    Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
    Write-Host "  Removed PID file" -ForegroundColor Green
}

# Step 3: Wait for ports to release
Write-Host ""
Write-Host "Step 2: Waiting 5 seconds for ports to release..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Step 4: Verify port 8001 is free
Write-Host ""
Write-Host "Step 3: Verifying port 8001 is free..." -ForegroundColor Yellow
$PortInUse = Get-NetTCPConnection -LocalPort 8001 -ErrorAction SilentlyContinue
if ($PortInUse) {
    Write-Host "  ERROR: Port 8001 still in use!" -ForegroundColor Red
    foreach ($conn in $PortInUse) {
        $ProcessId = $conn.OwningProcess
        $proc = Get-Process -Id $ProcessId -ErrorAction SilentlyContinue
        Write-Host "    Held by: $($proc.Name) (PID: $ProcessId)" -ForegroundColor Yellow
        Write-Host "    Force killing..." -ForegroundColor Red
        Stop-Process -Id $ProcessId -Force -ErrorAction SilentlyContinue
    }
    Start-Sleep -Seconds 2
} else {
    Write-Host "  Port 8001 is FREE!" -ForegroundColor Green
}

# Step 5: Start fresh backend
Write-Host ""
Write-Host "Step 4: Starting FRESH backend with NEW code..." -ForegroundColor Green
Write-Host ""
& "$PSScriptRoot\start-backend.ps1"

Write-Host ""
Write-Host "===============================================" -ForegroundColor Green
Write-Host "Backend restarted with FRESH code!" -ForegroundColor Green
Write-Host "All Python modules will be reloaded from disk" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Now try your query again in the UI" -ForegroundColor Cyan
Write-Host "You should see [SEARCH] logs in the output" -ForegroundColor Cyan
