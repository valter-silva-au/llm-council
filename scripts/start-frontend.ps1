# Start the LLM Council frontend server
$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$FrontendDir = "$ProjectRoot\frontend"
$PidFile = "$ProjectRoot\scripts\.frontend.pid"

# Check if already running
if (Test-Path $PidFile) {
    $ExistingPid = Get-Content $PidFile
    $Process = Get-Process -Id $ExistingPid -ErrorAction SilentlyContinue
    if ($Process) {
        Write-Host "Frontend is already running (PID: $ExistingPid)" -ForegroundColor Yellow
        Write-Host "Use .\stop-frontend.ps1 to stop it first"
        exit 1
    }
    Remove-Item $PidFile
}

Write-Host "Starting LLM Council frontend..." -ForegroundColor Cyan

try {
    # Start npm directly using Start-Job for background execution
    # This avoids the cmd.exe console attachment issue
    $LogFile = "$ProjectRoot\scripts\.frontend.log"
    $ErrFile = "$ProjectRoot\scripts\.frontend.err"

    # Clear previous logs
    "" | Out-File $LogFile
    "" | Out-File $ErrFile

    # Start node/npm in a completely separate process
    $Process = Start-Process -FilePath "node.exe" `
        -ArgumentList "$FrontendDir\node_modules\vite\bin\vite.js", "--host" `
        -WorkingDirectory $FrontendDir `
        -PassThru -WindowStyle Hidden `
        -RedirectStandardOutput $LogFile `
        -RedirectStandardError $ErrFile

    # Save PID
    $Process.Id | Out-File $PidFile -NoNewline

    # Wait a moment for Vite to start
    Start-Sleep -Seconds 3

    if ($Process.HasExited) {
        Write-Host "Frontend failed to start. Check .frontend.err for details:" -ForegroundColor Red
        Get-Content $ErrFile | Select-Object -Last 10
        exit 1
    }

    # Try to find the port from the log
    $Port = "5173"
    $LogContent = Get-Content $LogFile -Raw -ErrorAction SilentlyContinue
    if ($LogContent -match "localhost:(\d+)") {
        $Port = $Matches[1]
    }

    Write-Host "Frontend started successfully!" -ForegroundColor Green
    Write-Host "  PID: $($Process.Id)"
    Write-Host "  URL: http://localhost:$Port"
    Write-Host "  Logs: scripts\.frontend.log"
}
catch {
    Write-Host "Error starting frontend: $_" -ForegroundColor Red
    exit 1
}
