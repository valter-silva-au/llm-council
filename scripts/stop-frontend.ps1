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
    # Get child processes before killing parent
    $ChildProcesses = Get-CimInstance Win32_Process | Where-Object { $_.ParentProcessId -eq $ProcessId }

    # Stop the main process
    Stop-Process -Id $ProcessId -Force -ErrorAction SilentlyContinue

    # Stop any child processes (vite spawns child node processes)
    foreach ($child in $ChildProcesses) {
        Stop-Process -Id $child.ProcessId -Force -ErrorAction SilentlyContinue
    }

    # Clean up any orphaned node processes on Vite ports
    foreach ($Port in @(5173, 5174, 5175)) {
        try {
            $Connections = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
            foreach ($conn in $Connections) {
                $p = $conn.OwningProcess
                # Only kill node.exe processes, not other things
                $proc = Get-Process -Id $p -ErrorAction SilentlyContinue
                if ($proc -and $proc.Name -eq "node") {
                    Stop-Process -Id $p -Force -ErrorAction SilentlyContinue
                }
            }
        } catch {
            # Ignore errors - port might not be in use
        }
    }

    Remove-Item $PidFile -ErrorAction SilentlyContinue
    Write-Host "Frontend stopped successfully!" -ForegroundColor Green
}
catch {
    Write-Host "Error stopping frontend: $_" -ForegroundColor Red
    exit 1
}
