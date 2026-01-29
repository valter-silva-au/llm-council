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
    # Start the frontend using cmd.exe to run npm
    $Process = Start-Process -FilePath "cmd.exe" `
        -ArgumentList "/c", "cd /d `"$FrontendDir`" && npm run dev" `
        -PassThru -NoNewWindow -RedirectStandardOutput "$ProjectRoot\scripts\.frontend.log" `
        -RedirectStandardError "$ProjectRoot\scripts\.frontend.err"

    # Save PID
    $Process.Id | Out-File $PidFile -NoNewline

    # Wait a moment for Vite to start
    Start-Sleep -Seconds 4

    if ($Process.HasExited) {
        Write-Host "Frontend failed to start. Check .frontend.err for details:" -ForegroundColor Red
        Get-Content "$ProjectRoot\scripts\.frontend.err" | Select-Object -Last 10
        exit 1
    }

    # Try to find the port from the log
    $Port = "5173"
    $LogContent = Get-Content "$ProjectRoot\scripts\.frontend.log" -Raw -ErrorAction SilentlyContinue
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
